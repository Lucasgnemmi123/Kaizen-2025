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

# ---------- AUTO REFRESH (COMPATIBLE) ----------
st.markdown(
    f'<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">',
    unsafe_allow_html=True
)

# ---------- FUNCIÓN: CONVERTIR IMAGEN A BASE64 ----------
# Esto permite poner las imágenes dentro del HTML directamente para control total
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return ""

# Cargar imágenes en memoria
img_dhl = get_image_base64("assets/DHL.png")
img_aramark = get_image_base64("assets/Aramark.png")

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

# ---------- ESTILOS CSS (TABLAS FIJAS Y HEADER FLEX) ----------
estilo_tv = """
<style>
    /* 1. LAYOUT FULL SCREEN */
    .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* Ocultar elementos nativos de Streamlit */
    header[data-testid="stHeader"], footer, #MainMenu { display: none !important; }
    
    body { background-color: #ffffff; font-family: 'Arial', sans-serif; }

    /* 2. HEADER FLEXBOX (LOGOS Y HORA) */
    .header-container {
        display: flex;
        justify-content: space-between; /* Logos a los extremos */
        align-items: center; /* Centrado vertical perfecto */
        width: 100%;
        margin-bottom: 15px;
        background: white;
        padding: 5px 0;
        border-bottom: 2px solid #ddd;
    }
    
    .logo-box {
        width: 20%; /* Espacio para logo */
        display: flex;
        justify-content: center;
    }
    
    .logo-img {
        max-height: 80px; /* Altura máxima logo */
        max-width: 100%;
        width: auto;
        object-fit: contain;
    }

    .time-box {
        width: 60%;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 900;
        color: #333;
    }

    /* 3. TABLAS PERFECTAMENTE ALINEADAS */
    .table-wrapper {
        border: 2px solid #333;
        margin-bottom: 0px;
    }

    .zone-title {
        background-color: #000;
        color: #FFD700;
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        padding: 5px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed; /* <--- CLAVE: Fija el ancho de columnas */
    }

    /* Definición estricta de anchos de columna */
    /* Col 1: UBI (15%) */
    th:nth-child(1), td:nth-child(1) { width: 15%; text-align: center !important; }
    
    /* Col 2: DESTINO (45%) */
    th:nth-child(2), td:nth-child(2) { width: 45%; }
    
    /* Col 3: FECHA (25%) */
    th:nth-child(3), td:nth-child(3) { width: 25%; text-align: center !important; }
    
    /* Col 4: ESTADO (15%) */
    th:nth-child(4), td:nth-child(4) { width: 15%; text-align: center !important; }

    /* Estilos de Texto y Color */
    thead th {
        background-color: #d40511;
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 12px 5px;
        vertical-align: middle;
        text-transform: uppercase;
        border: 1px solid #999;
    }

    tbody td {
        font-size: 1.4rem;
        font-weight: 700;
        color: #000;
        padding: 8px 5px;
        border: 1px solid #ccc;
        vertical-align: middle;
        height: 55px; /* Altura mínima fila */
    }

    /* Alineación específica del CONTENIDO de Destino */
    /* El encabezado "DESTINO" estará centrado por defecto del th, 
       pero el dato se lee mejor a la izquierda. Si quieres el dato centrado,
       cambia 'left' por 'center' abajo */
    tbody td:nth-child(2) {
        text-align: left !important; 
        padding-left: 15px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Círculo Semáforo */
    .traffic-light {
        height: 35px;
        width: 35px;
        border-radius: 50%;
        display: inline-block;
        border: 2px solid rgba(0,0,0,0.2);
    }
    
    /* Filas alternas */
    tbody tr:nth-child(even) { background-color: #f4f4f4; }
</style>
"""
st.markdown(estilo_tv, unsafe_allow_html=True)

# ---------- HEADER HTML (RESPONSIVE) ----------
hora_chile = datetime.now(ZoneInfo("America/Santiago")).strftime("%H:%M:%S")

header_html = f"""
<div class="header-container">
    <div class="logo-box">
        <img src="{img_dhl}" class="logo-img" alt="DHL">
    </div>
    <div class="time-box">
        🕒 {hora_chile}
    </div>
    <div class="logo-box">
        <img src="{img_aramark}" class="logo-img" alt="Aramark">
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

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

    def render_semaforo(valor):
        v = str(valor).lower().strip()
        if v.startswith("vac"):
            color = "#00E676" # Verde brillante
        elif v.startswith("par"):
            color = "#FFD600" # Amarillo
        elif v.startswith("com"):
            color = "#FF1744" # Rojo vivo
        else:
            color = "#BDBDBD"
        return f"<div style='display:flex; justify-content:center;'><span class='traffic-light' style='background-color:{color};'></span></div>"

    def preparar_html_tabla(df_zone, title):
        display = df_zone.copy()
        display["Destino"] = display["Destino"].replace("", "—")
        display["Fecha Despacho"] = display["Fecha Despacho"].replace("", "—")
        display["Ocupacion_html"] = display["Ocupacion"].apply(render_semaforo)
        
        display = display[["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion_html"]]
        display.columns = ["UBI", "DESTINO", "FECHA", "ESTADO"]

        # Generar HTML plano
        table_html = display.to_html(escape=False, index=False, border=0)

        html_final = (
            f"<div class='table-wrapper'>"
            f"<div class='zone-title'>{title}</div>"
            f"{table_html}"
            f"</div>"
        )
        return html_final

    # Columnas de Streamlit para las dos tablas
    colJ, colD = st.columns(2, gap="medium")

    with colJ:
        st.markdown(preparar_html_tabla(zona_j, "ZONA J"), unsafe_allow_html=True)

    with colD:
        st.markdown(preparar_html_tabla(zona_d, "ZONA D"), unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ Error de conexión o datos")
    st.exception(e)
