import streamlit as st
import pandas as pd
import sqlite3
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF 2026 - Control Portafolio", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stTable td:nth-child(n+2), .stTable th:nth-child(n+2) { text-align: center !important; }
    .stTable td:nth-child(1), .stTable th:nth-child(1) { text-align: left !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_db(): return sqlite3.connect('otif_it_data.db')

def cargar_datos():
    conn = conectar_db()
    try:
        df = pd.read_sql_query("SELECT * FROM proyectos", conn)
        column_map = {
            "tren_e2e": "Tren E2E", "director": "Director", "rte_nombre": "RTE Nombre",
            "on_time": "On Time", "in_full": "In Full", "capex_aprob": "CAPEX Aprobado",
            "otif_x_proyecto": "OTIF X Proy"
        }
        if not df.empty:
            df.rename(columns=column_map, inplace=True)
            for col in ["CAPEX Aprobado"]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    except: df = pd.DataFrame()
    finally: conn.close()
    return df

# --- CONFIGURACIÓN DE NEGOCIO ---
# Definimos quiénes son los "Líderes de Consolidación" y quiénes les reportan
ESTRUCTURA_REPORTES = {
    "Karla Baltodano": {
        "rtes": ["Baltodano Karla", "Navarrete Arantzasu", "Moreno Jorge"]
    },
    "Mireya Mares": {
        "rtes": ["Mares Mireya", "Franco Edith", "Hernandez Consuelo"]
    },
    "Vanessa Miranda": {
        "directores": ["Rojas Juan Manuel", "Diaz de Leon Lino", "Miranda Vanessa"]
    }
}

# --- PROCESAMIENTO DE RESUMEN ---
def generar_resumen_consolidado(df_input):
    if df_input.empty:
        return pd.DataFrame(columns=["Líder / Director", "On Time (%)", "In Full (%)", "Total CAPEX", "OTIF Global (%)"])

    # 1. Lista de todos los Directores únicos presentes en la BD
    directores_unicos = df_input["Director"].unique().tolist()
    
    # 2. Lista de Líderes de Consolidación
    lideres_fijos = list(ESTRUCTURA_REPORTES.keys())
    
    # Combinamos ambas listas y quitamos los nombres que ya son "Líderes" para no duplicar filas
    nombres_maestra = sorted(list(set(directores_unicos + lideres_fijos)))
    
    filas_resumen = []

    for nombre in nombres_maestra:
        # Filtro para Directores individuales
        mask_director = (df_input["Director"] == nombre)
        
        # Filtro para Líderes (Consolidan lo propio + lo de su equipo)
        mask_lider = pd.Series([False] * len(df_input))
        if nombre in ESTRUCTURA_REPORTES:
            reglas = ESTRUCTURA_REPORTES[nombre]
            if "rtes" in reglas:
                mask_lider |= df_input["RTE Nombre"].isin(reglas["rtes"])
            if "directores" in reglas:
                mask_lider |= df_input["Director"].isin(reglas["directores"])
        
        # Combinamos: Un proyecto cuenta si el nombre es el Director O si cae en su regla de Líder
        df_filtrado = df_input[mask_director | mask_lider].drop_duplicates()

        if not df_filtrado.empty:
            ot = (df_filtrado["On Time"] == "SÍ").mean() * 100
            inf = (df_filtrado["In Full"] == "SÍ").mean() * 100
            otif = (df_filtrado["OTIF X Proy"] == "SÍ").mean() * 100
            capex = df_filtrado["CAPEX Aprobado"].sum()
            
            filas_resumen.append({
                "Líder / Director": nombre,
                "On Time (%)": ot,
                "In Full (%)": inf,
                "Total CAPEX": capex,
                "OTIF Global (%)": otif
            })
        else:
            # Si no tiene proyectos, lo mostramos en ceros para control
            filas_resumen.append({
                "Líder / Director": nombre, "On Time (%)": 0, "In Full (%)": 0, "Total CAPEX": 0, "OTIF Global (%)": 0
            })

    return pd.DataFrame(filas_resumen)

# --- INTERFAZ ---
st.title("📊 Dashboard OTIF - Portafolio 2026")

df_datos = cargar_datos()

with st.expander("📈 Resumen de Cumplimiento por Líder / Director", expanded=True):
    resumen_final = generar_resumen_consolidado(df_datos)
    
    # Mostramos la tabla con formato
    st.table(resumen_final.style.format({
        "On Time (%)": "{:.1f}%", 
        "In Full (%)": "{:.1f}%",
        "Total CAPEX": "$ {:,.2f}", 
        "OTIF Global (%)": "{:.1f}%"
    }))

# ... (El resto del código de Registro y Matriz se mantiene igual que la v6)
