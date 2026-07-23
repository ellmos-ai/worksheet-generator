# KONZEPT — worksheet-generator (beschlossen 2026-07-23, User-Vorgaben)

## Zweck

Public-fähiges Skill/Modul, das **Fördermaterial ERZEUGT** (Arbeitsblätter,
Übungsmaterial) — es wird KEIN fertiges Material veröffentlicht, sondern der
Generator. Zielgruppe: pädagogische/therapeutische Fachkräfte mit lokalem
LLM-Agenten (Claude Code u. a.).

## Eingaben (drei Quellen, kombinierbar)

1. **Vorhandenes Material auf Platte:** konfigurierbarer Material-Ordner des
   Nutzers (Scan/Index; Formate txt/md/docx/pdf) als Stil- und Inhaltsvorlage.
2. **Recherche:** Websuche bzw. konfigurierbare lokale Wissensbasis
   (`config.local.json`-Override — bei Lukas: `.WISSEN`; im Public-Default: aus).
3. **Förderziel-Steuerung:** ICF-Code(s) + Freitext-Ziel + Niveau/Alter.

## ICF: Bring-your-own (law-checker-Registry-Muster)

- Public-Modul liefert NUR eine schlanke Struktur (Codes als Schlüssel) und ein
  Abruf-Skript `icf_fetch.py` (analog `gesetze_fetch.py`), mit dem sich Nutzer
  die ICF-Referenz selbst beschaffen (WHO/BfArM-Quelle, Quelle+Abrufdatum im
  Dateikopf). VOR Release: ICF-Lizenzcheck via `/rechtsabteilung`
  (WHO/BfArM-Nutzungsbedingungen; nur Codes+Kurztitel bundeln, keine Volltexte).
- **Lukas' kuratierte deutsche ICF-Datei bleibt PRIVAT** (bessere Übersetzung):
  wird via `config.local.json` (gitignored) eingebunden, nie committet.

## Ausgabe über Renderer-Adapter (Kern schlank, Design optional)

| Renderer | Status |
|---|---|
| Markdown/HTML | Kern (immer dabei) |
| PDF | Kern (aus HTML) |
| Word (.docx) | Kern (python-docx, schlichte Vorlage) |
| PowerPoint | optionaler Adapter → delegiert an pptx-Design-Skill |
| Canva | optionaler Adapter → delegiert an Canva-Connector (MCP) |

Adapter-Prinzip: Der Generator erzeugt ein strukturiertes Arbeitsblatt-JSON
(Schema versioniert); Renderer sind austauschbar und erkennen zur Laufzeit,
welche Design-Skills/Connectoren verfügbar sind (Skill-Doku nennt die Optionen).

## Herkunft

`bach_source/worksheet_generator/` = Rohsicherung aus Alt-BACH
`agents/_experts/worksheet_generator/` (generator.py, templates/, rolle.txt,
SKILL.md; kopiert 2026-07-23). Neutralisierung statt 1:1-Port: BACH-Pfade raus,
Klienten-/Personenbezug raus (Material wird IMMER ohne Klientendaten erzeugt —
Pseudonym/Niveau statt Name).

## Abgrenzung

- Berichte/Klientendaten: NICHT hier (→ Berichts-Pipeline/foerderplaner).
- Fertiges Material: wird nicht mitgeliefert (nur synthetische Beispiele).
