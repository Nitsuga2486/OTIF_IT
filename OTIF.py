import streamlit as st
import pandas as pd

# Configuración de la página para aprovechar el ancho del monitor
st.set_page_config(page_title="Estructura OTIF IT", layout="wide")

st.title("📊 Estructura de Seguimiento OTIF - Área IT")
st.markdown("---")

# 1. DEFINICIÓN DE LA ESTRUCTURA (16 COLUMNAS)
# Creamos un DataFrame vacío o con una fila de ejemplo para mostrar los nombres exactos
columnas = [
    "1 Tren E2E",
    "2 Director",
    "3 RTE Nombre",
    "4 Mes de Salida",
    "5 Fecha Planeada",
    "6 Fecha Real",
    "7 On Time",
    "8 In Full",
    "9 CAPEX Aprobado por Finanzas",
    "10 Ejecutado CAPEX",
    "11 % Budget",
    "12 On Budget",
    "13 OTIF X Proyecto",
    "14 OPEX Aprobado por Finanzas",
    "15 Ejecutado OPEX",
    "16 Comentarios"
]

# Creamos un DataFrame de ejemplo vacío con la estructura solicitada
df_estructura = pd.DataFrame(columns=columnas)

# Agregamos una fila vacía para que la tabla sea visible en la web
df_estructura.loc[0] = [""] * len(columnas)

# 2. VISUALIZACIÓN EN STREAMLIT
st.subheader("Layout de las 16 Columnas")

# Mostramos la estructura
st.dataframe(
    df_estructura, 
    use_container_width=True, 
    hide_index=True
)

# 3. NOTA TÉCNICA
st.info("Esta es la estructura base solicitada. El diseño está optimizado para desplazamiento horizontal debido al número de columnas.")
