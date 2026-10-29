"""One-time (idempotent) Garage setup: layout, buckets, keys, grants, quotas, lifecycle.

Run on the server as root after ``docker compose up -d garage``::

    python3 tools/garage_setup.py            # dry run: prints the plan
    python3 tools/garage_setup.py --apply    # creates what is missing, stores keys in Vault

Reads GARAGE_ADMIN_TOKEN from /opt/syndicate/.env and the Vault operator token the
same way ``scripts/syndicate_vault.py`` does. Prints no secret: secret access keys go
straight to Vault ``agents/<id>/storage`` and are never written to stdout or disk.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
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

ENV_FILE = Path("/opt/syndicate/.env")
NODE_CAPACITY = 150 * 1024 ** 3  # layout capacity; buckets are capped by quotas


def _env(name: str) -> str:
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(f"{name} is not set in {ENV_FILE}")


def _garage_ip() -> str:
    out = subprocess.run(
        ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}", "syndicate-garage-1"],
        check=True, capture_output=True, text=True,
    ).stdout.split()
    if not out:
        raise SystemExit("garage container has no IP: is it running?")
    return out[0]


class Admin:
    def __init__(self, base: str, token: str) -> None:
        self.base, self.token = base, token

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        req = urllib.request.Request(f"{self.base}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {self.token}",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
        return json.loads(raw) if raw else None


def ensure_layout(admin: Admin, apply: bool) -> None:
    layout = admin.call("GET", "/v2/GetClusterLayout")
    if layout["roles"]:
        print(f"layout: ok (version {layout['version']})")
        return
    node = admin.call("GET", "/v2/GetClusterStatus")["nodes"][0]["id"]
    print(f"layout: assign node {node[:12]}… zone dc1, capacity {NODE_CAPACITY // 1024 ** 3} GiB")
    if apply:
        admin.call("POST", "/v2/UpdateClusterLayout",
                   {"roles": [{"id": node, "zone": "dc1", "capacity": NODE_CAPACITY, "tags": ["syndicate"]}]})
        admin.call("POST", "/v2/ApplyClusterLayout", {"version": layout["version"] + 1})


def ensure_bucket(admin: Admin, name: str, quota: int, apply: bool) -> Optional[str]:
    try:
        bucket = admin.call("GET", f"/v2/GetBucketInfo?globalAlias={name}")
        print(f"bucket {name}: exists")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        print(f"bucket {name}: create, quota {quota // 1024 ** 3} GiB")
        if not apply:
            return None
        bucket = admin.call("POST", "/v2/CreateBucket", {"globalAlias": name})
    if apply:
        admin.call("POST", f"/v2/UpdateBucket?id={bucket['id']}", {"quotas": {"maxSize": quota, "maxObjects": None}})
    return bucket["id"]


def ensure_key(admin: Admin, agent_id: str, apply: bool) -> Optional[Dict[str, Any]]:
    name = bucket_for(agent_id)
    keys = [k for k in admin.call("GET", "/v2/ListKeys") if k.get("name") == name]
    if keys:
        print(f"key {name}: exists")
        return admin.call("GET", f"/v2/GetKeyInfo?id={keys[0]['id']}&showSecretKey=true")
    print(f"key {name}: create")
    return admin.call("POST", "/v2/CreateKey", {"name": name, "neverExpires": True}) if apply else None


def grant(admin: Admin, bucket_id: str, key_id: str, read: bool, write: bool, owner: bool) -> None:
    admin.call("POST", "/v2/AllowBucketKey", {"bucketId": bucket_id, "accessKeyId": key_id,
                                              "permissions": {"read": read, "write": write, "owner": owner}})


def set_tmp_expiry(key: Dict[str, Any], bucket: str, endpoint: str) -> None:
    import boto3

    s3 = boto3.client("s3", endpoint_url=endpoint, region_name="garage",
                      aws_access_key_id=key["accessKeyId"], aws_secret_access_key=key["secretAccessKey"])
    s3.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration={"Rules": [
        {"ID": "tmp-expiry", "Status": "Enabled", "Filter": {"Prefix": TMP_PREFIX}, "Expiration": {"Days": TMP_DAYS}},
        {"ID": "abort-uploads", "Status": "Enabled", "Filter": {"Prefix": ""},
         "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}},
    ]})


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="create what is missing and store keys in Vault")
    args = parser.parse_args(argv)
    ip = _garage_ip()
    admin = Admin(f"http://{ip}:3903", _env("GARAGE_ADMIN_TOKEN"))
    ensure_layout(admin, args.apply)
    shared_id = ensure_bucket(admin, SHARED_BUCKET, QUOTA_SHARED_BYTES, args.apply)
    put_secret = None
    if args.apply:
        sys.path.insert(0, str(ROOT / "scripts"))
        from syndicate_vault import put_secret  # type: ignore[no-redef]
    for agent_id in DIRECTOR_IDS:
        bucket_id = ensure_bucket(admin, bucket_for(agent_id), QUOTA_AGENT_BYTES, args.apply)
        key = ensure_key(admin, agent_id, args.apply)
        if not args.apply or key is None or bucket_id is None or shared_id is None:
            continue
        key_id = key["accessKeyId"]
        grant(admin, bucket_id, key_id, read=True, write=True, owner=True)
        grant(admin, shared_id, key_id, read=True, write=agent_id in SHARED_WRITERS, owner=False)
        set_tmp_expiry(key, bucket_for(agent_id), f"http://{ip}:3900")
        put_secret(f"agents/{agent_id}/{STORAGE}",
                   {"access_key_id": key_id, "secret_access_key": key["secretAccessKey"],
                    "bucket": bucket_for(agent_id), "endpoint": "http://garage:3900"})
        print(f"grants {agent_id}: own rw, shared {'rw' if agent_id in SHARED_WRITERS else 'r'}, tmp/ {TMP_DAYS}d; key in Vault")
    print("done" if args.apply else "dry run: nothing changed (use --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
