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

# ---------- ESTILOS CSS (ALINEACIÓN PERFECTA) ----------
st.markdown("""
<style>
    /* 1. Ajustes del Layout */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 98% !important;
    }
    header, footer { display: none !important; }

    /* 2. Alineación Vertical (Flexbox para las columnas) */
    div[data-testid="column"] {
        display: flex;
        align-items: center; /* Centrado vertical */
        justify-content: center;
        height: 100%;
    }

    /* 3. INPUTS Y SELECTS (Altura Forzada 55px) */
    /* Esto afecta a la caja de texto Destino y al Select de Fecha */
    .stTextInput input, div[data-baseweb="select"] > div {
        height: 55px !important;      /* Altura exacta */
        min-height: 55px !important;
        font-size: 18px !important;   /* Letra legible */
        border-radius: 6px;
        border: 1px solid #ced4da;
        line-height: normal;
    }

    /* 4. TARJETA DE IDENTIFICACIÓN (Altura Forzada 55px) */
    /* Esto afecta al cuadro UBI (J-01, etc) */
    .id-badge {
        width: 100%;
        height: 55px !important;      /* MISMA ALTURA EXACTA QUE EL INPUT */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 800;
        border-radius: 6px;
        color: #212529;
        border: 1px solid rgba(0,0,0,0.1);
        box-sizing: border-box;       /* Para que el borde no sume altura extra */
    }

    /* 5. BOTONES (Altura Forzada 55px) */
    div[data-testid="stButton"] button {
        width: 100%;
        height: 55px !important;      /* MISMA ALTURA EXACTA */
        border-radius: 6px;
        border: 1px solid transparent;
        font-weight: 600;
        font-size: 15px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* --- COLORES DE BOTONES --- */
    /* Parcial (Verde) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(1) button {
        background-color: #198754; color: white;
    }
    /* Lleno (Rojo) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(2) button {
        background-color: #dc3545; color: white;
    }
    /* Reestablecer (Gris) */
    div[data-testid="column"]:nth-of-type(4) div[data-testid="column"]:nth-of-type(3) button {
        background-color: #6c757d; color: white;
    }

    /* Colores Estado ID */
    .bg-vacia { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; } 
    .bg-parcial { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; } 
    .bg-completa { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; } 

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
                st.toast("⚠️ Ingresa un Destino", icon="⚠️")
                return
            estado = "Completa"
            msg = f"🛑 {pre} marcado LLENO"

        sheet.update_cell(row, 2, dest)
        sheet.update_cell(row, 3, fecha)
        sheet.update_cell(row, 4, estado)
        st.toast(msg)
        return True
    except Exception as e: st.error(f"Error: {e}")

# ---------- INTERFAZ ----------

# Encabezados
h1, h2, h3, h4 = st.columns([1, 3, 2, 4.5]) 
h1.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d; font-size:14px;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d; font-size:14px;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d; font-size:14px;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:bold; color:#6c757d; font-size:14px;'>ACCIONES</div>", unsafe_allow_html=True)
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
        # Columnas alineadas
        c1, c2, c3, c4 = st.columns([1, 3, 2, 4.5], gap="small")
        
        with c1:
            # Aquí se aplica la clase .id-badge que tiene height: 55px !important
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        with c2:
            # Aquí el CSS fuerza el input a 55px
            new_dest = st.text_input("D", value=str(row['Destino']), key=f"input_dest_{pre}", label_visibility="collapsed", placeholder="Destino...")
            
        with c3:
            ops = get_fechas(str(row['Fecha Despacho']))
            idx = ops.index(str(row['Fecha Despacho'])) if str(row['Fecha Despacho']) in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx, key=f"select_date_{pre}", label_visibility="collapsed")
            
        with c4:
            b1, b2, b3 = st.columns([1, 0.9, 1.3], gap="small")
            
            with b1:
                if st.button("Parcial", icon=":material/save:", key=f"btn_save_{pre}"):
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()

            with b2:
                if st.button("Lleno", icon=":material/lock:", key=f"btn_full_{pre}"):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                if st.button("Reestablecer", icon=":material/refresh:", key=f"btn_reset_{pre}"):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)
