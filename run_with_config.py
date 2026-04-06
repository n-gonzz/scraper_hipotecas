#!/usr/bin/env python3
"""
Script principal que usa config.py para configuración
"""

import asyncio
import sys
import os

# Importar configuración
from config import (
    MAX_THREADS_PER_FORUM,
    ENABLE_RANKIA,
    ENABLE_BOGLEHEADS,
    ENABLE_FOROCOCHES,
    OUTPUT_FILENAME_BASE
)

from scraper import MortgageScraper


async def main():
    """
    Ejecuta el scraper con configuración de config.py
    """
    
    print("\n" + "="*80)
    print("🏦 SCRAPER DE OFERTAS HIPOTECARIAS (CON CONFIGURACIÓN)")
    print("="*80)
    print(f"Configuración:")
    print(f"  - Hilos por foro: {MAX_THREADS_PER_FORUM}")
    print(f"  - Rankia: {'✓' if ENABLE_RANKIA else '✗'}")
    print(f"  - Bogleheads: {'✓' if ENABLE_BOGLEHEADS else '✗'}")
    print(f"  - Forocoches: {'✓' if ENABLE_FOROCOCHES else '✗'}")
    print("\nIniciando scraping...\n")
    
    scraper = MortgageScraper()
    
    # Ejecutar scraping
    df = await scraper.run(max_threads_per_forum=MAX_THREADS_PER_FORUM)
    
    # Guardar con nombre configurado
    if not df.empty:
        scraper.save_results(df, base_filename=OUTPUT_FILENAME_BASE)
    else:
        print("\n⚠️  No se encontraron ofertas.")
    
    print("\n✅ Scraping completado.\n")


if __name__ == '__main__':
    asyncio.run(main())
