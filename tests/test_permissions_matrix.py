"""docs/PERMISSIONS_MATRIX.md має відповідати профілям агентів (генерується tools/export_permissions.py)."""

from pathlib import Path

from tools import export_permissions

ROOT = Path(__file__).resolve().parents[1]


def test_permissions_matrix_is_up_to_date_with_profiles() -> None:
    assert export_permissions.OUT.read_text(encoding="utf-8") == export_permissions.build()


def test_matrix_lists_every_profile() -> None:
    text = export_permissions.OUT.read_text(encoding="utf-8")
    for path in (ROOT / "config" / "agents").glob("*.profile.json"):
        agent_id = path.name.split(".")[0]
        assert f"| {agent_id} |" in text
