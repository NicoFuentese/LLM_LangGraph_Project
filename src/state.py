from typing import TypedDict, List, Dict

class EstadoChatbot(TypedDict):
    consulta_original: str
    consulta_normalizada: str
    intencion: str
    dentro_alcance: bool
    consulta_busqueda: str
    plan_de_busqueda: List[str]
    chunks_recuperados: List[str]
    metadatos_fuentes: List[Dict]
    contexto_suficiente: bool
    fuentes_validas: bool
    respuesta_valida: bool
    intentos_busqueda: int
    max_intentos: int
    respuesta_borrador: str
    citas_formateadas: str
    enlaces_oficiales: List[str]
    feedback_auditor: str
    respuesta_final: str
