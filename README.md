# Asistente Académico PUCV (LangGraph + RAG Multiagente)

Este proyecto implementa un asistente inteligente multicapa basado en un sistema multiagente estructurado con LangGraph y la API de Gemini/Gemma. Su objetivo es responder consultas complejas sobre el reglamento académico y de estudios de pregrado de la PUCV a partir de bases de conocimiento procesadas mediante RAG (Retrieval-Augmented Generation).

El sistema cuenta con planificación de búsquedas (descomposición de preguntas multicapa), validación estricta de fuentes de información y un auditor de respuestas para mitigar alucinaciones.

---

## Arquitectura Modular del Repositorio

El proyecto está estructurado de manera profesional y desacoplada para facilitar su mantenimiento y escalabilidad:

*   **`config/`**: Contiene la carga de variables de entorno y lógica para cargar y fusionar las bases de conocimiento (`settings.py`).
*   **`data/`**: Contiene las bases de datos originales en PDF (`raw/`) y estructuradas en formato JSON (`processed/`), además del script extractor (`extraer_pdfs.py`).
*   **`output/`**: Almacena los reportes resultantes de la suite de pruebas comparativas (`evaluacion_resultados.md`).
*   **`src/`**: Capa lógica del agente LangGraph:
    *   `state.py`: Definición del estado de control global del agente (`EstadoChatbot`).
    *   `llm.py`: Inicialización y configuración del cliente de LLM.
    *   `tools/`: Herramientas del Agente (RAG con keyword matching con pesos, validador de consistencia de fuentes y formateador de citas APA).
    *   `nodes/`: Nodos de procesamiento deterministas y basados en LLM (intención, planificación, evaluación, reformulación, generación y auditoría).
    *   `routers/`: Enrutamiento condicional para control de flujos y loops de reintento.
    *   `graph.py`: Ensamblado de nodos y aristas del StateGraph.
*   **`tests/`**: Suite de evaluación y comparativas de rendimiento:
    *   `baseline_rag.py`: Implementación de una línea base RAG tradicional de un paso (sin loops ni agentes).
    *   `evaluador_comparativo.py`: Script para orquestar la suite de 7 casos de prueba complejos, interrogar al Juez LLM y compilar métricas cuantitativas/cualitativas.
*   **`main.py`**: Punto de entrada para el CLI del chatbot interactivo o tests básicos.

---

## Instalación y Configuración

1. **Crear y activar entorno virtual**:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   Crea un archivo `.env` en la raíz del directorio `/LLM_LangGraph_Project` basándote en el ejemplo `.env.example`:
   ```env
   GOOGLE_API_KEY=tu_api_key_de_gemini
   GEMINI_MODEL=gemma-4-31b-it      # Modelo para el agente y RAG (ej. gemma-4-31b-it o gemini-2.0-flash)
   JUDGE_MODEL=gemma-4-31b-it       # Modelo Juez para el evaluador comparativo
   KB_TYPE=extended                 # 'standard' para KB simulada o 'extended' para KB completa integrada
   ```

---

## Ejecución y Pruebas

### 1. Chatbot Interactivo (Terminal)
Inicia la consola interactiva para chatear directamente con el agente multiagente estructurado:
```bash
python main.py
```

### 2. Suite de Pruebas de Grafo Básicas
Corre las preguntas de validación rápida configuradas en `main.py`:
```bash
python main.py test
```

### 3. Suite de Evaluación Comparativa (Multiagente vs. Baseline RAG)
Corre el evaluador completo de 7 preguntas compuestas, typos y fuera de alcance, utilizando el modelo Juez configurado en tu `.env`. Genera un reporte detallado de Factualidad, Recall, Latencia y Llamadas al LLM en la carpeta de salidas:
```bash
python tests/evaluador_comparativo.py
```
El reporte resultante se guardará en: `output/evaluacion_resultados.md`.