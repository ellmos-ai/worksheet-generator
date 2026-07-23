"""Arbeitsblatt-JSON-Schema (versioniert) fuer worksheet-generator.

Definiert die Datenstruktur, die generator.py erzeugt und renderers.py
konsumiert. Die Validierung ist ein reiner stdlib-Validator (keine
externe jsonschema-Abhaengigkeit), damit das Modul ohne Zusatz-Installation
lauffaehig bleibt.

Struktur (schema_version "2.0"):

    {
      "schema_version": "2.0",
      "meta": {
        "title": str,
        "generated_at": ISO-Zeitstempel,
        "targeting": {
          "mode": "foerder" | "curriculum",

          # mode == "foerder" (Foerder-/Therapiekontext, ICF-gestuetzt):
          "icf_codes": [str, ...],
          "icf_titles": {code: kurztitel, ...},
          "freitext": str,
          "niveau": str,          # z.B. "standard", "einfache_sprache", "aac"
          "alter": str,
          "thema": str,           # z.B. "mathe", "deutsch", "allgemein"

          # mode == "curriculum" (Schulkontext, Fach/Klassenstufe-gestuetzt):
          "subject": str,          # Unterrichtsfach
          "grade": str,            # Klassen- bzw. Lernstufe
          "topic": str,            # Thema
          "differenzierung": str,  # optional, z.B. "G"/"M"/"E"-Niveau
          "kompetenzfokus": [str, ...]  # optional, aus KOMPETENZFOKUS
        },
        "goal": {
          # Renderer-kompatible Projektion von "targeting" -- IMMER vorhanden,
          # unabhaengig vom Modus, damit renderers.py unveraendert bleibt.
          "icf_codes": [str, ...],
          "icf_titles": {code: kurztitel, ...},
          "freitext": str,
          "niveau": str,
          "alter": str,
          "thema": str
        },
        "sources": {
          "material_scan": [dateiname, ...],
          "material_notes": [{"file": ..., "excerpt": ...}, ...],
          "recherche_stichpunkte": [str, ...],
          "icf_reference_used": bool,
          "curriculum_notes": [{...}, ...],       # nur mode == "curriculum"
          "curriculum_warnings": [str, ...]        # nur mode == "curriculum"
        }
      },
      "sections": [
        {
          "type": "intro" | "task" | "bonus" | "custom",
          "title": str,
          "content": str,
          "items": [
            {
              "kind": "luecke" | "zuordnung" | "rechnung" | "frage" | "freitext",
              "prompt": str,
              "options": [str, ...],      # optional, z.B. fuer zuordnung
              "answer_space": bool,       # optional, Default True
              "hint": str                 # optional
            }, ...
          ]
        }, ...
      ]
    }

Migrationshinweis: schema_version "1.0" kannte nur "meta.goal" (ohne
"targeting", implizit Foerder-Modus). "2.0" fuehrt "targeting" als
kanonische, modusfaehige Struktur ein; "goal" bleibt als abgeleitete
Projektion fuer Renderer-Kompatibilitaet erhalten. Es gibt keinen
automatischen Migrator fuer 1.0-Dateien -- neu generieren.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

SCHEMA_VERSION = "2.0"

ITEM_KINDS = {"luecke", "zuordnung", "rechnung", "frage", "freitext"}
SECTION_TYPES = {"intro", "task", "bonus", "custom"}
TARGETING_MODES = {"foerder", "curriculum"}

# Kompetenzfokus-Vokabular fuer den Curriculum-Modus (ASCII-Identifier nach
# Codebase-Konvention, siehe ITEM_KINDS; "begruenden" statt "begründen").
KOMPETENZFOKUS = {
    "recherchieren",
    "begruenden",
    "vergleichen",
    "modellieren",
    "interpretieren",
    "transferieren",
    "reflektieren",
}


class SchemaError(ValueError):
    """Wird bei ungueltigem Arbeitsblatt-JSON ausgeloest."""


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SchemaError(msg)


def _validate_targeting(targeting: Any) -> None:
    _require(isinstance(targeting, dict), "meta.targeting fehlt oder ist kein Objekt")
    mode = targeting.get("mode")
    _require(mode in TARGETING_MODES, f"meta.targeting.mode ungueltig: {mode!r}")

    if mode == "foerder":
        _require(isinstance(targeting.get("icf_codes"), list), "targeting.icf_codes muss eine Liste sein")
        _require(isinstance(targeting.get("freitext"), str), "targeting.freitext muss ein String sein")
        _require(isinstance(targeting.get("niveau"), str) and targeting["niveau"], "targeting.niveau fehlt")
        _require("alter" in targeting, "targeting.alter fehlt")
    else:  # mode == "curriculum"
        _require(isinstance(targeting.get("subject"), str) and targeting["subject"], "targeting.subject fehlt")
        _require(isinstance(targeting.get("grade"), str) and targeting["grade"], "targeting.grade fehlt")
        _require(isinstance(targeting.get("topic"), str), "targeting.topic muss ein String sein")
        kompetenzfokus = targeting.get("kompetenzfokus", [])
        _require(isinstance(kompetenzfokus, list), "targeting.kompetenzfokus muss eine Liste sein")
        unbekannt = [k for k in kompetenzfokus if k not in KOMPETENZFOKUS]
        _require(not unbekannt, f"targeting.kompetenzfokus enthaelt unbekannte Werte: {unbekannt}")


def validate_worksheet(data: dict[str, Any]) -> None:
    """Prueft ein Arbeitsblatt-JSON gegen das Schema.

    Wirft SchemaError mit einer konkreten Fehlermeldung bei jedem Verstoss.
    Gibt nichts zurueck -- kein Rueckgabewert bedeutet gueltig.
    """
    _require(isinstance(data, dict), "Arbeitsblatt muss ein JSON-Objekt sein")
    _require(
        data.get("schema_version") == SCHEMA_VERSION,
        f"schema_version muss {SCHEMA_VERSION!r} sein, war: {data.get('schema_version')!r}",
    )

    meta = data.get("meta")
    _require(isinstance(meta, dict), "meta fehlt oder ist kein Objekt")
    _require(isinstance(meta.get("title"), str) and meta["title"], "meta.title fehlt")
    _require(
        isinstance(meta.get("generated_at"), str) and meta["generated_at"],
        "meta.generated_at fehlt",
    )

    _validate_targeting(meta.get("targeting"))

    # "goal" bleibt Pflicht -- Renderer-kompatible Projektion, unabhaengig
    # vom targeting.mode (renderers.py liest ausschliesslich hieraus).
    goal = meta.get("goal")
    _require(isinstance(goal, dict), "meta.goal fehlt oder ist kein Objekt")
    _require(isinstance(goal.get("icf_codes"), list), "meta.goal.icf_codes muss eine Liste sein")
    _require(isinstance(goal.get("freitext"), str), "meta.goal.freitext muss ein String sein")
    _require(isinstance(goal.get("niveau"), str) and goal["niveau"], "meta.goal.niveau fehlt")
    _require("alter" in goal, "meta.goal.alter fehlt")

    sources = meta.get("sources", {})
    _require(isinstance(sources, dict), "meta.sources muss ein Objekt sein")

    sections = data.get("sections")
    _require(isinstance(sections, list) and sections, "sections fehlt oder ist leer")
    for i, section in enumerate(sections):
        _require(isinstance(section, dict), f"sections[{i}] ist kein Objekt")
        _require(
            section.get("type") in SECTION_TYPES,
            f"sections[{i}].type ungueltig: {section.get('type')!r}",
        )
        _require(
            isinstance(section.get("title"), str) and section["title"],
            f"sections[{i}].title fehlt",
        )
        _require(
            isinstance(section.get("content", ""), str),
            f"sections[{i}].content muss ein String sein",
        )
        items = section.get("items", [])
        _require(isinstance(items, list), f"sections[{i}].items muss eine Liste sein")
        for j, item in enumerate(items):
            _require(isinstance(item, dict), f"sections[{i}].items[{j}] ist kein Objekt")
            _require(
                item.get("kind") in ITEM_KINDS,
                f"sections[{i}].items[{j}].kind ungueltig: {item.get('kind')!r}",
            )
            _require(
                isinstance(item.get("prompt"), str) and item["prompt"],
                f"sections[{i}].items[{j}].prompt fehlt",
            )


def new_worksheet_skeleton(
    title: str, targeting: dict, goal: dict, sources: dict | None = None
) -> dict:
    """Erzeugt ein leeres, schema-konformes Arbeitsblatt-Geruest ohne sections.

    targeting: kanonische Zielsteuerung (mode "foerder" oder "curriculum").
    goal: Renderer-kompatible Projektion (siehe Moduldoc oben).
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "title": title,
            "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "targeting": targeting,
            "goal": goal,
            "sources": sources or {},
        },
        "sections": [],
    }
