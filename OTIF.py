import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF IT - Seguimiento", layout="wide")

# Mapeo de dependencias
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

if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

# 2. INTERFAZ DE USUARIO
st.title("📊 Seguimiento OTIF IT")
st.markdown("---")

with st.expander("➕ Registrar Nuevo Proyecto", expanded=True):
    # Fila 1: Identificación
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        nombre_proyecto = st.text_input("Nombre del Proyecto (Tren E2E)")
    with c2:
        tren_tipo = st.selectbox("Clasificación Tren", options=list(CONFIG_TRENES.keys()))
    with c3:
        dir_sel = st.selectbox("Director", options=CONFIG_TRENES[tren_tipo]["directores"])
    with c4:
        rte_sel = st.selectbox("RTE Responsable", options=CONFIG_TRENES[tren_tipo]["rtes"])

    # Fila 2: Fechas y OTIF
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        f_plan = st.date_input("Fecha Planeada", format="DD/MM/YYYY")
    with c6:
        f_real = st.date_input("Fecha Real", format="DD/MM/YYYY")
    with c7:
        in_full = st.selectbox("In Full", ["SÍ", "NO"])
    with c8:
        comentarios = st.text_input("Comentarios")

    # Fila 3: Finanzas (CAPEX y OPEX)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        capex_aprob = st.number_input("CAPEX Aprobado Finanzas", min_value=0.0, format="%.2f")
    with f2:
        capex_ejec = st.number_input("Ejecutado CAPEX", min_value=0.0, format="%.2f")
    with f3:
        opex_aprob = st.number_input("OPEX Aprobado Finanzas", min_value=0.0, format="%.2f")
    with f4:
        opex_ejec = st.number_input("Ejecutado OPEX", min_value=0.0, format="%.2f")

    if st.button("Registrar en Tablero"):
        # Cálculos automáticos
        mes_txt = meses_espanol[f_real.month]
        on_time = "SÍ" if f_real <= f_plan else "NO"
        otif = "SÍ" if (on_time == "SÍ" and in_full == "SÍ") else "NO"
        
        # Cálculo de presupuesto global
        total_aprob = capex_aprob + opex_aprob
        total_ejec = capex_ejec + opex_ejec
        pct_budget = (total_ejec / total_aprob * 100) if total_aprob > 0 else 0
        on_budget = "SÍ" if total_ejec <= total_aprob else "NO"
        
        nuevo_registro = {
            "Tren E2E": nombre_proyecto,
            "Director": dir_sel,
            "RTE Nombre": rte_sel,
            "Mes de Salida": mes_txt,
            "Fecha Planeada": f_plan,
            "Fecha Real": f_real,
            "On Time": on_time,
            "In Full": in_full,
            "CAPEX Aprobado por Finanzas": capex_aprob,
            "Ejecutado CAPEX": capex_ejec,
            "% Budget": f"{pct_budget:.1f}%",
            "On Budget": on_budget,
            "OTIF X Proyecto": otif,
            "OPEX Aprobado por Finanzas": opex_aprob,
            "Ejecutado OPEX": opex_ejec,
            "Comentarios": comentarios
        }
        st.session_state.proyectos.append(nuevo_registro)
        st.rerun()

# 3. TABLERO
st.subheader("Tablero de Control (16 Columnas)")

if st.session_state.proyectos:
    df_mostrar = pd.DataFrame(st.session_state.proyectos)
    st.data_editor(
        df_mostrar,
        column_config={
            "Mes de Salida": st.column_config.TextColumn(disabled=True),
            "On Time": st.column_config.TextColumn(disabled=True),
            "On Budget": st.column_config.TextColumn(disabled=True),
            "OTIF X Proyecto": st.column_config.TextColumn(disabled=True),
            "% Budget": st.column_config.TextColumn(disabled=True),
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
