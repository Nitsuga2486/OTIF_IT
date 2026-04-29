import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Estructura OTIF IT", layout="wide")

st.title("📊 Estructura de Seguimiento OTIF - Área IT")
st.markdown("---")

# 1. DEFINICIÓN DE LAS 16 COLUMNAS
columnas = [
    "Tren E2E", "Director", "RTE Nombre", "Mes de Salida", 
    "Fecha Planeada", "Fecha Real", "On Time", "In Full", 
    "CAPEX Aprobado por Finanzas", "Ejecutado CAPEX", "% Budget", 
    "On Budget", "OTIF X Proyecto", "OPEX Aprobado por Finanzas", 
    "Ejecutado OPEX", "Comentarios"
]

# 2. LISTAS DE OPCIONES
opciones_tren = ["Comercial", "eCommerce", "Finanzas", "IT", "Nuevos Negocios", "Off Price", "Omnicanalidad", "One AXO", "Operaciones", "Operación en Tienda", "Palanca de Valor", "Privalia", "Recursos Humanos", "Sudamérica", "Ulta"]
opciones_director = ["Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"]
opciones_rte = ["Baltodano Karla", "Franco Edith", "Hernandez Consuelo", "Mares Mireya", "Moreno Jorge", "Navarrete Arantzasu", "N/A", "Miranda Vanessa"]

# Diccionario para traducir meses a español
meses_espanol = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Inicializar el estado de los datos si no existe
if 'df_data' not in st.session_state:
    st.session_state.df_data = pd.DataFrame([[None] * len(columnas)] * 5, columns=columnas)

# 3. LÓGICA PARA ACTUALIZAR EL MES AUTOMÁTICAMENTE
def update_data():
    df = st.session_state.df_data
    # Si hay una Fecha Real, extraemos el mes en texto
    for i in range(len(df)):
        if pd.notnull(df.at[i, "Fecha Real"]):
            fecha = pd.to_datetime(df.at[i, "Fecha Real"])
            df.at[i, "Mes de Salida"] = meses_espanol[fecha.month]
    st.session_state.df_data = df

# 4. VISUALIZACIÓN INTERACTIVA
st.subheader("Layout de Seguimiento")

edited_df = st.data_editor(
    st.session_state.df_data,
    column_config={
        "Tren E2E": st.column_config.SelectboxColumn("Tren E2E", options=opciones_tren),
        "Director": st.column_config.SelectboxColumn("Director", options=opciones_director),
        "RTE Nombre": st.column_config.SelectboxColumn("RTE Nombre", options=opciones_rte),
        "Mes de Salida": st.column_config.TextColumn("Mes de Salida", disabled=True, help="Se autocompleta con la Fecha Real"),
        "Fecha Planeada": st.column_config.DateColumn("Fecha Planeada", format="DD-MM-YYYY"),
        "Fecha Real": st.column_config.DateColumn("Fecha Real", format="DD-MM-YYYY"),
    },
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="editor"
)

# Detectar cambios y actualizar el DataFrame en sesión
if edited_df is not None:
    st.session_state.df_data = edited_df
    update_data()
    # Forzar recarga ligera para mostrar el mes actualizado
    if st.button("Actualizar Cálculos"):
        st.rerun()

st.info("💡 Al ingresar una 'Fecha Real' y presionar el botón inferior, el 'Mes de Salida' se calculará automáticamente en texto.")
