#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut eine lokale icf_local.json fuer das Modul worksheet-generator --
entweder aus einer selbst beschafften Quelldatei oder per Live-Abfrage der
offiziellen WHO ICD-11-API (mit eigenen Nutzer-Zugangsdaten).

WICHTIG (Lizenz): Dieses Repo bundelt KEINE ICF-Kurztitel oder -Volltexte.
Die ICF (International Classification of Functioning, Disability and
Health) steht unter WHO-Lizenz (CC BY-ND 3.0 IGO fuer die ICD-11/ICF/ICHI-
Familie; die deutsche Fassung von BfArM ist zusaetzlich amtliches Werk i.S.d.
§ 5 Abs. 2 UrhG mit Aenderungsverbot/Quellenangabe-Pflicht). Kurztitel
bezieht deshalb JEDER Nutzer selbst -- entweder ueber eine eigene Quelldatei
(Modus A) oder per eigener WHO-API-Registrierung (Modus B). Ergebnis-Datei
`icf_local.json` ist gitignored und nie Teil des Repos. Details/Herleitung:
`_intern/ICF-LIZENZ-CHECK.md` (interne Recherchenotiz, nicht Teil des Repos).

Unterscheidet sich damit bewusst von _tools/gesetze_fetch.py im
Schwestermodul rechtsabteilung (dort: gemeinfreie deutsche Bundesgesetze,
direkter Bulk-XML-Download von gesetze-im-internet.de) -- fuer die ICF gibt
es keine vergleichbar unkomplizierte, gemeinfreie Bulk-Quelle.

MODUS A -- eigene Quelldatei (Default, kein Netzwerkzugriff):
    Quellen-Optionen (vom Nutzer manuell zu beschaffen; jeweils eigene
    Nutzungsbedingungen der Anbieter beachten):
        - WHO ICF Browser:       https://apps.who.int/classifications/icfbrowser/
                                  (bzw. Nachfolgeangebote der WHO-FIC)
        - BfArM Klassifikationen: https://klassifikationen.bfarm.de/icf/
                                  (deutsche Fassung; Downloadbereich mit dem
                                  Systematischen Verzeichnis, u.a. als CSV/XML)

    Eingabeformate der Quelldatei (--source):
        - CSV mit Kopfzeile, Spalten 'code'/'kode'/'icf_code' und
          'title'/'kurztitel'/'bezeichnung' (Trennzeichen , oder ; werden
          automatisch erkannt).
        - JSON als Liste [{"code": "...", "title": "..."}, ...] oder als
          Objekt {"code": "title", ...}.

    Aufruf (aus dem Modulordner):
        PYTHONIOENCODING=utf-8 python _tools/icf_fetch.py --source pfad/zu/quelle.csv
        PYTHONIOENCODING=utf-8 python _tools/icf_fetch.py --source pfad/zu/quelle.json --out icf_local.json

MODUS B -- Live-Abfrage der WHO ICD-11-API (--who-api, eigene Registrierung
erforderlich): Kostenlose Registrierung unter https://icd.who.int/icdapi ->
client_id/client_secret. NIE in eine Datei oder in dieses Repo schreiben --
nur als Umgebungsvariablen setzen:
    WHO_ICD_CLIENT_ID, WHO_ICD_CLIENT_SECRET

    Aufruf:
        PYTHONIOENCODING=utf-8 python _tools/icf_fetch.py --who-api \\
            --codes d150,d115,d140 --lang de

    Technik (verifiziert 2026-07-23 gegen die WHO-ICD-API-Dokumentation,
    icd.who.int/docs/icd-api): OAuth2 Client-Credentials-Flow gegen
    https://icdaccessmanagement.who.int/connect/token (Basic-Auth mit
    client_id/secret, grant_type=client_credentials, scope=icdapi_access;
    Token ca. 1h gueltig). Die ICF ist als eigene Linearisierung/CodeSystem
    unter http://id.who.int/icd/release/11/icf gefuehrt; Codeinfo-Aufloesung
    analog zum dokumentierten MMS-Muster
    `.../release/11/{release}/{linearization}/codeinfo/{code}`. Requests
    brauchen die Header Authorization/Accept/Accept-Language/API-Version.
    Falls WHO den Pfad/die Release-ID aendert: `--release`/`--linearization`
    ueberschreiben (Default beide "icf") oder gegen die aktuelle
    Swagger-Doku (https://id.who.int/swagger/index.html) pruefen -- dieses
    Skript bricht pro Code sauber mit Fehlermeldung ab statt zu raten.

Ergebnis (beide Modi): icf_local.json im Modul-Root (gitignored, siehe
.gitignore) mit Quelle + Abrufdatum im Dateikopf (Felder
'_source'/'_retrieved'/'_note').
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as _dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent.parent

WHO_TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
WHO_API_BASE = "https://id.who.int/icd"


# ---------------------------------------------------------------------------
# MODUS A -- eigene Quelldatei (CSV/JSON), kein Netzwerkzugriff
# ---------------------------------------------------------------------------

def _parse_csv(path: Path) -> dict[str, str]:
    codes: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            return codes
        fields = {(name or "").strip().lower(): name for name in reader.fieldnames}
        code_field = fields.get("code") or fields.get("kode") or fields.get("icf_code")
        title_field = fields.get("title") or fields.get("kurztitel") or fields.get("bezeichnung")
        if not code_field or not title_field:
            raise SystemExit(
                f"FEHLER: CSV-Kopfzeile ohne erkennbare code/title-Spalten: {reader.fieldnames}"
            )
        for row in reader:
            code = (row.get(code_field) or "").strip()
            title = (row.get(title_field) or "").strip()
            if code:
                codes[code] = title
    return codes


def _parse_json(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    codes: dict[str, str] = {}
    if isinstance(data, dict):
        for code, title in data.items():
            codes[str(code)] = str(title)
    elif isinstance(data, list):
        for entry in data:
            code = str(entry.get("code", "")).strip()
            title = str(entry.get("title", "")).strip()
            if code:
                codes[code] = title
    else:
        raise SystemExit("FEHLER: JSON-Quelle muss ein Objekt oder eine Liste sein")
    return codes


def build_icf_local_from_file(source: Path, source_label: str) -> dict:
    suffix = source.suffix.lower()
    if suffix == ".json":
        codes = _parse_json(source)
    elif suffix == ".csv":
        codes = _parse_csv(source)
    else:
        raise SystemExit(f"FEHLER: nicht unterstuetztes Quellformat: {suffix} (erwartet .csv/.json)")

    if not codes:
        raise SystemExit("FEHLER: keine Codes aus der Quelldatei extrahiert")

    return _wrap(codes, source_label)


# ---------------------------------------------------------------------------
# MODUS B -- Live-Abfrage der WHO ICD-11-API (eigene Zugangsdaten des Nutzers)
# ---------------------------------------------------------------------------

def _who_get_token(client_id: str, client_secret: str) -> str:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": "icdapi_access"}).encode()
    req = urllib.request.Request(
        WHO_TOKEN_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    token = payload.get("access_token")
    if not token:
        raise SystemExit("FEHLER: WHO-Token-Antwort ohne access_token")
    return token


def _who_api_get(token: str, url: str, lang: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Accept-Language": lang,
            "API-Version": "v2",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extract_title(entity: dict) -> str:
    title = entity.get("title")
    if isinstance(title, dict):
        return str(title.get("@value", "")).strip()
    return str(title or "").strip()


def _who_fetch_title(token: str, release: str, linearization: str, code: str, lang: str) -> str:
    codeinfo_url = f"{WHO_API_BASE}/release/11/{release}/{linearization}/codeinfo/{code}"
    info = _who_api_get(token, codeinfo_url, lang)
    stem_id = info.get("stemId") or info.get("id")
    if not stem_id:
        raise RuntimeError(f"codeinfo-Antwort ohne stemId/id: {info}")
    entity = _who_api_get(token, stem_id, lang)
    title = _extract_title(entity)
    if not title:
        raise RuntimeError("Entity-Antwort ohne auswertbaren Titel")
    return title


def build_icf_local_from_who_api(
    codes: list[str], release: str, linearization: str, lang: str
) -> dict:
    client_id = os.environ.get("WHO_ICD_CLIENT_ID")
    client_secret = os.environ.get("WHO_ICD_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit(
            "FEHLER: WHO_ICD_CLIENT_ID/WHO_ICD_CLIENT_SECRET nicht gesetzt. "
            "Eigene, kostenlose Registrierung: https://icd.who.int/icdapi -- "
            "Zugangsdaten NUR als Umgebungsvariablen setzen, nie in Dateien ablegen."
        )

    print("Hole WHO-API-Token ...")
    token = _who_get_token(client_id, client_secret)

    result_codes: dict[str, str] = {}
    for code in codes:
        try:
            result_codes[code] = _who_fetch_title(token, release, linearization, code, lang)
            print(f"[{code}] {result_codes[code]}")
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, ValueError) as exc:
            print(
                f"[{code}] UEBERSPRUNGEN: {exc} -- Pfad/Release ggf. veraltet, "
                f"gegen https://id.who.int/swagger/index.html pruefen.",
                file=sys.stderr,
            )

    if not result_codes:
        raise SystemExit("FEHLER: keine Titel von der WHO-API erhalten")

    label = f"WHO ICD-11 API (id.who.int/icd/release/11/{release}/{linearization}), Sprache={lang}"
    return _wrap(result_codes, label)


# ---------------------------------------------------------------------------
# Gemeinsames Ausgabeformat
# ---------------------------------------------------------------------------

def _wrap(codes: dict[str, str], source_label: str) -> dict:
    return {
        "_source": source_label,
        "_retrieved": _dt.date.today().isoformat(),
        "_note": (
            "Lokal generiert via _tools/icf_fetch.py. Enthaelt nur Code + "
            "Kurztitel, keine ICF-Volltexte. Nicht Teil des Repos (siehe "
            ".gitignore) -- WHO-/BfArM-Lizenzbedingungen gelten fuer jeden "
            "Nutzer individuell (siehe Docstring dieses Skripts)."
        ),
        "codes": codes,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "--source", default=None, help="Modus A: Pfad zur selbst beschafften ICF-Quelldatei (CSV/JSON)"
    )
    parser.add_argument(
        "--source-label",
        default=None,
        help="Modus A: Freitext zur Herkunft, landet in icf_local.json['_source'] (Default: Dateiname)",
    )
    parser.add_argument("--who-api", action="store_true", help="Modus B: Live-Abfrage der WHO ICD-11-API")
    parser.add_argument("--codes", default=None, help="Modus B: kommagetrennte ICF-Codes, z.B. d150,d115")
    parser.add_argument("--lang", default="de", help="Modus B: Sprache (Accept-Language), Default de")
    parser.add_argument("--release", default="icf", help="Modus B: Release-Segment (Default: icf)")
    parser.add_argument("--linearization", default="icf", help="Modus B: Linearisierungsname (Default: icf)")
    parser.add_argument(
        "--out",
        default=str(MODULE_DIR / "icf_local.json"),
        help="Zieldatei (Default: icf_local.json im Modul-Root)",
    )
    args = parser.parse_args(argv)

    if args.who_api:
        if not args.codes:
            print("FEHLER: --who-api benoetigt --codes (kommagetrennte ICF-Codes)", file=sys.stderr)
            return 1
        codes = [c.strip() for c in args.codes.split(",") if c.strip()]
        result = build_icf_local_from_who_api(codes, args.release, args.linearization, args.lang)
    else:
        if not args.source:
            print("FEHLER: --source erforderlich (Modus A) oder --who-api setzen (Modus B)", file=sys.stderr)
            return 1
        source = Path(args.source)
        if not source.exists():
            print(f"FEHLER: Quelldatei nicht gefunden: {source}", file=sys.stderr)
            return 1
        label = args.source_label or source.name
        result = build_icf_local_from_file(source, label)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"icf_local.json geschrieben: {out_path} ({len(result['codes'])} Codes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
