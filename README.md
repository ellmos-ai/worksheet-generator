![worksheet-generator Banner](assets/banner.png)

# worksheet-generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ellmos-ai/worksheet-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/ellmos-ai/worksheet-generator/actions)
[![Pytest](https://img.shields.io/badge/pytest-16%20passed-brightgreen.svg)](tests/)
[![Local-First](https://img.shields.io/badge/privacy-100%25%20local--first-blue.svg)](#features)
[![llms.txt](https://img.shields.io/badge/llms.txt-available-green.svg)](llms.txt)
[![Language: DE](https://img.shields.io/badge/Language-Deutsch-de.svg)](README_de.md)

**Educational and therapeutic worksheet generator driven by local LLM agents (Claude Code, Antigravity, Open-WebUI).**

**English** | [Deutsch](README_de.md)

> [!NOTE]
> **AI Agent & LLM Integration:** This repository provides machine-readable specifications (`llms.txt`, `SKILL.md`, and `worksheet_generator/schema.py`) designed for seamless integration with local AI agents to automate worksheet generation, differentiation, and content enrichment.

> [!IMPORTANT]
> **Privacy & Offline First:** `worksheet-generator` operates 100% offline with zero client or personal data processing. Controls operate exclusively via abstract educational goals, ICF codes, or school curricula.

> [!TIP]
> **Ecosystem Integration:** Works out of the box with other `ellmos-ai` tools such as [report-forge](https://github.com/ellmos-ai/report-forge) (anonymized reporting pipelines), [USMC](https://github.com/ellmos-ai/usmc) (shared agent memory), and [ellmos-homebase-mcp](https://github.com/ellmos-ai/ellmos-homebase-mcp).

This module generates structured **worksheet JSONs** from an educational goal (free text + optional ICF codes), level, and age group, or school curriculum (subject, grade, topic), which can then be rendered to Markdown, HTML, or DOCX formats.

| Feature | Description |
|---|---|
| **Privacy & GDPR** | Local-first, 100% offline engine. Zero personal or client data required. |
| **Generation Modes** | (1) Goal & ICF codes (Special Education) / (2) Subject, Grade & Topic (Curriculum) |
| **Export Formats** | Markdown, HTML, DOCX (optional via `python-docx`) |
| **AI Agent Ready** | Includes `llms.txt` and `SKILL.md` for native use in Claude Code, Antigravity & LLM pipelines |

---

## Quick Start

### Python Library Usage

```python
from worksheet_generator import Foerderziel, generate_worksheet, save_worksheet
from worksheet_generator import renderers

ziel = Foerderziel(
    freitext="Mengen bis 10 erfassen",
    icf_codes=["d150"],
    niveau="einfache_sprache",
    alter="8",
    thema="mathe",
)
worksheet = generate_worksheet(ziel)
save_worksheet(worksheet, "output/worksheet.json")

print(renderers.to_markdown(worksheet))
```

### CLI Command Line

```bash
# Generate worksheet JSON (Special Education mode)
PYTHONIOENCODING=utf-8 python -m worksheet_generator generate \
  --freitext "Mengen bis 10 erfassen" --icf d150 --niveau einfache_sprache \
  --alter 8 --thema mathe --out output/worksheet.json

# Generate worksheet JSON (School Curriculum mode)
PYTHONIOENCODING=utf-8 python -m worksheet_generator generate \
  --subject Mathematik --grade 3 --topic "Einmaleins" --out output/worksheet.json

# Render to Markdown or HTML
PYTHONIOENCODING=utf-8 python -m worksheet_generator render \
  output/worksheet.json --format md
```

---

## Architecture & Workflow

```mermaid
flowchart TD
    subgraph Inputs["1. Input & Generation Mode"]
        A1["Educational Goal & ICF Codes<br/>(Special Education)"]
        A2["Subject, Grade & Topic<br/>(Curriculum Mode)"]
    end

    subgraph CoreEngine["2. Offline Generator Engine"]
        B1["Standard-library schema validation<br/>(worksheet_generator/schema.py)"]
        B2["Deterministic Generation<br/>(worksheet_generator/generator.py)"]
        B3["Curriculum & Context Adapter<br/>(Local Files / LernQuest DB)"]
    end

    subgraph AgentLayer["3. LLM Agent Enrichment"]
        E1["Claude Code / Antigravity / Open-WebUI<br/>(via SKILL.md & llms.txt)"]
    end

    subgraph OutputFormat["4. Multi-Format Exporters"]
        C1["Worksheet JSON Schema"]
        D1["Markdown (.md)"]
        D2["HTML (.html)"]
        D3["DOCX (.docx)"]
    end

    A1 --> B1
    A2 --> B1
    B1 --> B2
    B3 --> B2
    B2 --> C1
    C1 <--> E1
    C1 --> D1
    C1 --> D2
    C1 --> D3
```

---

## Export Renderers

| Renderer | Status | Dependencies |
|---|---|---|
| **Markdown** | Core, built-in | None (Standard Library) |
| **HTML** | Core, built-in | None (Standard Library) |
| **DOCX** | Core, optional | `pip install python-docx` |
| **PDF** | External | Convert from HTML (e.g. WeasyPrint / Chrome) |

---

## Ecosystem & Related Repositories

- [report-forge](https://github.com/ellmos-ai/report-forge): Anonymized report generation & document pipelines.
- [clirec](https://github.com/ellmos-ai/clirec): Record and playback terminal/GUI demonstrations.
- [USMC](https://github.com/ellmos-ai/usmc): Shared agent memory client for ellmos ecosystem.
- [ellmos-homebase-mcp](https://github.com/ellmos-ai/ellmos-homebase-mcp): Local-first LLM memory, knowledge, and swarm orchestration server.

---

## License

MIT License (see [LICENSE](LICENSE)).
