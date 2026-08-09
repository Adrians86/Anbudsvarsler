"""CI-test: leverandor/ skal aldri importere fra oppdragsgiver/."""
from pathlib import Path


def test_leverandor_never_imports_oppdragsgiver():
    root = Path(__file__).parent.parent
    leverandor_dir = root / "leverandor"
    violations = []
    for f in leverandor_dir.rglob("*.py"):
        content = f.read_text(encoding="utf-8")
        if "from oppdragsgiver" in content or "import oppdragsgiver" in content:
            violations.append(str(f))
    assert violations == [], f"Import-vegg brutt i: {violations}"
