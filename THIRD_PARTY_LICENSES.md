# Third-Party Licenses & Transparency — worksheet-generator

> Comprehensive license audit, Level 1 SBOM, and transparency report for `worksheet-generator` (ellmos-ai / open-bricks).
> Plain-text companion: [`THIRD_PARTY_LICENSES.txt`](THIRD_PARTY_LICENSES.txt).
> Last updated: 2026-11-02.

---

## 1. Project License

`worksheet-generator` is licensed under the **MIT License**.
See [LICENSE](LICENSE) for full details.

```text
MIT License

Copyright (c) 2026 Lukas Geiger

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 2. Direct Runtime Dependencies

`worksheet-generator` is architected with a **Zero-Mandatory-Dependencies** invariant (`INV-ZERODEP-03`):
The entire core generator, schema validator, curriculum adapter, Markdown renderer, and HTML renderer rely solely on the **Python Standard Library**.

| Component | License (SPDX) | Type | Origin / Copyright | Notes |
|---|---|---|---|---|
| **Python Standard Library** (`dataclasses`, `json`, `pathlib`, `re`, `argparse`, `sys`, `html`) | `PSF-2.0` | Core Runtime | Python Software Foundation | Bundled with Python 3.10+ runtimes |

---

## 3. Optional & Rendering Dependencies

Optional renderers can be installed via `pip install ".[docx]"`.

| Package | License (SPDX) | Usage | Link | Notes |
|---|---|---|---|---|
| **`python-docx`** | `MIT` | Optional DOCX export format (`worksheet_generator/renderers.py`) | [PyPI](https://pypi.org/project/python-docx/) | Permissive open-source license; only imported when DOCX rendering is invoked |

---

## 4. Development & Testing Tooling

Development, packaging, and automated testing dependencies (`pip install ".[test]"`):

| Tool | License (SPDX) | Usage | Link |
|---|---|---|---|
| **`pytest`** | `MIT` | Test runner and assertion framework | [pytest.org](https://docs.pytest.org/) |
| **`setuptools`** | `MIT` | PEP 517 / PEP 621 build backend and packaging | [PyPI](https://pypi.org/project/setuptools/) |
| **`build`** | `MIT` | Isolated PEP 517 package distribution builder | [PyPI](https://pypi.org/project/build/) |

---

## 5. Educational Frameworks & Classification Systems Notice

### ICF (International Classification of Functioning, Disability and Health)
- **Copyright Holder:** © World Health Organization (WHO), 2001 / 2026.
- **German Translation & Terminology:** © WHO / Bundesinstitut für Arzneimittel und Medizinprodukte (BfArM), § 5 (2) UrhG.
- **Bring-Your-Own-Reference Principle (`INV-ICF-05`):**
  `worksheet-generator` bundles **no** ICF full texts, short titles, diagnostic descriptions, or copyrighted catalog tables in this repository. It uses standard ICF alphanumeric codes (e.g. `d150`, `b140`, `d330`) strictly as neutral, abstract identifiers.
- **Licensing Demarcation:**
  The MIT license of this repository **does not** grant any rights to WHO or BfArM copyrighted classification texts. When users choose to enrich generated worksheets with official ICF short titles via the optional helper `_tools/icf_fetch.py`, the official WHO ICD-API terms and BfArM conditions apply directly and individually to the respective user.

---

## 6. Invariant Cross-Reference Matrix (INV-LOCAL-01 .. INV-SLA-10)

| Invariant ID | Operational Mandate | Technical Enforcement | License Scope |
|---|---|---|---|
| `INV-LOCAL-01` | 100% Local-First & Zero-Egress | Zero telemetry; offline generator execution | MIT / PSF-2.0 |
| `INV-UNPRIV-02` | Unprivileged RunAsInvoker | Standard non-elevated user mode | MIT / PSF-2.0 |
| `INV-ZERODEP-03` | Zero Mandatory Dependencies | 100% Python 3.10+ Standard Library | MIT / PSF-2.0 |
| `INV-ISOLATION-04`| Student & Client Privacy Isolation | Local processing; free text is preserved, not anonymized | MIT / PSF-2.0 |
| `INV-ICF-05` | Bring-Your-Own-Reference Demarcation | No bundled copyrighted classification texts | WHO / BfArM Boundary |
| `INV-PERMISSIVE-06`| Zero-Copyleft Isolation Guarantee | Strictly permissive (MIT, PSF-2.0); no copyleft | MIT / PSF-2.0 |
| `INV-OUTPUT-07` | Zero-Copyleft on Output | Worksheets are exclusive property of user | User IP |
| `INV-FORMAT-08` | Multi-Format Deterministic Export | Validated JSON, Markdown, HTML, optional DOCX | MIT / PSF-2.0 |
| `INV-SCHEMA-09` | Strict Schema & Contract Validation | Python dataclasses & schema definitions | MIT / PSF-2.0 |
| `INV-SLA-10` | 48h Security & Governance SLA | Committed response SLA; statutory disclaimer | § 521 BGB |

---

## 7. Output & Intellectual Property Guarantee

- **Zero-Copyleft on Generated Worksheets (`INV-OUTPUT-07`):**
  Any worksheet JSON, Markdown document, HTML preview, or DOCX document produced by `worksheet-generator` is the exclusive intellectual property of the generating educator, therapist, or institution.
- **No Viral Licensing:**
  Neither the MIT license of this generator nor the optional dependencies place copyleft obligations, telemetry hooks, or attribution mandates on the output files.
- **Local Data Isolation (`INV-LOCAL-01`, `INV-ISOLATION-04`):**
  The software operates strictly locally. No student data, goal text, or prompt parameters are transmitted over external networks during generation.

---

## 8. Statutory Disclaimer (§ 521 BGB) & 48h Security Response SLA

Die Bereitstellung dieser Software erfolgt als unentgeltliche Open-Source-Leistung gemäß deutschem Recht (§ 521 BGB - Gefälligkeitsrecht / unentgeltliche Zuwendung). Die Haftung ist auf Vorsatz und grobe Fahrlässigkeit beschränkt. Es wird keine Gewähr für Mängelfreiheit oder unterbrechungsfreie Funktionsfähigkeit übernommen.

Vulnerability reports received via GitHub Security Advisories or issues are acknowledged within 48 hours, triaged within 5 business days, and coordinated through responsible disclosure (`INV-SLA-10`).

Sensitive input and output require user review. The generator does not reject or anonymize personal data in free-text fields.
