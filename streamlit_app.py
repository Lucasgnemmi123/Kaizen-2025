import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
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

REFRESH_INTERVAL = 300  # segundos

# ---------- AUTO REFRESH (COMPATIBLE) ----------
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
            <div style='width:{ancho}px; height:60px; border:1px dashed #ccc; 
            display:flex; align-items:center; justify-content:center; 
            font-size:10px; color:#999; margin:auto;'>
            Sin Logo
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

# ---------- ESTILOS CSS (MODO TV MAXIMIZADO) ----------
estilo_tv = """
<style>
    /* 1. ELIMINAR TODOS LOS MÁRGENES INNECESARIOS */
    .block-container {
        padding-top: 0.5rem !important;   /* Pegado arriba */
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Ocultar elementos de Streamlit */
    header[data-testid="stHeader"], footer { display: none !important; }
    #MainMenu { visibility: hidden; }
    
    /* Fondo Blanco puro */
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
        background-color: #ffffff;
    }

    /* ESTILO TABLAS GIGANTES */
    
    /* Contenedor */
    .table-card {
        border: 2px solid #444;
        margin-top: 10px;
    }

    /* Título ZONA J / D */
    .zone-header {
        background-color: #000;
        color: #FFD700; /* Dorado */
        padding: 8px;
        font-size: 36px; /* Muy grande */
        font-weight: 900;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    /* Encabezados de Columna (Rojos) */
    thead th {
        background-color: #d40511;
        color: white;
        font-size: 28px;
        font-weight: 700;
        padding: 10px;
        text-align: center;
        border: 1px solid #999;
    }

    /* Datos (Celdas) */
    tbody td {
        font-size: 28px; /* Texto Gigante */
        font-weight: 700;
        color: #000;
        padding: 10px;
        border: 1px solid #bbb;
        vertical-align: middle;
        height: 60px; /* Altura mínima fila */
    }

    /* Zebra Striping */
    tbody tr:nth-of-type(even) { background-color: #f2f2f2; }
    tbody tr:nth-of-type(odd) { background-color: #ffffff; }

    /* Alineación Columnas */
    tbody td:nth-child(1) { text-align: center; width: 12%; } /* Ubi */
    tbody td:nth-child(2) { text-align: left; width: 48%; padding-left: 15px; } /* Destino */
    tbody td:nth-child(3) { text-align: center; width: 25%; } /* Fecha */
    tbody td:nth-child(4) { text-align: center; width: 15%; } /* Estado */

    /* Semáforo Gigante */
    .traffic-light {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-block;
        border: 2px solid rgba(0,0,0,0.4);
    }
    
    /* Estilo para la hora en el header */
    .time-display {
        font-size: 32px;
        font-weight: 900;
        text-align: center;
        color: #333;
        margin-top: 15px; /* Centrado vertical con logos */
    }
</style>
"""
st.markdown(estilo_tv, unsafe_allow_html=True)

# ---------- HEADER COMPACTO ----------
# Usamos columnas para poner logos y hora en una sola fila
h_col1, h_col2, h_col3 = st.columns([1, 4, 1])

with h_col1:
    cargar_imagen("assets/DHL.png", 120)

with h_col2:
    # Hora en grande en el centro, sin título amarillo
    hora_chile = datetime.now(ZoneInfo("America/Santiago")).strftime("%H:%M:%S")
    st.markdown(f"<div class='time-display'>🕒 {hora_chile} (GMT-3)</div>", unsafe_allow_html=True)

with h_col3:
    # Alineado a la derecha
    with st.container():
        st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)
        cargar_imagen("assets/Aramark.png", 120)
        st.markdown("</div>", unsafe_allow_html=True)

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
            color = "#00FF00" # Lime
        elif v.startswith("par"):
            color = "#FFD700" # Gold
        elif v.startswith("com"):
            color = "#FF0000" # Red
        else:
            color = "#DDDDDD"
        return f"<span class='traffic-light' style='background-color:{color};'></span>"

    def preparar_html_tabla(df_zone, title):
        display = df_zone.copy()
        display["Destino"] = display["Destino"].replace("", "—")
        display["Fecha Despacho"] = display["Fecha Despacho"].replace("", "—")
        display["Ocupacion_html"] = display["Ocupacion"].apply(render_semaforo)
        
        # Columnas renombradas corto para ahorrar espacio
        display = display[["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion_html"]]
        display.columns = ["UBI", "DESTINO", "FECHA DESPACHO", "ESTADO"]

        table_html = display.to_html(escape=False, index=False, border=0)

        html_final = (
            f"<div class='table-card'>"
            f"<div class='zone-header'>{title}</div>"
            f"{table_html}"
            f"</div>"
        )
        return html_final

    # Columnas principales
    colJ, colD = st.columns(2, gap="medium")

    with colJ:
        st.markdown(preparar_html_tabla(zona_j, "ZONA J"), unsafe_allow_html=True)

    with colD:
        st.markdown(preparar_html_tabla(zona_d, "ZONA D"), unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ Error de conexión con Google Sheets")
    st.exception(e)
