import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import textwrap
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Editor de Placas LG", layout="centered")

# Inyectar CSS para mejorar la UX en móviles
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        border-radius: 10px;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        font-size: 16px !important; /* Evita zoom automático en iPhone */
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE REINICIO ---
def reiniciar_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- CONSTANTES ---
CARPETA_FUENTES = "fonts"
CARPETA_PLANTILLAS = "templates"
FUENTE_SUBTITULO_BOLD = "Roboto-Bold.ttf"
FUENTE_TITULO_BOLD = "Merriweather_24pt-ExtraBold.ttf"

# --- ENCABEZADO ---
st.title("📸 Creador de Placas")
st.info("Sigue los pasos. Puedes editar los textos y ver el cambio al instante sin resubir la foto.")

# --- PASO 1: SUBIR FOTO ---
st.header("1️⃣ Sube tu imagen")
# Usamos una 'key' para poder resetear el componente
foto_usuario = st.file_uploader("Selecciona una foto", type=["jpg", "png", "jpeg"], key="foto_subida")

# --- PASO 2: DISEÑO Y COLOR ---
st.header("2️⃣ Configura el diseño")

col1, col2 = st.columns(2)

with col1:
    if os.path.exists(CARPETA_PLANTILLAS):
        templates = [f for f in os.listdir(CARPETA_PLANTILLAS) if f.endswith(('.png', '.jpg'))]
        plantilla_sel = st.selectbox("Elige la plantilla", templates, key="sel_plantilla")
    else:
        st.error("Carpeta 'templates' no encontrada.")
        plantilla_sel = None

with col2:
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

# --- VISTA PREVIA Y PROCESAMIENTO ---
st.divider()

if foto_usuario and titulo_input and plantilla_sel:
    try:
        # Procesar imagen base (proporcional)
        usuario_img = Image.open(foto_usuario).convert("RGBA")
        fondo = ImageOps.fit(usuario_img, (1080, 1350), method=Image.Resampling.LANCZOS)
        
        # Superponer plantilla
        plantilla = Image.open(os.path.join(CARPETA_PLANTILLAS, plantilla_sel)).convert("RGBA")
        final_img = Image.alpha_composite(fondo, plantilla)
        draw = ImageDraw.Draw(final_img)

        # Cargar fuentes
        try:
            font_sub = ImageFont.truetype(os.path.join(CARPETA_FUENTES, FUENTE_SUBTITULO_BOLD), 35)
            font_tit = ImageFont.truetype(os.path.join(CARPETA_FUENTES, FUENTE_TITULO_BOLD), 65)
        except:
            font_sub = font_tit = ImageFont.load_default()

        # Dibujar Texto
        X_MARGEN = 60
        draw.text((X_MARGEN, 100), subtitulo_input.upper(), font=font_sub, fill=color_texto, anchor="la")
        
        titulo_wrapped = textwrap.fill(titulo_input, width=26)
        draw.multiline_text((X_MARGEN, 180), titulo_wrapped, font=font_tit, fill=color_texto, 
                            anchor="la", spacing=15, align="left")

        # --- RESULTADO Y ACCIONES ---
        st.header("4️⃣ Resultado")
        st.image(final_img, use_container_width=True)

        # Botones de Acción
        col_down, col_reset = st.columns(2)
        
        with col_down:
            buf = BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button(
                label="✅ Descargar Placa", 
                data=buf.getvalue(), 
                file_name="placa_lg.png", 
                mime="image/png"
            )
            
        with col_reset:
            if st.button("🔄 Reiniciar Todo"):
                reiniciar_app()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Completa los campos anteriores para generar la vista previa.")
    if st.button("🔄 Limpiar Formulario"):
        reiniciar_app()
