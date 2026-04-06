# 📘 Guía de Uso Rápida - Scraper de Hipotecas

## 🚀 Inicio Rápido

### 1. Primera ejecución - Test
```bash
cd /app/mortgage_scraper
python test_scraper.py
```

Esto verificará que todo esté configurado correctamente.

### 2. Modo Demo (3 hilos por foro)
```bash
python demo.py
```

Perfecto para probar sin saturar servidores.

### 3. Scraping Completo (20 hilos por foro)
```bash
python scraper.py
```

⚠️ **Importante**: Puede tomar 30-60 minutos dependiendo del número de hilos.

---

## ⚙️ Configuración Personalizada

### Cambiar cantidad de hilos a procesar

Edita `scraper.py` en la última línea:

```python
# Procesar solo 10 hilos por foro (más rápido)
df = asyncio.run(scraper.run(max_threads_per_forum=10))

# Procesar 50 hilos por foro (más completo)
df = asyncio.run(scraper.run(max_threads_per_forum=50))
```

### Añadir más foros

En la clase `MortgageScraper`, modifica el diccionario `FORUMS`:

```python
FORUMS = {
    'rankia': 'https://www.rankia.com/foros/hipotecas',
    'tu_foro': 'https://ejemplo.com/foro',
    # ...
}
```

Y crea una función `scrape_tu_foro()`.

### Filtrar por fecha (meses recientes)

En `scraper.py`, método `is_recent()`:

```python
def is_recent(self, date_str: str, months: int = 12):  # Cambiar 24 a 12
```

---

## 📊 Interpretar Resultados

### Archivos de salida

Se generan en `output/` con formato:
- `ofertas_hipotecarias_YYYYMMDD_HHMMSS.csv`
- `ofertas_hipotecarias_YYYYMMDD_HHMMSS.xlsx`

### Columnas importantes

| Columna | Qué significa |
|---------|---------------|
| **TIN Negociado** | El TIN real que el usuario consiguió |
| **Diferencia** | Ahorro en puntos porcentuales (pp) |
| **Condiciones** | Costes ocultos (seguros, vinculaciones) |
| **Contexto** | Cómo lo consiguió (broker, antigüedad, etc.) |

### Ejemplo de análisis

```python
import pandas as pd

df = pd.read_csv('output/ofertas_hipotecarias_20260115_143022.csv')

# Mejor oferta por banco
df.groupby('banco')['tin_negociado'].min()

# Bancos con más ofertas
df['banco'].value_counts()

# Promedio de TIN por tipo
df.groupby('tipo')['tin_negociado'].mean()
```

---

## 🔧 Solución de Problemas

### Error: Module not found
```bash
pip install -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Error: Timeout
- Reducir `max_threads_per_forum` a 5-10
- Verificar conexión a internet
- Algunos foros pueden estar caídos (es normal)

### No se encuentran ofertas
- Los keywords pueden no coincidir (normal en algunos hilos)
- Probar con más hilos: `max_threads_per_forum=50`
- Verificar que los foros estén accesibles

### Error de IA: Rate limit
- El Emergent LLM Key tiene límite de llamadas
- Reducir hilos procesados
- Añadir pause más larga entre llamadas en `scrape_thread()`

---

## 💡 Consejos de Uso

### Para mejor calidad de datos
1. **Más hilos = más datos**: Aumentar `max_threads_per_forum` a 30-50
2. **Filtrar por fecha**: Ajustar `months` en `is_recent()` a 6-12 meses
3. **Revisar manualmente**: Algunos casos pueden requerir verificación

### Para velocidad
1. **Menos hilos**: `max_threads_per_forum=10`
2. **Solo Rankia**: Comentar otros foros en `run()`
3. **Sin IA**: Usar solo regex (requiere modificar código)

### Para investigación
1. **Exportar JSON**: Modificar `save_results()` para incluir JSON
2. **Guardar texto crudo**: Añadir columna con texto original
3. **Metadata**: Guardar fecha de scraping, versión, etc.

---

## 📈 Análisis Avanzado

### En Excel
1. Abrir `.xlsx` generado
2. Usar tablas dinámicas para análisis
3. Filtros por banco, tipo, rango TIN

### En Python (Pandas)
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('output/ofertas_hipotecarias_XXX.csv')

# Gráfico: TIN por banco
df.groupby('banco')['tin_negociado'].mean().plot(kind='bar')
plt.title('TIN Promedio por Banco')
plt.show()

# Tabla: Mejores ofertas
top_10 = df.nsmallest(10, 'tin_negociado')[['banco', 'tin_negociado', 'condiciones']]
print(top_10)
```

---

## 🛡️ Buenas Prácticas

- ✅ Respetar rate limits de los foros
- ✅ No ejecutar scraping excesivo (usar con moderación)
- ✅ Verificar datos importantes manualmente
- ✅ No compartir datos personales encontrados
- ✅ Usar datos para investigación/comparación personal

---

## 📞 Debugging

### Ver logs detallados

En `scraper.py`, cambiar nivel de logging:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar de INFO a DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Probar un hilo específico

```python
import asyncio
from scraper import MortgageScraper

scraper = MortgageScraper()
url = "https://www.rankia.com/foros/hipotecas/temas/XXXXX"
ofertas = asyncio.run(scraper.scrape_thread(url))
print(ofertas)
```

---

## ✅ Checklist Pre-Ejecución

- [ ] Instaladas todas las dependencias: `pip install -r requirements.txt`
- [ ] Archivo `.env` existe con `EMERGENT_LLM_KEY`
- [ ] Test pasó correctamente: `python test_scraper.py`
- [ ] Carpeta `output/` existe
- [ ] Conexión a internet estable
- [ ] Tiempo disponible (30-60 min para scraping completo)

---

## 🎯 Flujo Recomendado

```
1. python test_scraper.py     ← Verificar configuración
          ↓
2. python demo.py             ← Probar con datos reales (limitado)
          ↓
3. python scraper.py          ← Scraping completo
          ↓
4. Analizar output/*.xlsx     ← Revisar resultados
```

---

**¡Listo para scrapear! 🚀**