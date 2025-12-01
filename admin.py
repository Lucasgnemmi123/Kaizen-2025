import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time

# ---------- CONFIGURACIÓN ----------
st.set_page_config(
    page_title="Admin Panel",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- ESTILOS CSS (PROFESIONAL Y CENTRADO) ----------
st.markdown("""
<style>
    /* 1. Ajustes del Contenedor Principal */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 98% !important;
    }
    header, footer { display: none !important; }

    /* 2. Alineación Vertical Perfecta (Flexbox) */
    /* Esto centra verticalmente los elementos dentro de las columnas */
    div[data-testid="column"] {
        display: flex;
        align-items: center; /* Centro vertical */
        justify-content: center; /* Centro horizontal */
        height: 100%;
    }

    /* 3. Estilos de Botones (GIGANTES Y UNIFORMES) */
    div[data-testid="stButton"] button {
        width: 100%;
        height: 52px; /* Altura forzada para igualar a los inputs */
        font-size: 24px !important; /* Iconos grandes */
        font-weight: 900;
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 0px !important; /* Quitar padding interno para centrar texto */
        line-height: 52px; /* Centrar verticalmente el texto/icono */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Efecto Hover */
    div[data-testid="stButton"] button:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Estilos específicos para botón FULL (Rojo) */
    div[data-testid="stButton"] button:active {
        background-color: #ddd;
    }

    /* 4. Inputs y Selects */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        height: 52px; /* Misma altura que botones */
        font-size: 18px;
        font-weight: bold;
        align-items: center;
    }

    /* 5. ID Badge (El cuadro de color J-01) */
    .id-badge {
        font-size: 26px;
        font-weight: 900;
        text-align: center;
        color: #333;
        padding: 10px 0;
        border-radius: 8px;
        width: 100%;
        border: 2px solid rgba(0,0,0,0.1);
        text-shadow: 0 1px 2px rgba(255,255,255,0.3);
    }

    /* Colores de Estado */
    .status-vacia { background-color: #2ECC71; color: white; border: 2px solid #27AE60; }
    .status-parcial { background-color: #F1C40F; color: black; border: 2px solid #D4AC0D; }
    .status-completa { background-color: #E74C3C; color: white; border: 2px solid #C0392B; }

    /* Separador invisible entre filas */
    .spacer { margin-bottom: 15px; }

</style>
""", unsafe_allow_html=True)

# ---------- CONEXIÓN GOOGLE SHEETS ----------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def conectar_gsheets():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error credenciales: {e}")
        st.stop()

SHEET_ID = "1M9Sccc-3bA33N1MNJtkTCcrDSKK_wfRjeDnqxsrlEtA"
HOJA_NOMBRE = "Hoja 1"
client = conectar_gsheets()
sheet = client.open_by_key(SHEET_ID).worksheet(HOJA_NOMBRE)

# ---------- LÓGICA ----------
def obtener_datos():
    return pd.DataFrame(sheet.get_all_records())

def generar_fechas(fecha_actual):
    opciones = []
    hoy = datetime.now()
    for i in range(3):
        opciones.append((hoy + timedelta(days=i)).strftime("%d-%m-%Y"))
    if fecha_actual and fecha_actual not in opciones:
        opciones.insert(0, fecha_actual)
    return opciones

def procesar_accion(pre, dest, fecha, tipo):
    try:
        cell = sheet.find(str(pre), in_column=1)
        row = cell.row
        
        estado = "Vacia"
        msg = ""
        
        if tipo == "reset":
            dest, fecha, estado = "", "", "Vacia"
            msg = f"♻️ {pre} Liberado"
        elif tipo == "parcial":
            if not dest: estado = "Vacia"
            else: estado = "Parcial"
            msg = f"💾 {pre} Guardado"
        elif tipo == "full":
            if not dest:
                st.toast("⚠️ Falta Destino", icon="⚠️")
                return
            estado = "Completa"
            msg = f"🛑 {pre} es FULL"

        sheet.update_cell(row, 2, dest)
        sheet.update_cell(row, 3, fecha)
        sheet.update_cell(row, 4, estado)
        st.toast(msg)
        return True
    except Exception as e:
        st.error(f"Error: {e}")

# ---------- UI ----------

# Encabezados
h1, h2, h3, h4 = st.columns([1, 3, 2, 3])
h1.markdown("<h4 style='text-align:center; margin:0; color:#555;'>UBI</h4>", unsafe_allow_html=True)
h2.markdown("<h4 style='text-align:center; margin:0; color:#555;'>DESTINO</h4>", unsafe_allow_html=True)
h3.markdown("<h4 style='text-align:center; margin:0; color:#555;'>FECHA</h4>", unsafe_allow_html=True)
h4.markdown("<h4 style='text-align:center; margin:0; color:#555;'>ACCIONES</h4>", unsafe_allow_html=True)
st.markdown("<hr style='margin:5px 0 15px 0; border-top:1px solid #ccc;'>", unsafe_allow_html=True)

df = obtener_datos()

for idx, row in df.iterrows():
    pre = str(row['Pre-Stage'])
    dest = str(row['Destino'])
    fecha = str(row['Fecha Despacho'])
    ocup = str(row['Ocupacion'])
    
    # Clase CSS dinámica
    css = "status-vacia"
    if ocup == "Parcial": css = "status-parcial"
    elif ocup == "Completa": css = "status-completa"

    # Tarjeta / Fila
    with st.container():
        # Columnas ajustadas para que los botones tengan espacio
        c1, c2, c3, c4 = st.columns([1, 3, 2, 3], gap="small")
        
        # 1. ID
        with c1:
            st.markdown(f"<div class='id-badge {css}'>{pre}</div>", unsafe_allow_html=True)
            
        # 2. Destino
        with c2:
            new_dest = st.text_input("D", value=dest, key=f"d{pre}", label_visibility="collapsed", placeholder="Destino...")
            
        # 3. Fecha
        with c3:
            ops = generar_fechas(fecha)
            idx_f = ops.index(fecha) if fecha in ops else 0
            new_date = st.selectbox("F", options=ops, index=idx_f, key=f"f{pre}", label_visibility="collapsed")
            
        # 4. Botones (Dividimos la columna 4 en 3 sub-botones)
        with c4:
            b1, b2, b3 = st.columns([1, 1.2, 1], gap="small") # El del medio un poco más ancho para el texto FULL
            
            with b1:
                # Botón Guardar (Icono grande)
                if st.button("💾", key=f"s{pre}", help="Guardar Parcial"):
                    if procesar_accion(pre, new_dest, new_date, "parcial"): st.rerun()
            
            with b2:
                # Botón Full (Texto + Icono) - Usamos type="primary" para que salga rojo/destacado
                if st.button("🛑 FULL", key=f"fl{pre}", type="primary", help="Marcar Completa"):
                    if procesar_accion(pre, new_dest, new_date, "full"): st.rerun()
                    
            with b3:
                # Botón Reset (Icono grande)
                if st.button("♻️", key=f"r{pre}", help="Limpiar"):
                    if procesar_accion(pre, new_dest, new_date, "reset"): st.rerun()

    # Espacio entre filas
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
