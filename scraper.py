#!/usr/bin/env python3
"""
Sistema de Scraping de Ofertas Hipotecarias
Extrae ofertas reales negociadas por usuarios en foros españoles
"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
import asyncio
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()


class MortgageScraper:
    """Scraper de ofertas hipotecarias de foros españoles"""
    
    KEYWORDS = [
    'TIN', 'TAE', 'bonificado', 'sin vincular', 
    'FEIN', 'FIPER', 'Sabadell', 'Openbank', 
    'Santander', 'BBVA', 'MyInvestor', 'Evo'
]
    
    FORUMS = {
        'rankia': 'https://www.rankia.com/foros/hipotecas',
        'bogleheads': 'https://bogleheads.es/foro/',
        'forocoches': 'https://www.forocoches.com/', # Ojo con el login/muro
        'mediavida': 'https://www.mediavida.com/foro/',
        'soloarquitectura': 'https://www.soloarquitectura.com/foros/',
        # --- Sugerencias añadidas ---
        'helpmycash': 'https://www.helpmycash.com/foros/hipotecas/',
        'burbuja': 'https://www.burbuja.info/inmobiliaria/forums/burbuja-inmobiliaria.7/',
        'nuevosvecinos': 'https://www.nuevosvecinos.com/foros',
        'reddit_espf': 'https://www.reddit.com/r/ESPersonalFinance/',
        'inverforo': 'https://www.inverforo.com/foro/hipotecas-y-vivienda/'
    }
    
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY no encontrada en .env")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = []
        self.processed_urls = set()
        
    def is_recent(self, date_str: str, months: int = 24) -> bool:
        """Verifica si el contenido es reciente"""
        try:
            # Intentar parsear diferentes formatos de fecha
            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                try:
                    post_date = datetime.strptime(date_str, fmt)
                    cutoff_date = datetime.now() - timedelta(days=months*30)
                    return post_date >= cutoff_date
                except:
                    continue
        except:
            pass
        return True  # Por defecto aceptar si no podemos determinar fecha
    
    def contains_keywords(self, text: str) -> bool:
        """Verifica si el texto contiene keywords relevantes"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.KEYWORDS)
    
    def clean_text(self, html_content: str) -> str:
        """Limpia HTML y retorna texto plano"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Eliminar scripts, estilos, etc.
        for tag in soup(['script', 'style', 'meta', 'link']):
            tag.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_percentage(self, text: str) -> List[str]:
        """Extrae porcentajes del texto"""
        # Patrones para TIN/TAE
        patterns = [
            r'\d+[.,]\d+\s*%',
            r'\d+[.,]\d+\s*pp',
            r'euríbor\s*\+\s*\d+[.,]\d+',
            r'euribor\s*\+\s*\d+[.,]\d+'
        ]
        
        percentages = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            percentages.extend(matches)
        
        return percentages
    
    async def extract_mortgage_data_with_ai(self, text: str, url: str) -> List[Dict]:
        """Usa GPT-4o para extraer datos estructurados"""
        
        # Si el texto es muy largo, tomar solo los primeros 8000 caracteres
        if len(text) > 8000:
            text = text[:8000]
        
        prompt = f"""Analiza el siguiente texto de un foro español sobre hipotecas y extrae TODAS las ofertas hipotecarias reales mencionadas.

Para cada oferta encontrada, extrae:
- banco: nombre del banco
- tin_oficial: TIN oficial si se menciona (o "No especificado")
- tin_negociado: TIN que el usuario consiguió negociar
- tae: TAE si se menciona (o "No especificado")
- tipo: fija, variable, o mixta
- condiciones: seguros, nómina, vinculaciones mencionadas
- contexto: broker, negociación directa, cliente antiguo, etc.
- resumen: breve descripción del caso (máximo 100 palabras)

SOLO extrae ofertas con datos numéricos concretos. NO inventes información.
Si no hay ofertas hipotecarias reales con números, responde con una lista vacía.

Responde ÚNICAMENTE con un JSON válido con esta estructura:
{{
  "ofertas": [
    {{
      "banco": "...",
      "tin_oficial": "...",
      "tin_negociado": "...",
      "tae": "...",
      "tipo": "...",
      "condiciones": "...",
      "contexto": "...",
      "resumen": "..."
    }}
  ]
}}

Texto del foro:
{text}
"""
        
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"scraper_{int(time.time())}",
                system_message="Eres un experto en extraer datos financieros estructurados de texto desordenado. Responde SOLO con JSON válido."
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Limpiar respuesta para obtener solo JSON
            response_text = response.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            data = json.loads(response_text)
            ofertas = data.get('ofertas', [])
            
            # Añadir URL a cada oferta
            for oferta in ofertas:
                oferta['url'] = url
            
            return ofertas
            
        except Exception as e:
            logger.error(f"Error en extracción con IA: {e}")
            return []
    
    def scrape_rankia(self, max_threads: int = 50) -> List[str]:
        """Scrape Rankia foro de hipotecas"""
        logger.info("Scrapeando Rankia...")
        thread_urls = []
        
        try:
            base_url = self.FORUMS['rankia']
            response = self.session.get(base_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlaces a hilos
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text().strip()
                    
                    # Filtrar por keywords
                    if self.contains_keywords(title) and 'foro' in href:
                        full_url = urljoin(base_url, href)
                        if full_url not in self.processed_urls and full_url not in thread_urls:
                            thread_urls.append(full_url)
                            
                            if len(thread_urls) >= max_threads:
                                break
                
                logger.info(f"Encontrados {len(thread_urls)} hilos en Rankia")
            
        except Exception as e:
            logger.error(f"Error scrapeando Rankia: {e}")
        
        return thread_urls
    
    def scrape_bogleheads(self, max_threads: int = 30) -> List[str]:
        """Scrape Bogleheads foro"""
        logger.info("Scrapeando Bogleheads...")
        thread_urls = []
        
        try:
            # Buscar en sección de hipotecas/finanzas personales
            search_urls = [
                'https://bogleheads.es/foro/viewforum.php?f=2',  # Finanzas personales
                'https://bogleheads.es/foro/viewforum.php?f=1'   # General
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        links = soup.find_all('a', class_='topictitle')
                        
                        for link in links:
                            title = link.get_text().strip()
                            href = link.get('href', '')
                            
                            if self.contains_keywords(title):
                                full_url = urljoin(search_url, href)
                                if full_url not in self.processed_urls and full_url not in thread_urls:
                                    thread_urls.append(full_url)
                                    
                                    if len(thread_urls) >= max_threads:
                                        break
                except Exception as e:
                    logger.warning(f"Error en {search_url}: {e}")
                    continue
            
            logger.info(f"Encontrados {len(thread_urls)} hilos en Bogleheads")
            
        except Exception as e:
            logger.error(f"Error scrapeando Bogleheads: {e}")
        
        return thread_urls
    
    def scrape_forocoches(self, max_threads: int = 30) -> List[str]:
        """Scrape Forocoches"""
        logger.info("Scrapeando Forocoches...")
        thread_urls = []
        
        try:
            # Buscar en sección de economía
            base_url = 'https://www.forocoches.com/foro/forumdisplay.php?f=4'  # Economía
            response = self.session.get(base_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', id=re.compile(r'thread_title_\d+'))
                
                for link in links:
                    title = link.get_text().strip()
                    href = link.get('href', '')
                    
                    if self.contains_keywords(title):
                        full_url = urljoin(base_url, href)
                        if full_url not in self.processed_urls and full_url not in thread_urls:
                            thread_urls.append(full_url)
                            
                            if len(thread_urls) >= max_threads:
                                break
                
                logger.info(f"Encontrados {len(thread_urls)} hilos en Forocoches")
        
        except Exception as e:
            logger.error(f"Error scrapeando Forocoches: {e}")
        
        return thread_urls
    
    async def scrape_thread(self, url: str) -> List[Dict]:
        """Extrae contenido de un hilo específico"""
        
        if url in self.processed_urls:
            return []
        
        self.processed_urls.add(url)
        
        try:
            logger.info(f"Procesando: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            # Extraer texto limpio
            text = self.clean_text(response.content)
            
            # Verificar que contenga keywords relevantes
            if not self.contains_keywords(text):
                return []
            
            # Extraer datos con IA
            ofertas = await self.extract_mortgage_data_with_ai(text, url)
            
            if ofertas:
                logger.info(f"✓ Encontradas {len(ofertas)} ofertas en {url}")
            
            # Pequeña pausa para no sobrecargar servidores
            time.sleep(1)
            
            return ofertas
            
        except Exception as e:
            logger.error(f"Error procesando {url}: {e}")
            return []
    
    def normalize_data(self, ofertas: List[Dict]) -> pd.DataFrame:
        """Normaliza y estructura los datos"""
        
        if not ofertas:
            return pd.DataFrame()
        
        df = pd.DataFrame(ofertas)
        
        # Asegurar todas las columnas necesarias
        required_columns = [
            'banco', 'tin_oficial', 'tin_negociado', 'tae',
            'tipo', 'condiciones', 'contexto', 'resumen', 'url'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = 'No especificado'
        
        # Reordenar columnas
        df = df[required_columns]
        
        # Calcular diferencia si es posible
        def calculate_difference(row):
            try:
                oficial = row['tin_oficial']
                negociado = row['tin_negociado']
                
                # Extraer números
                oficial_num = re.findall(r'\d+[.,]\d+', str(oficial))
                negociado_num = re.findall(r'\d+[.,]\d+', str(negociado))
                
                if oficial_num and negociado_num:
                    oficial_val = float(oficial_num[0].replace(',', '.'))
                    negociado_val = float(negociado_num[0].replace(',', '.'))
                    diff = negociado_val - oficial_val
                    return f"{diff:+.2f} pp"
            except:
                pass
            return 'No calculable'
        
        df['diferencia'] = df.apply(calculate_difference, axis=1)
        
        # Reordenar con diferencia
        column_order = [
            'banco', 'tin_oficial', 'tin_negociado', 'tae', 'diferencia',
            'tipo', 'condiciones', 'contexto', 'resumen', 'url'
        ]
        df = df[column_order]
        
        # Eliminar duplicados
        df = df.drop_duplicates(subset=['banco', 'tin_negociado', 'resumen'], keep='first')
        
        return df
    
    def save_results(self, df: pd.DataFrame, base_filename: str = 'ofertas_hipotecarias'):
        """Guarda resultados en CSV y Excel"""
        
        if df.empty:
            logger.warning("No hay datos para guardar")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar CSV
        csv_path = f'output/{base_filename}_{timestamp}.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"✓ CSV guardado: {csv_path}")
        
        # Guardar Excel
        excel_path = f'output/{base_filename}_{timestamp}.xlsx'
        df.to_excel(excel_path, index=False, engine='openpyxl')
        logger.info(f"✓ Excel guardado: {excel_path}")
        
        # Mostrar estadísticas
        print("\n" + "="*80)
        print("📊 ESTADÍSTICAS DE SCRAPING")
        print("="*80)
        print(f"Total de ofertas encontradas: {len(df)}")
        print(f"\nBancos únicos: {df['banco'].nunique()}")
        print(f"\nDistribución por tipo:")
        print(df['tipo'].value_counts())
        print("\n" + "="*80)
        print(f"\n✓ Archivos guardados en:")
        print(f"  - {csv_path}")
        print(f"  - {excel_path}")
        print("="*80 + "\n")
    
    async def run(self, max_threads_per_forum: int = 20):
        """Ejecuta el scraping completo"""
        
        print("\n" + "="*80)
        print("🏦 SCRAPER DE OFERTAS HIPOTECARIAS")
        print("="*80)
        print("Iniciando scraping de foros españoles...\n")
        
        all_thread_urls = []
        
        # Recolectar URLs de hilos
        print("📍 Fase 1: Recolectando hilos relevantes...\n")
        
        all_thread_urls.extend(self.scrape_rankia(max_threads_per_forum))
        all_thread_urls.extend(self.scrape_bogleheads(max_threads_per_forum))
        all_thread_urls.extend(self.scrape_forocoches(max_threads_per_forum))
        
        print(f"\n✓ Total de hilos a procesar: {len(all_thread_urls)}\n")
        
        # Procesar hilos
        print("📍 Fase 2: Extrayendo ofertas con IA...\n")
        
        all_ofertas = []
        for i, url in enumerate(all_thread_urls, 1):
            print(f"[{i}/{len(all_thread_urls)}] Procesando...")
            ofertas = await self.scrape_thread(url)
            all_ofertas.extend(ofertas)
            
            # Mostrar progreso cada 10 hilos
            if i % 10 == 0:
                print(f"  → Ofertas acumuladas hasta ahora: {len(all_ofertas)}\n")
        
        # Normalizar y guardar
        print("\n📍 Fase 3: Normalizando y guardando datos...\n")
        
        df = self.normalize_data(all_ofertas)
        self.save_results(df)
        
        return df


if __name__ == '__main__':
    scraper = MortgageScraper()
    
    # Ejecutar scraping
    df = asyncio.run(scraper.run(max_threads_per_forum=200))
    
    # Mostrar muestra de resultados
    if not df.empty:
        print("\n📋 MUESTRA DE RESULTADOS (primeras 5 ofertas):\n")
        print(df.head().to_string())
