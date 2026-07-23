"""Tests fuer den Curriculum-Modus (targeting.mode "curriculum"): Schema,
Generator und die Curriculum-Quellen-Adapter (local-files, lernquest).

Der lernquest-Adapter wird gegen eine SYNTHETISCHE Mini-SQLite-DB getestet,
deren Tabellenschema exakt dem real vorgefundenen Schema aus
`lernquest/core/db.py` (initialize_schema, Tabelle "competencies")
nachgebaut ist -- Stand der Sichtung: 2026-07-23. Keine echten LernQuest-
Daten, kein Zugriff auf das echte LernQuest-Projekt in diesem Test.

Aufruf:
    PYTHONIOENCODING=utf-8 python -m pytest tests/test_curriculum.py -v
    (Fallback ohne pytest:) PYTHONIOENCODING=utf-8 python tests/test_curriculum.py
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent.parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from worksheet_generator import Curriculumziel, generate_worksheet, schema  # noqa: E402
from worksheet_generator import curriculum_sources as cs  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "curriculum_local"

# Nachbau des real vorgefundenen LernQuest-Schemas (lernquest/core/db.py,
# initialize_schema -> Tabelle "competencies"), NUR die fuer diesen Adapter
# relevante Tabelle -- gesichtet 2026-07-23, NUR LESEND im Adapter genutzt.
_LERNQUEST_SCHEMA = """
    CREATE TABLE competencies (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        bundesland              TEXT    NOT NULL,
        fach                    TEXT    NOT NULL,
        jahrgangsstufe          TEXT    NOT NULL,
        schulform               TEXT,
        differenzierungsniveau  TEXT,
        kompetenzbereich        TEXT    NOT NULL,
        kompetenzbeschreibung   TEXT    NOT NULL,
        inhaltsbezug            TEXT,
        quelle_name             TEXT    NOT NULL,
        quelle_url              TEXT,
        quelle_version           TEXT,
        quelle_abrufdatum       TEXT,
        lizenzhinweis           TEXT,
        erstellt_am             TEXT    NOT NULL DEFAULT (datetime('now')),
        aktualisiert_am         TEXT    NOT NULL DEFAULT (datetime('now'))
    );
"""


def _build_synthetic_lernquest_db(path: Path) -> None:
    conn = sqlite3.connect(str(path))
    conn.executescript(_LERNQUEST_SCHEMA)
    conn.execute(
        "INSERT INTO competencies "
        "(bundesland, fach, jahrgangsstufe, kompetenzbereich, kompetenzbeschreibung, "
        "inhaltsbezug, quelle_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "Bayern", "Sachkunde", "7/8", "Naturphaenomene",
            "Den Wasserkreislauf mit Fachbegriffen beschreiben (synthetisches Testfixture).",
            "Wasserkreislauf", "Test-Fixture (nicht real, kein amtlicher Lehrplan)",
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Schema: targeting-Modi
# ---------------------------------------------------------------------------

def test_schema_validates_curriculum_targeting():
    targeting = {
        "mode": "curriculum", "subject": "Sachkunde", "grade": "7/8",
        "topic": "Wasserkreislauf", "differenzierung": "G",
        "kompetenzfokus": ["vergleichen", "interpretieren"],
    }
    goal = {"icf_codes": [], "icf_titles": {}, "freitext": "Sachkunde -- Wasserkreislauf",
            "niveau": "G", "alter": "7/8", "thema": "allgemein"}
    worksheet = schema.new_worksheet_skeleton("Testblatt", targeting, goal)
    worksheet["sections"] = [{"type": "intro", "title": "Einleitung", "content": "x", "items": []}]
    schema.validate_worksheet(worksheet)  # wirft bei Fehler


def test_schema_rejects_unknown_targeting_mode():
    targeting = {"mode": "unbekannt"}
    goal = {"icf_codes": [], "freitext": "", "niveau": "standard", "alter": ""}
    worksheet = schema.new_worksheet_skeleton("Testblatt", targeting, goal)
    worksheet["sections"] = [{"type": "intro", "title": "x", "content": "", "items": []}]
    try:
        schema.validate_worksheet(worksheet)
    except schema.SchemaError:
        pass
    else:
        raise AssertionError("SchemaError bei unbekanntem targeting.mode erwartet")


def test_schema_rejects_unknown_kompetenzfokus():
    targeting = {
        "mode": "curriculum", "subject": "Mathe", "grade": "3",
        "topic": "", "kompetenzfokus": ["fliegen"],
    }
    goal = {"icf_codes": [], "freitext": "Mathe", "niveau": "standard", "alter": "3"}
    worksheet = schema.new_worksheet_skeleton("Testblatt", targeting, goal)
    worksheet["sections"] = [{"type": "intro", "title": "x", "content": "", "items": []}]
    try:
        schema.validate_worksheet(worksheet)
    except schema.SchemaError:
        pass
    else:
        raise AssertionError("SchemaError bei unbekanntem kompetenzfokus-Wert erwartet")


# ---------------------------------------------------------------------------
# Generator: Curriculum-Modus
# ---------------------------------------------------------------------------

def test_generate_curriculum_worksheet_with_kompetenzfokus():
    ziel = Curriculumziel(
        subject="Sachkunde", grade="7/8", topic="Wasserkreislauf (synthetisches Beispiel)",
        differenzierung="G", kompetenzfokus=["vergleichen", "interpretieren"],
    )
    worksheet = generate_worksheet(ziel)
    schema.validate_worksheet(worksheet)

    assert worksheet["meta"]["targeting"]["mode"] == "curriculum"
    assert worksheet["meta"]["targeting"]["subject"] == "Sachkunde"
    assert worksheet["meta"]["goal"]["alter"] == "7/8"  # grade -> goal.alter (Renderer-Projektion)
    assert worksheet["meta"]["goal"]["niveau"] == "G"   # differenzierung -> goal.niveau

    task_section = next(s for s in worksheet["sections"] if s["type"] == "task")
    hints = [item.get("hint", "") for item in task_section["items"]]
    assert any("vergleichen" in h for h in hints)
    assert any("interpretieren" in h for h in hints)


def test_generate_curriculum_worksheet_without_kompetenzfokus_has_fallback_items():
    ziel = Curriculumziel(subject="Mathematik", grade="3", topic="Einmaleins")
    worksheet = generate_worksheet(ziel)
    schema.validate_worksheet(worksheet)

    # Mathematik -> bekannte Aufgaben-Bank-Zuordnung (thema "mathe")
    assert worksheet["meta"]["goal"]["thema"] == "mathe"

    task_section = next(s for s in worksheet["sections"] if s["type"] == "task")
    assert len(task_section["items"]) >= 1


# ---------------------------------------------------------------------------
# Adapter: local-files
# ---------------------------------------------------------------------------

def test_local_files_adapter_finds_matching_fixture():
    notes, warnings = cs.fetch_curriculum_context(
        [{"type": "local-files", "path": str(FIXTURES_DIR)}],
        subject="Sachkunde", grade="7/8", topic="Wasserkreislauf",
    )
    assert not warnings
    sources = [n["source"] for n in notes]
    assert any("sachkunde_7_8.md" in s for s in sources)
    assert not any("musik_5_6.md" in s for s in sources)  # Negativfall: unpassendes Fach ausgeschlossen


def test_local_files_adapter_missing_folder_warns_without_crash():
    notes, warnings = cs.fetch_curriculum_context(
        [{"type": "local-files", "path": str(FIXTURES_DIR / "existiert_nicht")}],
        subject="Sachkunde", grade="7/8", topic="Wasserkreislauf",
    )
    assert notes == []
    assert warnings and "nicht gefunden" in warnings[0]


# ---------------------------------------------------------------------------
# Adapter: lernquest (experimentell, synthetische Mini-DB)
# ---------------------------------------------------------------------------

def test_lernquest_adapter_finds_synthetic_row():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "lernquest_test.db"
        _build_synthetic_lernquest_db(db_path)

        notes, warnings = cs.fetch_curriculum_context(
            [{"type": "lernquest", "db_path": str(db_path)}],
            subject="Sachkunde", grade="7/8", topic="Wasserkreislauf",
        )
        assert not warnings
        assert len(notes) == 1
        assert notes[0]["kompetenzbereich"] == "Naturphaenomene"
        assert notes[0]["source"] == "lernquest"


def test_lernquest_adapter_missing_db_warns_without_crash():
    notes, warnings = cs.fetch_curriculum_context(
        [{"type": "lernquest", "db_path": r"C:\pfad\der\nicht\existiert\lernquest.db"}],
        subject="Sachkunde", grade="7/8", topic="Wasserkreislauf",
    )
    assert notes == []
    assert warnings and "nicht gefunden" in warnings[0]


def test_lernquest_adapter_missing_table_warns_without_crash():
    """DB existiert, aber ohne 'competencies'-Tabelle (z.B. leere/andere DB) --
    entspricht dem Fall 'LernQuest-Register nicht verfuegbar' aus dem Auftrag."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "leer.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE andere_tabelle (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

        notes, warnings = cs.fetch_curriculum_context(
            [{"type": "lernquest", "db_path": str(db_path)}],
            subject="Sachkunde", grade="7/8", topic="Wasserkreislauf",
        )
        assert notes == []
        assert warnings and "nicht verfuegbar" in warnings[0]


def test_lernquest_adapter_env_var_fallback(monkeypatch=None):
    """Ohne db_path im Eintrag wird ENV LERNQUEST_DB genutzt."""
    import os

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "lernquest_env.db"
        _build_synthetic_lernquest_db(db_path)

        old = os.environ.get(cs.LERNQUEST_ENV_VAR)
        os.environ[cs.LERNQUEST_ENV_VAR] = str(db_path)
        try:
            notes, warnings = cs.fetch_curriculum_context(
                [{"type": "lernquest"}], subject="Sachkunde", grade="7/8", topic="",
            )
        finally:
            if old is None:
                os.environ.pop(cs.LERNQUEST_ENV_VAR, None)
            else:
                os.environ[cs.LERNQUEST_ENV_VAR] = old

        assert not warnings
        assert len(notes) == 1


# ---------------------------------------------------------------------------
# Integration: generate_worksheet mit curriculum_sources
# ---------------------------------------------------------------------------

def test_generate_worksheet_integrates_curriculum_sources():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "lernquest_integration.db"
        _build_synthetic_lernquest_db(db_path)

        ziel = Curriculumziel(subject="Sachkunde", grade="7/8", topic="Wasserkreislauf")
        worksheet = generate_worksheet(
            ziel,
            curriculum_sources=[
                {"type": "local-files", "path": str(FIXTURES_DIR)},
                {"type": "lernquest", "db_path": str(db_path)},
            ],
        )
        schema.validate_worksheet(worksheet)
        notes = worksheet["meta"]["sources"]["curriculum_notes"]
        sources = [n.get("source") for n in notes]
        assert any("local-files" in s for s in sources)
        assert any(s == "lernquest" for s in sources)
        assert worksheet["meta"]["sources"]["curriculum_warnings"] == []


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
