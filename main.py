import sys
import io

# Reconfigurar salida estándar para UTF-8 en entornos Windows
if sys.platform.startswith("win"):
    try:
         sys.stdout.reconfigure(encoding='utf-8')
         sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
         sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.state import EstadoChatbot
from src.graph import construir_grafo

def ejecutar(consulta: str):
    app = construir_grafo()

    estado_inicial: EstadoChatbot = {
        "consulta_original": consulta,
        "consulta_normalizada": "",
        "intencion": "",
        "dentro_alcance": False,
        "consulta_busqueda": "",
        "plan_de_busqueda": [],
        "chunks_recuperados": [],
        "metadatos_fuentes": [],
        "contexto_suficiente": False,
        "fuentes_validas": False,
        "respuesta_valida": False,
        "intentos_busqueda": 0,
        "max_intentos": 3,
        "respuesta_borrador": "",
        "citas_formateadas": "",
        "enlaces_oficiales": [],
        "feedback_auditor": "",
        "respuesta_final": "",
    }

    print(f"\n{'='*65}")
    print(f"CONSULTA: {consulta}")
    print(f"{'='*65}")

    estado_acumulado = dict(estado_inicial)
    for evento in app.stream(estado_inicial):
        for nodo, valores in evento.items():
            estado_acumulado.update(valores)

    print(f"\n{'='*65}")
    print("RESPUESTA FINAL:")
    print(f"{'='*65}")
    print(estado_acumulado.get("respuesta_final", "(sin respuesta)"))
    print(f"{'='*65}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        ejecutar("¿Cómo funciona una convalidación de asignaturas en la PUCV?")
        ejecutar("¿Cuál es la nota mínima para aprobar una asignatura?")
        ejecutar("¿Cuál es la capital de Francia?")
    else:
        app = construir_grafo()
        print("\nAsistente Académico PUCV — Modo Chat (Estructura Modular)")
        print("Escribe tu consulta o 'salir' para terminar.\n")

        while True:
            try:
                consulta = input("Tu consulta: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nHasta luego.")
                break

            if not consulta:
                continue
            if consulta.lower() in {"salir", "exit", "quit"}:
                print("Hasta luego.")
                break

            ejecutar(consulta)
