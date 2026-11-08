# Security Policy

## Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. **Use GitHub's [private vulnerability reporting](https://github.com/ellmos-ai/worksheet-generator/security/advisories/new)**
3. Include: description, steps to reproduce, potential impact

### How to Report

1. Go to: https://github.com/ellmos-ai/worksheet-generator/security/advisories/new
2. Fill out the form (title, description, severity, affected versions)
3. Submit privately (not visible to public until disclosed)

## Security Scope & Principles

- **Local-First & Client Privacy:** Worksheet generation, curriculum matching, and pedagogy workflows operate entirely client-side. No telemetry, cloud logging, or automated egress of student or client data is performed.
- **Fail-Closed Secret & API Protection:** Credentials and tokens for optional external APIs (such as WHO ICD-11 API credentials via `_tools/icf_fetch.py`) are strictly confined to gitignored local configuration (`config.local.json`) or environment variables, and never bundled in generated worksheets or repositories.
- **Safe Rendering & Content Sanitization:** Output renderers (Markdown, HTML, DOCX) perform structured validation against `schema.py` and prevent script execution or insecure remote inclusions.
- **Zero-Copyleft Guarantee:** Generated worksheets and teaching materials remain entirely unencumbered by copyleft licenses and are freely usable by schools, clinics, and educators.

## Response SLA & Invariants

- **INV-SLA-10 (48-Hour Response SLA):** You will receive an initial response and acknowledgment of your report within 48 hours.
- **INV-SLA-09 (5-Day Vulnerability Triage):** Full vulnerability verification, severity assessment, and mitigation plan within 5 business days.
- **Coordinated Disclosure:** We kindly request allowing a reasonable remediation window before any public disclosure.
