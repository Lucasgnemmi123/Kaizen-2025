import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="Admin Panel",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- ESTILOS CSS PROFESIONALES ----------
st.markdown("""
<style>
    /* 1. Limpieza General */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }
    header, footer { display: none !important; }
    
    /* 2. Alineación Vertical de Columnas */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }

    /* 3. Tarjeta de Fila (Card Design) */
    .row-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px 0px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 4. Estilo del ID (J-01, D-01...) */
    .id-badge {
        font-size: 24px;
        font-weight: 900;
        text-align: center;
        color: #333;
        padding: 8px;
        border-radius: 6px;
        width: 100%;
        display: block;
        border: 2px solid #333;
    }

    /* Colores de Estado para el ID */
    .status-vacia { background-color: #2ECC71; border-color: #27AE60; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); }
    .status-parcial { background-color: #F1C40F; border-color: #D4AC0D; color: black; }
    .status-completa { background-color: #E74C3C; border-color: #C0392B; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); }

    /* 5. Inputs (Campos de texto) */
    .stTextInput input {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #ccc;
    }
    
    /* 6. Botones Personalizados */
    div[data-testid="stButton"] button {
        width: 100%;
        border-radius: 6px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 0.1rem;
        transition: all 0.2s;
    }

    /* Hover Effects */
    div[data-testid="stButton"] button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------- CONEXIÓN GOOGLE SHEETS ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def conectar_gsheets():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gsheets"], scopes=SCOPES
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error de credenciales: {e}")
        st.stop()

# Constantes
SHEET_ID = "1M9Sccc-3bA33N1MNJtkTCcrDSKK_wfRjeDnqxsrlEtA"
HOJA_NOMBRE = "Hoja 1"

client = conectar_gsheets()
sheet = client.open_by_key(SHEET_ID).worksheet(HOJA_NOMBRE)

# ---------- LÓGICA DE DATOS ----------

def obtener_datos_frescos():
    """Obtiene datos SIN CACHÉ para garantizar sincronización real"""
    return pd.DataFrame(sheet.get_all_records())

def generar_fechas_dinamicas(fecha_actual_db):
    """Genera Hoy, Mañana, Pasado. Mantiene la fecha actual seleccionada."""
    opciones = []
    hoy = datetime.now()
    
    # Generar 3 días
    for i in range(3):
        f = hoy + timedelta(days=i)
        opciones.append(f.strftime("%d-%m-%Y"))
    
    # Si la fecha que viene de la BD es vieja o distinta, la agregamos al principio
    # para que el usuario vea qué fecha tenía guardada
    if fecha_actual_db and fecha_actual_db not in opciones:
        opciones.insert(0, fecha_actual_db)
        
    return opciones

def actualizar_fila(pre_stage, destino, fecha, accion):
    """
    Maneja Guardar, Full y Reset en una sola función.
    accion: 'parcial', 'completa', 'reset'
    """
    try:
        # Buscar fila
        cell = sheet.find(str(pre_stage), in_column=1)
        row = cell.row
        
        estado = "Vacia"
        
        if accion == "reset":
            destino = ""
            fecha = ""
            estado = "Vacia"
            msg = f"♻️ {pre_stage} Liberado"
            
        elif accion == "parcial":
            if not destino: # Si intenta guardar vacío, es un reset implícito
                estado = "Vacia"
            else:
                estado = "Parcial"
            msg = f"💾 {pre_stage} Guardado (Parcial)"
            
        elif accion == "completa":
            if not destino:
                st.warning("⚠️ Debes escribir un destino para marcar FULL")
                return False
            estado = "Completa"
            msg = f"🛑 {pre_stage} marcado FULL"

        # Escritura en bloque (más segura)
        sheet.update_cell(row, 2, destino)
        sheet.update_cell(row, 3, fecha)
        sheet.update_cell(row, 4, estado)
        
        st.toast(msg)
        return True
        
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return False

# ---------- INTERFAZ GRÁFICA ----------

# 1. Cargar datos frescos
df = obtener_datos_frescos()

# 2. Encabezados "Falsos" para guiar la vista
h1, h2, h3, h4 = st.columns([1, 3, 2, 2.5])
h1.markdown("<div style='text-align:center; font-weight:bold; color:#777;'>UBICACIÓN</div>", unsafe_allow_html=True)
h2.markdown("<div style='text-align:center; font-weight:bold; color:#777;'>DESTINO / CLIENTE</div>", unsafe_allow_html=True)
h3.markdown("<div style='text-align:center; font-weight:bold; color:#777;'>FECHA</div>", unsafe_allow_html=True)
h4.markdown("<div style='text-align:center; font-weight:bold; color:#777;'>ACCIONES</div>", unsafe_allow_html=True)
st.markdown("<hr style='margin:5px 0; border-top:2px solid #333;'>", unsafe_allow_html=True)

# 3. Iterar filas
for idx, row in df.iterrows():
    pre = str(row['Pre-Stage'])
    dest_val = str(row['Destino'])
    fecha_val = str(row['Fecha Despacho'])
    ocup_val = str(row['Ocupacion']) # Vacia, Parcial, Completa

    # Determinar clase CSS para el color del ID
    css_class = "status-vacia"
    if ocup_val == "Parcial": css_class = "status-parcial"
    elif ocup_val == "Completa": css_class = "status-completa"

    # --- CONTENEDOR VISUAL (TARJETA) ---
    with st.container():
        # Columnas: ID | Input Destino | Input Fecha | Botones
        c_id, c_dest, c_fec, c_btn = st.columns([1, 3, 2, 2.5])
        
        # COL 1: ID VISUAL
        with c_id:
            st.markdown(f"<div class='id-badge {css_class}'>{pre}</div>", unsafe_allow_html=True)

        # COL 2: INPUT DESTINO
        with c_dest:
            new_dest = st.text_input(
                "Destino", 
                value=dest_val, 
                key=f"d_{pre}", 
                label_visibility="collapsed",
                placeholder="Ingresa destino..."
            )

        # COL 3: INPUT FECHA
        with c_fec:
            opciones = generar_fechas_dinamicas(fecha_val)
            # Buscar índice seguro
            try: sel_idx = opciones.index(fecha_val)
            except: sel_idx = 0
            
            new_date = st.selectbox(
                "Fecha", 
                options=opciones, 
                index=sel_idx, 
                key=f"f_{pre}", 
                label_visibility="collapsed"
            )

        # COL 4: BOTONES DE ACCIÓN (AQUÍ ESTÁ LA MAGIA)
        with c_btn:
            # Sub-columnas para los 3 botones bien pegaditos
            b1, b2, b3 = st.columns(3, gap="small")
            
            with b1:
                # Botón PARCIAL (Amarillo/Naranja)
                if st.button("💾", key=f"save_{pre}", help="Guardar como Parcial"):
                    if actualizar_fila(pre, new_dest, new_date, "parcial"):
                        st.rerun()

            with b2:
                # Botón FULL (Rojo) - Se destaca más
                if st.button("🛑 FULL", key=f"full_{pre}", type="primary", help="Marcar como Completa"):
                    if actualizar_fila(pre, new_dest, new_date, "completa"):
                        st.rerun()

            with b3:
                # Botón RESET (Verde/Gris)
                # Usamos type="secondary" pero lo estilizaremos visualmente si se pudiera,
                # por ahora standard.
                if st.button("♻️", key=f"clean_{pre}", help="Vaciar ubicación"):
                    if actualizar_fila(pre, new_dest, new_date, "reset"):
                        st.rerun()
        
        # Separador sutil entre tarjetas
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
