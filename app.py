import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import textwrap
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Editor de Placas LG", layout="centered")

# CSS para mejorar la UX en móviles
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        border-radius: 10px;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE REINICIO ---
def reiniciar_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- CARGA DE FUENTES CON RESPALDO ---
def cargar_fuente(ruta_fuente, tamano):
    try:
        return ImageFont.truetype(ruta_fuente, tamano)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", tamano)
        except OSError:
            return ImageFont.load_default()

# --- CONSTANTES ---
CARPETA_FUENTES = "fonts"
CARPETA_PLANTILLAS = "templates"
FUENTE_SUBTITULO_BOLD = "Roboto-Bold.ttf"
FUENTE_TITULO_BOLD = "Merriweather_24pt-ExtraBold.ttf"

st.title("📸 Creador de Placas")
st.info("Diseño optimizado: El título ahora es más grande y las listas están ordenadas.")

# --- PASO 1: SUBIR FOTO ---
st.header("1️⃣ Sube tu imagen")
foto_usuario = st.file_uploader("Selecciona una foto", type=["jpg", "png", "jpeg"], key="foto_subida")

# --- PASO 2: DISEÑO Y COLOR ---
st.header("2️⃣ Configura el diseño")

col1, col2 = st.columns(2)

with col1:
    if os.path.exists(CARPETA_PLANTILLAS):
        templates = [f for f in os.listdir(CARPETA_PLANTILLAS) if f.endswith(('.png', '.jpg'))]
        templates.sort() # Ordenar alfabéticamente las plantillas
        plantilla_sel = st.selectbox("Elige la plantilla", templates, key="sel_plantilla") if templates else None
    else:
        st.error("Carpeta 'templates' no encontrada.")
        plantilla_sel = None

with col2:
    # Lista de colores ordenada según tu pedido
    colores_predefinidos = {
        "Azul LG": "#005CC3",
        "Rojo": "#C30000",
        "Verde": "#0A920E",
        "Personalizado": "CUSTOM"
    }
    seleccion_color = st.selectbox("Color del texto", list(colores_predefinidos.keys()), key="sel_color")
    
    if seleccion_color == "Personalizado":
        color_texto = st.color_picker("Color propio", "#005b9f", key="color_custom")
    else:
        color_texto = colores_predefinidos[seleccion_color]

# --- PASO 3: CONTENIDO ---
st.header("3️⃣ Escribe el contenido")
subtitulo_input = st.text_input("Subtítulo", "UNO POR UNO", key="input_sub")
titulo_input = st.text_area("Título de la placa", "Escribe el mensaje aquí...", key="input_tit")

st.divider()

if foto_usuario and titulo_input and plantilla_sel:
    try:
        usuario_img = Image.open(foto_usuario).convert("RGBA")
        fondo = ImageOps.fit(usuario_img, (1080, 1350), method=Image.Resampling.LANCZOS)
        
        plantilla = Image.open(os.path.join(CARPETA_PLANTILLAS, plantilla_sel)).convert("RGBA")
        final_img = Image.alpha_composite(fondo, plantilla)
        draw = ImageDraw.Draw(final_img)

        # Cargar fuentes
        ruta_sub = os.path.join(CARPETA_FUENTES, FUENTE_SUBTITULO_BOLD)
        ruta_tit = os.path.join(CARPETA_FUENTES, FUENTE_TITULO_BOLD)
        
        font_sub = cargar_fuente(ruta_sub, 45) 
        font_tit = cargar_fuente(ruta_tit, 95) # Título aumentado a 95

        X_MARGEN = 60
        draw.text((X_MARGEN, 100), subtitulo_input.upper(), font=font_sub, fill=color_texto, anchor="la")
        
        # Ajustamos el 'width' a 18 para que el texto grande no se desborde
        titulo_wrapped = textwrap.fill(titulo_input, width=18)
        draw.multiline_text((X_MARGEN, 180), titulo_wrapped, font=font_tit, fill=color_texto, 
                            anchor="la", spacing=15, align="left")

        # --- RESULTADO Y ACCIONES ---
        st.header("4️⃣ Resultado")
        st.image(final_img, use_container_width=True)

        col_down, col_reset = st.columns(2)
        
        with col_down:
            buf = BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button("✅ Descargar Placa", buf.getvalue(), "placa_final.png", "image/png")
            
        with col_reset:
            if st.button("🔄 Reiniciar"):
                reiniciar_app()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Completa los campos anteriores para ver la vista previa.")
    if st.button("🔄 Limpiar Formulario"):
        reiniciar_app()
