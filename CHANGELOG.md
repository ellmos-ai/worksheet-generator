# Changelog

Alle relevanten Änderungen an `worksheet-generator` werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-08-22

### Behoben
- Setuptools-Paketentdeckung auf `worksheet_generator*` begrenzt, damit
  dokumentationsbezogene Root-Ordner wie `assets/` nicht als Python-Pakete gelten.
- Standardkonfiguration als geprüfte Paketressource aufgenommen; ein installiertes
  Wheel verwendet sie auch außerhalb des Repository-Ordners.
- Eigener CI-Paketjob baut Wheel und sdist und prüft Status, Generierung und
  Markdown-Rendering aus einer isolierten Wheel-Installation.

## [0.2.1] - 2026-08-22

### Geändert
- Lizenzmetadaten auf PEP 639 umgestellt: SPDX-Ausdruck `MIT`, explizite
  Einbindung der Root-`LICENSE` und Entfernung des veralteten Lizenz-Classifiers.
- Minimale Setuptools-Version für die verwendete PEP-639-Unterstützung auf
  77.0.3 angehoben und der Metadatenvertrag durch einen Regressionstest gesichert.

## [0.2.0] - 2026-08-11

### Hinzugefügt
- **Schul-/Curriculum-Modus (nachdokumentiert):** Der zweite Generierungsmodus
  (`--subject`/`--grade`/`--topic`, `Curriculumziel`, `worksheet_generator/curriculum_sources.py`
  mit den Adaptern `local-files` und `lernquest`) war seit `2ddd04b` im Code und in
  `__init__.__version__ = "0.2.0"` hinterlegt, hatte aber nie einen Changelog-Eintrag.
- `.gitattributes`: Zeilenenden werden im Repository auf LF festgeschrieben.

### Geändert
- **Versionsstand vereinheitlicht:** `pyproject.toml` stand auf `0.1.2`, während der
  Code bereits `0.2.0` auswies. Maßgeblich ist der Code — alle Träger stehen jetzt
  auf `0.2.0`.
- **Aussagen an den Code angeglichen:** Die Formulierung „100% offline" gilt für die
  Generator-Engine; das optionale Werkzeug `_tools/icf_fetch.py --who-api` greift auf
  ausdrückliche Anweisung des Nutzers auf die WHO-API zu. Beide READMEs sagen das jetzt.
- **Englische Dokumentation ergänzt:** Der ICF-Lizenzhinweis (WHO/BfArM, MIT deckt keine
  ICF-Inhalte) sowie Installation, Konfiguration, Curriculum-Modus und Tests standen
  bisher nur in `README_de.md`.

### Entfernt
- Interne Arbeitsdatei `TODO.md` und interne Verweise (nicht öffentliche Ablagen,
  Notiz-Pfade und Projektnamen) aus dem veröffentlichten Stand genommen.

## [0.1.2] - 2026-07-27

### Hinzugefügt
- **Dokumentations-Parität & i18n:** `README_de.md` als vollständige deutsche Dokumentation mit Systemarchitektur, GFM-Callouts und Ökosystem-Verlinkungen ergänzt.
- **Bilinguale Startseite:** `README.md` mit Sprachwechsel und konsistenten Schnellstart-Anleitungen aktualisiert.

### Geändert
- **LLM-Metadaten:** `llms.txt` um `README_de.md` ergänzt und auf den aktuellen Prüfstand synchronisiert.
- **Projekt-Version:** `pyproject.toml` auf `0.1.2` angehoben.

## [0.1.1] - 2026-07-26

### Hinzugefügt
- **Discoverability & README-Design:** GFM Callout Notes (`> [!NOTE]`, `> [!IMPORTANT]`), zusätzliche Shields.io Badges (pytest, local-first privacy) und Mermaid Systemarchitektur-Diagramm in `README.md` integriert.
- **Pytest-Konfiguration:** `[tool.pytest.ini_options]` in `pyproject.toml` nachgerüstet.

### Geändert
- **LLM-Metadaten:** Verification & Timestamp in `llms.txt` auf `2026-07-26` aktualisiert.

## [0.1.0] - 2026-07-24

### Hinzugefügt
- Technisches Hygiene- & Dokumentations-Update.
- Maschinenlesbares `llms.txt` im Repo-Root für KI-Agenten und RAG-Systeme.
- Standardisiertes `pyproject.toml` mit Paket-Metadaten und Discoverability-Keywords.
- GitHub Actions CI Workflow (`.github/workflows/tests.yml`) für automatisierte Pytest-Matrix-Tests unter Linux und Windows.
- Shields.io Badges, Schnellübersicht und Discoverability-Erweiterungen in `README.md`.
- `repository` URL in `ellmos-module.v2.json` eingetragen.
