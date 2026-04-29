import streamlit as st
import pandas as pd
import sqlite3
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OTIF 2026 - Control Portafolio", layout="wide")

# --- ESTILOS CSS PARA TABLAS ---
st.markdown("""
    <style>
    .stTable td:nth-child(n+2), .stTable th:nth-child(n+2) { text-align: center !important; }
    .stTable td:nth-child(1), .stTable th:nth-child(1) { text-align: left !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES DE NEGOCIO Y ESTRUCTURA ---
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

ESTRUCTURA_REPORTES = {
    "Karla Baltodano": {"rtes": ["Baltodano Karla", "Navarrete Arantzasu", "Moreno Jorge"]},
    "Mireya Mares": {"rtes": ["Mares Mireya", "Franco Edith", "Hernandez Consuelo"]},
    "Vanessa Miranda": {"directores": ["Rojas Juan Manuel", "Diaz de Leon Lino", "Miranda Vanessa"]}
}

MESES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

# --- FUNCIONES DE PERSISTENCIA ---
def conectar_db(): return sqlite3.connect('otif_it_data.db')

def crear_tabla():
    conn = conectar_db()
    c = conn.cursor()
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
    query = "INSERT INTO proyectos (tren_e2e, director, rte_nombre, mes_salida, fecha_plan, fecha_real, on_time, in_full, capex_aprob, capex_ejec, pct_budget, on_budget, otif_x_proyecto, opex_aprob, opex_ejec, comentarios) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    c.execute(query, (d["tren_e2e"], d["director"], d["rte_nombre"], d["mes_salida"], str(d["fecha_plan"]), str(d["fecha_real"]), d["on_time"], d["in_full"], d["capex_aprob"], d["capex_ejec"], d["pct_budget"], d["on_budget"], d["otif_x_proyecto"], d["opex_aprob"], d["opex_ejec"], d["comentarios"]))
    conn.commit()
    conn.close()

def cargar_datos():
    conn = conectar_db()
    try:
        df = pd.read_sql_query("SELECT * FROM proyectos", conn)
        if not df.empty:
            df.rename(columns={"tren_e2e": "Tren E2E", "director": "Director", "rte_nombre": "RTE Nombre", "on_time": "On Time", "in_full": "In Full", "capex_aprob": "CAPEX Aprobado", "otif_x_proyecto": "OTIF X Proy"}, inplace=True)
            for col in ["CAPEX Aprobado", "capex_ejec", "opex_aprob", "opex_ejec"]:
                if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    except: df = pd.DataFrame()
    finally: conn.close()
    return df

def eliminar_registros(ids):
    conn = conectar_db()
    c = conn.cursor()
    c.execute(f"DELETE FROM proyectos WHERE id IN ({','.join(['?']*len(ids))})", ids)
    conn.commit()
    conn.close()

def clean_numeric(val):
    clean = re.sub(r'[^\d.]', '', str(val))
    try: return float(clean)
    except: return 0.0

crear_tabla()

# --- INTERFAZ ---
st.title("📊 Dashboard OTIF - Portafolio 2026")

# SECCIÓN 1: REGISTRO
with st.expander("➕ Nuevo Registro de Proyecto", expanded=False):
    c_tren, c_dir, c_rte = st.columns(3)
    with c_tren: tren_t = st.selectbox("1. Selecciona Tren", options=["Seleccionar"] + list(CONFIG_TRENES.keys()), key="sel_tren")
    
    op_dir = ["Seleccionar"] + CONFIG_TRENES[tren_t]["directores"] if tren_t != "Seleccionar" else ["Seleccionar"]
    op_rte = ["Seleccionar"] + CONFIG_TRENES[tren_t]["rtes"] if tren_t != "Seleccionar" else ["Seleccionar"]

    with c_dir: dir_s = st.selectbox("2. Director Responsable", options=op_dir, key="sel_dir")
    with c_rte: rte_s = st.selectbox("3. RTE asignado", options=op_rte, key="sel_rte")

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
            if "Seleccionar" in [tren_t, dir_s, rte_s, in_f_sel] or not nombre_p.strip():
                st.error("⚠️ Completa todos los campos obligatorios.")
            else:
                ca, ce, oa, oe = clean_numeric(t_ca), clean_numeric(t_ce), clean_numeric(t_oa), clean_numeric(t_oe)
                t_aprob, t_ejec = ca + oa, ce + oe
                ot = "SÍ" if f_r <= f_p else "NO"
                on_b = "SÍ" if t_ejec <= t_aprob else "NO"
                
                if in_f_sel == "Sin avance": otif_final = "Sin avance"
                elif es_ppto_anterior or ca == 0.01: otif_final = "SÍ" if (ot == "SÍ" and in_f_sel == "SÍ") else "NO"
                else: otif_final = "SÍ" if (ot == "SÍ" and in_f_sel == "SÍ" and on_b == "SÍ") else "NO"

                guardar_registro({"tren_e2e": nombre_p, "director": dir_s, "rte_nombre": rte_s, "mes_salida": MESES[f_r.month], "fecha_plan": f_p, "fecha_real": f_r, "on_time": ot, "in_full": in_f_sel, "capex_aprob": ca, "capex_ejec": ce, "pct_budget": f"{(t_ejec/t_aprob*100):.1f}%" if t_aprob > 0 else "0.0%", "on_budget": on_b, "otif_x_proyecto": otif_final, "opex_aprob": oa, "opex_ejec": oe, "comentarios": com})
                st.success("✅ Registrado."); st.rerun()

# --- PROCESAMIENTO DE RESUMEN (DOBLE CONTABILIZACIÓN) ---
df_datos = cargar_datos()

with st.expander("📈 Resumen de Cumplimiento por Líder / Director", expanded=True):
    if not df_datos.empty:
        dir_bd = df_datos["Director"].unique().tolist()
        dir_conf = [d for t in CONFIG_TRENES.values() for d in t["directores"]]
        nombres_maestra = sorted(list(set(dir_bd + dir_conf + list(ESTRUCTURA_REPORTES.keys()))))
        
        filas = []
        for n in nombres_maestra:
            mask_dir = (df_datos["Director"] == n)
            mask_lid = pd.Series([False]*len(df_datos))
            if n in ESTRUCTURA_REPORTES:
                reglas = ESTRUCTURA_REPORTES[n]
                if "rtes" in reglas: mask_lid |= df_datos["RTE Nombre"].isin(reglas["rtes"])
                if "directores" in reglas: mask_lid |= df_datos["Director"].isin(reglas["directores"])
            
            df_f = df_datos[mask_dir | mask_lid].drop_duplicates()
            if not df_f.empty:
                filas.append({"Líder / Director": n, "On Time (%)": (df_f["On Time"] == "SÍ").mean()*100, "In Full (%)": (df_f["In Full"] == "SÍ").mean()*100, "Total CAPEX": df_f["CAPEX Aprobado"].sum(), "OTIF Global (%)": (df_f["OTIF X Proy"] == "SÍ").mean()*100})
            else:
                filas.append({"Líder / Director": n, "On Time (%)": 0, "In Full (%)": 0, "Total CAPEX": 0, "OTIF Global (%)": 0})
        
        st.table(pd.DataFrame(filas).style.format({"On Time (%)": "{:.1f}%", "In Full (%)": "{:.1f}%", "Total CAPEX": "$ {:,.2f}", "OTIF Global (%)": "{:.1f}%"}))
    else: st.info("Sin datos.")

# --- MATRIZ PRINCIPAL ---
if not df_datos.empty:
    with st.expander("🗂️ Matriz Principal - Detalle", expanded=True):
        df_edit = df_datos.copy(); df_edit.insert(0, "Seleccionar", False)
        res_ed = st.data_editor(df_edit.drop(columns=['id']), column_config={"CAPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f")}, use_container_width=True, hide_index=True, key="editor_vFinal")
        
        ids_del = df_datos.iloc[res_ed[res_ed["Seleccionar"] == True].index]["id"].tolist()
        c1, c2 = st.columns([1, 5])
        with c1: 
            if st.button(f"🗑️ Borrar ({len(ids_del)})", type="primary", disabled=len(ids_del)==0): eliminar_registros(ids_del); st.rerun()
        with c2: st.download_button("📥 Exportar CSV", df_datos.to_csv(index=False).encode('utf-8-sig'), "OTIF_Matrix_2026.csv", "text/csv")
