import json
import re
from typing import Dict, Any
from src.llm import llm
from src.state import EstadoChatbot

def _get_content(respuesta) -> str:
    """Extrae texto de la respuesta del LLM (compatible con string y lista de bloques)."""
    content = respuesta.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else getattr(part, "text", str(part))
            for part in content
        )
    return str(content)

def _parsear_json(respuesta_o_texto, default: Any = None) -> Any:
    """Parsea JSON de una respuesta LLM o de un string, limpiando markdown."""
    texto = _get_content(respuesta_o_texto) if hasattr(respuesta_o_texto, "content") else str(respuesta_o_texto)
    limpio = re.sub(r"```json\s*|\s*```", "", texto.strip()).strip()
    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        return default

def generar_plan(state: EstadoChatbot) -> Dict:
    """LLM 1: clasifica intención, decide si entra al alcance y genera un plan de búsqueda de hasta 3 pasos."""
    prompt = f"""Eres un clasificador de consultas y planificador de búsquedas para el chatbot académico de la PUCV.
Determina si la consulta es sobre procedimientos académicos universitarios (convalidación,
titulación, créditos, fechas, secretaría, evaluación, requisitos, becas, etc.).

Si la consulta está dentro de alcance:
- "intencion" debe ser "reglamento_academico"
- "dentro_alcance" debe ser true
- "plan_de_busqueda" debe ser una lista con un máximo de 3 pasos de búsqueda independientes en español, optimizados para buscar en una base de datos (por ejemplo, buscar palabras clave como "requisitos titulación", "convalidar asignaturas", "reprobar asignatura").

Si la consulta está fuera de alcance:
- "intencion" debe ser "fuera_de_alcance"
- "dentro_alcance" debe ser false
- "plan_de_busqueda" debe ser una lista vacía [].

Consulta: "{state['consulta_normalizada']}"

Responde ÚNICAMENTE con JSON:
{{"intencion": "reglamento_academico" o "fuera_de_alcance", "dentro_alcance": true o false, "plan_de_busqueda": ["paso 1", "paso 2", ...]}}"""

    respuesta = llm.invoke(prompt)
    datos = _parsear_json(respuesta, {})

    intencion = datos.get("intencion", "fuera_de_alcance")
    dentro_alcance = datos.get("dentro_alcance", False)
    plan_de_busqueda = datos.get("plan_de_busqueda", [])

    if isinstance(plan_de_busqueda, str):
        plan_de_busqueda = [plan_de_busqueda]
    elif not isinstance(plan_de_busqueda, list):
        plan_de_busqueda = []

    print(f"[2. generar_plan] -> intencion: {intencion}, dentro_alcance: {dentro_alcance}, plan: {plan_de_busqueda}")
    return {
        "intencion": intencion,
        "dentro_alcance": dentro_alcance,
        "plan_de_busqueda": plan_de_busqueda,
    }

def evaluar_evidencia(state: EstadoChatbot) -> Dict:
    """LLM 2: evalúa si los chunks recuperados son relevantes y suficientes."""
    if not state["chunks_recuperados"]:
        print("[4. evaluar_evidencia] -> sin chunks")
        return {"contexto_suficiente": False, "fuentes_validas": False}

    contexto = "\n\n".join(state["chunks_recuperados"])
    prompt = f"""Evalúa si los siguientes fragmentos de documentación académica PUCV son
suficientes y relevantes para responder la consulta del estudiante.

Consulta: "{state['consulta_normalizada']}"

Fragmentos recuperados:
---
{contexto}
---

Responde ÚNICAMENTE con JSON:
{{"contexto_suficiente": true o false, "fuentes_validas": true o false, "explicacion": "breve razón"}}"""

    respuesta = llm.invoke(prompt)
    datos = _parsear_json(respuesta, {})

    suficiente = datos.get("contexto_suficiente", bool(state["chunks_recuperados"]))
    fuentes_validas = datos.get("fuentes_validas", suficiente)

    print(f"[4. evaluar_evidencia] -> suficiente: {suficiente}, fuentes_validas: {fuentes_validas}")
    return {"contexto_suficiente": suficiente, "fuentes_validas": fuentes_validas}

def reformular_busqueda(state: EstadoChatbot) -> Dict:
    """LLM 3: genera un plan de búsqueda alternativo y más preciso para el siguiente intento."""
    plan_anterior = ", ".join(f"'{p}'" for p in state.get("plan_de_busqueda", []))
    prompt = f"""La búsqueda anterior usando el plan actual no encontró contexto suficiente.
Reformula o detalla los pasos de búsqueda para hacer una recuperación más efectiva en la base de conocimiento sobre reglamentos académicos PUCV.

Consulta original: "{state['consulta_normalizada']}"
Plan de búsqueda anterior: [{plan_anterior}]
Intento #{state['intentos_busqueda']}

Genera un nuevo plan de búsqueda alternativo con un máximo de 3 pasos más específicos. Responde ÚNICAMENTE con JSON:
{{"nuevo_plan": ["paso 1", "paso 2", ...]}}"""

    respuesta = llm.invoke(prompt)
    datos = _parsear_json(respuesta, {})
    nuevo_plan = datos.get("nuevo_plan", state.get("plan_de_busqueda", []))

    if isinstance(nuevo_plan, str):
        nuevo_plan = [nuevo_plan]
    elif not isinstance(nuevo_plan, list):
        nuevo_plan = []

    print(f"[5. reformular_busqueda] -> nuevo plan: {nuevo_plan}")
    return {"plan_de_busqueda": nuevo_plan}

def generar_respuesta(state: EstadoChatbot) -> Dict:
    """LLM 4: genera una respuesta fluida basada en los chunks recuperados."""
    contexto = "\n\n".join(state["chunks_recuperados"])
    feedback = state.get("feedback_auditor", "")

    instruccion_feedback = f"\nConsiderar feedback anterior: {feedback}" if feedback else ""

    prompt = f"""Eres un asistente académico experto en el Reglamento de Estudios de Pregrado de la PUCV.
Genera una respuesta clara, precisa y bien estructurada basándote ÚNICAMENTE en la evidencia proporcionada.
{instruccion_feedback}

Consulta del estudiante: "{state['consulta_normalizada']}"

Evidencia recuperada:
---
{contexto}
---

Redacta una respuesta completa en español, con párrafos estructurados. No inventes información
que no esté en la evidencia. Cita artículos específicos cuando corresponda."""

    respuesta = llm.invoke(prompt)
    borrador = _get_content(respuesta).strip()

    print(f"[6. generar_respuesta] -> borrador generado ({len(borrador)} chars)")
    return {"respuesta_borrador": borrador, "feedback_auditor": ""}

def auditar_respuesta(state: EstadoChatbot) -> Dict:
    """LLM 5: verifica que la respuesta sea fiel a la evidencia y bien formada."""
    contexto = "\n\n".join(state["chunks_recuperados"])

    prompt = f"""Eres un auditor de calidad para respuestas académicas. Verifica que la respuesta:
1. Sea fiel a la evidencia (sin inventar datos)
2. Responda efectivamente la consulta del estudiante
3. Sea clara y bien estructurada

Consulta: "{state['consulta_normalizada']}"

Evidencia disponible:
---
{contexto}
---

Respuesta generada:
---
{state['respuesta_borrador']}
---

Responde ÚNICAMENTE con JSON:
{{"aprobada": true o false, "feedback": "observación si no está aprobada, vacío si está bien"}}"""

    respuesta = llm.invoke(prompt)
    datos = _parsear_json(respuesta, {})

    aprobada = datos.get("aprobada", True)
    feedback = datos.get("feedback", "")

    print(f"[8. auditar_respuesta] -> aprobada: {aprobada}" + (f" | feedback: {feedback}" if feedback else ""))
    return {"respuesta_valida": aprobada, "feedback_auditor": feedback}
