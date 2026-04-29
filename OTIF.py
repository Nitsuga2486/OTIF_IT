# OTIF - On-Time In-Full Module
# This module contains functionality for OTIF tracking and analysis

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Gestión OTIF & Budget IT", layout="wide")

st.title("📊 Tablero de Control de Proyectos IT")

# 1. Carga de Datos (Simulada para el ejemplo)
@st.cache_data
def load_data():
    # En un entorno real, aquí usarías pd.read_csv('tu_archivo.csv')
    data = {
        "Tren E2E": ["Proyecto Alfa", "Proyecto Beta"],
        "Director": ["Director A", "Director B"],
        "RTE Nombre": ["RTE 1", "RTE 2"],
        "Mes de Salida": ["Enero", "Febrero"],
        "Fecha Planeada": pd.to_datetime(["2026-01-15", "2026-02-20"]),
        "Fecha Real": pd.to_datetime(["2026-01-14", "2026-02-25"]),
        "In Full": ["SÍ", "NO"],
        "CAPEX Aprobado": [100000, 250000],
        "Ejecutado CAPEX": [95000, 260000],
        "OPEX Aprobado": [20000, 50000],
        "Ejecutado OPEX": [18000, 45000],
        "Comentarios": ["En tiempo", "Retraso por proveedores"]
    }
    df = pd.DataFrame(data)
    
    # --- CÁLCULOS AUTOMÁTICOS ---
    # 7. On Time
    df['On Time'] = np.where(df['Fecha Real'] <= df['Fecha Planeada'], "SÍ", "NO")
    
    # 11. % Budget
    df['Total Aprobado'] = df['CAPEX Aprobado'] + df['OPEX Aprobado']
    df['Total Ejecutado'] = df['Ejecutado CAPEX'] + df['Ejecutado OPEX']
    df['% Budget'] = (df['Total Ejecutado'] / df['Total Aprobado']) * 100
    
    # 12. On Budget
    df['On Budget'] = np.where(df['Total Ejecutado'] <= df['Total Aprobado'], "SÍ", "NO")
    
    # 13. OTIF X Proyecto
    df['OTIF X Proyecto'] = np.where((df['On Time'] == "SÍ") & (df['In Full'] == "SÍ"), "SÍ", "NO")
    
    # Reordenar columnas según tu diseño
    columnas_orden = [
        "Tren E2E", "Director", "RTE Nombre", "Mes de Salida", "Fecha Planeada", 
        "Fecha Real", "On Time", "In Full", "CAPEX Aprobado", "Ejecutado CAPEX", 
        "% Budget", "On Budget", "OTIF X Proyecto", "OPEX Aprobado", 
        "Ejecutado OPEX", "Comentarios"
    ]
    return df[columnas_orden]

df = load_data()

# 2. Visualización de Métricas Clave
total_otif = (df['OTIF X Proyecto'] == "SÍ").sum() / len(df) * 100
total_budget = (df['On Budget'] == "SÍ").sum() / len(df) * 100

m1, m2, m3 = st.columns(3)
m1.metric("OTIF Global", f"{total_otif:.1f}%")
m2.metric("Cumplimiento Presupuesto", f"{total_budget:.1f}%")
m3.metric("Proyectos Activos", len(df))

st.markdown("---")

# 3. Tabla Interactiva
st.subheader("Detalle de las 16 Columnas de Seguimiento")

# Formateo para resaltar SÍ/NO
def color_si_no(val):
    color = '#d4edda' if val == "SÍ" else '#f8d7da' if val == "NO" else None
    return f'background-color: {color}'

st.dataframe(df.style.applymap(color_si_no, subset=['On Time', 'In Full', 'On Budget', 'OTIF X Proyecto']))
