# Changelog

Alle relevanten Änderungen an `worksheet-generator` werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
