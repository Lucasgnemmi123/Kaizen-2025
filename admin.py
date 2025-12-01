import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time

# ---------- CONFIGURACIÓN ----------
st.set_page_config(
    page_title="Gestión Kaizen",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CSS BLINDADO (NO MÁS BLANCO) ----------
st.markdown("""
<style>
    /* 1. Layout y Reset */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 98% !important;
    }
    header, footer { display: none !important; }

    /* 2. Alineación Vertical */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    /* 3. INPUTS Y SELECTS (Altura 45px - Gris suave) */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        height: 45px !important;
        min-height: 45px !important;
        background-color: #f1f3f5 !important; /* Gris muy claro */
        border-radius: 6px !important;
        border: 1px solid #ced4da !important;
    }
    div[data-baseweb="base-input"] input {
        height: 43px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #212529 !important;
    }

    /* 4. BADGE DE IDENTIFICACIÓN */
    .id-badge {
        height: 45px !important;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 800;
        border-radius: 6px;
        border: 1px solid rgba(0,0,0,0.1);
        text-shadow: 0 1px 1px rgba(255,255,255,0.4);
    }

    /* 5. ESTILOS DE BOTONES (SOLUCIÓN DEFINITIVA) */
    
    /* Reseteo agresivo de TODOS los botones */
    div[data-testid="stButton"] button {
        height: 45px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: white !important;
        transition: all 0.15s ease-in-out !important;
        background-image: none !important; /* Quita gradientes default */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* Prevenir que se pongan blancos al hacer click o focus */
    div[data-testid="stButton"] button:focus, 
    div[data-testid="stButton"] button:active,
    div[data-testid="stButton"] button:focus-visible {
        box-shadow: none !important;
        outline: none !important;
        border: none !important;
        color: white !important; /* Mantiene texto blanco */
    }

    /* --- INYECCIÓN DE COLORES --- */
    /* Usamos selectores jerárquicos para pintar cada botón según su columna */

    /* === BOTÓN 1: PARCIAL (VERDE) === */
    /* Columna principal 4 -> Columna anidada 1 */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background-color: #198754 !important;
    }
    /* Hover Verde Oscuro */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button:hover {
        background-color: #146c43 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(25, 135, 84, 0.4) !important;
    }
    /* Active Verde */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button:active {
        background-color: #0f5132 !important;
    }

    /* === BOTÓN 2: LLENO (ROJO) === */
    /* Columna principal 4 -> Columna anidada 2 */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background-color: #dc3545 !important;
    }
    /* Hover Rojo Oscuro */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button:hover {
        background-color: #b02a37 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4) !important;
    }
    /* Active Rojo */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button:active {
        background-color: #842029 !important;
    }

    /* === BOTÓN 3: REESTABLECER (GRIS) === */
    /* Columna principal 4 -> Columna anidada 3 */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background-color: #6c757d !important;
    }
    /* Hover Gris Oscuro */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button:hover {
        background-color: #565e64 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(108, 117, 125, 0.4) !important;
    }
    /* Active Gris */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button:active {
        background-color: #3d4246 !important;
    }

    /* Colores Estado ID */
    .bg-vacia { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; } 
    .bg-parcial { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; } 
    .bg-completa { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; } 

    hr { margin: 12px 0; border-color: #dee2e6; }

</style>
""", unsafe_allow_html=True)

# ---------- CONEXIÓN ----------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def conectar():
    try:
        return gspread.authorize(Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPES))
    except: st.stop()

SHEET_ID = "1M9Sccc-3bA33N1MNJtkTCcrDSKK_wfRjeDnqxsrlEtA"
HOJA_NOMBRE = "Hoja 1"
client = conectar()
sheet = client.open_by_key(SHEET_ID).worksheet(HOJA_NOMBRE)

# ---------- LÓGICA ----------
def get_data():
    return pd.DataFrame(sheet.get_all_records())

def get_fechas(actual):
    lista = [(datetime.now() + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(3)]
    if actual and actual not in lista: lista.insert(0, actual)
    return lista

def accion(pre, dest, fecha, tipo):
    try:
        row = sheet.find(str(pre), in_column=1).row
        estado, msg = "Vacia", ""
        
        if tipo == "reset":
            dest, fecha, estado = "", "", "Vacia"
            msg = f"♻️ {pre} Liberado"
        elif tipo == "parcial":
            estado = "Parcial" if dest else "Vacia"
            msg = f"💾 {pre} Guardado"
        elif tipo == "full":
            if not dest:
                st.toast("⚠️ Falta Destino", icon="⚠️")
                return
            estado = "Completa"
            msg = f"🛑 {pre} FULL"

        sheet.update_cell(row, 2, dest)
        sheet.update_cell(row, 3, fecha)
        sheet.update_cell(row, 4, estado)
        st.toast(msg)
        return True
    except Exception as e: st.error(f"Error: {e}")

# ---------- INTERFAZ ----------

# Encabezados
h1, h2, h3, h4 = st.columns([1, 3, 2, 4.5]) 
h1.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px; letter-spacing:0.5px;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px; letter-spacing:0.5px;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px; letter-spacing:0.5px;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px; letter-spacing:0.5px;'>ACCIONES</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

df = get_data()

for _, row in df.iterrows():
    pre = str(row['Pre-Stage'])
    ocup = str(row['Ocupacion'])
    css = "bg-vacia"
    if ocup == "Parcial": css = "bg-parcial"
    elif ocup == "Completa": css = "bg-completa"

    with st.container():
        # Columnas
        c1, c2, c3, c4 = st.columns([1, 3, 2, 4.5], gap="small")
        
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        with c2:
            new_dest = st.text_input("D", value=str(row['Destino']), key=f"d_{pre}", label_visibility="collapsed", placeholder="Destino...")
            
        with c3:
            ops = get_fechas(str(row['Fecha Despacho']))
            idx = ops.index(str(row['Fecha Despacho'])) if str(row['Fecha Despacho']) in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx, key=f"f_{pre}", label_visibility="collapsed")
            
        with c4:
            b1, b2, b3 = st.columns([1, 0.9, 1.3], gap="small")
            
            with b1:
                # Usamos use_container_width=True para asegurar que llene el espacio del selector CSS
                if st.button("Parcial", icon=":material/save:", key=f"s_{pre}", use_container_width=True):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                if st.button("Lleno", icon=":material/lock:", key=f"l_{pre}", use_container_width=True):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                if st.button("Reestablecer", icon=":material/refresh:", key=f"r_{pre}", use_container_width=True):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
