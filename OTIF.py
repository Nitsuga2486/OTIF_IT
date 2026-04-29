import streamlit as st
import pandas as pd
import sqlite3
import re
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF IT - Seguimiento", layout="wide")

# --- FUNCIONES DE PERSISTENCIA (SQLite) ---
def conectar_db():
    # Se conecta al archivo .db en la misma carpeta
    return sqlite3.connect('otif_it_data.db')

def crear_tabla():
    conn = conectar_db()
    c = conn.cursor()
    # Creamos la estructura basada en tus 16 columnas
    c.execute('''CREATE TABLE IF NOT EXISTS proyectos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tren_e2e TEXT, director TEXT, rte_nombre TEXT, mes_salida TEXT,
                  fecha_plan TEXT, fecha_real TEXT, on_time TEXT, in_full TEXT,
                  capex_aprob REAL, capex_ejec REAL, pct_budget TEXT, on_budget TEXT,
                  otif_proyecto TEXT, opex_aprob REAL, opex_ejec REAL, comentarios TEXT)''')
    conn.commit()
    conn.close()

def guardar_registro(d):
    conn = conectar_db()
    c = conn.cursor()
    query = '''INSERT INTO proyectos (tren_e2e, director, rte_nombre, mes_salida, fecha_plan, fecha_real, 
               on_time, in_full, capex_aprob, capex_ejec, pct_budget, on_budget, otif_proyecto, 
               opex_aprob, opex_ejec, comentarios) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    c.execute(query, (
        d["Tren E2E"], d["Director"], d["RTE Nombre"], d["Mes de Salida"],
        str(d["Fecha Planeada"]), str(d["Fecha Real"]), d["On Time"], d["In Full"],
        d["CAPEX Aprobado por Finanzas"], d["Ejecutado CAPEX"], d["% Budget"], d["On Budget"],
        d["OTIF X Proyecto"], d["OPEX Aprobado por Finanzas"], d["Ejecutado OPEX"], d["Comentarios"]
    ))
    conn.commit()
    conn.close()

def cargar_datos():
    conn = conectar_db()
    try:
        df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# Inicializar DB
crear_tabla()

# --- CONFIGURACIÓN DE NEGOCIO ---
CONFIG_TRENES = {
    "Comercial": {"directores": ["Ortiz de Montellanos Enrique"], "rtes": ["Hernandez Consuelo", "Mares Mireya"]},
    "eCommerce": {"directores": ["Muñoz Julio"], "rtes": ["Baltodano Karla"]},
    "Finanzas": {"directores": ["Ortiz de Montellanos Enrique"], "rtes": ["Franco Edith"]},
    "IT": {"directores": ["Reyes Israel", "Lopez-Portillo Salvador"], "rtes": ["Moreno Jorge", "Baltodano Karla", "Navarrete Arantzasu"]},
    "Nuevos Negocios": {
        "directores": ["Botello Antonio", "Diaz de Leon Lino", "Lopez-Portillo Salvador", "Miranda Vanessa", "Muñoz Julio", "Ortiz de Montellanos Enrique", "Posada Evelyn", "Quezada Guillermo", "Rojas Juan Manuel", "Reyes Israel"],
        "rtes": ["N/A", "Franco Edith", "Hernandez Consuelo", "Navarrete Arantzasu", "Mares Mireya", "Baltodano Karla", "Moreno Jorge"]
    },
    "Off Price": {"directores": ["Ortiz de Montellanos Enrique"], "rtes": ["Franco Edith", "Mares Mireya"]},
    "Omnicanalidad": {"directores": ["Muñoz Julio"], "rtes": ["Baltodano Karla", "Navarrete Arantzasu"]},
    "One AXO": {"directores": ["Diaz de Leon Lino", "Rojas Juan Manuel"], "rtes": ["N/A", "Miranda Vanessa"]},
    "Operaciones": {"directores": ["Ortiz de Montellanos Enrique"], "rtes": ["Hernandez Consuelo"]},
    "Operación en Tienda": {"directores": ["Ortiz de Montellanos Enrique"], "rtes": ["Hernandez Consuelo", "Franco Edith"]},
    "Palanca de Valor": {"directores": ["Ortiz de Montellanos Enrique", "Posada Evelyn"], "rtes": ["Baltodano Karla", "Moreno Jorge", "N/A"]},
    "Privalia": {"directores": ["Botello Antonio"], "rtes": ["N/A"]},
    "Recursos Humanos": {"directores": ["Ortiz de Montellanos Enrique"], "rtes": ["Baltodano Karla"]},
    "Sudamérica": {"directores": ["Quezada Guillermo"], "rtes": ["N/A"]},
    "Ulta": {"directores": ["Muñoz Julio", "Diaz de Leon Lino"], "rtes": ["Navarrete Arantzasu", "N/A"]}
}

meses_espanol = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def clean_numeric(value):
    if not value: return 0.0
    clean_val = re.sub(r'[^\d.]', '', value)
    try: return float(clean_val)
    except: return 0.0

# 2. INTERFAZ DE USUARIO
st.title("📊 Seguimiento OTIF IT")
st.markdown("---")

with st.expander("➕ Registrar Nuevo Proyecto", expanded=True):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: nombre_proyecto = st.text_input("Nombre del Proyecto (Tren E2E)")
    with c2: tren_tipo = st.selectbox("Clasificación Tren", options=list(CONFIG_TRENES.keys()))
    with c3: dir_sel = st.selectbox("Director", options=CONFIG_TRENES[tren_tipo]["directores"])
    with c4: rte_sel = st.selectbox("RTE Responsable", options=CONFIG_TRENES[tren_tipo]["rtes"])

    c5, c6, c7, c8 = st.columns(4)
    with c5: f_plan = st.date_input("Fecha Planeada", format="DD/MM/YYYY")
    with c6: f_real = st.date_input("Fecha Real", format="DD/MM/YYYY")
    with c7: in_full = st.selectbox("In Full", ["SÍ", "NO"])
    with c8: comentarios = st.text_input("Comentarios")

    st.markdown("### Presupuesto (Moneda Nacional)")
    f1, f2, f3, f4 = st.columns(4)
    with f1: t_capex_aprob = st.text_input("CAPEX Aprobado Finanzas", value="0.00")
    with f2: t_capex_ejec = st.text_input("Ejecutado CAPEX", value="0.00")
    with f3: t_opex_aprob = st.text_input("OPEX Aprobado Finanzas", value="0.00")
    with f4: t_opex_ejec = st.text_input("Ejecutado OPEX", value="0.00")

    if st.button("💾 Guardar en Base de Datos"):
        c_aprob, c_ejec = clean_numeric(t_capex_aprob), clean_numeric(t_capex_ejec)
        o_aprob, o_ejec = clean_numeric(t_opex_aprob), clean_numeric(t_opex_ejec)

        mes_txt = meses_espanol[f_real.month]
        on_time = "SÍ" if f_real <= f_plan else "NO"
        otif = "SÍ" if (on_time == "SÍ" and in_full == "SÍ") else "NO"
        
        t_aprob, t_ejec = c_aprob + o_aprob, c_ejec + o_ejec
        pct_b = f"{(t_ejec / t_aprob * 100):.1f}%" if t_aprob > 0 else "0.0%"
        on_b = "SÍ" if t_ejec <= t_aprob else "NO"
        
        nuevo_registro = {
            "Tren E2E": nombre_proyecto, "Director": dir_sel, "RTE Nombre": rte_sel,
            "Mes de Salida": mes_txt, "Fecha Planeada": f_plan, "Fecha Real": f_real,
            "On Time": on_time, "In Full": in_full,
            "CAPEX Aprobado por Finanzas": c_aprob, "Ejecutado CAPEX": c_ejec,
            "% Budget": pct_b, "On Budget": on_b, "OTIF X Proyecto": otif,
            "OPEX Aprobado por Finanzas": o_aprob, "Ejecutado OPEX": o_ejec,
            "Comentarios": comentarios
        }
        guardar_registro(nuevo_registro)
        st.success("✅ Registro guardado exitosamente.")
        st.rerun()

# 3. TABLERO DE CONTROL (Desde DB)
st.subheader("Tablero de Control Histórico")
df_mostrar = cargar_datos()

if not df_mostrar.empty:
    st.data_editor(
        df_mostrar.drop(columns=['id']),
        column_config={
            "Fecha Planeada": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Fecha Real": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "CAPEX Aprobado por Finanzas": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado CAPEX": st.column_config.NumberColumn(format="$ %,.2f"),
            "OPEX Aprobado por Finanzas": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado OPEX": st.column_config.NumberColumn(format="$ %,.2f"),
        },
        use_container_width=True, hide_index=True
    )
    
    # Opción de descarga
    csv = df_mostrar.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte CSV", data=csv, file_name="Reporte_OTIF.csv", mime="text/csv")
else:
    st.info("No hay proyectos en la base de datos.")
