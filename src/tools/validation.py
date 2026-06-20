from typing import List, Dict
from langchain_core.tools import tool

@tool
def validar_fuentes(metadatos_fuentes: List[Dict] = None) -> Dict:
    """TOOL 2: valida vigencia y completitud de las fuentes recuperadas."""
    fuentes = metadatos_fuentes or []
    fuentes_validas = all(
        f.get("vigente", False)
        and f.get("articulo")
        and f.get("documento")
        and f.get("pagina")
        for f in fuentes
    ) if fuentes else False

    print(f"[TOOL 2. validar_fuentes] -> fuentes_validas: {fuentes_validas}")
    return {"fuentes_validas": fuentes_validas}
