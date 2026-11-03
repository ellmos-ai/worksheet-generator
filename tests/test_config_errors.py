"""Exercise configuration errors through the real CLI and documented examples."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from worksheet_generator import cli


def _local_config(monkeypatch, tmp_path, config):
    path = tmp_path / "config.local.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setattr(cli, "RUNTIME_ROOT", tmp_path)
    monkeypatch.setattr(cli, "DEFAULT_CONFIG", tmp_path / "config.json")
    monkeypatch.setattr(cli, "LOCAL_CONFIG", path)


@pytest.mark.parametrize("sources", [
    {"local_files": "SYNTHETIC_PRIVATE_VALUE"},
    "local-files",
    [None],
    ["local-files"],
    [{"type": []}],
    [{"type": None}],
])
@pytest.mark.parametrize("command", ["status", "generate"])
def test_invalid_curriculum_config_fails_cleanly_without_output(
    monkeypatch, tmp_path, capsys, sources, command
):
    _local_config(monkeypatch, tmp_path, {"curriculum_sources": sources})
    output = tmp_path / "worksheet.json"
    args = [command]
    if command == "generate":
        args += ["--subject", "Mathematik", "--grade", "1", "--out", str(output)]
    assert cli.main(args) == 1
    captured = capsys.readouterr()
    assert "FEHLER: curriculum_sources" in captured.err
    assert "SYNTHETIC_PRIVATE_VALUE" not in captured.err
    assert not output.exists()


@pytest.mark.parametrize("sources", [None, [], [{"type": "future-adapter"}]])
def test_disabled_and_unknown_sources_keep_existing_behavior(
    monkeypatch, tmp_path, sources
):
    _local_config(monkeypatch, tmp_path, {"curriculum_sources": sources})
    assert cli.main(["status"]) == 0
    output = tmp_path / "worksheet.json"
    assert cli.main([
        "generate", "--subject", "Mathematik", "--grade", "1", "--out", str(output)
    ]) == 0
    worksheet = json.loads(output.read_text(encoding="utf-8"))
    assert worksheet["meta"]["targeting"]["mode"] == "curriculum"
    if sources:
        assert any("future-adapter" in warning for warning in
                   worksheet["meta"]["sources"]["curriculum_warnings"])


def test_foerder_mode_does_not_consume_curriculum_configuration(monkeypatch, tmp_path):
    _local_config(monkeypatch, tmp_path, {"curriculum_sources": {"local_files": "unused"}})
    output = tmp_path / "worksheet.json"
    assert cli.main([
        "generate", "--freitext", "Synthetisches Testziel", "--no-icf", "--out", str(output)
    ]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["meta"]["targeting"]["mode"] == "foerder"


@pytest.mark.parametrize("readme", ["README.md", "README_de.md"])
def test_documented_config_works_with_real_local_curriculum(
    monkeypatch, tmp_path, readme
):
    text = (Path(__file__).parents[1] / readme).read_text(encoding="utf-8")
    block = next(block for block in re.findall(r"```json\s*\n(.*?)```", text, re.DOTALL)
                 if '"curriculum_sources"' in block)
    config = json.loads(block)
    curricula = tmp_path / "curricula"
    curricula.mkdir()
    (curricula / "Mathematik.md").write_text(
        "# Mathematik\nSYNTHETIC_CURRICULUM_CONTEXT", encoding="utf-8"
    )
    config["curriculum_sources"][0]["path"] = str(curricula)
    _local_config(monkeypatch, tmp_path, config)
    assert cli.main(["status"]) == 0
    output = tmp_path / "worksheet.json"
    assert cli.main([
        "generate", "--subject", "Mathematik", "--grade", "1", "--out", str(output)
    ]) == 0
    notes = json.loads(output.read_text(encoding="utf-8"))["meta"]["sources"]["curriculum_notes"]
    assert any("SYNTHETIC_CURRICULUM_CONTEXT" in note.get("excerpt", "") for note in notes)
