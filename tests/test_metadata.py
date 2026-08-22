import json
from pathlib import Path
import re

from worksheet_generator import cli


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_uses_pep639_license_metadata() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert re.search(
        r'^requires = \["setuptools>=77\.0\.3"\]$', pyproject, re.MULTILINE
    )
    assert re.search(r'^license = "MIT"$', pyproject, re.MULTILINE)
    assert re.search(r'^license-files = \["LICENSE"\]$', pyproject, re.MULTILINE)
    assert '"License ::' not in pyproject


def test_pyproject_scopes_package_discovery() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert re.search(
        r'^\[tool\.setuptools\.packages\.find\]\s*\n'
        r'include = \["worksheet_generator\*"\]$',
        pyproject,
        re.MULTILINE,
    )
    assert re.search(
        r'^\[tool\.setuptools\.package-data\]\s*\n'
        r'worksheet_generator = \["default_config\.json"\]$',
        pyproject,
        re.MULTILINE,
    )


def test_packaged_default_config_is_runtime_fallback(tmp_path, monkeypatch) -> None:
    project_config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    packaged_config = json.loads(
        cli.PACKAGE_DEFAULT_CONFIG.read_text(encoding="utf-8")
    )
    assert packaged_config == project_config

    monkeypatch.setattr(cli, "DEFAULT_CONFIG", tmp_path / "missing.json")
    monkeypatch.setattr(cli, "LOCAL_CONFIG", tmp_path / "missing-local.json")
    assert cli.load_config() == project_config
