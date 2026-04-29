import streamlit as st
import pandas as pd
import sqlite3
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF 2026 Ongoing", layout="wide")

# --- FUNCIONES DE PERSISTENCIA ---
def conectar_db():
    return sqlite3.connect('otif_it_data.db')

def crear_tabla():
    conn = conectar_db()
    c = conn.cursor()
    # Definimos exactamente 16 columnas de datos + 1 id autoincremental
    c.execute('''CREATE TABLE IF NOT EXISTS proyectos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tren_e2e TEXT, director TEXT, rte_nombre TEXT, mes_salida TEXT,
                  fecha_plan TEXT, fecha_real TEXT, on_time TEXT, in_full TEXT,
                  capex_aprob REAL, capex_ejec REAL, pct_budget TEXT, on_budget TEXT,
                  otif_x_proyecto TEXT, opex_aprob REAL, opex_ejec REAL, comentarios TEXT)''')
    conn.commit()
    conn.close()

def guardar_registro(d):
    conn = conectar_db()
    c = conn.cursor()
    # La consulta debe tener exactamente 16 signos de interrogación (uno por cada columna menos el ID)
    query = '''INSERT INTO proyectos 
               (tren_e2e, director, rte_nombre, mes_salida, fecha_plan, fecha_real, 
                on_time, in_full, capex_aprob, capex_ejec, pct_budget, on_budget, 
                otif_x_proyecto, opex_aprob, opex_ejec, comentarios) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    
    valores = (
        d["tren_e2e"], d["director"], d["rte_nombre"], d["mes_salida"],
        str(d["fecha_plan"]), str(d["fecha_real"]), d["on_time"], d["in_full"],
        d["capex_aprob"], d["capex_ejec"], d["pct_budget"], d["on_budget"],
        d["otif_x_proyecto"], d["opex_aprob"], d["opex_ejec"], d["comentarios"]
    )
    
    c.execute(query, valores)
    conn.commit()
    conn.close()

def cargar_datos():
    conn = conectar_db()
    try:
        df = pd.read_sql_query("SELECT * FROM proyectos", conn)
        column_map = {
            "id": "id", "tren_e2e": "Tren E2E", "director": "Director", "rte_nombre": "RTE Nombre",
            "mes_salida": "Mes de Salida", "fecha_plan": "Fecha Planeada", "fecha_real": "Fecha Real",
            "on_time": "On Time", "in_full": "In Full", "capex_aprob": "CAPEX Aprobado",
            "capex_ejec": "Ejecutado CAPEX", "pct_budget": "% Budget", "on_budget": "On Budget",
            "otif_x_proyecto": "OTIF X Proyecto", "opex_aprob": "OPEX Aprobado",
            "opex_ejec": "Ejecutado OPEX", "comentarios": "Comentarios"
        }
        if not df.empty:
            df.rename(columns=column_map, inplace=True)
    except:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def eliminar_registros(ids):
    conn = conectar_db()
    c = conn.cursor()
    c.execute(f"DELETE FROM proyectos WHERE id IN ({','.join(['?']*len(ids))})", ids)
    conn.commit()
    conn.close()

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

meses_espanol = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

def clean_numeric(value):
    if not value: return 0.0
    clean_val = re.sub(r'[^\d.]', '', str(value))
    try: return float(clean_val)
    except: return 0.0

# --- INTERFAZ ---
st.title("📊 Dashboard OTIF - Portafolio 2026")

with st.expander("➕ Nuevo Registro de Proyecto", expanded=True):
    c2, c3, c4, c1 = st.columns([1, 1, 1, 2])
    with c2: tren_t = st.selectbox("Tren", options=list(CONFIG_TRENES.keys()))
    with c3: dir_s = st.selectbox("Director", options=CONFIG_TRENES[tren_t]["directores"])
    with c4: rte_s = st.selectbox("RTE Responsable", options=CONFIG_TRENES[tren_t]["rtes"])
    with c1: nombre_p = st.text_input("Nombre del Proyecto")

    c5, c6, c7, c8 = st.columns(4)
    with c5: f_p = st.date_input("Fecha Planeada", format="DD/MM/YYYY")
    with c6: f_r = st.date_input("Fecha Real", format="DD/MM/YYYY")
    with c7: in_f = st.selectbox("In Full", ["Sin avance", "SÍ", "NO"])
    with c8: com = st.text_input("Comentarios")

    st.markdown("### Finanzas")
    f1, f2, f3, f4 = st.columns(4)
    with f1: t_ca = st.text_input("CAPEX Aprobado", value="0.00")
    with f2: t_ce = st.text_input("Ejecutado CAPEX", value="0.00")
    with f3: t_oa = st.text_input("OPEX Aprobado", value="0.00")
    with f4: t_oe = st.text_input("Ejecutado OPEX", value="0.00")

    if st.button("💾 Guardar Proyecto"):
        ca, ce, oa, oe = clean_numeric(t_ca), clean_numeric(t_ce), clean_numeric(t_oa), clean_numeric(t_oe)
        t_aprob, t_ejec = ca + oa, ce + oe
        
        on_b = "SÍ" if t_ejec <= t_aprob else "NO"
        pct_b = f"{(t_ejec / t_aprob * 100):.1f}%" if t_aprob > 0 else "0.0%"
        ot = "SÍ" if f_r <= f_p else "NO"

        if in_f == "Sin avance":
            otif_final = "Sin avance"
        elif ca == 0.01:
            otif_final = "SÍ" if (ot == "SÍ" and in_f == "SÍ") else "NO"
        else:
            otif_final = "SÍ" if (ot == "SÍ" and in_f == "SÍ" and on_b == "SÍ") else "NO"

        mes = meses_espanol[f_r.month]
        
        datos = {
            "tren_e2e": nombre_p, "director": dir_s, "rte_nombre": rte_s, "mes_salida": mes,
            "fecha_plan": f_p, "fecha_real": f_r, "on_time": ot, "in_full": in_f,
            "capex_aprob": ca, "capex_ejec": ce, "pct_budget": pct_b, "on_budget": on_b,
            "otif_x_proyecto": otif_final, "opex_aprob": oa, "opex_ejec": oe, "comentarios": com
        }
        guardar_registro(datos)
        st.success(f"Proyecto {nombre_p} registrado exitosamente.")
        st.rerun()

# --- TABLERO ---
df_datos = cargar_datos()

if not df_datos.empty:
    if "OTIF X Proyecto" in df_datos.columns:
        st.subheader("📈 Resumen de Cumplimiento por Director")
        df_validos = df_datos[df_datos["OTIF X Proyecto"].isin(["SÍ", "NO"])].copy()
        if not df_validos.empty:
            df_validos["Puntos"] = df_validos["OTIF X Proyecto"].map({"SÍ": 1, "NO": 0})
            resumen = df_validos.groupby("Director")["Puntos"].mean() * 100
            resumen_df = resumen.reset_index()
            resumen_df.columns = ["Director", "% OTIF Global"]
            st.table(resumen_df.style.format({"% OTIF Global": "{:.1f}%"}))
    
    st.subheader("Matriz Principal (Detalle por Proyecto)")
    df_con_check = df_datos.copy()
    df_con_check.insert(0, "Seleccionar", False)
    
    res_edicion = st.data_editor(
        df_con_check.drop(columns=['id']), 
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(""),
            "CAPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado CAPEX": st.column_config.NumberColumn(format="$ %,.2f"),
            "OPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado OPEX": st.column_config.NumberColumn(format="$ %,.2f"),
            "Fecha Planeada": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Fecha Real": st.column_config.DateColumn(format="DD/MM/YYYY"),
        },
        disabled=[col for col in df_con_check.columns if col != "Seleccionar"],
        use_container_width=True, hide_index=True, key="main_editor_v5"
    )

    filas_marcadas = res_edicion[res_edicion["Seleccionar"] == True].index
    ids_a_eliminar = df_datos.iloc[filas_marcadas]["id"].tolist()

    col_acc1, col_acc2 = st.columns([1, 5])
    with col_acc1:
        if st.button(f"🗑️ Borrar ({len(ids_a_eliminar)})", type="primary", disabled=len(ids_a_eliminar)==0):
            eliminar_registros(ids_a_eliminar)
            st.rerun()
    with col_acc2:
        st.download_button("📥 Exportar (CSV)", df_datos.to_csv(index=False).encode('utf-8'), "OTIF_Matrix.csv")
else:
    st.info("No hay registros en la base de datos.")
