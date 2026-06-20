from langgraph.graph import StateGraph, START, END
from src.state import EstadoChatbot
from src.nodes.deterministic import normalizar_consulta, finalizar_respuesta, respuesta_segura
from src.nodes.llm_nodes import generar_plan, evaluar_evidencia, reformular_busqueda, generar_respuesta, auditar_respuesta
from src.tools.rag_tool import recuperar_evidencia
from src.tools.validation import validar_fuentes
from src.tools.formatter import formatear_citas
from src.routers.conditional import router_alcance, router_evidencia, router_auditoria

def construir_grafo():
    grafo = StateGraph(EstadoChatbot)

    # Registrar Nodos
    grafo.add_node("normalizar_consulta", normalizar_consulta)
    grafo.add_node("generar_plan", generar_plan)
    grafo.add_node("recuperar_evidencia", recuperar_evidencia)
    grafo.add_node("evaluar_evidencia", evaluar_evidencia)
    grafo.add_node("reformular_busqueda", reformular_busqueda)
    grafo.add_node("generar_respuesta", generar_respuesta)
    grafo.add_node("validar_fuentes", validar_fuentes)
    grafo.add_node("formatear_citas", formatear_citas)
    grafo.add_node("auditar_respuesta", auditar_respuesta)
    grafo.add_node("finalizar_respuesta", finalizar_respuesta)
    grafo.add_node("respuesta_segura", respuesta_segura)

    # Conectar Aristas Fijas
    grafo.add_edge(START, "normalizar_consulta")
    grafo.add_edge("normalizar_consulta", "generar_plan")

    # Router 1: Alcance
    grafo.add_conditional_edges(
        "generar_plan",
        router_alcance,
        {
            "recuperar_evidencia": "recuperar_evidencia",
            "respuesta_segura": "respuesta_segura",
        },
    )

    grafo.add_edge("recuperar_evidencia", "evaluar_evidencia")

    # Router 2: Evidencia RAG
    grafo.add_conditional_edges(
        "evaluar_evidencia",
        router_evidencia,
        {
            "generar_respuesta": "validar_fuentes",
            "reformular_busqueda": "reformular_busqueda",
            "respuesta_segura": "respuesta_segura",
        },
    )

    # Loop de reintento
    grafo.add_edge("reformular_busqueda", "recuperar_evidencia")

    # Flujo de generación y auditoría
    grafo.add_edge("validar_fuentes", "generar_respuesta")
    grafo.add_edge("generar_respuesta", "formatear_citas")
    grafo.add_edge("formatear_citas", "auditar_respuesta")

    # Router 3: Auditoría
    grafo.add_conditional_edges(
        "auditar_respuesta",
        router_auditoria,
        {
            "finalizar_respuesta": "finalizar_respuesta",
            "generar_respuesta": "generar_respuesta",
        },
    )

    # Conectar a Fin
    grafo.add_edge("finalizar_respuesta", END)
    grafo.add_edge("respuesta_segura", END)

    return grafo.compile()
