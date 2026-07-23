---
name: worksheet-generator
description: Erzeugt individualisierte Arbeitsblaetter und Uebungsmaterial fuer Foerder- und Lernzwecke aus einem Foerderziel (Freitext + optionale ICF-Codes), Niveau und Alter -- optional angereichert durch einen Scan vorhandenen Materials (txt/md/docx) und/oder bereits recherchierte Stichpunkte. Nutze diesen Skill, wenn ein Arbeitsblatt, Uebungsblatt oder Foerdermaterial fuer eine paedagogische/therapeutische Fachkraft erstellt werden soll -- auch bei Formulierungen wie "erstelle ein Arbeitsblatt zu X", "Uebungsblatt fuer Foerderziel Y", "Material zum ICF-Code Z". Erzeugt niemals Klienten-/Personenbezug (kein Name, keine Diagnose) -- nur Ziel, Niveau, Alter. ICF-Referenz ist bring-your-own (_tools/icf_fetch.py).
---

# worksheet-generator -- Foerdermaterial-Generator

Erzeugt Fördermaterial (Arbeitsblätter, Übungsmaterial) für pädagogische und
therapeutische Fachkräfte mit einem lokalen LLM-Agenten. Das Modul liefert den
**Generator**, kein fertiges Material -- Ausgaben landen lokal beim Nutzer
(`output/`, gitignored), nie im Repo (Ausnahme: das eine synthetische
Beispiel in `examples/`).

**Kein Klienten-/Personenbezug:** Die Steuerung erfolgt ausschliesslich über
Förderziel (Freitext), ICF-Code(s), Niveau und Alter -- niemals über Namen
oder Diagnosen. Für Berichte oder Klientendaten ist dieses Modul nicht
zuständig (siehe Abgrenzung unten).

**Hinweis:** Material-Generator, kein Therapieprogramm und kein
Heilversprechen -- ersetzt keine fachliche Einschätzung durch qualifizierte
Fachkräfte. Erzeugte Arbeitsblätter vor Einsatz fachlich prüfen und
anpassen.

## Workflow

1. **Ziel wählen.** Förderziel als Freitext formulieren (z.B. "Mengen bis 10
   erfassen"), optional passende ICF-Code(s), Niveau
   (`standard`/`einfache_sprache`/`aac`/eigene Bezeichnung) und Alter bzw.
   Altersspanne festlegen. Optional ein Thema wählen, das eine eingebaute
   Aufgaben-Bank steuert (`mathe`, `deutsch`, sonst `allgemein`).
2. **Material scannen (optional).** Einen oder mehrere Ordner mit
   vorhandenem Material (`.txt`/`.md`/`.docx`) als Stil-/Kontextreferenz
   angeben -- über `config.json: material_dirs`, `config.local.json`-Override
   oder `--material-dir` auf der CLI. Der Scan liest kurze Exzerpte je Datei
   und trägt sie als Provenienz in `meta.sources.material_notes` ein; er
   fabriziert daraus KEINEN Aufgabeninhalt.
3. **Recherche einbringen (optional).** Bereits recherchierte Stichpunkte
   (z.B. aus einer vorgeschalteten Websuche oder einer lokalen Wissensbasis)
   als Liste übergeben (`--recherche`, mehrfach angebbar). Dieser Generator
   führt selbst KEINE Websuche durch -- die Stichpunkte werden direkt als
   konkrete Aufgaben-Prompts in die Aufgaben-Sektion übernommen.
4. **Generieren.** `generate_worksheet()` (Bibliothek) bzw.
   `python -m worksheet_generator generate ...` (CLI) erzeugt ein
   schema-konformes Arbeitsblatt-JSON (`worksheet_generator/schema.py`,
   `schema_version` versioniert). Themenspezifische Platzhalter sind als
   `(ANZUPASSEN)` markiert -- die inhaltliche Feinausarbeitung (konkrete,
   thematisch zugespitzte Aufgabentexte) übernimmt der aufrufende
   LLM-Agent, indem er das JSON vor dem Rendern anreichert.
5. **Rendern.** `python -m worksheet_generator render <json> --format
   md|html|docx` erzeugt die Ausgabedatei. `md`/`html` funktionieren immer
   ohne Zusatzabhängigkeiten; `docx` benötigt `python-docx` (fehlt es,
   meldet der Renderer das sauber statt abzustürzen).

## ICF-Referenz: bring-your-own

> Dieses Modul enthält KEINE ICF-Volltexte. Es nutzt ausschließlich amtliche
> ICF-Codes als neutrale Bezeichner. Kurztitel bezieht das mitgelieferte
> Fetch-Skript optional direkt von der Quelle (WHO ICD-11-API / BfArM) — so
> gelten für jeden Nutzer die jeweils aktuellen WHO/BfArM-Lizenzbedingungen
> (CC BY-ND 3.0 IGO bzw. § 5 Abs. 2 UrhG). ICF © WHO; deutsche Fassung ©
> WHO/BfArM. Die MIT-Lizenz dieses Repos erstreckt sich NICHT auf
> ICF-Inhalte.

Dieses Modul bündelt **keine** ICF-Kurztitel oder -Volltexte (ICF steht
unter WHO-Lizenz, deutsche Fassung zusätzlich unter BfArM-Bedingungen --
Details/Herleitung: interne Recherchenotiz `_intern/ICF-LIZENZ-CHECK.md`,
nicht Teil des Repos). `_tools/icf_fetch.py` bietet zwei Modi, um eine
lokale `icf_local.json` (Code + Kurztitel, Quelle + Abrufdatum im
Dateikopf) zu erzeugen:

- **Modus A -- eigene Quelldatei** (Default, kein Netzwerkzugriff): wandelt
  eine vom Nutzer selbst beschaffte CSV/JSON-Datei (z.B. Export aus dem
  WHO ICF Browser oder von `klassifikationen.bfarm.de`) um.
- **Modus B -- WHO-ICD-11-API** (`--who-api`): fragt Kurztitel live über die
  offizielle WHO-API ab, mit eigener kostenloser Registrierung
  (`WHO_ICD_CLIENT_ID`/`WHO_ICD_CLIENT_SECRET` als Umgebungsvariablen, nie
  in einer Datei ablegen).

Ohne `icf_local.json` funktioniert der Generator weiter -- ICF-Codes werden
dann ohne Kurztitel übernommen. Details, Lizenzhinweise und die genaue
API-Technik: Docstring von `_tools/icf_fetch.py`.

## Schulmodus (Curriculum)

`--subject <Fach>` schaltet vom Förder- in den Curriculum-Modus: Fach +
`--grade` (Klassen-/Lernstufe) + `--topic`, optional `--level`
(Differenzierung, z. B. G/M/E) und `--kompetenz` (kommagetrennt:
recherchieren, begründen, vergleichen, modellieren, interpretieren,
transferieren, reflektieren). Lehrplan-Kontext kommt optional aus
`curriculum_sources` (config): `local-files` (eigene Lehrplan-Auszüge)
und `lernquest` (experimentell, liest read-only aus einer lokalen
LernQuest-DB via `db_path`/ENV `LERNQUEST_DB`). Auszüge sind Kontext,
keine amtliche Quelle — Lehrplan-Treue prüft der Anwender.

## Design-Delegation (optional, manuelle Folgeschritte)

Für ansprechendere Ausgabeformen als Markdown/HTML/DOCX kann das erzeugte
Arbeitsblatt-JSON manuell an spezialisierte Skills/Connectoren übergeben
werden -- das ist bewusst NICHT in diesem Kern-Modul verdrahtet:

- **PowerPoint:** Inhalte aus dem Arbeitsblatt-JSON in eine Präsentation
  überführen, dabei den `pptx`-Skill für Layout/Gestaltung nutzen.
- **Canva:** Inhalte in ein Canva-Design überführen, dabei den
  Canva-Connector (MCP) nutzen, sofern verfügbar.
- **PDF:** HTML-Ausgabe extern nach PDF wandeln (z.B. `cc_md_to_pdf`/
  `fc_md_to_pdf` aus ellmos CodeCommander/FileCommander MCP, ein
  Browser-Druckdialog oder pandoc) -- absichtlich nicht im Kern erzwungen.

## CLI-Kurzreferenz

```bash
PYTHONIOENCODING=utf-8 python -m worksheet_generator generate \
  --freitext "Mengen bis 10 erfassen" --icf d150 --niveau einfache_sprache \
  --alter 8 --thema mathe --out output/worksheet.json

PYTHONIOENCODING=utf-8 python -m worksheet_generator render \
  output/worksheet.json --format md

PYTHONIOENCODING=utf-8 python -m worksheet_generator status
```

## Dateien

```
worksheet-generator/
├── worksheet_generator/    # Python-Paket: schema, generator, renderers, cli
├── _tools/icf_fetch.py     # ICF-Quelldatei -> icf_local.json (bring-your-own)
├── config.json             # Defaults (material_dirs, icf_source, renderers)
├── config.local.example.json  # Vorlage fuer config.local.json (gitignored)
├── examples/                # Ein synthetisches Beispiel (Input + Output)
├── tests/test_smoke.py      # Schema-Validierung + Generator + md-Renderer
└── bach_source/             # Rohsicherung des BACH-Vorgaengers (Referenz)
```

## Abgrenzung

- Berichte/Klientendaten: NICHT hier -- siehe Berichts-Pipeline/foerderplaner.
- Fertiges Material: wird nicht mitgeliefert, nur synthetische Beispiele.

Siehe auch: `KONZEPT.md` (Herkunft, Designentscheidungen), `README.md`
(Installation, API), `TODO.md` (offene Punkte).
