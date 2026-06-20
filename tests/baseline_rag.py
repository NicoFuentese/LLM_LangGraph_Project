import sys
import io
from pathlib import Path

# Agregar el directorio raíz al path de Python para resolver importaciones
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Reconfigurar salida estándar para UTF-8 en entornos Windows
if sys.platform.startswith("win"):
    try:
         sys.stdout.reconfigure(encoding='utf-8')
         sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
         sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.llm import llm
from src.tools.rag_tool import buscar_en_kb

def _get_content(respuesta) -> str:
    """Extrae texto de la respuesta del LLM de forma segura."""
    content = getattr(respuesta, "content", respuesta)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else getattr(part, "text", str(part))
            for part in content
        )
    return str(content)

def ejecutar_baseline(consulta: str) -> str:
    """Ejecuta una respuesta RAG de un solo paso sobre la base de conocimiento cargada."""
    # Recuperación simple de los primeros 3 chunks
    resultados = buscar_en_kb(consulta)[:3]
    contexto = "\n\n".join(r["texto"] for r in resultados) if resultados else "No se encontraron fragmentos de información."

    prompt = f"""Eres un asistente académico de la PUCV.
Responde la consulta del estudiante basándote únicamente en la evidencia proporcionada.
Si la consulta está fuera del alcance del sistema académico (por ejemplo, temas generales, otros países, etc.), indica que la pregunta está fuera de alcance.
Si no encuentras información suficiente en el contexto de referencia, indícalo claramente.

Contexto de referencia:
---
{contexto}
---

Consulta del estudiante: "{consulta}"

Redacta tu respuesta en español:"""

    try:
        respuesta = llm.invoke(prompt)
        return _get_content(respuesta).strip()
    except Exception as e:
        return f"Error en ejecución del Baseline: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        consulta = " ".join(sys.argv[1:])
        print(ejecutar_baseline(consulta))
    else:
        print(ejecutar_baseline("¿Cuál es la nota mínima para aprobar una asignatura?"))
