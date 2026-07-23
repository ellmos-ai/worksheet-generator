# Beispiel (synthetisch)

Ein einziges, vollständig fiktives Beispiel -- kein echtes Fördermaterial,
kein Klienten-/Personenbezug. Zeigt den vollen Pfad Förderziel → Generator →
Renderer anhand eines erfundenen Förderziels ("Farben benennen und
sortieren").

## Dateien

- `worksheet.json` -- Ausgabe von `generate_worksheet()` (schema-konform,
  `schema_version: "1.0"`).
- `worksheet.md` -- gerendert mit `renderers.to_markdown()`.
- `worksheet.html` -- gerendert mit `renderers.to_html()`.

(Kein DOCX-Beispiel im Repo -- Binärdatei, unnötig für die Demonstration;
DOCX-Rendering ist über `tests/test_smoke.py` und den Docstring von
`renderers.to_docx()` abgedeckt.)

## Curriculum-Beispiel (Schulmodus)

- `worksheet_curriculum.json` / `worksheet_curriculum.md` -- fiktives
  Schul-Arbeitsblatt (Mathematik, Klasse 3, Einmaleins, Differenzierung M,
  Kompetenzfokus Begruenden/Vergleichen), erzeugt mit:

```bash
PYTHONIOENCODING=utf-8 python -m worksheet_generator generate \
  --subject Mathematik --grade 3 --topic "Einmaleins" --level M \
  --kompetenz "begruenden,vergleichen" --out examples/worksheet_curriculum.json
PYTHONIOENCODING=utf-8 python -m worksheet_generator render examples/worksheet_curriculum.json --format md --out examples/worksheet_curriculum.md
```

## Erzeugt mit

```bash
PYTHONIOENCODING=utf-8 python -m worksheet_generator generate \
  --freitext "Farben benennen und sortieren (fiktives Beispiel)" \
  --icf d137 --niveau aac --alter 6 --thema allgemein \
  --recherche "Welche Farbe hat die Sonne auf dem Bild?" \
  --no-icf --out examples/worksheet.json

PYTHONIOENCODING=utf-8 python -m worksheet_generator render examples/worksheet.json --format md --out examples/worksheet.md
PYTHONIOENCODING=utf-8 python -m worksheet_generator render examples/worksheet.json --format html --out examples/worksheet.html
```

`--no-icf` wurde gesetzt, weil keine lokale `icf_local.json` vorliegt (siehe
`_tools/icf_fetch.py`) -- der ICF-Code `d137` erscheint daher ohne Kurztitel.
Die beiden Aufgaben mit `(ANZUPASSEN)` sind bewusste Platzhalter aus der
eingebauten Aufgaben-Bank (Thema `allgemein`); die dritte Aufgabe stammt aus
dem übergebenen `--recherche`-Stichpunkt und zeigt, wie bereits recherchierte
Inhalte direkt als konkrete Aufgaben-Prompts übernommen werden.
