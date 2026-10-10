"""Sam vendored skills: structure, licenses, no FMP network path, deps isolated."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "sam_core" / "vendor"
PROFILE = ROOT / "config" / "agents" / "sam.profile.json"


def _profile():
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def test_vendor_items_are_inactive_and_point_to_existing_paths():
    items = _profile()["skill_vendor"]["items"]
    vendored = [i for i in items if i["activation"] == "vendored_inactive"]
    assert len(vendored) == 8
    for item in vendored:
        assert (ROOT / item["vendor_path"]).is_dir(), item["id"]


def test_vendor_has_license_files():
    assert (VENDOR / "tradermonty-claude-trading-skills" / "LICENSE").is_file()
    assert (VENDOR / "riskkit" / "LICENSE").is_file()
    assert (VENDOR / "cot_reports" / "LICENSE").is_file()


def test_fmp_network_adapter_removed_from_vendor():
    assert list(VENDOR.rglob("fmp_price_adapter*")) == []


def test_no_order_execution_code_in_vendor():
    banned = ("order_send", "place_order", "create_order", "submit_order")
    for path in VENDOR.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in banned:
            assert token not in text, f"{token} in {path.relative_to(ROOT)}"


def test_sam_deps_not_in_core_requirements():
    core = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "pandas-market-calendars" not in core
    assert "beautifulsoup4" not in core
    assert (ROOT / "requirements-sam.txt").is_file()
