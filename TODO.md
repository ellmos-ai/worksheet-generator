# TODO — worksheet-generator

- [x] `bach_source/worksheet_generator/` gesichtet: generator.py/templates/
  als Vorbild fuer die neue Engine genutzt; `output/` geleert (enthielt
  Alt-Ballast mit realistisch wirkenden Klientendaten -- geloescht, 2026-07-23).
- [x] Kern gebaut: Arbeitsblatt-JSON-Schema (`worksheet_generator/schema.py`,
  versioniert) + Generator (Material-Scan txt/md/docx + Recherche-Stichpunkte
  + ICF-Titel-Anreicherung, `worksheet_generator/generator.py`) + Renderer
  md/html (Kern) + docx (optional, python-docx) in
  `worksheet_generator/renderers.py`. PDF bewusst nicht selbst gebaut, nur
  dokumentiert (HTML → PDF extern, siehe SKILL.md). CLI:
  `worksheet_generator/cli.py` (`generate`/`render`/`status`).
- [ ] Optionale Adapter: pptx-Skill-Delegation, Canva-Connector-Delegation
  (Laufzeit-Erkennung, sauberes Degradieren wenn nicht installiert) --
  aktuell nur als manuelle Folgeschritte in SKILL.md dokumentiert, noch
  nicht als Code-Adapter gebaut.
- [x] `icf_fetch.py` gebaut (`_tools/icf_fetch.py`), zwei Modi: (A) eigene
  Quelldatei CSV/JSON -> icf_local.json, kein Netzwerkzugriff (Muster
  analog gesetze_fetch.py, aber ohne Auto-Download); (B) `--who-api`
  Live-Abfrage der WHO-ICD-11-API mit eigener Nutzer-Registrierung
  (OAuth2 Client-Credentials, verifiziert 2026-07-23 via WHO-API-Doku).
  config.json/config.local.example.json vorhanden (private ICF-Datei NUR
  als lokaler, gitignored Override -- `icf_local.json` selbst nie im Repo).
- [x] ICF-Lizenzcheck (Websuche-Niveau) durch Worker w2 durchgefuehrt, siehe
  `_intern/ICF-LIZENZ-CHECK.md` (nicht Teil des Repos). Entscheidung
  umgesetzt: Repo bundelt NUR Codes, KEINE deutschen Kurztitel/Volltexte.
- [ ] **Wiedervorlage aus dem Lizenzcheck:** Vor einem optionalen
  Convenience-Bundle mit deutschen Kurztiteln muessten die
  BfArM-Downloadbedingungen im Volltext manuell auf Drittweiterverbreitung
  geprueft werden (`_intern/ICF-LIZENZ-CHECK.md`, Abschnitt
  "Wiedervorlage"). Aktuell nicht geplant -- nur als offener Punkt notiert.
- [x] Formaler ICF-Lizenzcheck (Gutachtenstufe): Operator-Entscheid
  2026-07-23 -- NICHT mehr noetig, da das Repo nach Variante b (siehe oben)
  ohnehin KEINE ICF-Inhalte (Codes/Kurztitel/Volltexte) mehr bundelt; der
  Pruefgegenstand ist damit entfallen. Die Websuche-Ersteinschaetzung von
  Worker w2 (`_intern/ICF-LIZENZ-CHECK.md`) gilt als ausreichend dokumentierte
  Grundlage fuer diese Entscheidung.
- [x] SKILL.md (nutzerneutral), README, synthetisches Beispiel
  (`examples/`), Tests (`tests/test_smoke.py`) -- alle vorhanden, Tests
  gruen (4/4, siehe Session-Rueckgabe).
- [ ] Release-Gates via /repo-publish-check (Voll-Modus) → User-Freigabe → Repo.
