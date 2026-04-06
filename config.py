#!/usr/bin/env python3
"""
Archivo de configuración del scraper
Modifica estos valores según tus necesidades
"""

# ====================================
# CONFIGURACIÓN DE SCRAPING
# ====================================

# Cantidad de hilos a procesar por foro
# Valores recomendados:
#   - Normal: 20-30
#   - Completo: 50-100
MAX_THREADS_PER_FORUM = 20

# Meses de antigüedad máxima de posts
# Solo procesa posts de los últimos X meses
MAX_POST_AGE_MONTHS = 24

# Pausa entre requests (segundos)
# Aumentar si hay problemas de rate limiting
REQUEST_DELAY_SECONDS = 1

# Timeout para requests HTTP (segundos)
REQUEST_TIMEOUT = 15

# ====================================
# KEYWORDS DE BÚSQUEDA
# ====================================

# Palabras clave para filtrar hilos relevantes
SEARCH_KEYWORDS = [
    'hipoteca',
    'tin',
    'tae',
    'euribor',
    'euríbor',
    'fijo',
    'variable',
    'mixta',
    'banco',
    'oferta',
    'negociado',
    'negociación',
    'broker',
    'vinculación',
    'ibercaja',
    'bbva',
    'santander',
    'caixabank',
    'bankinter',
    'ing',
    'sabadell',
    'openbank',
    'evo',
    'deutsche bank'
]

# ====================================
# FOROS A SCRAPEAR
# ====================================

# Habilitar/deshabilitar foros específicos
ENABLE_RANKIA = True
ENABLE_BOGLEHEADS = True
ENABLE_FOROCOCHES = True
ENABLE_MEDIAVIDA = False  # Deshabilitado por defecto
ENABLE_SOLOARQUITECTURA = False  # Deshabilitado por defecto

# ====================================
# CONFIGURACIÓN DE IA
# ====================================

# Modelo de OpenAI a usar
AI_MODEL = "gpt-4o"  # Opciones: gpt-4o, gpt-5.1, gpt-5.2

# Proveedor
AI_PROVIDER = "openai"

# Longitud máxima de texto a enviar a IA (caracteres)
MAX_TEXT_LENGTH_FOR_AI = 8000

# ====================================
# CONFIGURACIÓN DE OUTPUT
# ====================================

# Nombre base de archivos de salida
OUTPUT_FILENAME_BASE = "ofertas_hipotecarias"

# Formatos de exportación
EXPORT_CSV = True
EXPORT_EXCEL = True
EXPORT_JSON = False  # Opcional

# Carpeta de salida
OUTPUT_FOLDER = "output"

# ====================================
# LOGGING
# ====================================

# Nivel de logging
# Opciones: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Mostrar progreso detallado
SHOW_PROGRESS = True

# ====================================
# AVANZADO
# ====================================

# User Agent para requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Reintentos en caso de error
MAX_RETRIES = 2

# Ignorar errores SSL (no recomendado)
VERIFY_SSL = True
