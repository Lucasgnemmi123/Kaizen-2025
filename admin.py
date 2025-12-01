import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# ---------- CONFIGURACIÓN ----------
st.set_page_config(
    page_title="Gestión Kaizen",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CSS ESTABLE Y CORRECTO ----------
st.markdown("""
<style>
    /* Layout */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 98% !important;
    }
    header, footer { display: none !important; }

    /* Centrado vertical */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Inputs */
    div[data-baseweb="input"], 
    div[data-baseweb="select"] > div {
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

    /* Badge */
    .id-badge {
        height: 45px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 800;
        border-radius: 6px;
        border: 1px solid rgba(0,0,0,0.1);
        width: 100%;
    }
    .bg-vacia { background-color: #d1e7dd; color: #0f5132; border-color: #badbcc; } 
    .bg-parcial { background-color: #fff3cd; color: #664d03; border-color: #ffecb5; } 
    .bg-completa { background-color: #f8d7da; color: #842029; border-color: #f5c2c7; } 

    /* Botones con clases específicas */
    .btn-parcial {
        background: #198754 !important;
        color: white !important;
    }
    .btn-parcial:hover { background: #146c43 !important; }

    .btn-full {
        background: #dc3545 !important;
        color: white !important;
    }
    .btn-full:hover { background: #b02a37 !important; }

    .btn-reset {
        background: #6c757d !important;
        color: white !important;
    }
    .btn-reset:hover { background: #565e64 !important; }

    /* Botón base */
    div[data-testid="stButton"] button {
        height: 45px !important;
        width: 100% !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        font-size: 14px;
    }

    hr { margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# ---------- GOOGLE SHEETS ----------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def conectar():
    return gspread.authorize(
        Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPES)
    )

SHEET_ID = "1M9Sccc-3bA33N1MNJtkTCcrDSKK_wfRjeDnqxsrlEtA"
HOJA_NOMBRE = "Hoja 1"

client = conectar()
sheet = client.open_by_key(SHEET_ID).worksheet(HOJA_NOMBRE)

# ---------- FUNCIONES ----------
def get_data():
    return pd.DataFrame(sheet.get_all_records())

def get_fechas(actual):
    lista = [(datetime.now() + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(3)]
    if actual and actual not in lista:
        lista.insert(0, actual)
    return lista

def accion(pre, dest, fecha, tipo):
    try:
        row = sheet.find(str(pre), in_column=1).row
        estado = "Vacia"

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

    except Exception as e:
        st.error(f"Error: {e}")

# ---------- UI ----------
df = get_data()

# Encabezados
h1, h2, h3, h4 = st.columns([1, 3, 2, 4.5])
h1.markdown("<div style='text-align:center; font-weight:700; color:#6c757d;'>UBI</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:700; color:#6c757d;'>DESTINO</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:700; color:#6c757d;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:700; color:#6c757d;'>ACCIONES</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Filas dinámicas
for _, row in df.iterrows():
    pre = str(row["Pre-Stage"])
    ocup = str(row["Ocupacion"])

    css = "bg-vacia"
    if ocup == "Parcial": css = "bg-parcial"
    elif ocup == "Completa": css = "bg-completa"

    with st.container():
        c1, c2, c3, c4 = st.columns([1, 3, 2, 4.5])

        # UBI
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)

        # DESTINO
        with c2:
            new_dest = st.text_input("dest", value=str(row["Destino"]),
                                     key=f"d_{pre}", label_visibility="collapsed")

        # FECHA
        with c3:
            ops = get_fechas(str(row["Fecha Despacho"]))
            idx = ops.index(str(row["Fecha Despacho"])) if str(row["Fecha Despacho"]) in ops else 0
            new_date = st.selectbox("fecha", options=ops, index=idx,
                                    key=f"f_{pre}", label_visibility="collapsed")

        # BOTONES
        with c4:
            b1, b2, b3 = st.columns([1, 1, 1])

            with b1:
                if st.button("Parcial", key=f"s_{pre}"):
                    st.markdown("<style>#s_"+pre+" button{}</style>", unsafe_allow_html=True)
                    if accion(pre, new_dest, new_date, "parcial"): st.rerun()
                st.markdown("<style>#s_"+pre+" button{}</style>", unsafe_allow_html=True)

            with b2:
                if st.button("Lleno", key=f"l_{pre}"):
                    if accion(pre, new_dest, new_date, "full"): st.rerun()

            with b3:
                if st.button("Reestablecer", key=f"r_{pre}"):
                    if accion(pre, new_dest, new_date, "reset"): st.rerun()

    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)
