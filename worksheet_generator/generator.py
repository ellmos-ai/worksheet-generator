"""Kern-Generator: baut aus Foerderziel ODER Curriculumziel + optionalem
Material-Scan + optionalen Recherche-/Curriculum-Kontexten ein
schema-konformes Arbeitsblatt-JSON (siehe schema.py).

Zwei Zielsteuerungs-Modi (schema.TARGETING_MODES):

  - "foerder": Foerderziel-Freitext + optionale ICF-Codes (bestehend seit
    v1, siehe Foerderziel).
  - "curriculum": Unterrichtsfach + Klassen-/Lernstufe + Thema, optional
    Differenzierung und Kompetenzfokus (siehe Curriculumziel). Kontext kann
    zusaetzlich aus konfigurierten curriculum_sources-Adaptern kommen
    (siehe curriculum_sources.py: local-files, experimentell lernquest).

Der Generator arbeitet in BEIDEN Modi rein deterministisch und offline
(kein LLM-Aufruf; Curriculum-Quellen-Adapter greifen nur auf lokale
Dateien/DBs zu, kein Internet). Platzhalter-Items sind bewusst als
"(ANZUPASSEN)" markiert. Die inhaltliche Feinausarbeitung obliegt dem
aufrufenden LLM-Agenten, der das JSON vor dem Rendern anreichert --
bereits recherchierte Stichpunkte (recherche_stichpunkte) werden direkt als
konkrete Aufgaben-Prompts uebernommen.

Aufruf als Bibliothek (Foerder-Modus):
    from worksheet_generator.generator import Foerderziel, generate_worksheet
    ziel = Foerderziel(freitext="Mengen bis 10 erfassen", icf_codes=["d150"],
                        niveau="einfache_sprache", alter="8", thema="mathe")
    worksheet = generate_worksheet(ziel)

Aufruf als Bibliothek (Curriculum-Modus):
    from worksheet_generator.generator import Curriculumziel, generate_worksheet
    ziel = Curriculumziel(subject="Sachkunde", grade="7/8", topic="Wasserkreislauf",
                           differenzierung="G", kompetenzfokus=["vergleichen"])
    worksheet = generate_worksheet(ziel)

Aufruf ueber CLI: siehe cli.py (`python -m worksheet_generator generate ...`)
-- der Modus wird automatisch anhand der uebergebenen Parameter erkannt.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

from . import curriculum_sources as _curriculum_sources
from . import schema

SUPPORTED_MATERIAL_SUFFIXES = {".txt", ".md", ".docx"}
EXCERPT_CHARS = 400

# Faecher, fuer die eine eingebaute Aufgaben-Bank existiert (siehe _TASK_BANK)
# -- steuert im Curriculum-Modus die Wiederverwendung der Foerder-Baenke.
_SUBJECT_TO_THEMA = {
    "mathe": "mathe",
    "mathematik": "mathe",
    "deutsch": "deutsch",
}


@dataclasses.dataclass
class Foerderziel:
    """Steuerungs-Input fuer die Arbeitsblatt-Erzeugung im Foerder-Modus.

    Enthaelt bewusst KEINE Klienten-/Personenbezuege (kein Name, keine
    Diagnose) -- nur Foerderziel, Niveau, Alter und Thema. Personalisierung
    erfolgt ueber Niveau/Interessen-Freitext, nicht ueber Identifizierbarkeit.
    """

    freitext: str
    icf_codes: list[str] = dataclasses.field(default_factory=list)
    niveau: str = "standard"  # z.B. "standard", "einfache_sprache", "aac"
    alter: str = ""
    thema: str = "allgemein"  # steuert die eingebaute Aufgaben-Bank


@dataclasses.dataclass
class Curriculumziel:
    """Steuerungs-Input fuer die Arbeitsblatt-Erzeugung im Curriculum-Modus
    (schulische Arbeitsblaetter nach Fach/Klassenstufe statt Foerderziel).

    Enthaelt bewusst KEINE Schueler-/Personenbezuege -- nur Fach,
    Klassen-/Lernstufe, Thema und optionale Differenzierung/Kompetenzfokus.
    """

    subject: str
    grade: str
    topic: str = ""
    differenzierung: str = ""  # z.B. "G"/"M"/"E"-Niveau
    kompetenzfokus: list[str] = dataclasses.field(default_factory=list)  # siehe schema.KOMPETENZFOKUS


# Eingebaute Aufgaben-Baenke je Thema (Foerder-Modus) -- rein strukturelle
# Platzhalter, KEIN Ersatz fuer fachliche Ausarbeitung. Recherche-Stichpunkte
# (falls vorhanden) liefern die konkreten, echten Aufgaben-Prompts.
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

# Kompetenzfokus (Curriculum-Modus) -> passender Item-kind (schema.ITEM_KINDS).
# Der Kompetenzfokus selbst steht zusaetzlich im Prompt-Text, damit er auch
# ohne Item-Schema-Erweiterung sichtbar bleibt.
_KOMPETENZFOKUS_KIND: dict[str, str] = {
    "recherchieren": "frage",
    "begruenden": "frage",
    "vergleichen": "zuordnung",
    "modellieren": "freitext",
    "interpretieren": "frage",
    "transferieren": "freitext",
    "reflektieren": "freitext",
}

_KOMPETENZFOKUS_LABEL: dict[str, str] = {
    "recherchieren": "Recherchieren",
    "begruenden": "Begruenden",
    "vergleichen": "Vergleichen",
    "modellieren": "Modellieren",
    "interpretieren": "Interpretieren",
    "transferieren": "Transferieren",
    "reflektieren": "Reflektieren",
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


def _subject_to_thema(subject: str) -> str:
    """Mappt ein Unterrichtsfach auf eine Aufgaben-Bank aus _TASK_BANK,
    Default 'allgemein' fuer unbekannte Faecher."""
    return _SUBJECT_TO_THEMA.get(subject.strip().lower(), "allgemein")


# ---------------------------------------------------------------------------
# Foerder-Modus
# ---------------------------------------------------------------------------

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


def _generate_foerder_worksheet(
    ziel: Foerderziel,
    material_dirs: list[str] | None,
    recherche_stichpunkte: list[str] | None,
    icf_reference: dict | None,
) -> dict:
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
    targeting = {"mode": "foerder", **goal}
    sources = {
        "material_scan": [n["file"] for n in material_notes],
        "material_notes": material_notes,
        "recherche_stichpunkte": list(recherche_stichpunkte or []),
        "icf_reference_used": bool(icf_reference),
    }

    title = f"Arbeitsblatt: {ziel.freitext}" if ziel.freitext else "Arbeitsblatt"
    worksheet = schema.new_worksheet_skeleton(title, targeting, goal, sources)
    worksheet["sections"] = [
        _build_intro(ziel),
        _build_task_section(ziel, recherche_stichpunkte),
        _build_bonus_section(),
    ]
    schema.validate_worksheet(worksheet)
    return worksheet


# ---------------------------------------------------------------------------
# Curriculum-Modus
# ---------------------------------------------------------------------------

def _build_curriculum_intro(ziel: Curriculumziel) -> dict:
    topic_text = f" zum Thema {ziel.topic}" if ziel.topic else ""
    content = f"Arbeitsblatt {ziel.subject}, Klassen-/Lernstufe {ziel.grade}{topic_text}."
    if ziel.differenzierung:
        content += f" Differenzierung: {ziel.differenzierung}."
    return {"type": "intro", "title": "Einleitung", "content": content, "items": []}


def _build_curriculum_task_section(
    ziel: Curriculumziel, recherche_stichpunkte: list[str] | None
) -> dict:
    items: list[dict[str, Any]] = []
    if ziel.kompetenzfokus:
        for fokus in ziel.kompetenzfokus:
            kind = _KOMPETENZFOKUS_KIND.get(fokus, "frage")
            label = _KOMPETENZFOKUS_LABEL.get(fokus, fokus)
            thema_text = ziel.topic or ziel.subject
            items.append({
                "kind": kind,
                "prompt": f"Aufgabe mit Kompetenzfokus {label} zu {thema_text} (ANZUPASSEN).",
                "hint": f"kompetenzfokus: {fokus}",
            })
    else:
        thema_text = ziel.topic or ziel.subject
        items.append({"kind": "frage", "prompt": f"Aufgabe zu {thema_text} (ANZUPASSEN)."})
        items.append({"kind": "freitext", "prompt": "Freie Bearbeitung bzw. Notizfeld (ANZUPASSEN)."})

    for punkt in recherche_stichpunkte or []:
        items.append({"kind": "frage", "prompt": punkt})

    content = f"Fach: {ziel.subject} | Klassen-/Lernstufe: {ziel.grade}"
    if ziel.differenzierung:
        content += f" | Differenzierung: {ziel.differenzierung}"
    return {"type": "task", "title": "Aufgaben", "content": content, "items": items}


def _generate_curriculum_worksheet(
    ziel: Curriculumziel,
    material_dirs: list[str] | None,
    recherche_stichpunkte: list[str] | None,
    curriculum_sources_config: list[dict] | None,
) -> dict:
    material_notes = scan_material(material_dirs)

    curriculum_notes, curriculum_warnings = _curriculum_sources.fetch_curriculum_context(
        curriculum_sources_config, subject=ziel.subject, grade=ziel.grade, topic=ziel.topic
    )

    targeting = {
        "mode": "curriculum",
        "subject": ziel.subject,
        "grade": ziel.grade,
        "topic": ziel.topic,
        "differenzierung": ziel.differenzierung,
        "kompetenzfokus": list(ziel.kompetenzfokus),
    }
    # Renderer-kompatible Projektion (renderers.py bleibt unveraendert und
    # liest ausschliesslich aus meta.goal) -- Fach mappt auf eine bekannte
    # Aufgaben-Bank (_subject_to_thema), Differenzierung -> niveau, Klassen-/
    # Lernstufe -> alter.
    goal = {
        "icf_codes": [],
        "icf_titles": {},
        "freitext": f"{ziel.subject} -- {ziel.topic}" if ziel.topic else ziel.subject,
        "niveau": ziel.differenzierung or "standard",
        "alter": ziel.grade,
        "thema": _subject_to_thema(ziel.subject),
    }
    sources = {
        "material_scan": [n["file"] for n in material_notes],
        "material_notes": material_notes,
        "recherche_stichpunkte": list(recherche_stichpunkte or []),
        "icf_reference_used": False,
        "curriculum_notes": curriculum_notes,
        "curriculum_warnings": curriculum_warnings,
    }

    title = f"Arbeitsblatt: {ziel.subject} -- {ziel.topic}" if ziel.topic else f"Arbeitsblatt: {ziel.subject}"
    worksheet = schema.new_worksheet_skeleton(title, targeting, goal, sources)
    worksheet["sections"] = [
        _build_curriculum_intro(ziel),
        _build_curriculum_task_section(ziel, recherche_stichpunkte),
        _build_bonus_section(),
    ]
    schema.validate_worksheet(worksheet)
    return worksheet


# ---------------------------------------------------------------------------
# Oeffentliche API (Dispatcher)
# ---------------------------------------------------------------------------

def generate_worksheet(
    ziel: Foerderziel | Curriculumziel,
    material_dirs: list[str] | None = None,
    recherche_stichpunkte: list[str] | None = None,
    icf_reference: dict | None = None,
    curriculum_sources: list[dict] | None = None,
) -> dict:
    """Erzeugt ein schema-konformes Arbeitsblatt-JSON (schema.SCHEMA_VERSION).

    Der Modus wird am Typ von ziel erkannt: Foerderziel -> targeting.mode
    "foerder" (ICF-gestuetzt), Curriculumziel -> targeting.mode "curriculum"
    (Fach/Klassenstufe-gestuetzt, siehe curriculum_sources.py fuer Adapter).

    Args:
        ziel: Foerderziel- ODER Curriculumziel-Steuerung (kein
            Klienten-/Schueler-Personenbezug in beiden Faellen).
        material_dirs: optionale Pfade zu Material-Ordnern (Stil-/Kontextscan
            von txt/md/docx-Dateien; Default aus config.json: material_dirs).
        recherche_stichpunkte: optionale, bereits ausserhalb recherchierte
            Stichpunkte -- dieser Generator fuehrt selbst KEINE Websuche durch.
        icf_reference: nur Foerder-Modus. Optionale geladene ICF-Referenz
            (code -> kurztitel, siehe _tools/icf_fetch.py / icf_local.json).
        curriculum_sources: nur Curriculum-Modus. Liste konfigurierter
            Quellen-Adapter (siehe config.json: curriculum_sources).

    Returns:
        Ein dict, das gegen schema.validate_worksheet() gueltig ist.
    """
    if isinstance(ziel, Curriculumziel):
        return _generate_curriculum_worksheet(
            ziel, material_dirs, recherche_stichpunkte, curriculum_sources
        )
    return _generate_foerder_worksheet(ziel, material_dirs, recherche_stichpunkte, icf_reference)


def save_worksheet(worksheet: dict, out_path: str | Path) -> Path:
    """Schreibt das Arbeitsblatt-JSON UTF-8-kodiert nach out_path."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(worksheet, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
