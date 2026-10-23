import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _vault_policies():
    spec = importlib.util.spec_from_file_location("vault_policies_least_privilege_test", ROOT / "tools/vault_policies.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_acl_capabilities_are_read_only_except_token_self_renewal():
    policies = _vault_policies().build_policies()
    block_pattern = re.compile(
        r'path "([^"]+)"\s*\{\s*capabilities = \[([^\]]*)\]\s*\}', re.MULTILINE
    )

    for policy_name, policy_text in policies.items():
        blocks = {path: {cap.strip().strip('"') for cap in caps.split(",")} for path, caps in block_pattern.findall(policy_text)}
        assert "auth/token/lookup-self" in blocks
        assert "auth/token/renew-self" in blocks
        assert blocks["auth/token/lookup-self"] == {"read"}
        assert blocks["auth/token/renew-self"] == {"update"}
        for path, capabilities in blocks.items():
            if path in {"auth/token/lookup-self", "auth/token/renew-self"}:
                continue
            assert capabilities <= {"read", "list"}, f"{policy_name} grants write access to {path}"
            assert "read" in capabilities
            if "/metadata/" in path:
                assert "list" in capabilities
            else:
                assert capabilities == {"read"}
