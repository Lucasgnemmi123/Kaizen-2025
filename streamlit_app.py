import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import base64

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

REFRESH_INTERVAL = 300  # segundos

# ---------- AUTO REFRESH ----------
st.markdown(
    f'<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">',
    unsafe_allow_html=True
)

# ---------- IMÁGENES BASE64 ----------
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return ""

img_dhl = get_image_base64("assets/DHL.png")
img_aramark = get_image_base64("assets/Aramark.png")

# ---------- CARGAR DATOS ----------
@st.cache_data(ttl=10)
def cargar_datos():
    resp = requests.get(URL, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("values", [])
    if not data:
        return pd.DataFrame(columns=["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion"])
    df = pd.DataFrame(data[1:], columns=data[0]).fillna("")
    return df

# ---------- CSS CORREGIDO (ENCABEZADOS CENTRADOS) ----------
estilo_tv = """
<style>
    /* 1. LAYOUT FULL SCREEN */
    .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }
    header, footer, #MainMenu { display: none !important; }
    body { background-color: #ffffff; font-family: 'Arial', sans-serif; }

    /* 2. HEADER FLEXBOX */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 10px;
        background: white;
        border-bottom: 2px solid #ddd;
        padding-bottom: 5px;
    }
    .logo-box { width: 20%; display: flex; justify-content: center; }
    .logo-img { max-height: 80px; width: auto; }
    .time-box { width: 60%; text-align: center; font-size: 2.5rem; font-weight: 900; color: #333; }

    /* 3. TABLAS */
    .table-wrapper { border: 2px solid #333; }
    .zone-title {
        background-color: #000;
        color: #FFD700;
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        padding: 5px;
        text-transform: uppercase;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed; /* Mantiene anchos fijos */
    }

    /* ESTILOS DE ENCABEZADO (TH) - TODO CENTRADO */
    thead th {
        background-color: #d40511;
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 12px 5px;
        text-transform: uppercase;
        border: 1px solid #999;
        text-align: center !important; /* <--- FUERZA GLOBAL DE CENTRADO */
    }

    /* ESTILOS DE CELDAS (TD) */
    tbody td {
        font-size: 1.4rem;
        font-weight: 700;
        color: #000;
        padding: 8px 10px; /* Un poco más de padding lateral */
        border: 1px solid #ccc;
        vertical-align: middle;
        height: 55px;
    }

    /* --- DEFINICIÓN DE COLUMNAS --- */

    /* Columna 1: UBI */
    th:nth-child(1), td:nth-child(1) { 
        width: 15%; 
        text-align: center !important; 
    }
    
    /* Columna 2: DESTINO */
    th:nth-child(2) { 
        width: 45%; 
        text-align: center !important; /* El TITULO 'DESTINO' CENTRADO */
    }
    td:nth-child(2) {
        width: 45%;
        text-align: left !important; /* El DATO (Nombre) A LA IZQUIERDA PARA LEER BIEN */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Columna 3: FECHA */
    th:nth-child(3), td:nth-child(3) { 
        width: 25%; 
        text-align: center !important; 
    }
    
    /* Columna 4: ESTADO */
    th:nth-child(4), td:nth-child(4) { 
        width: 15%; 
        text-align: center !important; 
    }

    /* Semáforo */
    .traffic-light {
        height: 35px; width: 35px;
        border-radius: 50%;
        display: inline-block;
        border: 2px solid rgba(0,0,0,0.2);
    }
    tbody tr:nth-child(even) { background-color: #f4f4f4; }
</style>
"""
st.markdown(estilo_tv, unsafe_allow_html=True)

# ---------- HEADER ----------
hora_chile = datetime.now(ZoneInfo("America/Santiago")).strftime("%H:%M:%S")

header_html = f"""
<div class="header-container">
    <div class="logo-box"><img src="{img_dhl}" class="logo-img"></div>
    <div class="time-box">🕒 {hora_chile}</div>
    <div class="logo-box"><img src="{img_aramark}" class="logo-img"></div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ---------- LÓGICA ----------
try:
    df = cargar_datos()
    for col in ["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion"]:
        df[col] = df[col].astype(str).str.strip()

    zona_j = df[df["Pre-Stage"].str.upper().str.startswith("J")].reset_index(drop=True)
    zona_d = df[df["Pre-Stage"].str.upper().str.startswith("D")].reset_index(drop=True)

    cols = ["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion"]
    if zona_j.empty: zona_j = pd.DataFrame(columns=cols)
    if zona_d.empty: zona_d = pd.DataFrame(columns=cols)

    def render_semaforo(valor):
        v = str(valor).lower().strip()
        if v.startswith("vac"): color = "#00E676"
        elif v.startswith("par"): color = "#FFD600"
        elif v.startswith("com"): color = "#FF1744"
        else: color = "#BDBDBD"
        return f"<div style='display:flex; justify-content:center;'><span class='traffic-light' style='background-color:{color};'></span></div>"

    def preparar_html_tabla(df_zone, title):
        display = df_zone.copy()
        display["Destino"] = display["Destino"].replace("", "—")
        display["Fecha Despacho"] = display["Fecha Despacho"].replace("", "—")
        display["Ocupacion_html"] = display["Ocupacion"].apply(render_semaforo)
        
        display = display[["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion_html"]]
        display.columns = ["UBI", "DESTINO", "FECHA", "ESTADO"]

        table_html = display.to_html(escape=False, index=False, border=0)

        html_final = (
            f"<div class='table-wrapper'>"
            f"<div class='zone-title'>{title}</div>"
            f"{table_html}"
            f"</div>"
        )
        return html_final

    colJ, colD = st.columns(2, gap="medium")
    with colJ: st.markdown(preparar_html_tabla(zona_j, "ZONA J"), unsafe_allow_html=True)
    with colD: st.markdown(preparar_html_tabla(zona_d, "ZONA D"), unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ Error")
    st.exception(e)
