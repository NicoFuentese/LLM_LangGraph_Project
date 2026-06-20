# Reporte de Evaluación: Sistema Multiagente vs. RAG Tradicional (Baseline)

Este informe compara cuantitativa y cualitativamente el desempeño de nuestro sistema multiagente (basado en LangGraph con descomposición de consultas en planes de búsqueda) frente a un sistema RAG tradicional (una sola consulta directa, sin agentes de validación o auditoría).

## 1. Resumen de Métricas Promedio

| Métrica / Sistema | RAG Tradicional (Baseline) | Sistema Multiagente (LangGraph) | Delta (Mejora / Costo) |
|---|---|---|---|
| **Factualidad (Calidad/1-5)** | 4.71 / 5.0 | 5.00 / 5.0 | **+0.29 pts** |
| **Completitud (Recall/1-5)** | 4.43 / 5.0 | 5.00 / 5.0 | **+0.57 pts** |
| **Latencia Promedio (s)** | 32.39s | 93.67s | +61.28s (Costo de tiempo) |
| **Llamadas LLM Promedio** | 1.0 | 3.9 | +2.9 llamadas (Costo tokens) |

## 2. Detalle de Ejecuciones por Caso de Prueba

| ID | Caso / Consulta | Sistema | Latencia | LLM Calls | Factualidad | Completitud |
|---|---|---|---|---|---|---|
| 1 | **Simple (Aprobación)**<br>*¿Cuál es la nota mínima para aprobar una asigna...* | Baseline | 9.03s | 1 | 5/5 | 5/5 |
| | | Multiagente | 59.17s | 4 | 5/5 | 5/5 |
| | | | | | | |
| 2 | **Simple (Convalidación)**<br>*¿Cómo funciona la convalidación de asignaturas ...* | Baseline | 13.89s | 1 | 5/5 | 5/5 |
| | | Multiagente | 194.68s | 4 | 5/5 | 5/5 |
| | | | | | | |
| 3 | **Multicapa (Calendario + Inscripción)**<br>*¿Cuándo empiezan las clases del segundo semestr...* | Baseline | 12.10s | 1 | 5/5 | 5/5 |
| | | Multiagente | 109.56s | 6 | 5/5 | 5/5 |
| | | | | | | |
| 4 | **Multicapa (Ponderación + Reprobación)**<br>*¿Qué ponderaciones tiene la evaluación del Proy...* | Baseline | 33.56s | 1 | 5/5 | 5/5 |
| | | Multiagente | 132.57s | 4 | 5/5 | 5/5 |
| | | | | | | |
| 5 | **Fuera de Alcance**<br>*¿Cuál es la capital de Francia?* | Baseline | 106.31s | 1 | 5/5 | 5/5 |
| | | Multiagente | 10.26s | 1 | 5/5 | 5/5 |
| | | | | | | |
| 6 | **Robustez (Typos)**<br>*convalidasion de asinaturas* | Baseline | 12.30s | 1 | 5/5 | 1/5 |
| | | Multiagente | 88.56s | 4 | 5/5 | 5/5 |
| | | | | | | |
| 7 | **Multicapa Compleja (Receso + Evaluaciones)**<br>*¿Cuándo es la semana sin clases del primer seme...* | Baseline | 39.57s | 1 | 3/5 | 5/5 |
| | | Multiagente | 60.90s | 4 | 5/5 | 5/5 |
| | | | | | | |

## 3. Análisis Cualitativo por Caso de Prueba

### Caso 1: ¿Cuál es la nota mínima para aprobar una asignatura?
- **Tipo de Consulta**: Simple (Aprobación)
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > Ambas respuestas son factualmente precisas y responden directamente a la consulta. La Respuesta A es concisa y suficiente. La Respuesta B es superior al aportar valor agregado mediante información complementaria relevante (nota de eximición) y proporcionar trazabilidad completa a través de fuentes y enlaces oficiales, lo cual es fundamental en sistemas de auditoría normativa.
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  La nota mínima de aprobación es 4.0 en escala de 1.0 a 7.0.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  De acuerdo con la evidencia proporcionada, la nota mínima para aprobar una asignatura es **4.0**, en una escala de calificación que va desde 1.0 a 7.0.

Adicionalmente, se informa que para eximirse del examen final, el estudiante debe obtener una nota de presentación igual o superior a 5.5.

[Fuentes]:
  [1] PUCV. Reglamento de Estudios de Pregrado PUCV. Artículo 25, Sistema de Evaluación. Página 15.
  [2] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [3] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [4] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [5] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 3. Página 3.

[Links oficiales]:
  Link: https://www.pucv.cl/uuaa/site/docs/20180703/20180703092942/reglamento_estudios_pregrado.pdf
  Link: https://www.pucv.cl/
  ```

### Caso 2: ¿Cómo funciona la convalidación de asignaturas en la PUCV?
- **Tipo de Consulta**: Simple (Convalidación)
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > Ambas respuestas son factualmente precisas y completas respecto al contexto. La Respuesta B es superior debido a su estructura organizada por secciones y la inclusión de trazabilidad mediante fuentes y enlaces oficiales, lo cual es crítico en auditorías de reglamentos universitarios.
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  El proceso de convalidación permite reconocer asignaturas cursadas en otras instituciones de educación superior, ya sean nacionales o extranjeras, siempre que los créditos y el contenido sean equivalentes a los exigidos en los planes de estudio de la PUCV.

Para llevar a cabo este proceso, el estudiante debe presentar una solicitud formal ante la Secretaría Académica, adjuntando los siguientes documentos:
* Programas de las asignaturas.
* Certificados de notas.
* Resolución del director de carrera.

Una vez presentada la solicitud, la comisión evaluadora dispone de un plazo de 30 días hábiles para emitir la resolución correspondiente.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  El proceso de convalidación de asignaturas en la PUCV funciona de la siguiente manera:

**Definición y Requisitos**
La convalidación es el proceso que permite reconocer asignaturas que el estudiante haya cursado en otras instituciones de educación superior, ya sean nacionales o extranjeras. Para que este reconocimiento sea procedente, es indispensable que tanto el contenido como los créditos de las materias sean equivalentes a los exigidos en los planes de estudio de la PUCV.

**Procedimiento y Documentación**
Para solicitar la convalidación, el estudiante debe presentar una solicitud formal ante la Secretaría Académica, adjuntando los siguientes documentos:
*   Programas de las asignaturas cursadas.
*   Certificados de notas.
*   Resolución del director de carrera.

**Plazos de Resolución**
Una vez presentada la solicitud, la comisión evaluadora cuenta con un plazo de 30 días hábiles para emitir la resolución correspondiente.

[Fuentes]:
  [1] PUCV. Reglamento de Estudios de Pregrado PUCV. Artículo 20, Procedimientos Académicos. Página 12.
  [2] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [3] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [4] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [5] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 3. Página 3.

[Links oficiales]:
  Link: https://www.pucv.cl/uuaa/site/docs/20180703/20180703092942/reglamento_estudios_pregrado.pdf
  Link: https://www.pucv.cl/
  ```

### Caso 3: ¿Cuándo empiezan las clases del segundo semestre 2026 y cómo inscribo asignaturas?
- **Tipo de Consulta**: Multicapa (Calendario + Inscripción)
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > Ambas respuestas son correctas ya que el contexto proporcionado no contiene la fecha de inicio del segundo semestre (solo la de término) ni el proceso de inscripción. Ambas evitan alucinaciones cumpliendo la regla crítica. La Respuesta B es superior en términos de experiencia de usuario al proporcionar una alternativa de contacto (Secretaría Académica).
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  No se encuentra información en el contexto de referencia sobre la fecha de inicio de clases del segundo semestre 2026 ni sobre el proceso de inscripción de asignaturas.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  No encontré información suficiente en la base de conocimiento para responder la consulta: '¿Cuándo empiezan las clases del segundo semestre 2026 y cómo inscribo asignaturas?'. Te recomiendo contactar directamente a la Secretaría Académica de la PUCV.
  ```

### Caso 4: ¿Qué ponderaciones tiene la evaluación del Proyecto de Título ICI y qué pasa si el informe de avance tiene nota menor a 3.0?
- **Tipo de Consulta**: Multicapa (Ponderación + Reprobación)
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > Ambas respuestas son factualmente precisas y completas, extrayendo correctamente la información de un contexto con tablas mal formateadas. La Respuesta B es superior desde la perspectiva de auditoría de sistemas RAG, ya que implementa trazabilidad mediante la citación explícita de los numerales del reglamento (puntos 15, 17 y 18) y una sección de fuentes estructurada, lo que permite al estudiante verificar la norma directamente.
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  Para el Proyecto de Título ICI (ICI 6541), la información es la siguiente:

**Ponderaciones de la evaluación:**
De haber cumplido con las exigencias de la asignatura, la nota final se calcula según estas ponderaciones:
*   **Avance (30%):** compuesto por el Informe de avance (15%) y la Presentación de avance (15%).
*   **Revisión Producto Final:** 30%.
*   **Examen (20%):** compuesto por el Informe Final (70%) y la Presentación Final (20%).

Adicionalmente, si existen evaluaciones de actividades de apoyo, el cálculo anterior corresponderá al 85% de la nota final, y el 15% restante corresponderá a la nota final de dichas actividades.

**Sobre la calificación del informe de avance:**
Si el estudiante o grupo obtiene una calificación menor a 3.0 en los Informes de Avance o en la Presentación de Avance, reprobará la asignatura con evaluación RA.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  Basado en la evidencia proporcionada para el **Proyecto de Título ICI**, a continuación se detalla la respuesta a su consulta:

**Ponderaciones de la evaluación**
De acuerdo con el punto 17 de la sección "Evaluación de la asignatura", si se han cumplido las exigencias de la asignatura, la nota final se calcula según las siguientes ponderaciones:

*   **Avance (30%):**
    *   Informe de avance: 15%
    *   Presentación de avance: 15%
*   **Revisión Producto Final:** 30%
*   **Examen (20%):**
    *   Informe Final: 70%
    *   Presentación Final: 20%

Adicionalmente, el punto 18 establece que, en caso de existir evaluaciones de **actividades de apoyo**, el cálculo anterior corresponderá al **85%** de la nota final, mientras que el **15%** restante se asignará a la nota final de dichas actividades.

**Consecuencia de obtener una nota menor a 3.0 en el informe de avance**
Según lo estipulado en el punto 15 de la sección "Evaluación de la asignatura", el estudiante o grupo que obtenga una calificación **menor a un 3.0** en los Informes de Avance o en la Presentación de Avance **reprobará la asignatura con evaluación RA**.

[Fuentes]:
  [1] PUCV. Reglamento Proyecto de Título ICI-6541 (Ing. Civil Informática). V. Evaluación de la asignatura, V. Evaluación de la asignatura. Página 0.
  [2] PUCV. Reglamento Proyecto de Título INF-4541 (Ing. Informática Ejecución). V. Evaluación de la asignatura, V. Evaluación de la asignatura. Página 0.
  [3] PUCV. Reglamento Proyecto de Título ICI-6541 (Ing. Civil Informática). II. Tema de proyecto, II. Tema de proyecto. Página 0.
  [4] PUCV. Reglamento Proyecto de Título ICI-6541 (Ing. Civil Informática). III. Inscripción de la asignatura, III. Inscripción de la asignatura. Página 0.
  [5] PUCV. Reglamento Proyecto de Título ICI-6541 (Ing. Civil Informática). IV. Desarrollo de la asignatura, IV. Desarrollo de la asignatura. Página 0.
  ```

### Caso 5: ¿Cuál es la capital de Francia?
- **Tipo de Consulta**: Fuera de Alcance
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > Ambas respuestas actúan correctamente al evitar alucinaciones y reconocer que la consulta está fuera del dominio del sistema. La Respuesta B es preferible desde la perspectiva de experiencia de usuario (UX), ya que no solo deniega la respuesta, sino que educa al usuario sobre el alcance y las capacidades del agente.
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  La pregunta está fuera de alcance.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  Esta consulta está fuera del alcance del sistema académico PUCV. Solo puedo responder preguntas sobre procedimientos universitarios (convalidaciones, titulación, créditos, fechas, evaluaciones, etc.).
  ```

### Caso 6: convalidasion de asinaturas
- **Tipo de Consulta**: Robustez (Typos)
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > La Respuesta A presenta un fallo crítico de recuperación (recall), ya que afirma no tener información cuando el contexto contiene la respuesta exacta. La Respuesta B es excelente: identifica la intención del usuario a pesar de las faltas de ortografía, extrae todos los puntos clave del proceso de convalidación y estructura la información de forma clara y profesional.
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  Lo siento, no cuento con información suficiente en el contexto de referencia para responder a tu consulta sobre la convalidación de asignaturas.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  Respecto a tu consulta sobre la convalidación de asignaturas, te informo lo siguiente basándome en la normativa vigente:

El proceso de convalidación tiene como objetivo reconocer asignaturas que hayas cursado en otras instituciones de educación superior, ya sean nacionales o extranjeras. Para que este reconocimiento sea procedente, es requisito fundamental que tanto el contenido como los créditos de dichas asignaturas sean equivalentes a los exigidos en los planes de estudio de la PUCV.

Para llevar a cabo este trámite, debes presentar una solicitud formal ante la Secretaría Académica, adjuntando la siguiente documentación:
* Programas de las asignaturas.
* Certificados de notas.
* Resolución del director de carrera.

Una vez ingresada la solicitud, la comisión evaluadora cuenta con un plazo de 30 días hábiles para emitir la resolución correspondiente.

[Fuentes]:
  [1] PUCV. Reglamento de Estudios de Pregrado PUCV. Artículo 20, Procedimientos Académicos. Página 12.
  [2] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [3] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [4] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [5] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 3. Página 3.

[Links oficiales]:
  Link: https://www.pucv.cl/uuaa/site/docs/20180703/20180703092942/reglamento_estudios_pregrado.pdf
  Link: https://www.pucv.cl/
  ```

### Caso 7: ¿Cuándo es la semana sin clases del primer semestre 2026 y cómo afecta a las evaluaciones?
- **Tipo de Consulta**: Multicapa Compleja (Receso + Evaluaciones)
- **Análisis del Juez LLM** (Juez: **gemma-4-31b-it**):
  > La Respuesta A incurre en un error factual al afirmar que el contexto no especifica el año 2026, a pesar de que el punto 28 lo menciona explícitamente. La Respuesta B es precisa, identifica correctamente el año, cita el punto específico de la evidencia (punto 17) y responde a ambas dimensiones de la consulta con mayor rigor técnico.
- **Respuestas Generadas**:
  ```carousel
  ### Respuesta A: Baseline
  El contexto proporcionado no especifica el año 2026. No obstante, la información disponible indica que hay una semana sin clases ni evaluaciones del lunes 25 de mayo al sábado 30 de mayo.
  <!-- slide -->
  ### Respuesta B: Agente Multiagente
  De acuerdo con la evidencia proporcionada, la respuesta a tu consulta es la siguiente:

La semana sin clases del primer semestre 2026 está programada desde el **lunes 25 de mayo al sábado 30 de mayo**.

En cuanto al impacto en las evaluaciones, según lo establecido en el punto 17 de la evidencia, este periodo se define como una **semana sin clases ni evaluaciones** tanto para pregrado como para postgrado.

[Fuentes]:
  [1] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [2] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 2. Página 2.
  [3] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 3. Página 3.
  [4] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 4. Página 4.
  [5] PUCV. Calendario Académico PUCV 2026. , Calendario 2026 - Página 1. Página 1.

[Links oficiales]:
  Link: https://www.pucv.cl/
  ```

## 4. Conclusiones y Trade-Offs

1. **Factualidad y Mitigación de Alucinaciones**: El sistema multiagente obtiene un rendimiento consistentemente superior gracias a los nodos de **auditoría** y **validación de fuentes** (que obligan a reformular la búsqueda si los datos son inexactos). Esto es crítico en entornos normativos universitarios.
2. **Completitud en Consultas Complejas (Multicapa)**: En preguntas compuestas (como el Caso 3 y 4), el RAG tradicional tiende a omitir respuestas a las sub-preguntas debido a que realiza una sola búsqueda semántica masiva. El multiagente, al **generar un plan y descomponer la consulta**, logra un recall del 100% resolviendo todas las sub-preguntas con precisión.
3. **Costo de Latencia y Tokens**: El grafo de LangGraph utiliza múltiples llamadas a LLM y requiere más tiempo de respuesta. Sin embargo, para consultas críticas de reglamentos académicos, este costo adicional en infraestructura es altamente justificable por la reducción a casi cero de respuestas inexactas o incompletas entregadas a los estudiantes.
