![worksheet-generator Banner](assets/banner.png)

# worksheet-generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ellmos-ai/worksheet-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/worksheet-generator/actions)
[![Pytest](https://img.shields.io/badge/pytest-16%20passed-brightgreen.svg)](tests/)
[![Local-First](https://img.shields.io/badge/privacy-100%25%20local--first-blue.svg)](#eigenschaften)
[![llms.txt](https://img.shields.io/badge/llms.txt-available-green.svg)](llms.txt)

**Fördermaterial-Generator für pädagogische und therapeutische Fachkräfte mit lokalem LLM-Agenten (Claude Code u. a.).**

> [!NOTE]
> **AI Agent & LLM-Integration:** Dieses Repository liefert maschinenlesbare Schnittstellen (`llms.txt`, `SKILL.md` und `worksheet_generator/schema.py`), die von lokalen KI-Agenten (Claude Code, Antigravity, Open-WebUI) direkt zur automatisierten Arbeitsblatt-Generierung und Anreicherung genutzt werden können.

> [!IMPORTANT]
> **Datenschutz & Privacy:** `worksheet-generator` arbeitet 100% offline und verarbeitet keinerlei Klienten- oder Personendaten. Steuerung ausschließlich über abstrakte Förderziele, ICF-Codes oder Schulcurricula.

Dieses Modul erzeugt aus einem Förderziel (Freitext + optionale ICF-Codes), Niveau und Alter ein strukturiertes **Arbeitsblatt-JSON**, das anschließend nach Markdown, HTML oder DOCX gerendert werden kann. Es liefert den **Generator**, kein fertiges Fördermaterial -- im Repo liegt lediglich ein synthetisches Beispiel (`examples/`).

| Eigenschaft | Beschreibung |
|---|---|
| **Privacy & DSGVO** | Local-First, 100% offline Engine. Kein Personen- oder Klientenbezug. |
| **Generierungsmodi** | (1) Förderziel & ICF-Codes (Förder-Modus) / (2) Fach, Schulstufe & Thema (Curriculum-Modus) |
| **Exportformate** | Markdown, HTML, DOCX (optional via `python-docx`) |
| **AI Agent Ready** | Inklusive `llms.txt` und `SKILL.md` zur nahtlosen Integration in Claude Code, Antigravity & LLM-Pipelines |

**Kein Klienten-/Personenbezug:** Steuerung ausschließlich über Förderziel/Niveau/Alter, niemals über Name oder Diagnose.

**Hinweis:** Dieses Modul ist ein **Material-Generator**, kein Therapieprogramm und kein Heilversprechen. Es ersetzt keine fachliche Einschätzung durch qualifizierte pädagogische/therapeutische Fachkräfte -- erzeugte Arbeitsblätter sind vor dem Einsatz fachlich zu prüfen und anzupassen.

**Status:** Beta / Public-Kandidat -- siehe `TODO.md` für offene Punkte.

## Installation

Keine Pflicht-Abhängigkeiten -- reine Python-Standardbibliothek (Python ≥
3.10 wegen `X | Y`-Typannotationen und `dataclasses`). Optional für den
DOCX-Renderer:

```bash
pip install python-docx
```

## Nutzung

### Als Bibliothek

```python
from worksheet_generator import Foerderziel, generate_worksheet, save_worksheet
from worksheet_generator import renderers

ziel = Foerderziel(
    freitext="Mengen bis 10 erfassen",
    icf_codes=["d150"],
    niveau="einfache_sprache",
    alter="8",
    thema="mathe",
)
worksheet = generate_worksheet(ziel)
save_worksheet(worksheet, "output/worksheet.json")

print(renderers.to_markdown(worksheet))
```

### Über die CLI

```bash
PYTHONIOENCODING=utf-8 python -m worksheet_generator generate \
  --freitext "Mengen bis 10 erfassen" --icf d150 --niveau einfache_sprache \
  --alter 8 --thema mathe --out output/worksheet.json

PYTHONIOENCODING=utf-8 python -m worksheet_generator render \
  output/worksheet.json --format md

PYTHONIOENCODING=utf-8 python -m worksheet_generator status
```

`status` zeigt die aktive Konfiguration, ob eine `icf_local.json` vorliegt
und ob der optionale DOCX-Renderer verfügbar ist.

## Systemarchitektur & Workflow

```mermaid
flowchart TD
    subgraph Inputs["1. Eingabe & Modus"]
        A1["Förderziel & ICF-Codes<br/>(Förder-Modus)"]
        A2["Fach, Stufe & Thema<br/>(Schul-Modus)"]
    end

    subgraph CoreEngine["2. Offline Generator Engine"]
        B1["Pydantic Schema Validation<br/>(worksheet_generator/schema.py)"]
        B2["Deterministische Generierung<br/>(worksheet_generator/generator.py)"]
        B3["Lehrplan- & Context-Adapter<br/>(Local Files / LernQuest DB)"]
    end

    subgraph OutputFormat["3. Multi-Format Output"]
        C1["Arbeitsblatt JSON Schema"]
        D1["Markdown (.md)"]
        D2["HTML (.html)"]
        D3["DOCX (.docx)"]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B3 --> B2
    B2 --> C1
    C1 --> D1
    C1 --> D2
    C1 --> D3
```

## Arbeitsblatt-JSON-Schema

Definiert und validiert in `worksheet_generator/schema.py`
(`SCHEMA_VERSION`). Grobstruktur:

```
schema_version, meta{title, generated_at, goal{icf_codes, icf_titles,
freitext, niveau, alter, thema}, sources{material_scan, material_notes,
recherche_stichpunkte, icf_reference_used}}, sections[{type, title, content,
items[{kind, prompt, options?, answer_space?, hint?}]}]
```

`kind` je Item: `luecke`, `zuordnung`, `rechnung`, `frage`, `freitext`.
`type` je Section: `intro`, `task`, `bonus`, `custom`.

Der Generator arbeitet **deterministisch und offline** (kein LLM-, kein
Netzwerkzugriff): Themenspezifische Platzhalter sind als `(ANZUPASSEN)`
markiert; bereits recherchierte Stichpunkte (`recherche_stichpunkte`) werden
direkt als konkrete Aufgaben-Prompts übernommen. Die inhaltliche
Feinausarbeitung obliegt dem aufrufenden LLM-Agenten, der das JSON vor dem
Rendern anreichert.

## Konfiguration

`config.json` enthält die Defaults (`material_dirs`, `icf_source`,
`renderers`, `sprache`). Lokale, nicht versionierte Overrides gehören in
`config.local.json` (gitignored) -- Vorlage: `config.local.example.json`.

## Schulmodus (Curriculum)

Neben dem Förder-Modus (ICF/Förderziele) erzeugt der Generator Arbeitsblätter
für Unterrichtsfächer und Lernstufen. `--subject` schaltet den Modus um:

```bash
# Mathe, Klasse 3, Thema Einmaleins
python -m worksheet_generator generate --subject Mathematik --grade 3 --topic "Einmaleins" --out ab.json

# Gesellschaftswissenschaften 7/8 mit Differenzierung und Kompetenzfokus
python -m worksheet_generator generate --subject Gesellschaftswissenschaften --grade "7/8" \
  --topic "Wasserkreislauf" --level M --kompetenz recherchieren,begruenden --out ab.json
```

### Lehrplan-Quellen (`curriculum_sources`, optional)

Konfigurierbare Kontext-Quellen in `config.json`/`config.local.json`:

```json
"curriculum_sources": [
  {"type": "local-files", "path": "C:/eigene/lehrplan-auszuege"},
  {"type": "lernquest", "db_path": "optional; sonst ENV LERNQUEST_DB"}
]
```

- **local-files:** eigener Ordner mit Lehrplan-Auszügen/Themenlisten (`.md`/`.json`);
  das Fach muss die Datei über Dateinamen oder Titel-Überschrift qualifizieren.
- **lernquest (experimentell):** liest NUR LESEND aus einer lokalen
  LernQuest-Kompetenzregister-Datenbank (SQLite, `?mode=ro`; Pfad via
  `db_path` oder ENV `LERNQUEST_DB`). LernQuest ist in Entwicklung — fehlt
  DB/Tabelle, meldet der Adapter das als Warnung statt zu crashen; bei
  Schema-Änderungen wird der Adapter nachgezogen.

Hinweis: Die gelieferten Auszüge sind Prompt-KONTEXT, keine amtliche Quelle.
Lehrplan-Treue verantwortet der Nutzer — Referenz bleiben die amtlichen
Lehrpläne des jeweiligen Bundeslandes.

## ICF-Referenz (bring-your-own)

> Dieses Modul enthält KEINE ICF-Volltexte. Es nutzt ausschließlich amtliche
> ICF-Codes als neutrale Bezeichner. Kurztitel bezieht das mitgelieferte
> Fetch-Skript optional direkt von der Quelle (WHO ICD-11-API / BfArM) — so
> gelten für jeden Nutzer die jeweils aktuellen WHO/BfArM-Lizenzbedingungen
> (CC BY-ND 3.0 IGO bzw. § 5 Abs. 2 UrhG). ICF © WHO; deutsche Fassung ©
> WHO/BfArM. Die MIT-Lizenz dieses Repos erstreckt sich NICHT auf
> ICF-Inhalte.

Siehe `SKILL.md`, Abschnitt „ICF-Referenz: bring-your-own", und den
Docstring von `_tools/icf_fetch.py`. Kurzfassung: Dieses Modul bündelt
**keine** ICF-Kurztitel oder -Volltexte (WHO-/BfArM-Lizenz).
`_tools/icf_fetch.py` erzeugt eine lokale `icf_local.json` (Code +
Kurztitel, Quelle + Abrufdatum im Dateikopf; gitignored, nie Teil des
Repos) -- entweder aus einer selbst beschafften Quelldatei (Modus A) oder
per Live-Abfrage der WHO-ICD-11-API mit eigener Registrierung (Modus B):

```bash
# Modus A: eigene CSV/JSON-Quelldatei, kein Netzwerkzugriff
PYTHONIOENCODING=utf-8 python _tools/icf_fetch.py --source pfad/zu/quelle.csv

# Modus B: Live-Abfrage der WHO-API (eigene Registrierung via icd.who.int/icdapi)
WHO_ICD_CLIENT_ID=... WHO_ICD_CLIENT_SECRET=... \
PYTHONIOENCODING=utf-8 python _tools/icf_fetch.py --who-api --codes d150,d115 --lang de
```

## Renderer

| Renderer | Status |
|---|---|
| Markdown | Kern, immer verfügbar |
| HTML | Kern, immer verfügbar |
| DOCX | Kern, optional -- benötigt `python-docx` |
| PDF | nicht eingebaut -- HTML → PDF extern (siehe `SKILL.md`) |
| PowerPoint / Canva | optionale Design-Delegation, siehe `SKILL.md` |

## Tests

```bash
PYTHONIOENCODING=utf-8 python -m pytest tests/ -v
```

`tests/test_smoke.py` prüft Schema-Validierung, einen Generator-Lauf mit
synthetischem Mini-Input und den Markdown-Renderer.

## Herkunft

Extrahiert und neutralisiert aus dem BACH-Vorgänger
`agents/_experts/worksheet_generator/` -- BACH-Pfade und
Klienten-/Personenbezug entfernt. Die lokale Rohsicherung des
BACH-Vorgängers (`bach_source/`) diente nur als Referenz beim Bau dieser
Engine und ist bewusst **nicht** Teil dieses Repos (`.gitignore`). Details
in `KONZEPT.md`.

## Lizenz

MIT (siehe `LICENSE`), sofern nicht anders vermerkt.
