# worksheet-generator

**Fördermaterial-Generator für pädagogische und therapeutische Fachkräfte mit
lokalem LLM-Agenten (Claude Code u. a.).**

Dieses Modul erzeugt aus einem Förderziel (Freitext + optionale ICF-Codes),
Niveau und Alter ein strukturiertes **Arbeitsblatt-JSON**, das anschließend
nach Markdown, HTML oder DOCX gerendert werden kann. Es liefert den
**Generator**, kein fertiges Fördermaterial -- im Repo liegt lediglich ein
synthetisches Beispiel (`examples/`).

**Kein Klienten-/Personenbezug:** Steuerung ausschließlich über
Förderziel/Niveau/Alter, niemals über Name oder Diagnose.

**Hinweis:** Dieses Modul ist ein **Material-Generator**, kein
Therapieprogramm und kein Heilversprechen. Es ersetzt keine fachliche
Einschätzung durch qualifizierte pädagogische/therapeutische Fachkräfte --
erzeugte Arbeitsblätter sind vor dem Einsatz fachlich zu prüfen und
anzupassen.

**Status:** Development / Public-Kandidat -- siehe `TODO.md` für offene
Punkte vor einer Veröffentlichung.

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
