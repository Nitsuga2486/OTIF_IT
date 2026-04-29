import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF IT - Seguimiento", layout="wide")

# Mapeo de dependencias corregido
CONFIG_TRENES = {
    "Comercial": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Hernandez Consuelo", "Mares Mireya"]
    },
    "eCommerce": {
        "directores": ["Muñoz Julio"],
        "rtes": ["Baltodano Karla"]
    },
    "Finanzas": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Franco Edith"]
    },
    "IT": {
        "directores": ["Reyes Israel", "Lopez-Portillo Salvador"],
        "rtes": ["Moreno Jorge", "Baltodano Karla", "Navarrete Arantzasu"]
    },
    "Nuevos Negocios": {
        "directores": [
            "Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", 
            "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", 
            "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"
        ],
        "rtes": ["N/A", "Franco Edith", "Hernandez Consuelo", "Navarrete Arantzasu", "Mares Mireya", "Baltodano Karla", "Moreno Jorge"]
    },
    "Off Price": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Franco Edith", "Mares Mireya"]
    },
    "Omnicanalidad": {
        "directores": ["Muñoz Julio"],
        "rtes": ["Baltodano Karla", "Navarrete Arantzasu"]
    },
    "One AXO": {
        "directores": ["Diaz de Leon Lino", "Rojas Juan Manuel"],
        "rtes": ["N/A", "Miranda Vanessa"]
    },
    "Operaciones": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Hernandez Consuelo"]
    },
    "Operación en Tienda": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Hernandez Consuelo", "Franco Edith"]
    },
    "Palanca de Valor": {
        "directores": ["Ortiz de Montellanos Enrique", "Posada Evelyn"],
        "rtes": ["Baltodano Karla", "Moreno Jorge", "N/A"]
    },
    "Privalia": {
        "directores": ["Botello Antonio"],
        "rtes": ["N/A"]
    },
    "Recursos Humanos": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Baltodano Karla"]
    },
    "Sudamérica": {
        "directores": ["Quezada Guillermo"],
        "rtes": ["N/A"]
    },
    "Ulta": {
        "directores": ["Muñoz Julio", "Diaz de Leon Lino"],
        "rtes": ["Navarrete Arantzasu", "N/A"]
    }
}

meses_espanol = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Inicializar almacenamiento de datos en la sesión
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

# 2. INTERFAZ DE USUARIO
st.title("📊 Seguimiento OTIF IT")
st.markdown("---")

# Formulario de entrada
with st.expander("➕ Registrar Nuevo Proyecto / Tren", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tren_sel = st.selectbox("Tren E2E", options=list(CONFIG_TRENES.keys()))
    
    with col2:
        # Regla: Solo directores del tren seleccionado
        dir_opciones = CONFIG_TRENES[tren_sel]["directores"]
        dir_sel = st.selectbox("Director", options=dir_opciones)
        
    with col3:
        # Regla: Solo RTEs del tren seleccionado
        rte_opciones = CONFIG_TRENES[tren_sel]["rtes"]
        rte_sel = st.selectbox("RTE Nombre", options=rte_opciones)

    col4, col5, col6, col7 = st.columns(4)
    with col4:
        f_plan = st.date_input("Fecha Planeada", format="DD/MM/YYYY")
    with col5:
        f_real = st.date_input("Fecha Real", format="DD/MM/YYYY")
    with col6:
        in_full = st.selectbox("In Full", ["SÍ", "NO"])
    with col7:
        comentarios = st.text_input("Comentarios")

    if st.button("Registrar en Tablero"):
        # Cálculos Automáticos
        mes_txt = meses_espanol[f_real.month]
        on_time = "SÍ" if f_real <= f_plan else "NO"
        otif = "SÍ" if (on_time == "SÍ" and in_full == "SÍ") else "NO"
        
        nuevo_registro = {
            "Tren E2E": tren_sel,
            "Director": dir_sel,
            "RTE Nombre": rte_sel,
            "Mes de Salida": mes_txt,
            "Fecha Planeada": f_plan,
            "Fecha Real": f_real,
            "On Time": on_time,
            "In Full": in_full,
            "CAPEX Aprobado por Finanzas": 0.0,
            "Ejecutado CAPEX": 0.0,
            "% Budget": "0%",
            "On Budget": "SÍ",
            "OTIF X Proyecto": otif,
            "OPEX Aprobado por Finanzas": 0.0,
            "Ejecutado OPEX": 0.0,
            "Comentarios": comentarios
        }
        st.session_state.proyectos.append(nuevo_registro)
        st.rerun()

# 3. VISUALIZACIÓN DEL TABLERO
st.subheader("Tablero de Control (16 Columnas)")

if st.session_state.proyectos:
    df_mostrar = pd.DataFrame(st.session_state.proyectos)
    
    # Configuración de visualización y edición de montos
    st.data_editor(
        df_mostrar,
        column_config={
            "Mes de Salida": st.column_config.TextColumn(disabled=True),
            "On Time": st.column_config.TextColumn(disabled=True),
            "OTIF X Proyecto": st.column_config.TextColumn(disabled=True),
            "Fecha Planeada": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Fecha Real": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "CAPEX Aprobado por Finanzas": st.column_config.NumberColumn(format="$%.2f"),
            "Ejecutado CAPEX": st.column_config.NumberColumn(format="$%.2f"),
            "OPEX Aprobado por Finanzas": st.column_config.NumberColumn(format="$%.2f"),
            "Ejecutado OPEX": st.column_config.NumberColumn(format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True,
        key="main_table"
    )
    
    if st.button("Limpiar Tablero"):
        st.session_state.proyectos = []
        st.rerun()
else:
    st.info("No hay registros. Completa el formulario superior para empezar.")
