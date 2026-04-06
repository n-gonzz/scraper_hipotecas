# 🏦 Scraper de Ofertas Hipotecarias

Sistema automatizado de scraping y extracción de ofertas hipotecarias reales negociadas por usuarios en foros españoles.

## 🎯 Descripción

Este script en Python recopila ofertas hipotecarias reales de múltiples foros españoles, extrae datos estructurados usando IA (OpenAI GPT-4o) y los exporta a formatos CSV y Excel.

## 🌐 Fuentes de Datos

- **Rankia** - Foro de hipotecas
- **Bogleheads España** - Finanzas personales
- **Forocoches** - Sección de economía
- **Mediavida** - Foros generales
- **Soloarquitectura** - Foros de construcción

## 📋 Requisitos

- Python 3.11.9
- Dependencias listadas en `requirements.txt`
- Emergent LLM Key (ya configurada en `.env`)

## 🚀 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Instalar navegador para Playwright (opcional, para sitios dinámicos)
python -m playwright install chromium
```

## 💻 Uso

### Ejecución básica

```bash
python scraper.py
```

### Ejecución desde cualquier ubicación

```bash
cd /app/mortgage_scraper
python scraper.py
```

## 📊 Datos Extraídos

Para cada oferta hipotecaria encontrada:

| Campo | Descripción |
|-------|-------------|
| **Banco** | Nombre de la entidad financiera |
| **TIN Oficial** | TIN publicado oficialmente |
| **TIN Negociado** | TIN real conseguido por el usuario |
| **TAE** | Tasa Anual Equivalente |
| **Diferencia** | Diferencia en puntos porcentuales |
| **Tipo** | Fija, variable o mixta |
| **Condiciones** | Seguros, nómina, vinculaciones |
| **Contexto** | Broker, negociación directa, etc. |
| **Resumen** | Descripción breve del caso |
| **URL** | Enlace al hilo original |

## 📁 Archivos de Salida

Los resultados se guardan en la carpeta `output/` con timestamp:

- `ofertas_hipotecarias_YYYYMMDD_HHMMSS.csv`
- `ofertas_hipotecarias_YYYYMMDD_HHMMSS.xlsx`

## 🧠 Funcionamiento

1. **Recolección**: Busca hilos relevantes en cada foro
2. **Filtrado**: Aplica keywords y filtros temporales (últimos 24 meses)
3. **Extracción**: Limpia HTML y extrae texto
4. **IA**: Usa GPT-4o para identificar y estructurar ofertas
5. **Normalización**: Estandariza formatos y calcula diferencias
6. **Exportación**: Genera CSV y Excel

## ⚙️ Configuración

### Variables de entorno (`.env`)

**Opción 1: Emergent LLM Key (Incluida)**
```env
EMERGENT_LLM_KEY=sk-emergent-f843f724d814bAfEb4
```

**Opción 2: Tu propia API Key de OpenAI**
```env
OPENAI_API_KEY=sk-proj-TUAPIKEYAQUI
```

⚠️ **Nota sobre presupuesto**: Si el test muestra "Budget has been exceeded", necesitas:
1. Agregar saldo a tu Universal Key (Profile → Universal Key → Add Balance)
2. O usar tu propia API Key de OpenAI (ver NOTA_API_KEY.txt)

### Ajustar cantidad de hilos a procesar

En `scraper.py`, modificar el parámetro `max_threads_per_forum`:

```python
df = asyncio.run(scraper.run(max_threads_per_forum=20))  # Default: 20 por foro
```

## 📝 Logging

El script genera logs en consola con:
- Progreso de scraping
- Hilos encontrados por foro
- Ofertas extraídas
- Errores y advertencias

## 🔒 Consideraciones

- **Rate limiting**: El script incluye pausas entre peticiones
- **Robots.txt**: Respeta políticas de scraping de cada sitio
- **Datos reales**: Solo extrae información pública compartida por usuarios
- **Privacidad**: No recopila datos personales

## 🛠️ Estructura del Código

```python
MortgageScraper
├── scrape_rankia()          # Scraping Rankia
├── scrape_bogleheads()      # Scraping Bogleheads
├── scrape_forocoches()      # Scraping Forocoches
├── scrape_thread()          # Procesar hilo individual
├── clean_text()             # Limpiar HTML
├── extract_mortgage_data_with_ai()  # Extracción con GPT-4o
├── normalize_data()         # Normalizar formato
└── save_results()           # Exportar CSV/Excel
```

## 📈 Ejemplo de Salida

```
📊 ESTADÍSTICAS DE SCRAPING
================================================================================
Total de ofertas encontradas: 47

Bancos únicos: 12

Distribución por tipo:
fija        25
variable    15
mixta        7

✓ Archivos guardados en:
  - output/ofertas_hipotecarias_20260115_143022.csv
  - output/ofertas_hipotecarias_20260115_143022.xlsx
================================================================================
```

## 🐛 Solución de Problemas

### Error: "EMERGENT_LLM_KEY no encontrada"
```bash
# Verificar que existe el archivo .env
cat .env
```

### Error de instalación de emergentintegrations
```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Timeout en scraping
- Reducir `max_threads_per_forum` a un valor menor (ej: 10)
- Verificar conectividad a internet

## 📄 Licencia

Uso educativo y de investigación.

## 🤝 Contribuciones

Este es un script standalone. Para mejoras:
- Añadir más foros en `FORUMS`
- Mejorar regex de extracción de porcentajes
- Implementar caché de resultados
- Añadir soporte para Playwright en sitios dinámicos
