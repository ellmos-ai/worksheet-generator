"""Kern-Generator: baut aus Foerderziel + optionalem Material-Scan + optionalen
Recherche-Stichpunkten ein schema-konformes Arbeitsblatt-JSON (siehe schema.py).

Der Generator arbeitet rein deterministisch und offline (kein LLM-Aufruf,
kein Netzwerkzugriff) und liefert ein Arbeitsblatt-GERUEST mit einer
sinnvollen Aufgaben-Struktur passend zu Thema/Niveau. Platzhalter-Items sind
bewusst als "(ANZUPASSEN)" markiert. Die inhaltliche Feinausarbeitung (z.B.
konkrete, thematisch zugespitzte Aufgabentexte) obliegt dem aufrufenden
LLM-Agenten (Claude Code u.a.), der das JSON weiter anreichert, bevor
gerendert wird -- bereits recherchierte Stichpunkte (recherche_stichpunkte)
werden direkt als konkrete Aufgaben-Prompts uebernommen.

Aufruf als Bibliothek:
    from worksheet_generator.generator import Foerderziel, generate_worksheet
    ziel = Foerderziel(freitext="Mengen bis 10 erfassen", icf_codes=["d150"],
                        niveau="einfache_sprache", alter="8", thema="mathe")
    worksheet = generate_worksheet(ziel)

Aufruf ueber CLI: siehe cli.py (`python -m worksheet_generator generate ...`).
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

from . import schema

SUPPORTED_MATERIAL_SUFFIXES = {".txt", ".md", ".docx"}
EXCERPT_CHARS = 400


@dataclasses.dataclass
class Foerderziel:
    """Steuerungs-Input fuer die Arbeitsblatt-Erzeugung.

    Enthaelt bewusst KEINE Klienten-/Personenbezuege (kein Name, keine
    Diagnose) -- nur Foerderziel, Niveau, Alter und Thema. Personalisierung
    erfolgt ueber Niveau/Interessen-Freitext, nicht ueber Identifizierbarkeit.
    """

    freitext: str
    icf_codes: list[str] = dataclasses.field(default_factory=list)
    niveau: str = "standard"  # z.B. "standard", "einfache_sprache", "aac"
    alter: str = ""
    thema: str = "allgemein"  # steuert die eingebaute Aufgaben-Bank


# Eingebaute Aufgaben-Baenke je Thema -- rein strukturelle Platzhalter, KEIN
# Ersatz fuer fachliche Ausarbeitung. Recherche-Stichpunkte (falls vorhanden)
# liefern die konkreten, echten Aufgaben-Prompts.
_TASK_BANK: dict[str, list[dict[str, str]]] = {
    "mathe": [
        {"kind": "rechnung", "prompt": "Rechenaufgabe passend zum Foerderziel (ANZUPASSEN)."},
        {"kind": "luecke", "prompt": "Luecke: fehlende Zahl/fehlender Operator ergaenzen (ANZUPASSEN)."},
        {"kind": "zuordnung", "prompt": "Mengen bzw. Zahlen einander zuordnen (ANZUPASSEN)."},
    ],
    "deutsch": [
        {"kind": "luecke", "prompt": "Luecke: fehlendes Wort im Satz ergaenzen (ANZUPASSEN)."},
        {"kind": "zuordnung", "prompt": "Wort-Bild- bzw. Begriffs-Zuordnung (ANZUPASSEN)."},
        {"kind": "frage", "prompt": "Verstaendnisfrage zum Text (ANZUPASSEN)."},
    ],
    "allgemein": [
        {"kind": "frage", "prompt": "Frage passend zum Foerderziel (ANZUPASSEN)."},
        {"kind": "freitext", "prompt": "Freie Bearbeitung bzw. Notizfeld (ANZUPASSEN)."},
    ],
}


def _read_excerpt(file: Path) -> str:
    try:
        if file.suffix.lower() == ".docx":
            try:
                import docx  # python-docx, optionale Abhaengigkeit
            except ImportError:
                return "[docx uebersprungen: python-docx nicht installiert]"
            document = docx.Document(str(file))
            text = "\n".join(p.text for p in document.paragraphs)
        else:
            text = file.read_text(encoding="utf-8", errors="ignore")
        return text.strip()[:EXCERPT_CHARS]
    except Exception as exc:  # eine kaputte Datei darf den Scan nicht stoppen
        return f"[Fehler beim Lesen: {exc}]"


def _scan_material_dir(path: Path) -> list[dict[str, str]]:
    """Scannt einen Ordner nach txt/md/docx und liefert kurze Exzerpte
    (Dateiname + Anfangstext) als Stil-/Kontextnotizen fuer den Meta-Block.
    Liest keine Bild- oder PDF-Dateien."""
    notes: list[dict[str, str]] = []
    if not path.exists() or not path.is_dir():
        return notes
    for file in sorted(path.iterdir()):
        if not file.is_file() or file.suffix.lower() not in SUPPORTED_MATERIAL_SUFFIXES:
            continue
        excerpt = _read_excerpt(file)
        if excerpt:
            notes.append({"file": file.name, "excerpt": excerpt})
    return notes


def scan_material(material_dirs: list[str] | None) -> list[dict[str, str]]:
    """Scannt alle konfigurierten Material-Ordner (siehe config.json:
    material_dirs). Leere Liste/None -> kein Scan (Default: aus)."""
    notes: list[dict[str, str]] = []
    for entry in material_dirs or []:
        notes.extend(_scan_material_dir(Path(entry)))
    return notes


def _build_intro(ziel: Foerderziel) -> dict:
    ziel_text = ziel.freitext or "individuelles Foerderziel"
    return {
        "type": "intro",
        "title": "Einleitung",
        "content": f"Arbeitsblatt zum Foerderziel: {ziel_text}.",
        "items": [],
    }


def _build_task_section(ziel: Foerderziel, recherche_stichpunkte: list[str] | None) -> dict:
    bank = _TASK_BANK.get(ziel.thema, _TASK_BANK["allgemein"])
    items: list[dict[str, Any]] = [dict(entry) for entry in bank]
    # Recherche-Stichpunkte werden, falls vorhanden, als zusaetzliche,
    # bereits konkrete Aufgaben-Prompts angehaengt (kein Platzhalter).
    for punkt in recherche_stichpunkte or []:
        items.append({"kind": "frage", "prompt": punkt})
    content = f"Niveau: {ziel.niveau}"
    if ziel.alter:
        content += f" | Alter: {ziel.alter}"
    return {"type": "task", "title": "Aufgaben", "content": content, "items": items}


def _build_bonus_section() -> dict:
    return {
        "type": "bonus",
        "title": "Bonus",
        "content": "Kleines Raetsel oder Zusatzaufgabe zur Motivation.",
        "items": [{"kind": "freitext", "prompt": "Bonusaufgabe (ANZUPASSEN)."}],
    }


def generate_worksheet(
    ziel: Foerderziel,
    material_dirs: list[str] | None = None,
    recherche_stichpunkte: list[str] | None = None,
    icf_reference: dict | None = None,
) -> dict:
    """Erzeugt ein schema-konformes Arbeitsblatt-JSON (schema.SCHEMA_VERSION).

    Args:
        ziel: Foerderziel-Steuerung (kein Klienten-/Personenbezug).
        material_dirs: optionale Pfade zu Material-Ordnern (Stil-/Kontextscan
            von txt/md/docx-Dateien; Default aus config.json: material_dirs).
        recherche_stichpunkte: optionale, bereits ausserhalb recherchierte
            Stichpunkte -- dieser Generator fuehrt selbst KEINE Websuche durch.
        icf_reference: optionale geladene ICF-Referenz (code -> kurztitel,
            siehe _tools/icf_fetch.py / icf_local.json) zur Anreicherung des
            Meta-Blocks mit Kurztiteln.

    Returns:
        Ein dict, das gegen schema.validate_worksheet() gueltig ist.
    """
    material_notes = scan_material(material_dirs)

    icf_titles: dict[str, str] = {}
    if icf_reference:
        for code in ziel.icf_codes:
            if code in icf_reference:
                icf_titles[code] = icf_reference[code]

    goal = {
        "icf_codes": list(ziel.icf_codes),
        "icf_titles": icf_titles,
        "freitext": ziel.freitext,
        "niveau": ziel.niveau,
        "alter": ziel.alter,
        "thema": ziel.thema,
    }
    sources = {
        "material_scan": [n["file"] for n in material_notes],
        "material_notes": material_notes,
        "recherche_stichpunkte": list(recherche_stichpunkte or []),
        "icf_reference_used": bool(icf_reference),
    }

    title = f"Arbeitsblatt: {ziel.freitext}" if ziel.freitext else "Arbeitsblatt"
    worksheet = schema.new_worksheet_skeleton(title, goal, sources)
    worksheet["sections"] = [
        _build_intro(ziel),
        _build_task_section(ziel, recherche_stichpunkte),
        _build_bonus_section(),
    ]
    schema.validate_worksheet(worksheet)
    return worksheet


def save_worksheet(worksheet: dict, out_path: str | Path) -> Path:
    """Schreibt das Arbeitsblatt-JSON UTF-8-kodiert nach out_path."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(worksheet, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
