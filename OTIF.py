import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Estructura OTIF IT", layout="wide")

st.title("📊 Estructura de Seguimiento OTIF - Área IT")
st.markdown("---")

# 1. MAPEADO DE TRENES Y DIRECTORES
mapa_responsables = {
    "Comercial": ["Ortiz de Montellanos Enrique"],
    "eCommerce": ["Muñoz Julio"],
    "Finanzas": ["Ortiz de Montellanos Enrique"],
    "IT": ["Reyes Israel", "Lopez-Portillo Salvador"],
    "Nuevos Negocios": ["Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"],
    "Off Price": ["Ortiz de Montellanos Enrique"],
    "Omnicanalidad": ["Muñoz Julio"],
    "One AXO": ["Diaz de Leon Lino", "Rojas Juan Manuel"],
    "Operaciones": ["Ortiz de Montellanos Enrique"],
    "Operación en Tienda": ["Ortiz de Montellanos Enrique"],
    "Palanca de Valor": ["Ortiz de Montellanos Enrique", "Posada Evelyn"],
    "Privalia": ["Botello Antonio"],
    "Recursos Humanos": ["Ortiz de Montellanos Enrique"],
    "Sudamérica": ["Quezada Guillermo"],
    "Ulta": ["Muñoz Julio", "Diaz de Leon Lino"]
}

# 2. DEFINICIÓN DE LAS 16 COLUMNAS
columnas = [
    "Tren E2E", "Director", "RTE Nombre", "Mes de Salida", 
    "Fecha Planeada", "Fecha Real", "On Time", "In Full", 
    "CAPEX Aprobado por Finanzas", "Ejecutado CAPEX", "% Budget", 
    "On Budget", "OTIF X Proyecto", "OPEX Aprobado por Finanzas", 
    "Ejecutado OPEX", "Comentarios"
]

opciones_rte = ["Baltodano Karla", "Franco Edith", "Hernandez Consuelo", "Mares Mireya", "Moreno Jorge", "Navarrete Arantzasu", "N/A", "Miranda Vanessa"]

meses_espanol = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# 3. INICIALIZACIÓN DEL ESTADO
if 'df_data' not in st.session_state:
    df_init = pd.DataFrame([[None] * len(columnas)] * 5, columns=columnas)
    df_init['Fecha Planeada'] = pd.to_datetime(df_init['Fecha Planeada'])
    df_init['Fecha Real'] = pd.to_datetime(df_init['Fecha Real'])
    st.session_state.df_data = df_init

# 4. VISUALIZACIÓN INTERACTIVA
st.subheader("Layout de Seguimiento")

edited_df = st.data_editor(
    st.session_state.df_data,
    column_config={
        "Tren E2E": st.column_config.SelectboxColumn("Tren E2E", options=list(mapa_responsables.keys())),
        "Director": st.column_config.SelectboxColumn("Director", options=opciones_director_global := [
            "Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", 
            "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", 
            "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"
        ]),
        "RTE Nombre": st.column_config.SelectboxColumn("RTE Nombre", options=opciones_rte),
        "Mes de Salida": st.column_config.TextColumn("Mes de Salida", disabled=True),
        "Fecha Planeada": st.column_config.DateColumn("Fecha Planeada", format="DD/MM/YYYY"),
        "Fecha Real": st.column_config.DateColumn("Fecha Real", format="DD/MM/YYYY"),
    },
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="editor_it"
)

# 5. LÓGICA DE ACTUALIZACIÓN AUTOMÁTICA (MES Y FILTRADO)
if edited_df is not None:
    # Asegurar que las fechas sean tratadas como datetime
    edited_df['Fecha Real'] = pd.to_datetime(edited_df['Fecha Real'])
    
    # Actualizar Mes de Salida
    new_meses = edited_df['Fecha Real'].apply(lambda x: meses_espanol.get(x.month, "") if pd.notnull(x) else "")
    
    # Validar que el Director seleccionado sea coherente con el Tren (Opcional, informativo)
    # Por ahora, nos aseguramos de que el Mes de Salida se refleje.
    if not edited_df['Mes de Salida'].equals(new_meses):
        edited_df['Mes de Salida'] = new_meses
        st.session_state.df_data = edited_df
        st.rerun()

st.info("💡 La columna 'Mes de Salida' se calcula automáticamente al elegir una 'Fecha Real'.")
