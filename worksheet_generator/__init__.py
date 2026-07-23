"""worksheet-generator -- Foerdermaterial-Generator (Arbeitsblatt-JSON + Renderer).

Erzeugt aus Foerderziel/ICF-Code(n)/Niveau/Alter (optional angereichert durch
einen Material-Ordner-Scan und/oder bereits recherchierte Stichpunkte) ein
schema-konformes Arbeitsblatt-JSON (siehe schema.py) und rendert es in
Markdown/HTML/DOCX (siehe renderers.py). Enthaelt bewusst KEINE
Klienten-/Personenbezuege -- Steuerung erfolgt ausschliesslich ueber
Foerderziel + Niveau + Alter.

Oeffentliche API:
    from worksheet_generator import Foerderziel, generate_worksheet, save_worksheet
    from worksheet_generator import renderers, schema
"""
from .generator import Foerderziel, generate_worksheet, save_worksheet
from . import renderers, schema

__version__ = "0.1.0"
__all__ = [
    "Foerderziel",
    "generate_worksheet",
    "save_worksheet",
    "renderers",
    "schema",
]
