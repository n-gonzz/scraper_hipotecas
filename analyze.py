#!/usr/bin/env python3
"""
Script de análisis de datos hipotecarios extraídos
Genera estadísticas y visualizaciones básicas
"""

import pandas as pd
import os
import glob
from datetime import datetime

def find_latest_csv():
    """Encuentra el CSV más reciente en output/"""
    files = glob.glob('output/ofertas_hipotecarias_*.csv')
    if not files:
        return None
    return max(files, key=os.path.getctime)

def extract_tin_value(tin_str):
    """Extrae valor numérico del TIN"""
    import re
    try:
        match = re.search(r'(\d+[.,]\d+)', str(tin_str))
        if match:
            return float(match.group(1).replace(',', '.'))
    except:
        pass
    return None

def analyze_data(csv_path):
    """Analiza datos del CSV"""
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE OFERTAS HIPOTECARIAS")
    print("="*80)
    print(f"Archivo: {csv_path}\n")
    
    # Cargar datos
    df = pd.read_csv(csv_path)
    
    if df.empty:
        print("❌ No hay datos para analizar")
        return
    
    # ====================================
    # ESTADÍSTICAS GENERALES
    # ====================================
    
    print("📈 ESTADÍSTICAS GENERALES")
    print("-" * 80)
    print(f"Total de ofertas: {len(df)}")
    print(f"Bancos únicos: {df['banco'].nunique()}")
    print(f"Fuentes únicas: {df['url'].nunique()}")
    
    # ====================================
    # DISTRIBUCIÓN POR TIPO
    # ====================================
    
    print("\n📊 DISTRIBUCIÓN POR TIPO DE HIPOTECA")
    print("-" * 80)
    tipo_counts = df['tipo'].value_counts()
    for tipo, count in tipo_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {tipo.capitalize():12} : {count:3} ofertas ({percentage:.1f}%)")
    
    # ====================================
    # TOP BANCOS
    # ====================================
    
    print("\n🏦 TOP 10 BANCOS POR NÚMERO DE OFERTAS")
    print("-" * 80)
    banco_counts = df['banco'].value_counts().head(10)
    for i, (banco, count) in enumerate(banco_counts.items(), 1):
        print(f"  {i:2}. {banco:30} : {count} ofertas")
    
    # ====================================
    # MEJORES OFERTAS POR TIN
    # ====================================
    
    print("\n💰 TOP 10 MEJORES OFERTAS (MENOR TIN NEGOCIADO)")
    print("-" * 80)
    
    # Extraer valores numéricos de TIN
    df['tin_numerico'] = df['tin_negociado'].apply(extract_tin_value)
    
    mejores = df.dropna(subset=['tin_numerico']).nsmallest(10, 'tin_numerico')
    
    for i, row in enumerate(mejores.itertuples(), 1):
        print(f"  {i:2}. {row.banco:20} - TIN: {row.tin_negociado:10} - {row.tipo}")
        if row.condiciones and row.condiciones != 'No especificado':
            print(f"      └─ Condiciones: {row.condiciones[:60]}...")
    
    # ====================================
    # ESTADÍSTICAS DE TIN
    # ====================================
    
    if df['tin_numerico'].notna().sum() > 0:
        print("\n📊 ESTADÍSTICAS DE TIN NEGOCIADO")
        print("-" * 80)
        print(f"  Mínimo    : {df['tin_numerico'].min():.2f}%")
        print(f"  Máximo    : {df['tin_numerico'].max():.2f}%")
        print(f"  Promedio  : {df['tin_numerico'].mean():.2f}%")
        print(f"  Mediana   : {df['tin_numerico'].median():.2f}%")
    
    # ====================================
    # ANÁLISIS DE CONDICIONES
    # ====================================
    
    print("\n📋 CONDICIONES MÁS COMUNES")
    print("-" * 80)
    
    condiciones_keywords = {
        'seguro': 0,
        'nómina': 0,
        'vinculación': 0,
        'broker': 0,
        'sin condiciones': 0
    }
    
    for cond in df['condiciones']:
        cond_lower = str(cond).lower()
        if 'seguro' in cond_lower:
            condiciones_keywords['seguro'] += 1
        if 'nómina' in cond_lower or 'nomina' in cond_lower:
            condiciones_keywords['nómina'] += 1
        if 'vinculación' in cond_lower or 'vinculacion' in cond_lower:
            condiciones_keywords['vinculación'] += 1
        if 'sin condiciones' in cond_lower:
            condiciones_keywords['sin condiciones'] += 1
    
    for ctx in df['contexto']:
        ctx_lower = str(ctx).lower()
        if 'broker' in ctx_lower:
            condiciones_keywords['broker'] += 1
    
    for keyword, count in sorted(condiciones_keywords.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            percentage = (count / len(df)) * 100
            print(f"  {keyword.capitalize():20} : {count:3} ofertas ({percentage:.1f}%)")
    
    # ====================================
    # RESUMEN FINAL
    # ====================================
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)
    
    print("\n💡 INSIGHTS:")
    
    # Insight 1: Tipo más común
    tipo_popular = df['tipo'].mode()[0]
    print(f"  • El tipo más común es: {tipo_popular}")
    
    # Insight 2: Rango TIN
    if df['tin_numerico'].notna().sum() > 0:
        tin_min = df['tin_numerico'].min()
        tin_max = df['tin_numerico'].max()
        diferencia = tin_max - tin_min
        print(f"  • Rango de TIN: {tin_min:.2f}% - {tin_max:.2f}% (diferencia: {diferencia:.2f} pp)")
    
    # Insight 3: Broker
    broker_count = condiciones_keywords['broker']
    if broker_count > 0:
        broker_pct = (broker_count / len(df)) * 100
        print(f"  • {broker_pct:.1f}% de ofertas negociadas con broker")
    
    print("\n")

def generate_summary_report(csv_path, output_file='output/analisis_resumen.txt'):
    """Genera reporte de texto con resumen"""
    
    df = pd.read_csv(csv_path)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("REPORTE DE ANÁLISIS - OFERTAS HIPOTECARIAS\n")
        f.write("="*80 + "\n")
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Archivo analizado: {csv_path}\n")
        f.write(f"Total ofertas: {len(df)}\n")
        f.write("="*80 + "\n\n")
        
        f.write("TOP 10 BANCOS:\n")
        f.write("-" * 80 + "\n")
        for i, (banco, count) in enumerate(df['banco'].value_counts().head(10).items(), 1):
            f.write(f"{i:2}. {banco:30} : {count} ofertas\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("DISTRIBUCIÓN POR TIPO:\n")
        f.write("-" * 80 + "\n")
        for tipo, count in df['tipo'].value_counts().items():
            pct = (count / len(df)) * 100
            f.write(f"{tipo:12} : {count:3} ({pct:.1f}%)\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("="*80 + "\n")
    
    print(f"✅ Reporte guardado en: {output_file}\n")

def main():
    """Función principal"""
    
    # Buscar CSV más reciente
    csv_path = find_latest_csv()
    
    if not csv_path:
        print("\n❌ No se encontraron archivos CSV en output/")
        print("   Ejecuta primero: python scraper.py\n")
        return
    
    # Analizar datos
    analyze_data(csv_path)
    
    # Generar reporte
    generate_summary_report(csv_path)

if __name__ == '__main__':
    main()
