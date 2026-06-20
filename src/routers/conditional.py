from src.state import EstadoChatbot

def router_alcance(state: EstadoChatbot) -> str:
    """Router 1: ¿la consulta entra al flujo RAG o sale con respuesta segura?"""
    if state.get("dentro_alcance"):
        return "recuperar_evidencia"
    return "respuesta_segura"

def router_evidencia(state: EstadoChatbot) -> str:
    """Router 2: ¿hay evidencia suficiente, hay que reformular o derivar a salida segura?"""
    max_intentos = state.get("max_intentos", 3)
    intentos = state.get("intentos_busqueda", 0)

    if state.get("contexto_suficiente") and state.get("fuentes_validas"):
        return "generar_respuesta"
    if intentos < max_intentos:
        return "reformular_busqueda"
    return "respuesta_segura"

def router_auditoria(state: EstadoChatbot) -> str:
    """Router 3: ¿la respuesta está aprobada o hay que regenerarla?"""
    if state.get("respuesta_valida"):
        return "finalizar_respuesta"
    return "generar_respuesta"
