from typing import List, Dict
from langchain_core.tools import tool

@tool
def formatear_citas(metadatos_fuentes: List[Dict] = None) -> Dict:
    """TOOL 3: formatea citas APA y extrae enlaces oficiales."""
    fuentes = metadatos_fuentes or []
    citas = []
    enlaces = []

    for f in fuentes:
        cita = (
            f"PUCV. {f.get('documento', 'Documento')}. "
            f"{f.get('articulo', '')}, {f.get('seccion', '')}. "
            f"Página {f.get('pagina', '?')}."
        )
        citas.append(cita)
        if f.get("url"):
            enlaces.append(f.get("url"))

    citas_str = "\n".join(f"  [{i+1}] {c}" for i, c in enumerate(citas))
    print(f"[TOOL 3. formatear_citas] -> {len(citas)} cita(s) formateada(s)")
    return {"citas_formateadas": citas_str, "enlaces_oficiales": list(set(enlaces))}
