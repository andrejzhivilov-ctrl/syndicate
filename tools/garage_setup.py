"""One-time (idempotent) Garage setup: layout, buckets, keys, grants, quotas, tmp/ expiry.

Run on the server as root after ``docker compose up -d garage``::

    python3 tools/garage_setup.py            # dry run: prints the plan
    python3 tools/garage_setup.py --apply    # creates what is missing, stores keys in Vault

Admin calls go through ``garage json-api`` inside the container, i.e. over
Garage's own authenticated and encrypted RPC. There is no admin HTTP API and no
admin token at all, so nothing secret crosses the Docker network in clear text.

Grants are *reconciled*: what an agent must not have (e.g. write on the shared
bucket) is explicitly denied on every run, not only left out.

Secret access keys go straight to Vault ``agents/<id>/storage`` (operator token,
as in ``scripts/syndicate_vault.py``) and are never printed or written to disk.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent_storage import (  # noqa: E402
    QUOTA_AGENT_BYTES,
    QUOTA_SHARED_BYTES,
    SHARED_BUCKET,
    SHARED_WRITERS,
    TMP_DAYS,
    TMP_PREFIX,
    bucket_for,
)
from src.vault_paths import DIRECTOR_IDS, STORAGE  # noqa: E402

CONTAINER = "syndicate-garage-1"
NODE_CAPACITY = 150 * 1024 ** 3  # layout capacity; buckets are capped by quotas
LIFECYCLE = [
    {"ID": "tmp-expiry", "Status": "Enabled", "Filter": {"Prefix": TMP_PREFIX}, "Expiration": {"Days": TMP_DAYS}},
    {"ID": "abort-uploads", "Status": "Enabled", "Filter": {"Prefix": ""},
     "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}},
]


class GarageError(RuntimeError):
    pass


def api(endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Any:
    """Call the admin API through the CLI's RPC channel; stdout is JSON, logs go to stderr."""
    proc = subprocess.run(["docker", "exec", "-i", CONTAINER, "/garage", "json-api", endpoint, "-"],
                          input=json.dumps(payload), capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        detail = next((line for line in proc.stderr.splitlines() if line.startswith("Error")), "unknown error")
        raise GarageError(f"{endpoint}: {detail}")
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def wait_healthy(timeout_s: int = 60) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if api("GetClusterHealth").get("status") == "healthy":
            return
        time.sleep(2)
    raise GarageError("cluster did not become healthy after the layout change")


def ensure_layout(apply: bool) -> bool:
    """True when buckets can be queried (a layout exists or was just applied)."""
    layout = api("GetClusterLayout")
    if layout["roles"]:
        print(f"layout: ok (version {layout['version']})")
        return True
    node = api("GetClusterStatus")["nodes"][0]["id"]
    print(f"layout: assign node {node[:12]}… zone dc1, capacity {NODE_CAPACITY // 1024 ** 3} GiB")
    if not apply:
        return False  # a fresh cluster answers nothing about buckets until it has a layout
    api("UpdateClusterLayout", {"roles": [{"id": node, "zone": "dc1", "capacity": NODE_CAPACITY,
                                           "tags": ["syndicate"]}]})
    api("ApplyClusterLayout", {"version": layout["version"] + 1})
    wait_healthy()
    return True


def plan_fresh_cluster() -> None:
    for name, quota in [(SHARED_BUCKET, QUOTA_SHARED_BYTES)] + [(bucket_for(a), QUOTA_AGENT_BYTES) for a in DIRECTOR_IDS]:
        print(f"bucket {name}: create, quota {quota // 1024 ** 3} GiB, {TMP_PREFIX} expires in {TMP_DAYS} d")
    for agent_id in DIRECTOR_IDS:
        print(f"key {bucket_for(agent_id)}: create; own rw, shared "
              f"{'rw' if agent_id in SHARED_WRITERS else 'r'}; key to Vault agents/{agent_id}/{STORAGE}")


def ensure_bucket(name: str, quota: int, apply: bool) -> Optional[str]:
    try:
        bucket = api("GetBucketInfo", {"globalAlias": name})
        print(f"bucket {name}: exists")
    except GarageError as exc:
        if "NoSuchBucket" not in str(exc):
            raise
        print(f"bucket {name}: create, quota {quota // 1024 ** 3} GiB, {TMP_PREFIX} expires in {TMP_DAYS} d")
        if not apply:
            return None
        bucket = api("CreateBucket", {"globalAlias": name})
    if apply:
        api("UpdateBucket", {"id": bucket["id"], "body": {"quotas": {"maxSize": quota, "maxObjects": None},
                                                          "lifecycleRules": LIFECYCLE}})
    return bucket["id"]


def ensure_key(agent_id: str, apply: bool) -> Optional[Dict[str, Any]]:
    name = bucket_for(agent_id)
    keys = [k for k in api("ListKeys") if k.get("name") == name]
    if keys:
        print(f"key {name}: exists")
        return api("GetKeyInfo", {"id": keys[0]["id"], "showSecretKey": True})
    print(f"key {name}: create")
    return api("CreateKey", {"name": name, "neverExpires": True}) if apply else None


def reconcile(bucket_id: str, key_id: str, *, read: bool, write: bool, owner: bool) -> None:
    """Allow what is wanted and explicitly deny the rest (a rerun also revokes)."""
    wanted = {"read": read, "write": write, "owner": owner}
    allow = {k: v for k, v in wanted.items() if v}
    deny = {k: True for k, v in wanted.items() if not v}
    if allow:
        api("AllowBucketKey", {"bucketId": bucket_id, "accessKeyId": key_id, "permissions": allow})
    if deny:
        api("DenyBucketKey", {"bucketId": bucket_id, "accessKeyId": key_id, "permissions": deny})


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="create what is missing and store keys in Vault")
    args = parser.parse_args(argv)
    if not ensure_layout(args.apply):
        plan_fresh_cluster()
        print("dry run: nothing changed (use --apply)")
        return 0
    shared_id = ensure_bucket(SHARED_BUCKET, QUOTA_SHARED_BYTES, args.apply)
    put_secret = None
    if args.apply:
        sys.path.insert(0, str(ROOT / "scripts"))
        from syndicate_vault import put_secret  # type: ignore[no-redef]
    for agent_id in DIRECTOR_IDS:
        bucket_id = ensure_bucket(bucket_for(agent_id), QUOTA_AGENT_BYTES, args.apply)
        key = ensure_key(agent_id, args.apply)
        if not args.apply or key is None or bucket_id is None or shared_id is None:
            continue
        key_id = key["accessKeyId"]
        reconcile(bucket_id, key_id, read=True, write=True, owner=False)
        reconcile(shared_id, key_id, read=True, write=agent_id in SHARED_WRITERS, owner=False)
        put_secret(f"agents/{agent_id}/{STORAGE}",
                   {"access_key_id": key_id, "secret_access_key": key["secretAccessKey"],
                    "bucket": bucket_for(agent_id), "endpoint": "http://garage:3900"})
        print(f"grants {agent_id}: own rw, shared {'rw' if agent_id in SHARED_WRITERS else 'r'}; key in Vault")
    print("done" if args.apply else "dry run: nothing changed (use --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
