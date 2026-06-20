import re
from typing import Dict
from src.state import EstadoChatbot

def normalizar_consulta(state: EstadoChatbot) -> Dict:
    normalizada = state["consulta_original"].lower().strip()
    normalizada = re.sub(r"\s+", " ", normalizada)
    print(f"\n[1. normalizar_consulta] -> '{normalizada}'")
    return {
        "consulta_normalizada": normalizada,
        "consulta_busqueda": normalizada,
    }

def finalizar_respuesta(state: EstadoChatbot) -> Dict:
    partes = [state.get("respuesta_borrador", "")]
    if state.get("citas_formateadas"):
        partes.append(f"\n[Fuentes]:\n{state['citas_formateadas']}")
    if state.get("enlaces_oficiales"):
        links = "\n".join(f"  Link: {url}" for url in state["enlaces_oficiales"])
        partes.append(f"\n[Links oficiales]:\n{links}")

    respuesta_final = "\n".join(partes)
    print(f"[10. finalizar_respuesta] -> respuesta ensamblada ({len(respuesta_final)} chars)")
    return {"respuesta_final": respuesta_final}

def respuesta_segura(state: EstadoChatbot) -> Dict:
    if not state.get("dentro_alcance"):
        mensaje = (
            "Esta consulta está fuera del alcance del sistema académico PUCV. "
            "Solo puedo responder preguntas sobre procedimientos universitarios "
            "(convalidaciones, titulación, créditos, fechas, evaluaciones, etc.)."
        )
    else:
        mensaje = (
            "No encontré información suficiente en la base de conocimiento para responder "
            f"la consulta: '{state['consulta_original']}'. "
            "Te recomiendo contactar directamente a la Secretaría Académica de la PUCV."
        )
    print(f"[11. respuesta_segura] -> derivación segura activada")
    return {"respuesta_final": mensaje, "respuesta_valida": False}
