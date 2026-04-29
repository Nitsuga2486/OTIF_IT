import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="OTIF IT - Captura Inteligente", layout="wide")

# Mapeo de dependencias (Tren -> Directores -> RTEs)
CONFIG_TRENES = {
    "Comercial": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Moreno Jorge", "Baltodano Karla"]
    },
    "eCommerce": {
        "directores": ["Muñoz Julio"],
        "rtes": ["Mares Mireya"]
    },
    "Finanzas": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Hernandez Consuelo"]
    },
    "IT": {
        "directores": ["Reyes Israel", "Lopez-Portillo Salvador"],
        "rtes": ["Moreno Jorge", "Baltodano Karla", "Navarrete Arantzasu"]
    },
    "Nuevos Negocios": {
        "directores": ["Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"],
        "rtes": ["N/A"]
    },
    "Off Price": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Franco Edith"]
    },
    "Omnicanalidad": {
        "directores": ["Muñoz Julio"],
        "rtes": ["Mares Mireya"]
    },
    "One AXO": {
        "directores": ["Diaz de Leon Lino", "Rojas Juan Manuel"],
        "rtes": ["N/A"]
    },
    "Operaciones": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Hernandez Consuelo"]
    },
    "Operación en Tienda": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Franco Edith"]
    },
    "Palanca de Valor": {
        "directores": ["Ortiz de Montellanos Enrique", "Posada Evelyn"],
        "rtes": ["Baltodano Karla"]
    },
    "Privalia": {
        "directores": ["Botello Antonio"],
        "rtes": ["Mares Mireya"]
    },
    "Recursos Humanos": {
        "directores": ["Ortiz de Montellanos Enrique"],
        "rtes": ["Hernandez Consuelo"]
    },
    "Sudamérica": {
        "directores": ["Quezada Guillermo"],
        "rtes": ["N/A"]
    },
    "Ulta": {
        "directores": ["Muñoz Julio", "Diaz de Leon Lino"],
        "rtes": ["Franco Edith"]
    }
}

meses_espanol = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

# Inicializar almacenamiento de datos
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

# 2. FORMULARIO DE CAPTURA CON REGLAS
st.title("📊 Seguimiento OTIF IT - Entrada de Datos")
with st.expander("➕ Agregar Nuevo Proyecto / Tren", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tren_sel = st.selectbox("Selecciona Tren E2E", options=list(CONFIG_TRENES.keys()))
    
    # Aquí aplicamos la regla de filtrado basada en la selección anterior
    with col2:
        dir_opciones = CONFIG_TRENES[tren_sel]["directores"]
        dir_sel = st.selectbox("Director Responsable", options=dir_opciones)
        
    with col3:
        rte_opciones = CONFIG_TRENES[tren_sel]["rtes"]
        rte_sel = st.selectbox("RTE Asignado", options=rte_opciones)

    col4, col5, col6 = st.columns(3)
    with col4:
        f_plan = st.date_input("Fecha Planeada")
    with col5:
        f_real = st.date_input("Fecha Real")
    with col6:
        in_full = st.selectbox("In Full", ["SÍ", "NO"])

    if st.button("Registrar en Tablero"):
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
            "CAPEX Aprobado por Finanzas": 0,
            "Ejecutado CAPEX": 0,
            "% Budget": "0%",
            "On Budget": "SÍ",
            "OTIF X Proyecto": otif,
            "OPEX Aprobado por Finanzas": 0,
            "Ejecutado OPEX": 0,
            "Comentarios": ""
        }
        st.session_state.proyectos.append(nuevo_registro)
        st.success("Proyecto agregado con éxito.")

# 3. TABLERO DE RESULTADOS
st.markdown("---")
st.subheader("Tablero de Seguimiento (16 Columnas)")

if st.session_state.proyectos:
    df_mostrar = pd.DataFrame(st.session_state.proyectos)
    
    # Editor para las columnas restantes (Capex, Opex, Comentarios)
    st.data_editor(
        df_mostrar,
        column_config={
            "Mes de Salida": st.column_config.TextColumn(disabled=True),
            "On Time": st.column_config.TextColumn(disabled=True),
            "OTIF X Proyecto": st.column_config.TextColumn(disabled=True),
            "% Budget": st.column_config.TextColumn(disabled=True),
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Aún no hay proyectos registrados. Utiliza el formulario superior.")
