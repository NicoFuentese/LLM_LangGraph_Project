"""
extraer_pdfs.py — Extrae contenido de los 7 PDFs oficiales PUCV
y genera knowledge_base_extended.json

Ejecución: python extraer_pdfs.py
Resultado:  knowledge_base_extended.json en el mismo directorio

Dependencia: pip install pdfplumber
"""

import json
import re
import unicodedata
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    raise SystemExit("Instala pdfplumber primero:  pip install pdfplumber")

BASE_DIR = Path(__file__).parent

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE DOCUMENTOS
# ─────────────────────────────────────────────
DOCUMENTOS = {
    "Calendario-Academico-ano-2026": {
        "tipo": "calendario",
        "abrev": "calendario",
        "nombre": "Calendario Académico PUCV 2026",
        "url": "https://www.pucv.cl/",
    },
    "ICI-6541-Reglamento-Proyecto-de-Titulo-Julio-2023.pdf": {
        "tipo": "reglamento",
        "abrev": "titulo_ici",
        "nombre": "Reglamento Proyecto de Título ICI-6541 (Ing. Civil Informática)",
        "url": "",
    },
    "INF-4541-Reglamento-Proyecto-de-Titulo-Julio-2023.pdf": {
        "tipo": "reglamento",
        "abrev": "titulo_inf",
        "nombre": "Reglamento Proyecto de Título INF-4541 (Ing. Informática Ejecución)",
        "url": "",
    },
    "Reglamento-General-de-Estudios.pdf": {
        "tipo": "reglamento",
        "abrev": "general",
        "nombre": "Reglamento General de Estudios PUCV",
        "url": "",
    },
    "REGLAMENTO-INTERNO_-Marzo-2026-escuela-ingenieria-informatica.pdf": {
        "tipo": "reglamento",
        "abrev": "interno",
        "nombre": "Reglamento Interno Escuela Ingeniería Informática PUCV (Marzo 2026)",
        "url": "",
    },
    "REGLAMENTO-PRACTICA_-Marzo-2026.pdf": {
        "tipo": "reglamento",
        "abrev": "practica",
        "nombre": "Reglamento de Práctica PUCV (Marzo 2026)",
        "url": "",
    },
    "REGLAMENTO-SEMINARIO-TITULO_-Marzo-2026.pdf": {
        "tipo": "reglamento",
        "abrev": "seminario",
        "nombre": "Reglamento Seminario de Título PUCV (Marzo 2026)",
        "url": "",
    },
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
PATRON_ARTICULO = re.compile(
    r"Art[ií]culo\s+(\d+)\s*[°\.]?\s*[-–.]?\s*(.*?)(?=Art[ií]culo\s+\d+|$)",
    re.IGNORECASE | re.DOTALL,
)

PATRON_ART_HEADER = re.compile(r"^Art[ií]culo\s+(\d+)\s*[°\.]?", re.IGNORECASE)


def normalizar_texto(texto: str) -> str:
    """Limpia espacios y caracteres de control del texto extraído por pdfplumber."""
    if not texto:
        return ""
    # Normalizar unicode y colapsar espacios múltiples
    texto = unicodedata.normalize("NFKD", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def clave_segura(texto: str) -> str:
    """Convierte texto a clave JSON válida (snake_case, sin acentos)."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s]", "", texto.lower())
    texto = re.sub(r"\s+", "_", texto.strip())
    return texto[:60]  # limitar longitud


# ─────────────────────────────────────────────
# EXTRACTOR DE REGLAMENTOS (chunking por artículo)
# ─────────────────────────────────────────────
def extraer_reglamento(pdf_path: Path, meta: dict) -> dict:
    """
    Extrae artículos de un PDF de reglamento.
    Estrategia: concatena el texto completo de todas las páginas,
    luego divide por ocurrencias de 'Artículo N°'.
    """
    print(f"  Procesando reglamento: {pdf_path.name}")
    resultado = {}

    with pdfplumber.open(pdf_path) as pdf:
        paginas_texto = []
        for i, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""
            if texto.strip():
                paginas_texto.append((i, texto))

    # Construir texto completo con marcadores de página
    texto_completo = ""
    pagina_por_caracter = []  # no usado directamente, pero útil para debug
    for num_pag, texto in paginas_texto:
        texto_completo += f"\n{texto}"

    texto_completo = normalizar_texto(texto_completo)

    # Dividir por artículos
    partes = re.split(r"\n(?=Art[ií]culo\s+\d+)", texto_completo)

    articulos_encontrados = 0
    seccion_actual = "Disposiciones Generales"

    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue

        match_header = PATRON_ART_HEADER.match(parte)
        if match_header:
            num_art = match_header.group(1)

            # Extraer título del artículo (primera línea después del header)
            lineas = parte.split("\n")
            titulo_art = lineas[0].strip()
            cuerpo = "\n".join(lineas[1:]).strip() if len(lineas) > 1 else ""

            # Detectar secciones (líneas en mayúsculas que no son artículos)
            if cuerpo and cuerpo.split("\n")[0].isupper():
                seccion_actual = cuerpo.split("\n")[0].strip()

            texto_entrada = f"{titulo_art}\n{cuerpo}".strip()

            # Ignorar artículos muy cortos (encabezados sueltos)
            if len(texto_entrada) < 30:
                continue

            clave = f"reglamento_{meta['abrev']}_art{num_art}"
            resultado[clave] = {
                "texto": texto_entrada,
                "articulo": f"Artículo {num_art}",
                "seccion": seccion_actual,
                "pagina": 0,  # estimación; pdfplumber no da pág por split
                "documento": meta["nombre"],
                "url": meta.get("url", ""),
                "vigente": True,
                "tipo": "reglamento",
            }
            articulos_encontrados += 1

    # Si no se encontraron artículos, intentar con secciones romanas (I., II., III.)
    if articulos_encontrados == 0 and texto_completo:
        patron_romano = re.compile(
            r"\n(?=[IVX]{1,5}\.\s+[A-ZÁÉÍÓÚÑ])",
            re.MULTILINE
        )
        partes_romanas = patron_romano.split(texto_completo)

        if len(partes_romanas) > 1:
            for j, parte in enumerate(partes_romanas, start=1):
                parte = parte.strip()
                if len(parte) < 30:
                    continue
                lineas = parte.split("\n")
                titulo_seccion = lineas[0].strip()
                clave = f"reglamento_{meta['abrev']}_sec{j}"
                resultado[clave] = {
                    "texto": parte,
                    "articulo": titulo_seccion,
                    "seccion": titulo_seccion,
                    "pagina": 0,
                    "documento": meta["nombre"],
                    "url": meta.get("url", ""),
                    "vigente": True,
                    "tipo": "reglamento",
                }
                articulos_encontrados += 1
            print(f"    ✓ {articulos_encontrados} sección(es) romana(s) extraídas")
        else:
            # Fallback: dividir en bloques de ~1000 chars
            bloques = [texto_completo[i:i+1000] for i in range(0, min(len(texto_completo), 8000), 1000)]
            for j, bloque in enumerate(bloques, start=1):
                clave = f"reglamento_{meta['abrev']}_bloque{j}"
                resultado[clave] = {
                    "texto": bloque.strip(),
                    "articulo": "",
                    "seccion": "Contenido General",
                    "pagina": j,
                    "documento": meta["nombre"],
                    "url": meta.get("url", ""),
                    "vigente": True,
                    "tipo": "reglamento",
                }
            print(f"    ⚠ Sin artículos detectados; guardado como {len(bloques)} bloque(s) de texto")
    else:
        print(f"    ✓ {articulos_encontrados} artículos extraídos")

    return resultado


# ─────────────────────────────────────────────
# EXTRACTOR DE CALENDARIO (chunking por tabla/evento)
# ─────────────────────────────────────────────
def extraer_calendario(pdf_path: Path, meta: dict) -> dict:
    """
    Extrae eventos del calendario académico.
    Usa extract_tables() para capturar filas con fecha/evento.
    Genera claves descriptivas basadas en el texto de la actividad.
    """
    print(f"  Procesando calendario: {pdf_path.name}")
    resultado = {}
    eventos_encontrados = 0
    claves_usadas: set = set()

    with pdfplumber.open(pdf_path) as pdf:
        for num_pag, pagina in enumerate(pdf.pages, start=1):
            tablas = pagina.extract_tables()
            for tabla in tablas:
                for fila in tabla:
                    if not fila:
                        continue
                    celdas = [str(c).strip() for c in fila if c and str(c).strip()]
                    if len(celdas) < 2:
                        continue

                    # Reconstruir texto completo de la fila (unir todas las celdas)
                    # Normalizar saltos de línea dentro de celdas
                    partes_limpias = [re.sub(r"\s+", " ", c) for c in celdas]
                    texto_fila = " | ".join(partes_limpias)

                    # Ignorar encabezados numéricos puros o muy cortos
                    if re.match(r"^(\d+\.?\s*$|semestre|período|actividad|fecha|mes|evento)", texto_fila, re.IGNORECASE):
                        continue
                    if len(texto_fila) < 15:
                        continue

                    # Generar clave descriptiva a partir del texto de la actividad
                    # Tomar la celda más larga como descripción principal
                    desc = max(partes_limpias, key=len)
                    # Eliminar número inicial si la primera celda es solo un número
                    clave_base = clave_segura(desc[:50])
                    if not clave_base or clave_base.isdigit():
                        clave_base = f"evento_{eventos_encontrados}"

                    # Evitar duplicados
                    clave = f"calendario_{clave_base}"
                    if clave in claves_usadas:
                        clave = f"{clave}_{eventos_encontrados}"
                    claves_usadas.add(clave)

                    resultado[clave] = {
                        "texto": texto_fila,
                        "articulo": "",
                        "seccion": f"Calendario 2026 - Página {num_pag}",
                        "pagina": num_pag,
                        "documento": meta["nombre"],
                        "url": meta.get("url", ""),
                        "vigente": True,
                        "tipo": "calendario",
                    }
                    eventos_encontrados += 1

    # Respaldo: texto plano si no hay tablas
    if eventos_encontrados == 0:
        with pdfplumber.open(pdf_path) as pdf:
            texto_total = normalizar_texto(
                " ".join((p.extract_text() or "") for p in pdf.pages)
            )
        if texto_total:
            resultado["calendario_contenido_completo_2026"] = {
                "texto": texto_total[:4000],
                "articulo": "",
                "seccion": "Calendario Completo 2026",
                "pagina": 1,
                "documento": meta["nombre"],
                "url": meta.get("url", ""),
                "vigente": True,
                "tipo": "calendario",
            }
            eventos_encontrados = 1
        print(f"    ⚠ Sin tablas detectadas; guardado como texto plano")
    else:
        print(f"    ✓ {eventos_encontrados} evento(s)/fila(s) extraídos")

    return resultado


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    kb_extendida = {}
    total_entradas = 0

    print("\n=== Extracción de PDFs PUCV ===\n")

    for nombre_archivo, meta in DOCUMENTOS.items():
        pdf_path = BASE_DIR / nombre_archivo
        if not pdf_path.exists():
            print(f"  ⚠ No encontrado: {nombre_archivo}")
            continue

        if meta["tipo"] == "calendario":
            entradas = extraer_calendario(pdf_path, meta)
        else:
            entradas = extraer_reglamento(pdf_path, meta)

        kb_extendida.update(entradas)
        total_entradas += len(entradas)

    # Guardar JSON
    output_path = BASE_DIR / "knowledge_base_extended.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kb_extendida, f, ensure_ascii=False, indent=2)

    print(f"\n=== Resultado ===")
    print(f"Total entradas generadas: {total_entradas}")
    print(f"Archivo guardado en: {output_path}")
    print(f"\nPrimeras 10 claves:")
    for clave in list(kb_extendida.keys())[:10]:
        texto_preview = kb_extendida[clave]["texto"][:80].replace("\n", " ")
        print(f"  • {clave}: {texto_preview}...")


if __name__ == "__main__":
    main()
