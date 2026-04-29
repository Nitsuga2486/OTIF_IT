import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Dashboard OTIF IT - Seguimiento", layout="wide")

st.title("📊 Dashboard de Seguimiento OTIF - Área IT")
st.markdown("---")

# 1. Función para cargar y procesar datos
@st.cache_data
def load_data():
    try:
        # Carga el archivo CSV (Asegúrate de que este archivo esté en tu repositorio)
        df = pd.read_csv('datos_otif_it.csv')
        
        # Convertir fechas a formato datetime
        df['Fecha Planeada'] = pd.to_datetime(df['Fecha Planeada'])
        df['Fecha Real'] = pd.to_datetime(df['Fecha Real'])
        
        # --- CÁLCULOS AUTOMÁTICOS ---
        
        # 7. On Time: Compara Fecha Real vs Fecha Planeada
        df['On Time'] = np.where(df['Fecha Real'] <= df['Fecha Planeada'], "SÍ", "NO")
        
        # 11. % Budget: (Ejecutado Total / Aprobado Total)
        total_aprobado = df['CAPEX Aprobado por Finanzas'] + df['OPEX Aprobado por Finanzas']
        total_ejecutado = df['Ejecutado CAPEX'] + df['Ejecutado OPEX']
        df['% Budget'] = (total_ejecutado / total_aprobado) * 100
        
        # 12. On Budget: Si lo ejecutado es menor o igual a lo aprobado
        df['On Budget'] = np.where(total_ejecutado <= total_aprobado, "SÍ", "NO")
        
        # 13. OTIF X Proyecto: Debe cumplir On Time (7) e In Full (8)
        # Nota: In Full debe ser una columna 'SÍ'/'NO' en tu CSV manual
        df['OTIF X Proyecto'] = np.where((df['On Time'] == "SÍ") & (df['In Full'] == "SÍ"), "SÍ", "NO")
        
        # Reordenar y asegurar las 16 columnas
        columnas_finales = [
            "Tren E2E", "Director", "RTE Nombre", "Mes de Salida", 
            "Fecha Planeada", "Fecha Real", "On Time", "In Full", 
            "CAPEX Aprobado por Finanzas", "Ejecutado CAPEX", "% Budget", 
            "On Budget", "OTIF X Proyecto", "OPEX Aprobado por Finanzas", 
            "Ejecutado OPEX", "Comentarios"
        ]
        
        return df[columnas_finales]
    except FileNotFoundError:
        return None

# Intentar cargar los datos
df = load_data()

if df is not None:
    # 2. KPIs Principales en la parte superior
    c1, c2, c3, c4 = st.columns(4)
    
    # Cálculos para métricas
    otif_global = (df['OTIF X Proyecto'] == "SÍ").mean() * 100
    on_time_global = (df['On Time'] == "SÍ").mean() * 100
    on_budget_global = (df['On Budget'] == "SÍ").mean() * 100
    
    c1.metric("OTIF Global", f"{otif_global:.1f}%")
    c2.metric("SLA (On-Time)", f"{on_time_global:.1f}%")
    c3.metric("On Budget", f"{on_budget_global:.1f}%")
    c4.metric("Proyectos Totales", len(df))

    st.markdown("### Detalle de Proyectos (16 Columnas)")

    # 3. Función de Estilo (Corrección de .map)
    def color_si_no(val):
        if val == "SÍ":
            return 'background-color: #d4edda; color: #155724' # Verde
        elif val == "NO":
            return 'background-color: #f8d7da; color: #721c24' # Rojo
        return None

    # Mostrar tabla interactiva
    st.dataframe(
        df.style.map(color_si_no, subset=['On Time', 'In Full', 'On Budget', 'OTIF X Proyecto'])
        .format({"% Budget": "{:.1f}%"}),
        use_container_width=True
    )
    
    # 4. Filtros en la barra lateral
    st.sidebar.header("Filtros")
    director_select = st.sidebar.multiselect("Filtrar por Director", options=df["Director"].unique())
    mes_select = st.sidebar.multiselect("Filtrar por Mes", options=df["Mes de Salida"].unique())
    
else:
    st.error("No se encontró el archivo 'datos_otif_it.csv'. Por favor súbelo a tu repositorio.")
