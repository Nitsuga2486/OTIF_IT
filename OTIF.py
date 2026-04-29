import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Estructura OTIF IT", layout="wide")

st.title("📊 Estructura de Seguimiento OTIF - Área IT")
st.markdown("---")

# 1. DEFINICIÓN DE OPCIONES (Fuera del editor para evitar SyntaxError)
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

meses_espanol = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# 2. DEFINICIÓN DE LAS 16 COLUMNAS
columnas = [
    "Tren E2E", "Director", "RTE Nombre", "Mes de Salida", 
    "Fecha Planeada", "Fecha Real", "On Time", "In Full", 
    "CAPEX Aprobado por Finanzas", "Ejecutado CAPEX", "% Budget", 
    "On Budget", "OTIF X Proyecto", "OPEX Aprobado por Finanzas", 
    "Ejecutado OPEX", "Comentarios"
]

# 3. INICIALIZACIÓN DEL ESTADO
if 'df_data' not in st.session_state:
    df_init = pd.DataFrame([[None] * len(columnas)] * 5, columns=columnas)
    # Forzar tipos datetime para evitar errores de validación
    df_init['Fecha Planeada'] = pd.to_datetime(df_init['Fecha Planeada'])
    df_init['Fecha Real'] = pd.to_datetime(df_init['Fecha Real'])
    st.session_state.df_data = df_init

# 4. VISUALIZACIÓN INTERACTIVA
st.subheader("Layout de Seguimiento")

edited_df = st.data_editor(
    st.session_state.df_data,
    column_config={
        "Tren E2E": st.column_config.SelectboxColumn("Tren E2E", options=opciones_tren),
        "Director": st.column_config.SelectboxColumn("Director", options=opciones_director),
        "RTE Nombre": st.column_config.SelectboxColumn("RTE Nombre", options=opciones_rte),
        "Mes de Salida": st.column_config.TextColumn("Mes de Salida", disabled=True),
        "Fecha Planeada": st.column_config.DateColumn("Fecha Planeada", format="DD/MM/YYYY"),
        "Fecha Real": st.column_config.DateColumn("Fecha Real", format="DD/MM/YYYY"),
    },
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="editor_otif_final"
)

# 5. LÓGICA DE PROCESAMIENTO
if edited_df is not None:
    # Asegurar que la columna Fecha Real sea datetime
    edited_df['Fecha Real'] = pd.to_datetime(edited_df['Fecha Real'])
    
    # Calcular el nombre del mes
    def calcular_mes(fecha):
        if pd.notnull(fecha):
            return meses_espanol.get(fecha.month, "")
        return ""

    nuevos_meses = edited_df['Fecha Real'].apply(calcular_mes)
    
    # Solo actualizamos el estado si hubo un cambio real en el Mes de Salida
    if not (edited_df['Mes de Salida'].fillna("") == nuevos_meses.fillna("")).all():
        edited_df['Mes de Salida'] = nuevos_meses
        st.session_state.df_data = edited_df
        st.rerun()

st.info("📅 El 'Mes de Salida' se actualiza automáticamente al seleccionar una 'Fecha Real'.")
