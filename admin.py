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

# ---------- CSS AGRESIVO (COLORES SÓLIDOS) ----------
st.markdown("""
<style>
    /* 1. Ajustes del Layout */
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

    /* 3. IGUALAR ALTURAS (45px) */
    
    /* Inputs y Selects */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        height: 45px !important;
        min-height: 45px !important;
        background-color: white !important;
        border-radius: 6px !important;
        border: 1px solid #ced4da !important;
    }
    div[data-baseweb="base-input"] input {
        height: 43px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }

    /* Badge UBI */
    .id-badge {
        height: 45px !important;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 900;
        border-radius: 6px;
        border: 1px solid rgba(0,0,0,0.1);
        text-shadow: 0 1px 1px rgba(255,255,255,0.4);
    }

    /* 4. ESTILOS DE BOTONES (FIX DEFINITIVO) */
    
    /* Base para TODOS los botones */
    div[data-testid="stButton"] button {
        height: 45px !important;
        width: 100%;
        border: none !important;
        border-radius: 6px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: white !important; /* Texto blanco SIEMPRE */
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        transition: background-color 0.2s, transform 0.1s !important;
    }
    
    /* Efecto al presionar (Active) */
    div[data-testid="stButton"] button:active {
        transform: scale(0.98) !important;
    }

    /* --- COLORES ESPECÍFICOS (USANDO SELECTORES DE ORDEN) --- */
    
    /* NOTA: La estructura es: Columna Principal 4 -> contiene 3 Columnas Anidadas */

    /* 1. BOTÓN PARCIAL (VERDE) */
    /* Seleccionamos el botón dentro de la 1ra columna anidada de la 4ta columna principal */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background-color: #27ae60 !important; /* Verde solido */
    }
    /* Hover Verde */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button:hover {
        background-color: #219150 !important; /* Verde más oscuro */
        color: white !important;
        border: none !important;
    }

    /* 2. BOTÓN LLENO (ROJO) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background-color: #c0392b !important; /* Rojo solido */
    }
    /* Hover Rojo */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button:hover {
        background-color: #a93226 !important; /* Rojo más oscuro */
        color: white !important;
        border: none !important;
    }

    /* 3. BOTÓN REESTABLECER (GRIS AZULADO) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background-color: #5d6d7e !important; /* Gris */
    }
    /* Hover Gris */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button:hover {
        background-color: #34495e !important; /* Gris oscuro */
        color: white !important;
        border: none !important;
    }

    /* Colores Estado ID */
    .bg-vacia { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; } 
    .bg-parcial { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; } 
    .bg-completa { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; } 

    hr { margin: 10px 0; border-color: #ddd; }

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
                st.toast("⚠️ Ingresa un Destino", icon="⚠️")
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
h1.markdown("<div style='text-align:center; font-weight:700; color:#555; font-size:14px;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:700; color:#555; font-size:14px;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:700; color:#555; font-size:14px;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:700; color:#555; font-size:14px;'>PANEL DE ACCIÓN</div>", unsafe_allow_html=True)
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
        
        # 1. UBI
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        # 2. DESTINO
        with c2:
            new_dest = st.text_input("D", value=str(row['Destino']), key=f"d_{pre}", label_visibility="collapsed", placeholder="Destino...")
            
        # 3. FECHA
        with c3:
            ops = get_fechas(str(row['Fecha Despacho']))
            idx = ops.index(str(row['Fecha Despacho'])) if str(row['Fecha Despacho']) in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx, key=f"f_{pre}", label_visibility="collapsed")
            
        # 4. BOTONES (Colores Sólidos forzados por CSS)
        with c4:
            b1, b2, b3 = st.columns([1, 0.9, 1.3], gap="small")
            
            with b1:
                # Botón Verde
                if st.button("Parcial", icon=":material/save:", key=f"s_{pre}"):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                # Botón Rojo
                if st.button("Lleno", icon=":material/lock:", key=f"l_{pre}"):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                # Botón Gris
                if st.button("Reestablecer", icon=":material/refresh:", key=f"r_{pre}"):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
