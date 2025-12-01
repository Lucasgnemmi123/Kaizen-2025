import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import time

# ---------- CONFIGURACIÓN GENERAL ----------
st.set_page_config(
    page_title="Panel Admin Kaizen",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- ESTILOS CSS ----------
# Estilos para que se parezca a tu HTML original (Input grandes, Botones de colores)
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    h1 { text-align: center; color: #333; margin-bottom: 20px; }
    
    /* Cajas de estado (Pre-Stage) */
    .status-box {
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        color: #000;
        border: 1px solid #999;
    }
    
    /* Separador de filas */
    .row-separator {
        border-top: 1px solid #ddd;
        margin-top: 5px;
        margin-bottom: 5px;
    }

    /* Botones personalizados */
    div[data-testid="stButton"] button {
        width: 100%;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------- CONEXIÓN GOOGLE SHEETS ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def obtener_conexion():
    """Conecta a Google Sheets usando secrets.toml"""
    creds = Credentials.from_service_account_info(
        st.secrets["gsheets"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client

# IDs y Constantes
SHEET_ID = "1M9Sccc-3bA33N1MNJtkTCcrDSKK_wfRjeDnqxsrlEtA"
HOJA_NOMBRE = "Hoja 1"

try:
    client = obtener_conexion()
    sheet = client.open_by_key(SHEET_ID).worksheet(HOJA_NOMBRE)
except Exception as e:
    st.error("🚨 Error de conexión. Verifica que hayas compartido la hoja con el email del JSON.")
    st.stop()

# ---------- FUNCIONES DE LÓGICA ----------

def cargar_datos():
    """Descarga los datos frescos de la hoja"""
    # get_all_records devuelve lista de dicts. Asumimos encabezados en fila 1.
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def generar_fechas(fecha_actual):
    """Genera lista: [Hoy, +1, +2]. Si fecha_actual existe y no está en rango, la agrega."""
    opciones = []
    hoy = datetime.now()
    for i in range(3):
        f = hoy + timedelta(days=i)
        opciones.append(f.strftime("%d-%m-%Y")) # Formato dd-mm-yyyy igual a tu script
    
    # Asegurar que la fecha que ya tiene la celda aparezca en la lista
    if fecha_actual and fecha_actual not in opciones:
        opciones.insert(0, fecha_actual)
    
    return opciones

def guardar_cambios(pre_stage, destino, fecha, es_full):
    """Lógica equivalente a saveRow() de Apps Script"""
    with st.spinner(f"Guardando {pre_stage}..."):
        # 1. Calcular Estado
        if not destino:
            ocupacion = "Vacia"
            fecha = "" # Limpiar fecha si no hay destino
            destino = ""
        elif es_full:
            ocupacion = "Completa"
        else:
            ocupacion = "Parcial"
        
        # 2. Buscar fila en Google Sheet (Columna 1 = Pre-Stage)
        try:
            cell = sheet.find(str(pre_stage), in_column=1)
            row_idx = cell.row
            
            # 3. Actualizar Celdas (Col 2: Destino, 3: Fecha, 4: Ocupacion)
            # update_cells es más eficiente si fueran muchas, pero update_cell es seguro fila por fila
            sheet.update_cell(row_idx, 2, destino)
            sheet.update_cell(row_idx, 3, fecha)
            sheet.update_cell(row_idx, 4, ocupacion)
            
            st.toast(f"✅ {pre_stage} actualizado a: {ocupacion}")
            return True
        except Exception as e:
            st.error(f"Error al guardar: {e}")
            return False

def resetear_fila(pre_stage):
    """Lógica equivalente a resetRow()"""
    with st.spinner(f"Reseteando {pre_stage}..."):
        try:
            cell = sheet.find(str(pre_stage), in_column=1)
            row_idx = cell.row
            
            sheet.update_cell(row_idx, 2, "")
            sheet.update_cell(row_idx, 3, "")
            sheet.update_cell(row_idx, 4, "Vacia")
            
            st.toast(f"♻️ {pre_stage} ha sido vaciado.")
            return True
        except Exception as e:
            st.error(f"Error al resetear: {e}")
            return False

# ---------- INTERFAZ (UI) ----------

st.markdown("<h1>🏭 Panel de Control de Preparaciones</h1>", unsafe_allow_html=True)

# Botón global de recarga manual (por si acaso)
if st.button("🔄 Recargar Datos Actuales"):
    st.rerun()

df = cargar_datos()

# Encabezados Visuales
cols = st.columns([1, 3, 2, 0.8, 1, 1])
titulos = ["Pre-Stage", "Destino", "Fecha", "Full", "Guardar", "Reset"]
for col, titulo in zip(cols, titulos):
    col.markdown(f"<div style='text-align:center; font-weight:bold; background:#eee; padding:5px; border:1px solid #999;'>{titulo}</div>", unsafe_allow_html=True)

st.write("") # Espacio

# Bucle para crear una fila de controles por cada registro
for i, row in df.iterrows():
    pre = str(row['Pre-Stage'])
    destino_val = str(row['Destino'])
    fecha_val = str(row['Fecha Despacho'])
    ocupacion_val = str(row['Ocupacion'])
    
    # Definir color según ocupación (Igual a tu CSS anterior)
    color_bg = "#BDC3C7" # Gris default
    if ocupacion_val == "Vacia": color_bg = "#A9DFBF" # Verde
    elif ocupacion_val == "Parcial": color_bg = "#F9E79F" # Amarillo
    elif ocupacion_val == "Completa": color_bg = "#F5B7B1" # Rojo
    
    # Contenedor de Fila
    c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 0.8, 1, 1], gap="small")
    
    # Col 1: Pre-Stage (Visual)
    with c1:
        st.markdown(
            f"<div class='status-box' style='background-color:{color_bg};'>{pre}</div>",
            unsafe_allow_html=True
        )
    
    # Col 2: Input Destino
    with c2:
        new_dest = st.text_input(
            "Dest", 
            value=destino_val, 
            key=f"dest_{pre}", 
            label_visibility="collapsed"
        )
        
    # Col 3: Select Fecha
    with c3:
        opciones = generar_fechas(fecha_val)
        # Buscar índice
        try:
            idx = opciones.index(fecha_val)
        except ValueError:
            idx = 0
            
        new_date = st.selectbox(
            "Fec", 
            options=opciones, 
            index=idx, 
            key=f"date_{pre}", 
            label_visibility="collapsed"
        )
        
    # Col 4: Checkbox Full
    with c4:
        # Centrar el checkbox es truculento en streamlit, usamos un contenedor vacío arriba
        st.write("") 
        is_full = (ocupacion_val == "Completa")
        new_full = st.checkbox("Full", value=is_full, key=f"full_{pre}")
        
    # Col 5: Botón Guardar (Verde)
    with c5:
        if st.button("💾", key=f"save_{pre}", help="Guardar cambios", type="secondary"):
            if guardar_cambios(pre, new_dest, new_date, new_full):
                time.sleep(0.5) # Pequeña pausa para ver el toast
                st.rerun()
                
    # Col 6: Botón Reset (Rojo)
    with c6:
        if st.button("🗑️", key=f"reset_{pre}", help="Borrar todo", type="primary"):
            if resetear_fila(pre):
                time.sleep(0.5)
                st.rerun()

    # Línea separadora
    st.markdown("<div class='row-separator'></div>", unsafe_allow_html=True)
