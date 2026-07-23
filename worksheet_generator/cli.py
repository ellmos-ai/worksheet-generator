"""CLI-Einstieg: `python -m worksheet_generator <command> ...`.

Befehle:
    generate  -- Foerderziel ODER Curriculumziel -> Arbeitsblatt-JSON schreiben
    render    -- Arbeitsblatt-JSON -> md/html/docx rendern
    status    -- Konfiguration + verfuegbare Renderer/ICF-Referenz anzeigen

`generate` erkennt den Modus automatisch: `--subject` gesetzt -> Curriculum-
Modus (Fach/Klassenstufe, benoetigt zusaetzlich `--grade`); sonst
Foerder-Modus (benoetigt `--freitext`, wie bisher).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import renderers, schema
from .generator import Curriculumziel, Foerderziel, generate_worksheet, save_worksheet

MODULE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = MODULE_ROOT / "config.json"
LOCAL_CONFIG = MODULE_ROOT / "config.local.json"


def load_config() -> dict:
    """Laedt config.json und ueberlagert sie mit config.local.json (falls
    vorhanden, gitignored). Fehlt config.json, wird ein leeres dict genutzt."""
    config: dict = {}
    if DEFAULT_CONFIG.exists():
        config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    if LOCAL_CONFIG.exists():
        config.update(json.loads(LOCAL_CONFIG.read_text(encoding="utf-8")))
    return config


def load_icf_reference(config: dict) -> dict | None:
    """Laedt icf_local.json (siehe _tools/icf_fetch.py), falls vorhanden.
    Gibt None zurueck, wenn keine lokale ICF-Referenz beschafft wurde."""
    icf_path = MODULE_ROOT / config.get("icf_local_path", "icf_local.json")
    if not icf_path.exists():
        return None
    data = json.loads(icf_path.read_text(encoding="utf-8"))
    return data.get("codes", data)


def cmd_generate(args: argparse.Namespace) -> int:
    config = load_config()
    material_dirs = args.material_dir if args.material_dir else config.get("material_dirs", [])

    if args.subject:
        if not args.grade:
            print("FEHLER: Curriculum-Modus (--subject gesetzt) benoetigt zusaetzlich --grade", file=sys.stderr)
            return 1
        ziel = Curriculumziel(
            subject=args.subject,
            grade=args.grade,
            topic=args.topic or "",
            differenzierung=args.level or "",
            kompetenzfokus=[k.strip() for k in args.kompetenz.split(",") if k.strip()] if args.kompetenz else [],
        )
        curriculum_sources_config = config.get("curriculum_sources", [])
        worksheet = generate_worksheet(
            ziel,
            material_dirs=material_dirs,
            recherche_stichpunkte=args.recherche,
            curriculum_sources=curriculum_sources_config,
        )
    else:
        if not args.freitext:
            print("FEHLER: Foerder-Modus (kein --subject) benoetigt --freitext", file=sys.stderr)
            return 1
        ziel = Foerderziel(
            freitext=args.freitext,
            icf_codes=[c.strip() for c in args.icf.split(",") if c.strip()] if args.icf else [],
            niveau=args.niveau,
            alter=args.alter,
            thema=args.thema,
        )
        icf_reference = None if args.no_icf else load_icf_reference(config)
        worksheet = generate_worksheet(
            ziel,
            material_dirs=material_dirs,
            recherche_stichpunkte=args.recherche,
            icf_reference=icf_reference,
        )

    out = save_worksheet(worksheet, args.out)
    print(f"Arbeitsblatt-JSON geschrieben: {out} (Modus: {worksheet['meta']['targeting']['mode']})")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    schema.validate_worksheet(data)

    out_path = Path(args.out) if args.out else Path(args.input).with_suffix(f".{args.format}")
    if args.format == "md":
        out_path.write_text(renderers.to_markdown(data), encoding="utf-8")
    elif args.format == "html":
        out_path.write_text(renderers.to_html(data), encoding="utf-8")
    elif args.format == "docx":
        try:
            renderers.to_docx(data, out_path)
        except renderers.RendererUnavailable as exc:
            print(f"UEBERSPRUNGEN: {exc}", file=sys.stderr)
            return 2
    else:
        print(f"Unbekanntes Format: {args.format}", file=sys.stderr)
        return 1
    print(f"Gerendert: {out_path}")
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    config = load_config()
    icf_reference = load_icf_reference(config)
    try:
        import docx  # noqa: F401

        docx_status = "verfuegbar"
    except ImportError:
        docx_status = "NICHT installiert (pip install python-docx)"

    curriculum_sources_config = config.get("curriculum_sources", [])

    print("worksheet-generator -- Status")
    print(f"  Schema-Version:     {schema.SCHEMA_VERSION}")
    print(f"  config.json:        {'gefunden' if DEFAULT_CONFIG.exists() else 'FEHLT'}")
    print(f"  config.local.json:  {'aktiv (Override)' if LOCAL_CONFIG.exists() else '(kein Override)'}")
    print(f"  material_dirs:      {config.get('material_dirs', [])}")
    if icf_reference:
        print(f"  icf_local.json:     geladen ({len(icf_reference)} Codes)")
    else:
        print("  icf_local.json:     NICHT vorhanden -- siehe _tools/icf_fetch.py")
    if curriculum_sources_config:
        typen = ", ".join(e.get("type", "?") for e in curriculum_sources_config)
        print(f"  curriculum_sources: {len(curriculum_sources_config)} konfiguriert ({typen})")
    else:
        print("  curriculum_sources: keine konfiguriert (Curriculum-Modus laeuft ohne Kontext-Adapter)")
    print("  Renderer md/html:   immer verfuegbar")
    print(f"  Renderer docx:      {docx_status}")
    print("  Renderer pdf:       nicht eingebaut -- HTML -> PDF extern (siehe SKILL.md)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worksheet_generator", description="Foerdermaterial-Generator"
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser(
        "generate",
        help="Arbeitsblatt-JSON erzeugen (Foerder-Modus per --freitext, Curriculum-Modus per --subject)",
    )
    # Foerder-Modus (bestehend)
    gen.add_argument("--freitext", default="", help="Foerder-Modus: Foerderziel als Freitext")
    gen.add_argument("--icf", default="", help="Foerder-Modus: kommagetrennte ICF-Codes, z.B. d140,d145")
    gen.add_argument("--niveau", default="standard", help="Foerder-Modus: z.B. standard, einfache_sprache, aac")
    gen.add_argument("--alter", default="", help="Foerder-Modus: Alter bzw. Altersspanne")
    gen.add_argument("--thema", default="allgemein", help="Foerder-Modus: Aufgaben-Bank, z.B. mathe, deutsch")
    gen.add_argument("--no-icf", action="store_true", help="Foerder-Modus: ICF-Referenz nicht laden")
    # Curriculum-Modus (neu) -- --subject gesetzt schaltet den Modus um
    gen.add_argument("--subject", default="", help="Curriculum-Modus: Unterrichtsfach (schaltet den Modus um)")
    gen.add_argument("--grade", default="", help="Curriculum-Modus: Klassen- bzw. Lernstufe")
    gen.add_argument("--topic", default="", help="Curriculum-Modus: Thema")
    gen.add_argument("--level", default="", help="Curriculum-Modus: Differenzierung, z.B. G/M/E")
    gen.add_argument(
        "--kompetenz", default="",
        help="Curriculum-Modus: kommagetrennter Kompetenzfokus, z.B. vergleichen,interpretieren",
    )
    # Gemeinsam
    gen.add_argument(
        "--material-dir", action="append", help="Material-Ordner (mehrfach angebbar)"
    )
    gen.add_argument(
        "--recherche", action="append", help="Bereits recherchierter Stichpunkt (mehrfach angebbar)"
    )
    gen.add_argument("--out", default="output/worksheet.json", help="Zieldatei fuer das JSON")
    gen.set_defaults(func=cmd_generate)

    ren = sub.add_parser("render", help="Arbeitsblatt-JSON in ein Format rendern")
    ren.add_argument("input", help="Pfad zum Arbeitsblatt-JSON")
    ren.add_argument("--format", choices=["md", "html", "docx"], default="md")
    ren.add_argument("--out", default=None, help="Zieldatei (Default: Input-Pfad mit neuer Endung)")
    ren.set_defaults(func=cmd_render)

    stat = sub.add_parser("status", help="Konfiguration + Renderer-Verfuegbarkeit anzeigen")
    stat.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
