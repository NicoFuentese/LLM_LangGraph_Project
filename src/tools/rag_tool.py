import re
import unicodedata
from typing import List, Dict, Any
from langchain_core.tools import tool
from config.settings import KNOWLEDGE_BASE, KB_ORIGINAL

def _norm(texto: str) -> str:
    """Normaliza texto para comparación (sin acentos, minúsculas)."""
    texto = unicodedata.normalize("NFKD", texto)
    return texto.encode("ascii", "ignore").decode("ascii").lower()

def buscar_en_kb(consulta: str) -> List[Dict]:
    """
    Busca en la KB cargada (original o fusionada).
    Prioridad: 1) coincidencia en clave, 2) keywords en texto con sinónimos.
    """
    consulta_norm = _norm(consulta)
    palabras = set(re.findall(r"\b\w{4,}\b", consulta_norm))

    # Expandir sinónimos comunes para mejorar recall
    sinonimos = {
        "receso": ["sin clases", "semana sin", "receso", "interperiodo"],
        "practica": ["practica", "practicas", "profesional"],
        "titulo": ["titulo", "titulacion", "proyecto titulo", "seminario titulo"],
        "examen": ["examen", "examenes", "evaluacion", "prueba"],
        "matricula": ["matricula", "inscripcion", "inscripcion asignaturas"],
        "inicio": ["inicio", "comienzo", "empieza", "comienza"],
        "clases": ["clases", "semestre", "actividades"],
    }
    palabras_expandidas = set(palabras)
    for pal in palabras:
        for clave_sin, expansiones in sinonimos.items():
            if pal in clave_sin or clave_sin in pal:
                palabras_expandidas.update(expansiones)

    resultados = []
    vistos = set()

    # 1) Coincidencia por clave (exacta o parcial)
    for clave, articulo in KNOWLEDGE_BASE.items():
        clave_norm = _norm(clave.replace("_", " "))
        # Si la consulta no generó palabras clave de más de 4 letras, intentar coincidencia directa en clave
        if not palabras_expandidas:
            if consulta_norm in clave_norm or clave_norm in consulta_norm:
                if clave not in vistos:
                    resultados.append({"clave": clave, **articulo})
                    vistos.add(clave)
        elif any(p in clave_norm for p in palabras_expandidas):
            if clave not in vistos:
                resultados.append({"clave": clave, **articulo})
                vistos.add(clave)

    # 2) Coincidencia por keywords en el texto
    for clave, articulo in KNOWLEDGE_BASE.items():
        if clave in vistos:
            continue
        texto_norm = _norm(articulo["texto"])
        if palabras_expandidas and any(p in texto_norm for p in palabras_expandidas):
            resultados.append({"clave": clave, **articulo})
            vistos.add(clave)

    # Ordenar: originales primero, luego calendario, luego reglamentos
    def prioridad(r):
        c = r["clave"]
        if c in KB_ORIGINAL:
            return 0
        if "calendario" in c:
            return 1
        return 2

    resultados.sort(key=prioridad)
    return resultados

@tool
def recuperar_evidencia(plan_de_busqueda: List[str] = None, intentos_busqueda: int = 0) -> Dict:
    """TOOL 1 (RAG): recupera chunks relevantes de la base de conocimiento iterando sobre el plan de búsqueda."""
    plan = plan_de_busqueda or []
    if isinstance(plan, str):
        plan = [plan]

    resultados_dict = {}
    for paso in plan:
        res_paso = buscar_en_kb(paso)
        for r in res_paso:
            resultados_dict[r["clave"]] = r

    # Para el plan de búsqueda permitimos hasta 5 chunks
    resultados = list(resultados_dict.values())[:5]

    chunks = [r["texto"] for r in resultados]
    metadatos = [{k: v for k, v in r.items() if k != "texto"} for r in resultados]
    intentos = intentos_busqueda + 1

    print(f"[3. recuperar_evidencia] -> {len(chunks)} chunk(s) | intento #{intentos} usando plan: {plan}")
    for m in metadatos:
        print(f"   * {m.get('documento', '')} | {m.get('articulo', '')} | p.{m.get('pagina', '')}")

    return {
        "chunks_recuperados": chunks,
        "metadatos_fuentes": metadatos,
        "intentos_busqueda": intentos,
    }
