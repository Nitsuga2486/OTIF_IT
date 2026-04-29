import streamlit as st
import pandas as pd

# Configuración de la página para aprovechar el ancho del monitor
st.set_page_config(page_title="Estructura OTIF IT", layout="wide")

st.title("📊 Estructura de Seguimiento OTIF - Área IT")
st.markdown("---")

# 1. DEFINICIÓN DE LAS 16 COLUMNAS
columnas = [
    "Tren E2E",
    "Director",
    "RTE Nombre",
    "Mes de Salida",
    "Fecha Planeada",
    "Fecha Real",
    "On Time",
    "In Full",
    "CAPEX Aprobado por Finanzas",
    "Ejecutado CAPEX",
    "% Budget",
    "On Budget",
    "OTIF X Proyecto",
    "OPEX Aprobado por Finanzas",
    "Ejecutado OPEX",
    "Comentarios"
]

# 2. OPCIONES PARA EL MENÚ DESPLEGABLE (Ahora en Tren E2E)
opciones_tren = [
    "Comercial", "eCommerce", "Finanzas", "IT", "Nuevos Negocios", 
    "Off Price", "Omnicanalidad", "One AXO", "Operaciones", 
    "Operación en Tienda", "Palanca de Valor", "Privalia", 
    "Recursos Humanos", "Sudamérica", "Ulta"
]

# Creamos un DataFrame inicial con 5 filas vacías
df_estructura = pd.DataFrame([[""] * len(columnas)] * 5, columns=columnas)

# 3. VISUALIZACIÓN INTERACTIVA
st.subheader("Layout de Seguimiento")

# Configuramos la columna "Tren E2E" con el menú desplegable
st.data_editor(
    df_estructura,
    column_config={
        "Tren E2E": st.column_config.SelectboxColumn(
            "Tren E2E",
            help="Selecciona el Tren correspondiente",
            options=opciones_tren,
            required=True,
        )
    },
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic"  # Permite añadir filas con el botón "+" al final de la tabla
)

st.info("Estructura actualizada. El menú desplegable ahora se encuentra en la columna 'Tren E2E'.")
