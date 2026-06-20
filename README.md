# Asistente Académico PUCV (LangGraph + Gemini RAG)

Este proyecto implementa un asistente inteligente multicapa basado en un sistema multiagente con LangGraph y la API de Gemini (modelos `gemini-1.5-flash`). Su objetivo es responder consultas sobre el reglamento académico y de estudios de pregrado de la PUCV a partir de bases de conocimiento procesadas mediante RAG (Retrieval-Augmented Generation).

## Arquitectura Modular

El proyecto está estructurado de manera profesional y modular para facilitar su mantenimiento y escalabilidad:

- **`config/`**: Contiene la carga de variables de entorno y lógica para cargar y fusionar las bases de conocimiento (`settings.py`).
- **`data/`**: Contiene las bases de datos originales en PDF (`raw/`) y estructuradas en formato JSON (`processed/`), además del script extractor (`extraer_pdfs.py`).
- **`src/`**: Capa del agente LangGraph.
  - `state.py`: Definición del estado global del agente (`EstadoChatbot`).
  - `llm.py`: Inicialización del modelo LLM.
  - `tools/`: Herramientas de búsqueda RAG, validación de fuentes y formateador de citas APA.
  - `nodes/`: Nodos de lógica deterministas y basados en LLM (incluyendo descomposición de consultas multicapa).
  - `routers/`: Lógica de enrutamiento condicional.
  - `graph.py`: Ensamblado de nodos, aristas y compilación del grafo.
- **`main.py`**: Punto de entrada del programa (Modo CLI interactivo o suite de pruebas).

## Instalación y Configuración

1. Crea y activa tu entorno virtual de Python:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Configura tu API Key en `.env`:
   ```env
   GOOGLE_API_KEY=tu_api_key_de_gemini
   KB_TYPE=extended   # Opciones: 'standard' para KB simulada o 'extended' para la KB real completa
   ```

## Ejecución

- **Para correr la suite de pruebas predefinida**:
  ```bash
  python main.py test
  ```

- **Para iniciar el chat interactivo en la terminal**:
  ```bash
  python main.py
  ```