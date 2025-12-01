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

# ---------- CSS DEFINITIVO (SIN ERRORES DE COLOR) ----------
st.markdown("""
<style>
    /* 1. Layout Básico */
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

    /* 3. INPUTS Y SELECTS (Altura 45px) */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        height: 45px !important;
        min-height: 45px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="base-input"] input {
        height: 43px !important;
        font-size: 16px !important;
        color: #333 !important;
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
    }

    /* ============================================================
       5. SOLUCIÓN DEFINITIVA A LOS BOTONES
       ============================================================ */

    /* Regla base para TODOS los botones en la app */
    div[data-testid="stButton"] button {
        height: 45px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: none !important; /* Quitamos animaciones que causan parpadeo */
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }

    /* FORZAR TEXTO E ICONOS A BLANCO SIEMPRE */
    div[data-testid="stButton"] button * {
        color: white !important;
        fill: white !important;
    }

    /* --- COLORES POR POSICIÓN (ELIMINANDO EL BLANCO) --- */

    /* BOTÓN 1: PARCIAL (VERDE) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background: #198754 !important; /* Verde solido */
        color: white !important;
    }
    /* Estado Hover (Mouse encima) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button:hover {
        background: #146c43 !important; /* Verde oscuro */
    }
    
    /* BOTÓN 2: LLENO (ROJO) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background: #dc3545 !important; /* Rojo solido */
        color: white !important;
    }
    /* Estado Hover */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button:hover {
        background: #b02a37 !important; /* Rojo oscuro */
    }

    /* BOTÓN 3: REESTABLECER (GRIS) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background: #6c757d !important; /* Gris solido */
        color: white !important;
    }
    /* Estado Hover */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button:hover {
        background: #565e64 !important; /* Gris oscuro */
    }

    /* Evitar que al hacer click se ponga blanco/transparente */
    div[data-testid="stButton"] button:active, div[data-testid="stButton"] button:focus {
        color: white !important;
        border: none !important;
        outline: none !important;
        box-shadow: inset 0 3px 5px rgba(0,0,0,0.2) !important;
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
h1.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:700; color:#6c757d; font-size:13px;'>ACCIONES</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

df = get_data()

for _, row in df.iterrows():
    pre = str(row['Pre-Stage'])
    ocup = str(row['Ocupacion'])
    css = "bg-vacia"
    if ocup == "Parcial": css = "bg-parcial"
    elif ocup == "Completa": css = "bg-completa"

    with st.container():
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
                if st.button("Parcial", icon=":material/save:", key=f"s_{pre}", use_container_width=True):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                if st.button("Lleno", icon=":material/lock:", key=f"l_{pre}", use_container_width=True):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                if st.button("Reestablecer", icon=":material/refresh:", key=f"r_{pre}", use_container_width=True):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
