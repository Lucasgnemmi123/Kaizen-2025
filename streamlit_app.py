import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os

# Asegura que Streamlit busque imágenes en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------- CONFIGURACIÓN GENERAL ----------
st.set_page_config(
    page_title="Idea Kaizen",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- DATOS DE GOOGLE SHEETS ----------
API_KEY = "AIzaSyAzorWWIV3Rl8NFlHxlclWlwtBozwXzYSM"
SHEET_ID = "1M9Sccc-3bA33N1MNJtkTCcrDSKK_wfRjeDnqxsrlEtA"
RANGE = "Hoja 1"

URL = (
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE}"
    f"?alt=json&key={API_KEY}"
)

REFRESH_INTERVAL = 30  # segundos

# ---------- AUTO REFRESH COMPATIBLE STREAMLIT CLOUD ----------
st.markdown(
    f'<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">',
    unsafe_allow_html=True
)

# ---------- FUNCIÓN PARA CARGAR IMÁGENES ----------
def cargar_imagen(path, ancho):
    if os.path.exists(path):
        st.image(path, width=ancho)
    else:
        st.markdown(
            f"""
            <div style='width:{ancho}px; height:120px; border:2px dashed #999; 
            display:flex; align-items:center; justify-content:center; 
            font-size:14px; color:#555; border-radius:8px;'>
            {path} no encontrado
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------- FUNCIÓN PARA CARGAR DATOS ----------
@st.cache_data(ttl=10)
def cargar_datos():
    resp = requests.get(URL, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("values", [])
    
    if not data:
        return pd.DataFrame(columns=["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion"])
    
    df = pd.DataFrame(data[1:], columns=data[0]).fillna("")
    return df

# ---------- ESTILOS CSS ----------
big_css = """
<style>
body, table, th, td, h1, h2, h3, p, span, div {
    color: #000000 !important;
    font-weight: 600;
}

table {
    border-collapse: collapse;
    width: 100%;
    font-size: 18px !important;
}

thead th {
    background: #F7DC6F;
    padding: 10px !important;
    text-align: center !important;
    border: 2px solid #444;
}

tbody td {
    padding: 10px !important;
    text-align: center !important;
    border: 2px solid #444;
}

th:nth-child(2),
td:nth-child(2) {
    width: 320px !important;
    max-width: 320px !important;
    word-wrap: break-word !important;
}

.table-container {
    border: 3px solid #000000;
    padding: 8px;
    border-radius: 8px;
    background: #fff;
}

.circle {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    margin: auto;
}

.small-note {
    font-size:15px;
    text-align:center;
}
</style>
"""
st.markdown(big_css, unsafe_allow_html=True)

# ---------- ENCABEZADO ----------
header_left, header_center, header_right = st.columns([1, 5, 1])

with header_left:
    cargar_imagen("assets/DHL.png", 150)

with header_center:
    st.markdown(
        """
        <div style='
            text-align:center;
            background:#F7DC6F;
            padding:18px;
            border-radius:8px;
            font-size:28px;
            font-weight:800;
            width:100%;
        '>
            UBICACIÓN DE PREPARACIONES
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:
    cargar_imagen("assets/Aramark.png", 150)

st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

# ---------- CARGA Y PROCESO ----------
try:
    df = cargar_datos()

    # Limpieza
    for col in ["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion"]:
        df[col] = df[col].astype(str).str.strip()

    zona_j = df[df["Pre-Stage"].str.upper().str.startswith("J")].reset_index(drop=True)
    zona_d = df[df["Pre-Stage"].str.upper().str.startswith("D")].reset_index(drop=True)

    cols = ["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion"]
    if zona_j.empty: zona_j = pd.DataFrame(columns=cols)
    if zona_d.empty: zona_d = pd.DataFrame(columns=cols)

    # Semáforo
    def render_semaforo(valor):
        v = str(valor).lower().strip()
        if v.startswith("vac"):
            color = "#2ECC71"
        elif v.startswith("par"):
            color = "#F1C40F"
        elif v.startswith("com"):
            color = "#E74C3C"
        else:
            color = "#BDC3C7"
        return f"<div class='circle' style='background:{color};'></div>"

    # Tablas
    def preparar_html_tabla(df_zone, title):
        display = df_zone.copy()
        display["Destino"] = display["Destino"].replace("", "—")
        display["Fecha Despacho"] = display["Fecha Despacho"].replace("", "—")
        display["Ocupacion_html"] = display["Ocupacion"].apply(render_semaforo)
        display = display[["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion_html"]]
        display = display.rename(columns={"Ocupacion_html": "Ocupacion"})

        html = (
            f"<div class='table-container'>"
            f"<h3 style='text-align:center;margin-bottom:12px;'>{title}</h3>"
            + display.to_html(escape=False, index=False)
            + "</div>"
        )
        return html

    colJ, colD = st.columns(2)

    with colJ:
        st.markdown(preparar_html_tabla(zona_j, "PRE - STAGE ZONA J"), unsafe_allow_html=True)

    with colD:
        st.markdown(preparar_html_tabla(zona_d, "PRE - STAGE ZONA D"), unsafe_allow_html=True)

    st.markdown(
        f"<p class='small-note'>🔄 El tablero se actualizará en {REFRESH_INTERVAL} segundos...</p>",
        unsafe_allow_html=True
    )

except Exception as e:
    st.error("⚠️ Error al cargar los datos desde Google Sheets API.")
    st.exception(e)
