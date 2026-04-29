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

# 2. OPCIONES PARA LOS MENÚS DESPLEGABLES
opciones_tren = [
    "Comercial", "eCommerce", "Finanzas", "IT", "Nuevos Negocios", 
    "Off Price", "Omnicanalidad", "One AXO", "Operaciones", 
    "Operación en Tienda", "Palanca de Valor", "Privalia", 
    "Recursos Humanos", "Sudamérica", "Ulta"
]

opciones_director = [
    "Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", 
    "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", 
    "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"
]

opciones_rte = [
    "Baltodano Karla", "Franco Edith", "Hernandez Consuelo", 
    "Mares Mireya", "Moreno Jorge", "Navarrete Arantzasu", 
    "N/A", "Miranda Vanessa"
]

# Creamos un DataFrame inicial con 5 filas vacías
df_estructura = pd.DataFrame([[""] * len(columnas)] * 5, columns=columnas)

# 3. VISUALIZACIÓN INTERACTIVA
st.subheader("Layout de Seguimiento")

# Configuración de los editores de columna
st.data_editor(
    df_estructura,
    column_config={
        "Tren E2E": st.column_config.SelectboxColumn(
            "Tren E2E",
            help="Selecciona el Tren correspondiente",
            options=opciones_tren,
            required=True,
        ),
        "Director": st.column_config.SelectboxColumn(
            "Director",
            help="Selecciona el Director responsable",
            options=opciones_director,
            required=True,
        ),
        "RTE Nombre": st.column_config.SelectboxColumn(
            "RTE Nombre",
            help="Selecciona el RTE asignado",
            options=opciones_rte,
            required=True,
        )
    },
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic"
)

st.info("Estructura lista con validación en las primeras 3 columnas (Tren, Director y RTE).")
