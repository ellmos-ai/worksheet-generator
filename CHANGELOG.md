# Changelog

Alle relevanten Änderungen an `worksheet-generator` werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-07-27

### Hinzugefügt
- **Dokumentations-Parität & i18n:** `README_de.md` als vollständige deutsche Dokumentation mit erweiterten Systemarchitektur-Diagrammen, GFM Alert-Callouts (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`) und Ökosystem-Verlinkungen (`report-forge`, `USMC`, `ellmos-homebase-mcp`) angelegt.
- **Bilinguale Startseite (`README.md`):** Primäres README auf bilinguales / Englisches Layout mit Language-Switcher Badge (`[Deutsch](README_de.md)` \| `[English](README.md)`) und Schnellstart-Anleitungen aktualisiert.

### Geändert
- **LLM Metadaten (`llms.txt`):** Dateikartierung um `README_de.md` erweitert und `Last Checked` Timestamp auf `2026-07-27` aktualisiert.
- **Projekt-Version:** `pyproject.toml` auf `v0.1.2` angehoben.

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
