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

from worksheet_generator import Foerderziel, generate_worksheet, renderers, schema  # noqa: E402


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
