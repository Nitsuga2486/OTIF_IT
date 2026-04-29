import streamlit as st
import pandas as pd
import sqlite3
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF 2026 - Control Portafolio", layout="wide")

# --- FUNCIONES DE PERSISTENCIA ---
def conectar_db():
    return sqlite3.connect('otif_it_data.db')

def crear_tabla():
    conn = conectar_db()
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM proyectos LIMIT 1")
    except:
        c.execute("DROP TABLE IF EXISTS proyectos")
        c.execute('''CREATE TABLE proyectos
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
            "capex_ejec": "Ejecutado CPX", "pct_budget": "% Budget", "on_budget": "On Budget",
            "otif_x_proyecto": "OTIF X Proy", "opex_aprob": "OPEX Aprobado",
            "opex_ejec": "Ejecutado OPX", "comentarios": "Comentarios"
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
    "Ulta": {"directores": ["Muñoz Julio", "Diaz de Leon Lino"], "rtes": ["Navarrete Arantzasu", "Baltodano Karla", "N/A"]}
}

meses_espanol = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

def clean_numeric(value):
    if not value: return 0.0
    clean_val = re.sub(r'[^\d.]', '', str(value))
    try: return float(clean_val)
    except: return 0.0

# --- INTERFAZ ---
st.title("📊 Dashboard OTIF - Portafolio 2026")

# SECCIÓN 1: NUEVO REGISTRO
with st.expander("➕ Nuevo Registro de Proyecto", expanded=True):
    c_tren, c_dir, c_rte = st.columns(3)
    with c_tren:
        tren_t = st.selectbox("1. Selecciona Tren", options=["Seleccionar"] + list(CONFIG_TRENES.keys()), key="sel_tren")
    
    opciones_dir = ["Seleccionar"]
    opciones_rte = ["Seleccionar"]
    if tren_t != "Seleccionar":
        opciones_dir += CONFIG_TRENES[tren_t]["directores"]
        opciones_rte += CONFIG_TRENES[tren_t]["rtes"]

    with c_dir:
        dir_s = st.selectbox("2. Director Responsable", options=opciones_dir, key="sel_dir")
    with c_rte:
        rte_s = st.selectbox("3. RTE asignado", options=opciones_rte, key="sel_rte")

    with st.form("registro_proyecto", clear_on_submit=True):
        nombre_p = st.text_input("Nombre del Proyecto (Tren E2E)")
        c5, c6, c7, c8 = st.columns(4)
        with c5: f_p = st.date_input("Fecha Planeada", format="DD/MM/YYYY")
        with c6: f_r = st.date_input("Fecha Real", format="DD/MM/YYYY")
        with c7: in_f_sel = st.selectbox("In Full", ["Seleccionar", "Sin avance", "SÍ", "NO"])
        with c8: com = st.text_input("Comentarios")

        st.markdown("### Finanzas")
        es_ppto_anterior = st.checkbox("PPTO Año Anterior")
        f1, f2, f3, f4 = st.columns(4)
        with f1: t_ca = st.text_input("CAPEX Aprobado", value="0.00")
        with f2: t_ce = st.text_input("Ejecutado CPX", value="0.00")
        with f3: t_oa = st.text_input("OPEX Aprobado", value="0.00")
        with f4: t_oe = st.text_input("Ejecutado OPX", value="0.00")

        if st.form_submit_button("💾 Guardar Proyecto"):
            errores = []
            if tren_t == "Seleccionar": errores.append("Tren")
            if dir_s == "Seleccionar": errores.append("Director")
            if rte_s == "Seleccionar": errores.append("RTE")
            if in_f_sel == "Seleccionar": errores.append("In Full")
            if not nombre_p.strip(): errores.append("Nombre del Proyecto")

            if errores:
                st.error(f"⚠️ No se puede guardar. Faltan: {', '.join(errores)}")
            else:
                ca, ce, oa, oe = clean_numeric(t_ca), clean_numeric(t_ce), clean_numeric(t_oa), clean_numeric(t_oe)
                t_aprob, t_ejec = ca + oa, ce + oe
                on_b = "SÍ" if t_ejec <= t_aprob else "NO"
                pct_b = f"{(t_ejec / t_aprob * 100):.1f}%" if t_aprob > 0 else "0.0%"
                ot = "SÍ" if f_r <= f_p else "NO"

                if in_f_sel == "Sin avance":
                    otif_final = "Sin avance"
                elif es_ppto_anterior or ca == 0.01: 
                    otif_final = "SÍ" if (ot == "SÍ" and in_f_sel == "SÍ") else "NO"
                else:
                    otif_final = "SÍ" if (ot == "SÍ" and in_f_sel == "SÍ" and on_b == "SÍ") else "NO"

                mes = meses_espanol[f_r.month]
                datos = {
                    "tren_e2e": nombre_p, "director": dir_s, "rte_nombre": rte_s, "mes_salida": mes,
                    "fecha_plan": f_p, "fecha_real": f_r, "on_time": ot, "in_full": in_f_sel,
                    "capex_aprob": ca, "capex_ejec": ce, "pct_budget": pct_b, "on_budget": on_b,
                    "otif_x_proyecto": otif_final, "opex_aprob": oa, "opex_ejec": oe, "comentarios": com
                }
                guardar_registro(datos)
                st.success(f"✅ Proyecto {nombre_p} registrado.")
                st.rerun()

# --- PROCESAMIENTO DE DATOS ---
df_datos = cargar_datos()

# SECCIÓN 2: VISTA DE LÍDERES (Con todos los directores)
with st.expander("📈 Resumen de Cumplimiento por Líder / Director", expanded=True):
    # 1. Obtener todos los directores únicos de la configuración
    todos_los_directores = set()
    for tren in CONFIG_TRENES.values():
        todos_los_directores.update(tren["directores"])
    
    # 2. Crear la lista maestra de líderes a mostrar
    maestra_lideres = sorted(list(todos_los_directores))
    # Agregar líderes especiales si no están
    for especial in ["Karla Baltodano", "Mireya Mares", "Vanessa Miranda"]:
        if especial not in maestra_lideres:
            maestra_lideres.append(especial)

    if not df_datos.empty:
        def asignar_lider(row):
            d, r = row["Director"], row["RTE Nombre"]
            if r in ["Baltodano Karla", "Navarrete Arantzasu", "Moreno Jorge"]: return "Karla Baltodano"
            if r in ["Mares Mireya", "Franco Edith", "Hernandez Consuelo"]: return "Mireya Mares"
            if d in ["Rojas Juan Manuel", "Diaz de Leon Lino"]: return "Vanessa Miranda"
            if d == "Posada Evelyn": return "Evelyn Posada"
            return d

        df_res = df_datos.copy()
        df_res["Líder"] = df_res.apply(asignar_lider, axis=1)
        df_res["p_ot"] = df_res["On Time"].map({"SÍ": 1, "NO": 0})
        df_res["p_if"] = df_res["In Full"].map({"SÍ": 1, "NO": 0})
        df_res["p_otif"] = df_res["OTIF X Proy"].map({"SÍ": 1, "NO": 0})
        
        resumen_calculado = df_res.groupby("Líder").agg({
            "p_ot": "mean", "p_if": "mean", "CAPEX Aprobado": "sum", "p_otif": "mean", "id": "count"
        }).reset_index()
    else:
        resumen_calculado = pd.DataFrame(columns=["Líder", "p_ot", "p_if", "CAPEX Aprobado", "p_otif", "id"])

    # 3. Cruzar maestra con datos calculados para asegurar que aparezcan todos
    df_maestra = pd.DataFrame({"Líder": maestra_lideres})
    resumen_final = pd.merge(df_maestra, resumen_calculado, on="Líder", how="left").fillna(0)

    resumen_final.columns = ["Líder / Director", "On Time (%)", "In Full (%)", "Total CAPEX", "OTIF Global (%)", "Proyectos"]
    
    # Formateo
    resumen_final["On Time (%)"] *= 100
    resumen_final["In Full (%)"] *= 100
    resumen_final["OTIF Global (%)"] *= 100
    
    st.table(resumen_final.style.format({
        "On Time (%)": "{:.1f}%", "In Full (%)": "{:.1f}%",
        "Total CAPEX": "$ {:,.2f}", "OTIF Global (%)": "{:.1f}%",
        "Proyectos": "{:.0f}"
    }))

# SECCIÓN 3: MATRIZ PRINCIPAL
if not df_datos.empty:
    with st.expander("🗂️ Matriz Principal - Detalle de Proyectos", expanded=False):
        df_con_check = df_datos.copy()
        df_con_check.insert(0, "Seleccionar", False)
        res_edicion = st.data_editor(
            df_con_check.drop(columns=['id']), 
            column_config={
                "Seleccionar": st.column_config.CheckboxColumn(""),
                "CAPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f"),
                "Ejecutado CPX": st.column_config.NumberColumn(format="$ %,.2f"),
                "OPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f"),
                "Ejecutado OPX": st.column_config.NumberColumn(format="$ %,.2f"),
            },
            disabled=[col for col in df_con_check.columns if col != "Seleccionar"],
            use_container_width=True, hide_index=True, key="main_editor_final_v2"
        )
        
        ids_del = df_datos.iloc[res_edicion[res_edicion["Seleccionar"] == True].index]["id"].tolist()
        c_del, c_exp = st.columns([1, 5])
        with c_del:
            if st.button(f"🗑️ Borrar ({len(ids_del)})", type="primary", disabled=len(ids_del)==0):
                eliminar_registros(ids_del)
                st.rerun()
        with c_exp:
            st.download_button("📥 Exportar (CSV)", df_datos.to_csv(index=False).encode('utf-8'), "OTIF_Matrix.csv")
else:
    st.info("No hay registros en la base de datos.")
