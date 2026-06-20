import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Modelo de Gemini a utilizar (por defecto gemini-2.5-flash)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

# Modelo del Juez Evaluador (por defecto gemini-3.5-flash)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-3.5-flash").strip()

# Tipo de base de conocimiento (standard | extended)
KB_TYPE = os.getenv("KB_TYPE", "extended").strip().lower()

def _cargar_json(ruta: Path) -> dict:
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

# Cargar bases de datos
KB_ORIGINAL = _cargar_json(PROCESSED_DATA_DIR / "knowledge_base.json")
KB_EXTENDIDA = _cargar_json(PROCESSED_DATA_DIR / "knowledge_base_extended.json")

if KB_TYPE == "standard":
    KNOWLEDGE_BASE = KB_ORIGINAL
else:
    KNOWLEDGE_BASE = {**KB_ORIGINAL, **KB_EXTENDIDA}
