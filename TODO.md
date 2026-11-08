# TODO — worksheet-generator

## STATUS

| Category | Status | Notes |
|----------|--------|-------|
| Secrets | :green_circle: OK | 0 Secrets in getrackten Dateien; AST- und Text-Scan sauber |
| Private Data (PII) | :green_circle: OK | 0 personenbezogene Entwicklerdaten oder Klientendaten in getrackten Dateien |
| Hardcoded Paths | :green_circle: OK | Keine hardcodierten Entwickler-Pfade (<HOME>/...); portable relative Pfade |
| Database Files | :green_circle: OK | 0 `.db` oder SQLite-Dateien im Repository getrackt |
| .env Files | :green_circle: OK | 0 `.env`-Dateien getrackt; `.gitignore` schützt Umgebungsvariablen |
| BACH Internals | :green_circle: OK | 0 BACH-interne Dokumente; eigenständiges, portables Fördermaterial-Werkzeug |
| .gitignore | :green_circle: OK | Alle Pflichtmuster (`__pycache__`, `*.pyc`, `.env`, `*.db`, `data/`, etc.) gehärtet |
| Language & Parity | :green_circle: OK | Englisches `README.md`, zweisprachiges deutsches `README_de.md`, echte Umlaute |
| LICENSE & SBOM | :green_circle: OK | MIT-Lizenz, Level 1 SBOM (`THIRD_PARTY_LICENSES.md`), PEP 639 Metadaten |
| Overall | **PASS (10/10 Gates)** | `final_gate_check.py` 10 PASS, 0 FAIL, 0 WARN; Pytest grün |

**Audit-Datum:** 2026-11-08 (Geprüft durch Antigravity / Gemini worker via `[AI_MODULES_CARE]`)<br>
**Gate-Check-Ergebnis:** 10 PASS, 0 FAIL, 0 WARN (READY FOR PUBLIC RELEASE)<br>
**Testsuite-Status:** 28/28 Pytest-Tests bestanden (100% grün auf Windows)<br>
**Rolle:** Domain Module für Fördermaterial- und Arbeitsblattgenerierung (`domain.education.material-generation`)<br>
**Typisierung & PEP 561:** `worksheet_generator/py.typed` verankert, Trove-Classifier `"Typing :: Typed"`<br>
**Stand:** 2026-11-08 · Version 0.2.3

## Offen

- [ ] Optionale Adapter für Präsentations- und Visualisierungs-Tools (z. B. pptx-Export, Canva-Anbindung) als deklarative CLI-Submodule formalisieren.
- [ ] Zusätzliche Lehrplan-Standards und bundeslandspezifische Kompetenzraster in `tests/fixtures/curriculum_local` bereitstellen.

## Bewusst nicht gebaut

- **Direkte PDF-Generierung via C-Bibliotheken** — Statt schwergewichtiger nativer PDF-Abhängigkeiten setzt das Modul auf portables HTML/CSS-Drucken und Markdown-Renderer.
- **Proprietäres ICF-Kurztitel-Bundling** — Lizenzneutrales Konzept: ICF-Klassifikationscodes werden unterstützt, offizielle Kurztitel und Volltexte verbleiben beim Anwender bzw. der lizenzierten WHO-API.

## Abgeschlossene Aufgaben

- [x] **TASK-WG-01: Final Gate Check Härtung (10/10 PASS), PEP 561 py.typed, SECURITY.md & Plan-D-Parität (v0.2.3)** (`effort=low`, `scope=hygiene`, priority `high`).
  - **Ergebnis:** `.gitignore` um `*.db` und `data/` erweitert sowie `TODO.md`-Exklusion aufgelöst; `TODO.md` mit standardisierter 10-Gate `## STATUS`-Tabelle etabliert; PEP 561 Typisierungsmarker `worksheet_generator/py.typed` erstellt und in `pyproject.toml` als `package-data` sowie Trove-Classifier `"Typing :: Typed"` verankert; `SECURITY.md` für Local-First-Datenschutz, Zero-PII-Garantie auf Klientendaten und 48h-SLA hinzugefügt; Manifest `ellmos-module.v2.json` von `local-directory` auf `git-repository` retypisiert; Vertragstests in `tests/test_metadata.py` erweitert.
