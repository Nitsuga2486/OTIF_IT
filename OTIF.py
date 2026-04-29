import streamlit as st
import pandas as pd
import sqlite3
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF IT - Seguimiento", layout="wide")

# --- FUNCIONES DE PERSISTENCIA ---
def conectar_db():
    return sqlite3.connect('otif_it_data.db')

def crear_tabla():
    conn = conectar_db()
    c = conn.cursor()
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
    df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    conn.close()
    return df

def eliminar_registros(ids):
    conn = conectar_db()
    c = conn.cursor()
    # Eliminación múltiple mediante tupla de IDs
    c.execute(f"DELETE FROM proyectos WHERE id IN ({','.join(['?']*len(ids))})", ids)
    conn.commit()
    conn.close()

# Inicializar
crear_tabla()

# --- LÓGICA DE NEGOCIO (CONFIG_TRENES y meses_espanol omitidos aquí para brevedad, mantener los de tu código) ---
# [Insertar aquí tus diccionarios CONFIG_TRENES y meses_espanol]

def clean_numeric(value):
    if not value: return 0.0
    clean_val = re.sub(r'[^\d.]', '', value)
    try: return float(clean_val)
    except: return 0.0

# --- INTERFAZ ---
st.title("📊 Seguimiento OTIF IT")

# Formulario de registro (Expander cerrado por defecto para dar prioridad al tablero)
with st.expander("➕ Registrar Nuevo Proyecto", expanded=False):
    # [Insertar aquí tus columnas de registro c1..c8 y f1..f4]
    # Al final del botón de guardado, usar guardar_registro() y st.rerun()
    pass

# --- TABLERO DE CONTROL CON SELECCIÓN ---
st.subheader("Tablero de Control Histórico")
df_mostrar = cargar_datos()

if not df_mostrar.empty:
    # Agregamos una columna de selección al DataFrame
    df_con_check = df_mostrar.copy()
    df_con_check.insert(0, "Seleccionar", False)
    
    # Editor de datos con checkbox
    res_edicion = st.data_editor(
        df_con_check.drop(columns=['id']), 
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(
                "Eliminar?",
                help="Marca para seleccionar registros",
                default=False,
            ),
            "CAPEX Aprobado por Finanzas": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado CAPEX": st.column_config.NumberColumn(format="$ %,.2f"),
            "OPEX Aprobado por Finanzas": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado OPEX": st.column_config.NumberColumn(format="$ %,.2f"),
        },
        disabled=[col for col in df_con_check.columns if col != "Seleccionar"],
        use_container_width=True,
        hide_index=True,
        key="editor_proyectos"
    )

    # Lógica de eliminación basada en los checks
    # Identificamos qué filas fueron marcadas comparando el editor con el DF original
    indices_marcados = res_edicion[res_edicion["Seleccionar"] == True].index
    ids_a_eliminar = df_mostrar.iloc[indices_marcados]["id"].tolist()

    col_del1, col_del2 = st.columns([1, 4])
    with col_del1:
        if st.button(f"🗑️ Eliminar ({len(ids_a_eliminar)})", type="primary", disabled=len(ids_a_eliminar)==0):
            eliminar_registros(ids_a_eliminar)
            st.success("Registros eliminados")
            st.rerun()
            
    with col_del2:
        csv = df_mostrar.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte CSV", data=csv, file_name="Reporte_OTIF.csv", mime="text/csv")
else:
    st.info("No hay proyectos en la base de datos.")
