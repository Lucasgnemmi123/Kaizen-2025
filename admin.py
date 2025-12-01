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

# ---------- CSS PROFESIONAL (SOLUCIÓN DEFINITIVA DE ALTURAS) ----------
st.markdown("""
<style>
    /* 1. Reset Global y Layout */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 98% !important;
    }
    header, footer { display: none !important; }
    
    /* 2. Alineación Vertical (Flexbox) para todas las columnas */
    div[data-testid="column"] {
        display: flex;
        align-items: center; /* Centrado vertical estricto */
        justify-content: center;
        height: 100%;
    }

    /* 3. IGUALAR ALTURAS (LA SOLUCIÓN CLAVE) 
       Forzamos 45px de altura en Inputs, Selects, Botones y Badges */
       
    /* A) Inputs de Texto (Destino) */
    div[data-baseweb="input"] {
        height: 45px !important;
        background-color: white;
        border-radius: 6px;
        border: 1px solid #ced4da;
    }
    div[data-baseweb="base-input"] input {
        height: 43px !important; /* Un poco menos para el borde */
        font-size: 16px !important;
        padding: 0 10px !important;
        font-weight: 500;
        color: #333;
    }

    /* B) Selectbox (Fecha) */
    div[data-baseweb="select"] > div {
        height: 45px !important;
        min-height: 45px !important;
        border-radius: 6px;
        border-color: #ced4da;
        display: flex;
        align-items: center;
    }
    
    /* C) Badge UBI (J01) */
    .id-badge {
        height: 45px !important;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 900;
        border-radius: 6px;
        border: 1px solid rgba(0,0,0,0.15);
        text-shadow: 0 1px 1px rgba(255,255,255,0.4);
    }

    /* 4. BOTONES PROFESIONALES (COLORES SÓLIDOS) */
    div[data-testid="stButton"] button {
        height: 45px !important;
        width: 100%;
        border: none !important;
        border-radius: 6px;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: white !important; /* Texto blanco siempre */
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        filter: brightness(110%); /* Brillar al pasar mouse */
    }

    /* --- INYECCIÓN DE COLORES A LOS BOTONES --- */
    /* Usamos selectores específicos para "pintar" los botones de la última columna */

    /* Botón 1: Parcial -> VERDE */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
    }

    /* Botón 2: Lleno -> ROJO */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    }

    /* Botón 3: Reestablecer -> GRIS */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
    }

    /* Estilos Colores UBI */
    .bg-vacia { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; } 
    .bg-parcial { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; } 
    .bg-completa { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; } 

    /* Separador */
    hr { margin: 10px 0; border-color: #dee2e6; opacity: 0.5; }

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
        # Columnas alineadas
        c1, c2, c3, c4 = st.columns([1, 3, 2, 4.5], gap="small")
        
        # 1. UBI (Badge)
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        # 2. DESTINO (Input)
        with c2:
            new_dest = st.text_input("D", value=str(row['Destino']), key=f"d_{pre}", label_visibility="collapsed", placeholder="Ingresa destino...")
            
        # 3. FECHA (Select)
        with c3:
            ops = get_fechas(str(row['Fecha Despacho']))
            idx = ops.index(str(row['Fecha Despacho'])) if str(row['Fecha Despacho']) in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx, key=f"f_{pre}", label_visibility="collapsed")
            
        # 4. BOTONES (Coloreados por CSS)
        with c4:
            b1, b2, b3 = st.columns([1, 0.9, 1.3], gap="small")
            
            with b1:
                # Botón Verde (CSS auto)
                if st.button("Parcial", icon=":material/save:", key=f"s_{pre}"):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                # Botón Rojo (CSS auto)
                if st.button("Lleno", icon=":material/lock:", key=f"l_{pre}"):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                # Botón Gris (CSS auto)
                if st.button("Reestablecer", icon=":material/refresh:", key=f"r_{pre}"):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
