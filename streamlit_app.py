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
        # Placeholder estilizado si no hay imagen
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

# ---------- ESTILOS CSS (MEJORADOS VISUALMENTE) ----------
estilo_mejorado = """
<style>
    /* Reset básico y fuente */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background-color: #f9f9f9; /* Fondo suave para la app */
    }

    /* Título Principal */
    .main-title-container {
        background: linear-gradient(90deg, #FFCC00 0%, #F7DC6F 100%); /* Gradiente DHL */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .main-title-text {
        font-size: 2.5rem;
        font-weight: 800;
        color: #d40511; /* Rojo DHL para contraste o negro #000 */
        text-transform: uppercase;
        margin: 0;
        letter-spacing: 1px;
    }

    /* Contenedor de las Tablas (Card View) */
    .table-card {
        background: white;
        border-radius: 12px;
        padding: 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        overflow: hidden; /* Para respetar bordes redondeados */
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }

    /* Encabezado de Zona (J o D) */
    .zone-header {
        background-color: #333;
        color: #fff;
        padding: 15px;
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: 1px;
    }

    /* La Tabla en sí */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 1.2rem; /* Tamaño grande para TV */
    }

    /* Cabecera de la tabla */
    thead th {
        background-color: #d40511; /* Rojo corporativo o Gris Oscuro */
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 1rem;
        border-bottom: 3px solid #b0040e;
    }

    /* Celdas del cuerpo */
    tbody td {
        padding: 12px 10px;
        border-bottom: 1px solid #eee;
        color: #333;
        vertical-align: middle;
        font-weight: 500;
    }

    /* Zebra Striping (Filas alternas) */
    tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    tbody tr:hover {
        background-color: #fff8e1; /* Highlight al pasar mouse */
    }

    /* Columna Destino (Alineada izquierda y negrita) */
    tbody td:nth-child(2) {
        text-align: left !important;
        font-weight: 700;
        color: #000;
        padding-left: 20px;
    }
    
    /* Demás columnas centradas */
    tbody td:nth-child(1),
    tbody td:nth-child(3),
    tbody td:nth-child(4) {
        text-align: center;
    }

    /* Semáforo */
    .traffic-light {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: inset 0 -2px 5px rgba(0,0,0,0.2); /* Efecto 3D */
        border: 1px solid rgba(0,0,0,0.1);
    }

    /* Footer / Notas */
    .footer-note {
        font-size: 0.9rem;
        color: #777;
        text-align: center;
        margin-top: 20px;
    }
</style>
"""
st.markdown(estilo_mejorado, unsafe_allow_html=True)

# ---------- ENCABEZADO ----------
header_left, header_center, header_right = st.columns([1, 6, 1])

with header_left:
    # Centramos verticalmente la imagen
    st.write("") # Espaciador
    cargar_imagen("assets/DHL.png", 140)

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
    st.write("") # Espaciador
    cargar_imagen("assets/Aramark.png", 140)

# ---------- HORA GMT-3 ----------
hora_chile = datetime.now(ZoneInfo("America/Santiago")).strftime("%H:%M:%S")
st.markdown(f"<p style='text-align:center; font-size:18px; color:#555; font-weight:bold;'>🕒 Última actualización: {hora_chile}</p>", unsafe_allow_html=True)

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

    # Semáforo Lógica
    def render_semaforo(valor):
        v = str(valor).lower().strip()
        if v.startswith("vac"):
            color = "#2ECC71" # Verde
        elif v.startswith("par"):
            color = "#F1C40F" # Amarillo
        elif v.startswith("com"):
            color = "#E74C3C" # Rojo
        else:
            color = "#BDC3C7" # Gris
        return f"<span class='traffic-light' style='background-color:{color};'></span>"

    # Función Generadora de HTML Tabla
    def preparar_html_tabla(df_zone, title):
        display = df_zone.copy()
        display["Destino"] = display["Destino"].replace("", "—")
        display["Fecha Despacho"] = display["Fecha Despacho"].replace("", "—")
        display["Ocupacion_html"] = display["Ocupacion"].apply(render_semaforo)
        
        # Seleccionamos y renombramos
        display = display[["Pre-Stage", "Destino", "Fecha Despacho", "Ocupacion_html"]]
        display.columns = ["UBICACIÓN", "DESTINO", "FECHA", "ESTADO"]

        # Generamos la tabla HTML pura sin estilos inline de pandas
        table_html = display.to_html(escape=False, index=False, border=0)

        # Envolvemos en nuestra estructura de tarjeta CSS
        html_final = (
            f"<div class='table-card'>"
            f"<div class='zone-header'>{title}</div>"
            f"{table_html}"
            f"</div>"
        )
        return html_final

    # Layout de columnas para las tablas
    colJ, colD = st.columns(2, gap="large")

    with colJ:
        st.markdown(preparar_html_tabla(zona_j, "ZONA J"), unsafe_allow_html=True)

    with colD:
        st.markdown(preparar_html_tabla(zona_d, "ZONA D"), unsafe_allow_html=True)

    # Footer
    st.markdown(
        f"<div class='footer-note'>🔄 El tablero se actualizará automáticamente en {REFRESH_INTERVAL} segundos.</div>",
        unsafe_allow_html=True
    )

except Exception as e:
    st.error("⚠️ Error al cargar los datos desde Google Sheets API.")
    st.exception(e)
