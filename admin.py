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

# ---------- CSS PREMIUM (COLORES SÓLIDOS Y ELEGANTES) ----------
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

    /* 3. IGUALAR ALTURAS (50px) - Aspecto Sólido */
    
    /* Inputs y Selects */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        height: 50px !important;
        min-height: 50px !important;
        background-color: #f8f9fa !important; /* Gris muy suave, no blanco puro */
        border-radius: 8px !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05); /* Sombra interna sutil */
    }
    div[data-baseweb="base-input"] input {
        height: 48px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #495057 !important;
    }

    /* Badge UBI */
    .id-badge {
        height: 50px !important;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 800;
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 4. ESTILOS DE BOTONES PRO */
    
    /* Estilo Base para TODOS los botones */
    div[data-testid="stButton"] button {
        height: 50px !important;
        width: 100%;
        border: none !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Efecto al presionar */
    div[data-testid="stButton"] button:active {
        transform: scale(0.98) !important;
        box-shadow: 0 2px 3px rgba(0,0,0,0.1) !important;
    }

    /* --- COLORES PERSONALIZADOS (SIN BLANCO) --- */
    
    /* 1. BOTÓN PARCIAL (VERDE ESMERALDA) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(145deg, #10B981, #059669) !important; /* Emerald gradient */
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button:hover {
        background: #047857 !important; /* Darker Emerald */
        color: white !important;
        box-shadow: 0 6px 10px rgba(16, 185, 129, 0.3) !important;
    }

    /* 2. BOTÓN LLENO (ROJO CARMESÍ) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background: linear-gradient(145deg, #EF4444, #DC2626) !important; /* Red gradient */
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button:hover {
        background: #B91C1C !important; /* Darker Red */
        color: white !important;
        box-shadow: 0 6px 10px rgba(239, 68, 68, 0.3) !important;
    }

    /* 3. BOTÓN REESTABLECER (GRIS PIZARRA) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background: linear-gradient(145deg, #6B7280, #4B5563) !important; /* Cool Gray gradient */
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button:hover {
        background: #374151 !important; /* Darker Gray */
        color: white !important;
        box-shadow: 0 6px 10px rgba(107, 114, 128, 0.3) !important;
    }

    /* Colores Estado ID (Pasteles elegantes) */
    .bg-vacia { background-color: #ECFDF5; color: #065F46; border-color: #A7F3D0; } /* Mint */
    .bg-parcial { background-color: #FFFBEB; color: #92400E; border-color: #FDE68A; } /* Amber */
    .bg-completa { background-color: #FEF2F2; color: #991B1B; border-color: #FECACA; } /* Rose */

    hr { margin: 12px 0; border-color: #e5e7eb; }

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
h1.markdown("<div style='text-align:center; font-weight:700; color:#6B7280; font-size:13px; letter-spacing:1px;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:700; color:#6B7280; font-size:13px; letter-spacing:1px;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:700; color:#6B7280; font-size:13px; letter-spacing:1px;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:700; color:#6B7280; font-size:13px; letter-spacing:1px;'>ACCIONES</div>", unsafe_allow_html=True)
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
        
        # 1. UBI
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        # 2. DESTINO
        with c2:
            new_dest = st.text_input("D", value=str(row['Destino']), key=f"d_{pre}", label_visibility="collapsed", placeholder="Ingresa destino...")
            
        # 3. FECHA
        with c3:
            ops = get_fechas(str(row['Fecha Despacho']))
            idx = ops.index(str(row['Fecha Despacho'])) if str(row['Fecha Despacho']) in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx, key=f"f_{pre}", label_visibility="collapsed")
            
        # 4. BOTONES PRO
        with c4:
            b1, b2, b3 = st.columns([1, 0.9, 1.3], gap="small")
            
            with b1:
                if st.button("Parcial", icon=":material/save:", key=f"s_{pre}"):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                if st.button("Lleno", icon=":material/lock:", key=f"l_{pre}"):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                if st.button("Reestablecer", icon=":material/refresh:", key=f"r_{pre}"):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)
