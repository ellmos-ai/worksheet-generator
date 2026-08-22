from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_uses_pep639_license_metadata() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert re.search(
        r'^requires = \["setuptools>=77\.0\.3"\]$', pyproject, re.MULTILINE
    )
    assert re.search(r'^license = "MIT"$', pyproject, re.MULTILINE)
    assert re.search(r'^license-files = \["LICENSE"\]$', pyproject, re.MULTILINE)
    assert '"License ::' not in pyproject
