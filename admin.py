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

# ---------- ESTILOS CSS (ESTILO BOOTSTRAP) ----------
st.markdown("""
<style>
    /* 1. Ajustes del Layout */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 98% !important;
    }
    header, footer { display: none !important; }

    /* 2. Alineación Vertical (Flexbox) */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    /* 3. BOTONES ESTILO BOOTSTRAP */
    div[data-testid="stButton"] button {
        width: 100%;
        height: 50px;       /* Altura fija igual a inputs */
        border-radius: 6px; /* Bordes ligeramente redondeados (Bootstrap style) */
        border: 1px solid transparent;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: 0.5px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* --- COLORES SEMÁNTICOS (BOOTSTRAP) --- */
    
    /* Botón 1: PARCIAL -> Bootstrap Success (Verde) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background-color: #198754; 
        color: white;
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button:hover {
        background-color: #157347;
    }

    /* Botón 2: LLENO -> Bootstrap Danger (Rojo) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background-color: #dc3545; 
        color: white;
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button:hover {
        background-color: #bb2d3b;
    }
    
    /* Botón 3: REESTABLECER -> Bootstrap Secondary (Gris) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background-color: #6c757d; 
        color: white;
    }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button:hover {
        background-color: #5c636a;
    }

    /* 4. INPUTS Y SELECTS */
    .stTextInput input, div[data-baseweb="select"] > div {
        height: 50px;
        min-height: 50px;
        font-size: 16px;
        border-radius: 6px;
        border: 1px solid #ced4da; /* Gris Bootstrap */
    }

    /* 5. TARJETAS DE IDENTIFICACIÓN */
    .id-badge {
        width: 100%;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 800;
        border-radius: 6px;
        color: #212529;
        text-shadow: 0 1px 1px rgba(255,255,255,0.5);
        border: 1px solid rgba(0,0,0,0.1);
    }

    /* Colores Estado */
    .bg-vacia { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; } /* Verde claro */
    .bg-parcial { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; } /* Amarillo claro */
    .bg-completa { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; } /* Rojo claro */

    hr { margin: 15px 0; border-color: #dee2e6; }

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
            msg = f"♻️ {pre} Reestablecido"
        elif tipo == "parcial":
            estado = "Parcial" if dest else "Vacia"
            msg = f"💾 {pre} Guardado (Parcial)"
        elif tipo == "full":
            if not dest:
                st.toast("⚠️ Debes ingresar un Destino", icon="⚠️")
                return
            estado = "Completa"
            msg = f"🛑 {pre} marcado como LLENO"

        sheet.update_cell(row, 2, dest)
        sheet.update_cell(row, 3, fecha)
        sheet.update_cell(row, 4, estado)
        st.toast(msg)
        return True
    except Exception as e: st.error(f"Error: {e}")

# ---------- INTERFAZ ----------

# Encabezados
h1, h2, h3, h4 = st.columns([1, 3, 2, 4.5]) # Damos más espacio a la col 4
h1.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d;'>ACCIONES</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

df = get_data()

for _, row in df.iterrows():
    pre = str(row['Pre-Stage'])
    ocup = str(row['Ocupacion'])
    
    # Estilo badge
    css = "bg-vacia"
    if ocup == "Parcial": css = "bg-parcial"
    elif ocup == "Completa": css = "bg-completa"

    with st.container():
        # Columnas: Ajustamos para que quepan los textos largos
        c1, c2, c3, c4 = st.columns([1, 3, 2, 4.5], gap="small")
        
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        with c2:
            new_dest = st.text_input("D", value=str(row['Destino']), key=f"d{pre}", label_visibility="collapsed", placeholder="Ingresa destino...")
            
        with c3:
            ops = get_fechas(str(row['Fecha Despacho']))
            idx = ops.index(str(row['Fecha Despacho'])) if str(row['Fecha Despacho']) in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx, key=f"f{pre}", label_visibility="collapsed")
            
        with c4:
            # Sub-columnas: Le damos más espacio al botón "Reestablecer" (b3)
            b1, b2, b3 = st.columns([1, 0.9, 1.3], gap="small")
            
            with b1:
                # PARCIAL: Icono Save
                if st.button("Parcial", icon=":material/save:", key=f"s{pre}"):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                # LLENO: Icono Candado/Stop
                if st.button("Lleno", icon=":material/lock:", key=f"f{pre}"):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                # REESTABLECER: Icono Refrescar
                if st.button("Reestablecer", icon=":material/refresh:", key=f"r{pre}"):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)
