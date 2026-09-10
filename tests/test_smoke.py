"""Smoke-Test fuer worksheet-generator: Schema-Validierung, ein
Generator-Lauf mit synthetischem Mini-Input und der Markdown-Renderer.

Aufruf:
    PYTHONIOENCODING=utf-8 python -m pytest tests/ -v
    (Fallback ohne pytest:) PYTHONIOENCODING=utf-8 python tests/test_smoke.py
"""
from __future__ import annotations

import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent.parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from worksheet_generator import Foerderziel, cli, generate_worksheet, renderers, schema  # noqa: E402


def test_schema_validates_minimal_worksheet():
    goal = {"icf_codes": [], "freitext": "Test", "niveau": "standard", "alter": ""}
    targeting = {"mode": "foerder", **goal}
    worksheet = schema.new_worksheet_skeleton("Testblatt", targeting, goal)
    worksheet["sections"] = [
        {"type": "intro", "title": "Einleitung", "content": "Hallo", "items": []}
    ]
    schema.validate_worksheet(worksheet)  # wirft SchemaError bei Verstoss


def test_schema_rejects_invalid_item_kind():
    goal = {"icf_codes": [], "freitext": "Test", "niveau": "standard", "alter": ""}
    targeting = {"mode": "foerder", **goal}
    worksheet = schema.new_worksheet_skeleton("Testblatt", targeting, goal)
    worksheet["sections"] = [
        {
            "type": "task",
            "title": "Aufgaben",
            "content": "",
            "items": [{"kind": "unbekannt", "prompt": "x"}],
        }
    ]
    try:
        schema.validate_worksheet(worksheet)
    except schema.SchemaError:
        pass
    else:
        raise AssertionError("SchemaError erwartet, aber nicht ausgeloest")


def test_generate_worksheet_synthetic_mini_input():
    ziel = Foerderziel(
        freitext="Synthetisches Testziel: Formen benennen",
        icf_codes=["d115"],
        niveau="einfache_sprache",
        alter="7",
        thema="allgemein",
    )
    worksheet = generate_worksheet(ziel, recherche_stichpunkte=["Welche Form hat ein Ball?"])

    schema.validate_worksheet(worksheet)  # muss ohne Fehler durchlaufen
    assert worksheet["meta"]["targeting"]["mode"] == "foerder"
    assert worksheet["meta"]["goal"]["freitext"] == ziel.freitext
    assert worksheet["meta"]["goal"]["icf_codes"] == ["d115"]

    task_section = next(s for s in worksheet["sections"] if s["type"] == "task")
    prompts = [item["prompt"] for item in task_section["items"]]
    assert "Welche Form hat ein Ball?" in prompts


def test_markdown_renderer_produces_readable_output():
    ziel = Foerderziel(freitext="Formen benennen", niveau="standard", thema="allgemein")
    worksheet = generate_worksheet(ziel)
    md = renderers.to_markdown(worksheet)
    assert md.startswith("# Arbeitsblatt: Formen benennen")
    assert "## Aufgaben" in md


def test_html_renderer_produces_escaped_html():
    ziel = Foerderziel(
        freitext="Formen <benennen> & zuordnen",
        icf_codes=["d115"],
        niveau="standard",
        thema="allgemein",
    )
    worksheet = generate_worksheet(ziel)
    html = renderers.to_html(worksheet)
    assert "<!doctype html>" in html
    assert "&lt;benennen&gt; &amp; zuordnen" in html
    assert "<h2>Aufgaben</h2>" in html


def test_docx_renderer_missing_library_raises_unavailable(monkeypatch=None, tmp_path=None):
    import builtins
    import tempfile

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "docx":
            raise ImportError("No module named docx")
        return real_import(name, *args, **kwargs)

    if monkeypatch:
        monkeypatch.setattr(builtins, "__import__", fake_import)
    else:
        builtins.__import__ = fake_import

    target_path = (tmp_path / "test.docx") if tmp_path else (Path(tempfile.gettempdir()) / "test_smoke_docx.docx")
    try:
        ziel = Foerderziel(freitext="Formen benennen", niveau="standard", thema="allgemein")
        worksheet = generate_worksheet(ziel)
        try:
            renderers.to_docx(worksheet, target_path)
        except renderers.RendererUnavailable as exc:
            assert "python-docx nicht installiert" in str(exc)
        else:
            raise AssertionError("RendererUnavailable erwartet, aber nicht ausgeloest")
    finally:
        if not monkeypatch:
            builtins.__import__ = real_import


def test_cli_help_and_status(capsys=None):
    import io

    if capsys:
        ret_empty = cli.main([])
        assert ret_empty == 0
        captured_empty = capsys.readouterr()
        assert "worksheet_generator" in captured_empty.out or "usage:" in captured_empty.out

        ret_status = cli.main(["status"])
        assert ret_status == 0
        captured_status = capsys.readouterr()
        assert "worksheet-generator" in captured_status.out
    else:
        old_out = sys.stdout
        sys.stdout = io.StringIO()
        try:
            ret_empty = cli.main([])
            assert ret_empty == 0
            out = sys.stdout.getvalue()
            assert "worksheet_generator" in out or "usage:" in out

            sys.stdout = io.StringIO()
            ret_status = cli.main(["status"])
            assert ret_status == 0
            out_status = sys.stdout.getvalue()
            assert "worksheet-generator" in out_status
        finally:
            sys.stdout = old_out


def _run_all() -> int:
    tests = [obj for name, obj in globals().items() if name.startswith("test_") and callable(obj)]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"OK   {test.__name__}")
        except Exception as exc:  # eigenstaendiger Lauf ohne pytest
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} Tests bestanden")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
