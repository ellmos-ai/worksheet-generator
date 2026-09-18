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


def test_pyproject_scripts_and_optional_dependencies() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert re.search(
        r'^\[project\.scripts\]\s*\n'
        r'worksheet-generator = "worksheet_generator\.cli:main"$',
        pyproject,
        re.MULTILINE,
    )
    assert re.search(
        r'^\[project\.optional-dependencies\]\s*\n'
        r'docx = \["python-docx>=1\.1\.0"\]\s*\n'
        r'test = \["pytest>=8\.0\.0"\]$',
        pyproject,
        re.MULTILINE,
    )
    assert callable(cli.main)


def test_version_parity() -> None:
    import worksheet_generator

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
    assert match is not None
    assert match.group(1) == worksheet_generator.__version__
    assert worksheet_generator.__version__ == "0.2.3"


def test_documentation_and_license_artifacts() -> None:
    import worksheet_generator

    # 1. Third-party licenses
    tpl = ROOT / "THIRD_PARTY_LICENSES.md"
    assert tpl.is_file()
    tpl_text = tpl.read_text(encoding="utf-8")
    assert "PSF-2.0" in tpl_text
    assert "MIT" in tpl_text
    assert "ICF (International Classification of Functioning, Disability and Health)" in tpl_text
    assert "Zero-Copyleft on Generated Worksheets" in tpl_text

    # 2. Marketing log
    mlog = ROOT / "MARKETING-LOG.txt"
    assert mlog.is_file()
    mlog_text = mlog.read_text(encoding="utf-8")
    assert "[PERSONA-01]" in mlog_text
    assert "[PERSONA-04]" in mlog_text
    assert "10-Dimensionen-Vergleichsmatrix" in mlog_text

    # 3. llms.txt context index
    llms = ROOT / "llms.txt"
    assert llms.is_file()
    llms_text = llms.read_text(encoding="utf-8")
    assert f"Version: {worksheet_generator.__version__}" in llms_text
    assert "THIRD_PARTY_LICENSES.md" in llms_text
    assert "MARKETING-LOG.txt" in llms_text


def test_pyproject_pep621_urls() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for key in [
        "Homepage",
        "Documentation",
        '"German Documentation"',
        "Repository",
        "Issues",
        '"LLM Context Index"',
        '"Third-Party Licenses"',
        '"Marketing Log"',
    ]:
        assert key in pyproject


def test_bilingual_navigation_parity() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    en_nav = re.findall(r'^\d+\.\s+\[([^\]]+)\]\(#([^\)]+)\)', readme_en, re.MULTILINE)
    de_nav = re.findall(r'^\d+\.\s+\[([^\]]+)\]\(#([^\)]+)\)', readme_de, re.MULTILINE)

    assert len(en_nav) == 16, f"Expected 16 EN navigation points, got {len(en_nav)}"
    assert len(de_nav) == 16, f"Expected 16 DE navigation points, got {len(de_nav)}"

    # Ensure all anchors in navigation exist as headers in the respective files
    for title, anchor in en_nav:
        # Check that header exists matching the anchor
        expected_header = title.replace("&", "").replace("(", "").replace(")", "").strip()
        assert f"## {expected_header}" in readme_en or f"#{anchor}" in readme_en

    for title, anchor in de_nav:
        assert f"#{anchor}" in readme_de

