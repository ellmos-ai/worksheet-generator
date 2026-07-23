"""worksheet-generator -- Foerdermaterial-Generator (Arbeitsblatt-JSON + Renderer).

Erzeugt aus einem Foerderziel (ICF-gestuetzt, targeting.mode "foerder") ODER
einem Curriculumziel (Fach/Klassenstufe-gestuetzt, targeting.mode
"curriculum") -- optional angereichert durch einen Material-Ordner-Scan,
bereits recherchierte Stichpunkte und/oder konfigurierte
Curriculum-Quellen-Adapter -- ein schema-konformes Arbeitsblatt-JSON (siehe
schema.py) und rendert es in Markdown/HTML/DOCX (siehe renderers.py).
Enthaelt bewusst KEINE Klienten-/Schueler-Personenbezuege in beiden Modi.

Oeffentliche API:
    from worksheet_generator import Foerderziel, Curriculumziel, generate_worksheet, save_worksheet
    from worksheet_generator import renderers, schema, curriculum_sources
"""
from .generator import Curriculumziel, Foerderziel, generate_worksheet, save_worksheet
from . import curriculum_sources, renderers, schema

__version__ = "0.2.0"
__all__ = [
    "Foerderziel",
    "Curriculumziel",
    "generate_worksheet",
    "save_worksheet",
    "renderers",
    "schema",
    "curriculum_sources",
]
