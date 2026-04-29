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
        d["CAPEX Aprobado"], d["Ejecutado CAPEX"], d["% Budget"], d["On Budget"],
        d["OTIF X Proyecto"], d["OPEX Aprobado"], d["Ejecutado OPEX"], d["Comentarios"]
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
    clean_val = re.sub(r'[^\d.]', '', value)
    try: return float(clean_val)
    except: return 0.0

# --- INTERFAZ ---
st.title("📊 Dashboard OTIF - Portafolio 2026")

with st.expander("➕ Nuevo Registo de Proyecto", expanded=True):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c2: tren_t = st.selectbox("Tren", options=list(CONFIG_TRENES.keys()))
    with c3: dir_s = st.selectbox("Director", options=CONFIG_TRENES[tren_t]["directores"])
    with c4: rte_s = st.selectbox("RTE Responsable", options=CONFIG_TRENES[tren_t]["rtes"])
    with c1: nombre_p = st.text_input("Nombre del Proyecto")


    c5, c6, c7, c8 = st.columns(4)
    with c5: f_p = st.date_input("Fecha Planeada", format="DD/MM/YYYY")
    with c6: f_r = st.date_input("Fecha Real (Dejar hoy si no ha terminado)", format="DD/MM/YYYY")
    with c7: in_f = st.selectbox("In Full", ["SÍ", "NO"])
    with c8: com = st.text_input("Comentarios")

    st.markdown("### Finanzas")
    f1, f2, f3, f4 = st.columns(4)
    with f1: t_ca = st.text_input("CAPEX Aprobado", value="0.00")
    with f2: t_ce = st.text_input("Ejecutado CAPEX", value="0.00")
    with f3: t_oa = st.text_input("OPEX Aprobado", value="0.00")
    with f4: t_oe = st.text_input("Ejecutado OPEX", value="0.00")

    if st.button("💾 Guardar Proyecto"):
        ca, ce, oa, oe = clean_numeric(t_ca), clean_numeric(t_ce), clean_numeric(t_oa), clean_numeric(t_oe)
        
        # 1. Regla del Tope de Presupuesto
        t_aprob = ca + oa
        t_ejec = ce + oe
        on_b = "SÍ" if t_ejec <= t_aprob else "NO"
        pct_b = f"{(t_ejec / t_aprob * 100):.1f}%" if t_aprob > 0 else "0.0%"

        # 2. On Time
        ot = "SÍ" if f_r <= f_p else "NO"

        # 3. Lógica OTIF (Regla del Centavo y Manejo de Vacíos)
        if in_f == "Esperando...":
            otif_final = "Sin avance"
        elif ca == 0.01: # Regla del Centavo (Proyectos 2025)
            otif_final = "SÍ" if (ot == "SÍ" and in_f == "SÍ") else "NO"
        else:
            otif_final = "SÍ" if (ot == "SÍ" and in_f == "SÍ" and on_b == "SÍ") else "NO"

        mes = meses_espanol[f_r.month]
        
        datos = {
            "Tren E2E": nombre_p, "Director": dir_s, "RTE Nombre": rte_s, "Mes de Salida": mes,
            "Fecha Planeada": f_p, "Fecha Real": f_r, "On Time": ot, "In Full": in_f,
            "CAPEX Aprobado": ca, "Ejecutado CAPEX": ce, "% Budget": pct_b, "On Budget": on_b,
            "OTIF X Proyecto": otif_final, "OPEX Aprobado": oa, "Ejecutado OPEX": oe, "Comentarios": com
        }
        guardar_registro(datos)
        st.success(f"Proyecto {nombre_p} registrado siguiendo las Reglas del Manual.")
        st.rerun()

# --- TABLERO ---
st.subheader("Matriz Principal (Detalle por Proyecto)")
df_datos = cargar_datos()

if not df_datos.empty:
    df_con_check = df_datos.copy()
    df_con_check.insert(0, "Seleccionar", False)
    
    res_edicion = st.data_editor(
        df_con_check.drop(columns=['id']), 
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn("Eliminar?"),
            "CAPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado CAPEX": st.column_config.NumberColumn(format="$ %,.2f"),
            "OPEX Aprobado": st.column_config.NumberColumn(format="$ %,.2f"),
            "Ejecutado OPEX": st.column_config.NumberColumn(format="$ %,.2f"),
            "OTIF X Proyecto": st.column_config.TextColumn("OTIF Final", help="Calculado con Regla del Centavo si Aprobado = 0.01")
        },
        disabled=[col for col in df_con_check.columns if col != "Seleccionar"],
        use_container_width=True, hide_index=True, key="editor_manual_rules"
    )

    filas_marcadas = res_edicion[res_edicion["Seleccionar"] == True].index
    ids_a_eliminar = df_datos.iloc[filas_marcadas]["id"].tolist()

    col_acc1, col_acc2 = st.columns([1, 5])
    with col_acc1:
        if st.button(f"🗑️ Borrar ({len(ids_a_eliminar)})", type="primary", disabled=len(ids_a_eliminar)==0):
            eliminar_registros(ids_a_eliminar)
            st.rerun()
    with col_acc2:
        st.download_button("📥 Exportar Matriz (CSV)", df_datos.to_csv(index=False).encode('utf-8'), "OTIF_Matrix_2026.csv")
else:
    st.info("Inicia la captura para ver la Matriz Principal.")
