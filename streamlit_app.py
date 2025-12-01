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
            <div style='width:{ancho}px; height:80px; border:2px dashed #ccc; 
            display:flex; align-items:center; justify-content:center; 
            font-size:12px; color:#999; border-radius:8px; margin:auto;'>
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

# ---------- ESTILOS CSS (MODO TV / FULL SCREEN) ----------
estilo_tv = """
<style>
    /* 1. FORZAR FULL SCREEN Y QUITAR MÁRGENES */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important; /* Usa todo el ancho disponible */
    }
    
    /* Ocultar elementos de Streamlit que no sirven en TV */
    header[data-testid="stHeader"], footer {
        display: none !important;
    }
    
    #MainMenu {
        visibility: hidden;
    }

    /* Fuente Global */
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif; /* Arial es muy legible en pantallas */
        background-color: #ffffff;
    }

    /* Título Principal */
    .main-title-container {
        background: #F7DC6F; /* Amarillo DHL */
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #000;
    }
    .main-title-text {
        font-size: 40px; /* Título Gigante */
        font-weight: 900;
        color: #d40511; /* Rojo DHL */
        text-transform: uppercase;
        margin: 0;
        line-height: 1;
    }

    /* Contenedor Tablas */
    .table-card {
        border: 2px solid #333;
        border-radius: 0px; /* Bordes rectos se ven mejor en tablas técnicas */
        margin-bottom: 0px;
        background: white;
    }

    /* Encabezado ZONA J / ZONA D */
    .zone-header {
        background-color: #000;
        color: #F7DC6F; /* Amarillo sobre negro */
        padding: 10px;
        font-size: 32px; /* Muy grande */
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
    }

    /* TABLA GENERAL */
    table {
        width: 100%;
        border-collapse: collapse;
    }

    /* Encabezados de Columnas */
    thead th {
        background-color: #d40511;
        color: white;
        font-size: 26px; /* Letra grande encabezados */
        font-weight: 700;
        padding: 12px 5px;
        text-align: center;
        border: 1px solid #999;
    }

    /* Celdas de Datos */
    tbody td {
        font-size: 26px; /* Letra grande datos */
        font-weight: 700; /* Negrita para legibilidad */
        color: #000;
        padding: 12px 8px;
        border: 1px solid #bbb;
        vertical-align: middle;
    }

    /* Zebra Striping */
    tbody tr:nth-of-type(even) {
        background-color: #f0f0f0; /* Gris claro */
    }
    tbody tr:nth-of-type(odd) {
        background-color: #ffffff; /* Blanco */
    }

    /* Ajuste Específico de Columnas */
    
    /* Columna 1: Ubicación (Centrada) */
    tbody td:nth-child(1) { text-align: center; width: 15%; }
    
    /* Columna 2: Destino (Izquierda, toma el espacio sobrante) */
    tbody td:nth-child(2) { text-align: left; width: 45%; }
    
    /* Columna 3: Fecha (Centrada) */
    tbody td:nth-child(3) { text-align: center; width: 25%; }
    
    /* Columna 4: Estado/Semáforo (Centrada) */
    tbody td:nth-child(4) { text-align: center; width: 15%; }


    /* Semáforo Grande */
    .traffic-light {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: inline-block;
        border: 2px solid rgba(0,0,0,0.3);
    }
    
    /* Footer */
    .footer-note {
        font-size: 20px;
        font-weight: bold;
        color: #555;
        text-align: center;
        margin-top: 15px;
    }
</style>
"""
st.markdown(estilo_tv, unsafe_allow_html=True)

# ---------- ENCABEZADO ----------
# Ajustamos columnas (más espacio al centro)
header_left, header_center, header_right = st.columns([1.5, 7, 1.5])

with header_left:
    cargar_imagen("assets/DHL.png", 180) # Logo un poco más grande

with header_center:
    st.markdown(
        """
        <div class="main-title-container">
            <p class="main-title-text">UBICACIÓN DE PREPARACIONES</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:
    cargar_imagen("assets/Aramark.png", 180) # Logo un poco más grande

# ---------- HORA GMT-3 ----------
hora_chile = datetime.now(ZoneInfo("America/Santiago")).strftime("%H:%M:%S")
st.markdown(f"<p style='text-align:center; font-size:24px; color:#000; font-weight:bold; margin-top:-10px; margin-bottom:15px;'>🕒 ACTUALIZADO: {hora_chile}</p>", unsafe_allow_html=True)

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
            color = "#00FF00" # Verde Brillante (Lime)
        elif v.startswith("par"):
            color = "#FFD700" # Amarillo Oro
        elif v.startswith("com"):
            color = "#FF0000" # Rojo Puro
        else:
            color = "#CCCCCC"
        return f"<span class='traffic-light' style='background-color:{color};'></span>"

    def preparar_html_tabla(df_zone, title):
        display = df_zone.copy()
        display["Destino"] = display["Destino"].replace("", "—")
        display["Fecha Despacho"] = display["Fecha Despacho"].replace("", "—")
        display["Ocupacion_html"] = display["Ocupacion"].apply(render_semaforo)
        
        display = display[["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion_html"]]
        display.columns = ["UBI", "DESTINO", "FECHA", "ESTADO"] # Nombres cortos encabezados

        table_html = display.to_html(escape=False, index=False, border=0)

        html_final = (
            f"<div class='table-card'>"
            f"<div class='zone-header'>{title}</div>"
            f"{table_html}"
            f"</div>"
        )
        return html_final

    # Columas con un hueco pequeño en el medio (gap="small") para aprovechar espacio
    colJ, colD = st.columns(2, gap="small")

    with colJ:
        st.markdown(preparar_html_tabla(zona_j, "ZONA J"), unsafe_allow_html=True)

    with colD:
        st.markdown(preparar_html_tabla(zona_d, "ZONA D"), unsafe_allow_html=True)

    # Footer
    st.markdown(
        f"<div class='footer-note'>RECARGA EN {REFRESH_INTERVAL} SEG</div>",
        unsafe_allow_html=True
    )

except Exception as e:
    st.error("⚠️ Error de conexión")
    st.exception(e)
