# Changelog

Alle relevanten Änderungen an `worksheet-generator` werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Hinzugefügt
- **Sicherheitsrichtlinie (`SECURITY.md`):** Sicherheitsrichtlinie für verantwortungsvolle Offenlegung, Local-First-Datenschutz, Zero-PII-Garantie auf Klienten- und Schülerdaten, WHO-API-Schutz und 48-Stunden-SLA nach P-006-Standard etabliert.
- **PEP 561 Typisierungsunterstützung:** Typisierungsmarker `worksheet_generator/py.typed` angelegt, Trove-Classifier `"Typing :: Typed"` und Package-Data-Eintrag in `pyproject.toml` ergänzt.
- **Release-Gate Aufgabenregister (`TODO.md`):** Standardisiertes Aufgabenregister mit 10-Gate `## STATUS`-Tabelle zur automatisierten Verifikation von Sicherheits- und Release-Invarianten angelegt.
- **CI-Matrix- & Dependabot-Härtung:** `.github/dependabot.yml` für wöchentliche Updates von `github-actions` und `pip` (mit `open-pull-requests-limit: 0` zur Begrenzung regulärer Versions-PRs; Sicherheitsupdates werden dadurch nicht konfiguriert) provisioniert; `.github/workflows/tests.yml` um ein eventgebundenes Whitespace- und Merge-Marker-Gate für eingecheckte Commitbereiche ergänzt.
- **Level-1-SBOM & Transparenz-Audit:** Vollständiges Plain-Text-Begleitdokument `THIRD_PARTY_LICENSES.txt` mit Invarianten-Matrix (`INV-LOCAL-01` bis `INV-SLA-10`), Unprivileged RunAsInvoker Zertifizierung, gesetzlichem Haftungsausschluss (§ 521 BGB Gefälligkeitsrecht) und 48h Security Response SLA ergänzt; `THIRD_PARTY_LICENSES.md` synchronisiert.
- **PEP 621 Metadaten:** `Changelog`- und `Security Policy`-URLs in `[project.urls]` in `pyproject.toml` ergänzt.
- **Vertragstest-Erweiterung:** 4 neue hermetische Vertragstests in `tests/test_metadata.py` (`test_ci_workflow_and_dependabot_hygiene`, `test_gitignore_lock_defense`, `test_level1_sbom_parity_and_invariants`, `test_final_gate_compliance_and_pep561`) ergänzt; Testsuite auf 35 Tests erweitert (100% grün).

### Behoben
- Ungültige `curriculum_sources` werden bei Status und Curriculum-Generierung mit einer klaren Konfigurationsfehlermeldung statt eines Tracebacks abgewiesen, bevor ein Arbeitsblatt geschrieben wird. Leere Quellen, `null`, unbekannte Adapter als Warnung und der unabhängige Fördermodus bleiben erhalten.
- Die englischen/deutschen Konfigurationsbeispiele verwenden die tatsächliche Liste von Adapter-Objekten und unterstützte Konfigurationsfelder.

### Geändert
- **Katalog-Standardisierung (`ellmos-module.v2.json`):** `source_of_truth.type` von `local-directory` auf `git-repository` retypisiert, um `runtime_source` und `commit_sha` im `.MODULES`-Katalog nahtlos abzuleiten.
- **Gitignore- & Lock-Defense-Härtung (`.gitignore`):** Release-Gate-Schutz für Datenbanken (`*.db`, `*.sqlite`, `*.sqlite3`), `data/`, Multi-Agenten-Locks und Agenten-Arbeitsverzeichnisse integriert; `TODO.md`-Ausschluss aufgehoben.

## [0.2.3] - 2026-09-10

### Hinzugefügt
- **PEP 621 Skripte und optionale Abhängigkeiten:** Konsolenbefehl `worksheet-generator` als `[project.scripts]`-Einstiegspunkt sowie `docx` und `test` als `[project.optional-dependencies]` in `pyproject.toml` deklariert.
- **CI-Matrix-Härtung:** Test-Matrix in `.github/workflows/tests.yml` um `macos-latest` erweitert (deckt Ubuntu, Windows und macOS entsprechend der Plattformdeklaration in `ellmos-module.v2.json` ab), `fail-fast: false` und `workflow_dispatch` ergänzt, Bytecode-Kompilierung (`python -m compileall`) und Konsolenbefehlsprüfung im Paket-Smoke-Test integriert.
- **Vertragstests & Testsuite:** Vertragstests für PEP 621 Metadaten (`[project.scripts]`, `[project.optional-dependencies]`, Versionsparität), HTML-Renderer-Escaping, Fehlermeldung bei fehlendem `python-docx` und CLI-Befehlsaufruf ergänzt (Testsuite von 19 auf 24 Tests erweitert).

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
  bisher nur auf Deutsch; `README.md` ist jetzt vollständig.
