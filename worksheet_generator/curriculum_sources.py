"""Curriculum-Quellen-Adapter (bring-your-own, analog ICF) fuer den
Curriculum-Modus (targeting.mode == "curriculum").

Liefert zu Fach/Klassenstufe/Thema passenden KONTEXT (keine fertigen
Aufgaben) fuer generator.py -- landet in meta.sources.curriculum_notes
bzw. curriculum_warnings. Konfiguriert ueber config.json:

    "curriculum_sources": [
      {"type": "local-files", "path": "..."},
      {"type": "lernquest", "db_path": "..."}
    ]

Zwei Adapter:

  - "local-files": scannt einen Nutzer-Ordner mit eigenen
    Lehrplan-Auszuegen/Themenlisten (.md/.json), einfache
    Substring-Suche nach Fach/Thema als Relevanzfilter.

  - "lernquest" (EXPERIMENTELL): liest NUR LESEND aus einer lokalen
    LernQuest-Kompetenzregister-Datenbank (SQLite, Tabelle "competencies";
    Projekt: DEV_LernQuest_SOCIAL, Stand 2026-07-23 -- experimentell, Schema
    kann sich noch aendern). Pfad-Aufloesung: entry["db_path"] > ENV
    LERNQUEST_DB > kein Default. Als Doku-Konvention (NICHT hart verdrahtet):
    manche LernQuest-Installationen koennten unter
    "%LOCALAPPDATA%\\LernQuest\\lernquest.db" liegen -- das ist ein Hinweis
    fuer die eigene config.local.json, kein automatischer Fallback-Pfad.
    Verbindung erfolgt read-only (SQLite-URI "?mode=ro"); fehlt DB oder
    Tabelle, wird das sauber als Warnung gemeldet statt zu crashen.

Beide Adapter geben (notes, warnings) zurueck -- notes sind reiner Kontext,
KEINE automatisch uebernommenen Aufgaben-Prompts (anders als
recherche_stichpunkte, die der Nutzer bewusst als fertige Prompts angibt).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

CURRICULUM_FILE_SUFFIXES = {".md", ".json"}
CURRICULUM_EXCERPT_CHARS = 400
LERNQUEST_ENV_VAR = "LERNQUEST_DB"


def _adapter_local_files(
    entry: dict, subject: str, grade: str, topic: str
) -> tuple[list[dict], list[str]]:
    raw_path = entry.get("path")
    if not raw_path:
        return [], ["local-files: kein 'path' in curriculum_sources-Eintrag konfiguriert"]

    folder = Path(raw_path)
    if not folder.exists() or not folder.is_dir():
        return [], [f"local-files: Ordner nicht gefunden: {folder}"]

    notes: list[dict] = []
    subject_l = subject.lower() if subject else ""
    topic_l = topic.lower() if topic else ""
    for file in sorted(folder.iterdir()):
        if not file.is_file() or file.suffix.lower() not in CURRICULUM_FILE_SUFFIXES:
            continue
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:  # eine kaputte Datei darf den Scan nicht stoppen
            notes.append({"source": f"local-files:{file.name}", "excerpt": f"[Fehler: {exc}]"})
            continue
        # Fach ist Pflichtfilter und muss die DATEI qualifizieren (Dateiname oder
        # Titel-Überschrift) — ein beiläufiges Vorkommen des Fachworts im Fließtext
        # einer fach-fremden Datei zählt nicht als Treffer.
        first_heading = next(
            (line.lstrip("# ").lower() for line in text.splitlines() if line.startswith("#")),
            "",
        )
        name_and_title = f"{file.stem.lower()} {first_heading}"
        if subject_l and subject_l not in name_and_title:
            continue
        if not subject_l and topic_l and topic_l not in text.lower():
            continue
        notes.append({"source": f"local-files:{file.name}", "excerpt": text.strip()[:CURRICULUM_EXCERPT_CHARS]})

    if not notes:
        return [], [f"local-files: keine Treffer in {folder} fuer fach={subject!r} thema={topic!r}"]
    return notes, []


def _adapter_lernquest(
    entry: dict, subject: str, grade: str, topic: str
) -> tuple[list[dict], list[str]]:
    import os

    db_path = entry.get("db_path") or os.environ.get(LERNQUEST_ENV_VAR)
    if not db_path:
        return [], [
            f"lernquest: kein DB-Pfad -- curriculum_sources[].db_path oder "
            f"ENV {LERNQUEST_ENV_VAR} setzen (LernQuest-Register nicht verfuegbar)"
        ]

    path = Path(db_path)
    if not path.exists():
        return [], [f"lernquest: DB nicht gefunden unter {path} -- Register nicht verfuegbar"]

    try:
        uri = path.resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT bundesland, fach, jahrgangsstufe, schulform, "
                "differenzierungsniveau, kompetenzbereich, kompetenzbeschreibung, "
                "inhaltsbezug, quelle_name, quelle_abrufdatum FROM competencies "
                "WHERE (:fach = '' OR fach LIKE :fach_like) "
                "AND (:stufe = '' OR jahrgangsstufe LIKE :stufe_like) "
                "ORDER BY id LIMIT 20",
                {
                    "fach": subject or "",
                    "fach_like": f"%{subject}%",
                    "stufe": grade or "",
                    "stufe_like": f"%{grade}%",
                },
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.OperationalError as exc:
        # z.B. Tabelle "competencies" existiert (noch) nicht -- sauber melden.
        return [], [f"lernquest: Register nicht verfuegbar ({exc})"]
    except sqlite3.Error as exc:
        return [], [f"lernquest: Zugriffsfehler ({exc})"]

    notes = [dict(row) for row in rows]

    if topic:
        needle = topic.lower()
        gefiltert = [
            n for n in notes
            if needle in (n.get("inhaltsbezug") or "").lower()
            or needle in (n.get("kompetenzbeschreibung") or "").lower()
        ]
        if gefiltert:
            notes = gefiltert

    if not notes:
        return [], [f"lernquest: keine Treffer fuer fach={subject!r} jahrgangsstufe={grade!r}"]

    for n in notes:
        n["source"] = "lernquest"
    return notes, []


_ADAPTERS = {
    "local-files": _adapter_local_files,
    "lernquest": _adapter_lernquest,
}


def fetch_curriculum_context(
    curriculum_sources: list[dict] | None, subject: str, grade: str, topic: str
) -> tuple[list[dict], list[str]]:
    """Fragt alle konfigurierten Curriculum-Quellen ab und sammelt Kontext.

    Nicht verfuegbare/nicht treffende Quellen brechen den Lauf nicht ab --
    sie landen als Warnung in der zweiten Rueckgabe.

    Returns:
        (notes, warnings) -- notes sind reiner Prompt-KONTEXT, keine
        automatisch generierten Aufgaben.
    """
    all_notes: list[dict] = []
    all_warnings: list[str] = []
    for entry in curriculum_sources or []:
        adapter_type = entry.get("type")
        adapter = _ADAPTERS.get(adapter_type)
        if adapter is None:
            all_warnings.append(f"unbekannter curriculum_sources-Typ: {adapter_type!r}")
            continue
        try:
            notes, warnings = adapter(entry, subject, grade, topic)
        except Exception as exc:  # Adapter darf den Gesamtlauf nie crashen
            all_warnings.append(f"{adapter_type}: unerwarteter Fehler ({exc})")
            continue
        all_notes.extend(notes)
        all_warnings.extend(warnings)
    return all_notes, all_warnings
