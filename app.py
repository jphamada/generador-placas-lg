import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import textwrap
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Editor de Placas LG", layout="centered")

# CSS para botones grandes y tipografía clara en móviles
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    stTextInput > div > div > input { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE REINICIO ---
def reiniciar_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- CONSTANTES ---
CARPETA_FUENTES = "fonts"
CARPETA_PLANTILLAS = "templates"
FUENTE_SUBTITULO = "Roboto-Bold.ttf"
FUENTE_TITULO = "Merriweather_24pt-Black.ttf"

st.title("📸 Generador de Placas Pro")
st.info("Configuración restaurada: Fuentes extra grandes y diseño móvil.")

# --- PASO 1: IMAGEN ---
st.header("1️⃣ Sube tu imagen")
foto_usuario = st.file_uploader("Galería o Cámara", type=["jpg", "png", "jpeg"], key="foto_subida")

# --- PASO 2: DISEÑO Y COLOR ---
st.header("2️⃣ Configura el diseño")

col1, col2 = st.columns(2)

with col1:
    if os.path.exists(CARPETA_PLANTILLAS):
        templates = [f for f in os.listdir(CARPETA_PLANTILLAS) if f.endswith(('.png', '.jpg'))]
        templates.sort()
        plantilla_sel = st.selectbox("Plantilla", templates, key="sel_plantilla")
    else:
        st.error("Error: No hay carpeta 'templates'")
        plantilla_sel = None

with col2:
    colores_predefinidos = {
        "Azul LG": "#005CC3",
        "Rojo": "#C30000",
        "Verde": "#0A920E",
        "Personalizado": "CUSTOM"
    }
    seleccion_color = st.selectbox("Color Texto", list(colores_predefinidos.keys()), key="sel_color")
    
    if seleccion_color == "Personalizado":
        color_texto = st.color_picker("Color propio", "#005b9f", key="color_custom")
    else:
        color_texto = colores_predefinidos[seleccion_color]

# --- PASO 3: TEXTOS ---
st.header("3️⃣ Contenido")
subtitulo_input = st.text_input("Subtítulo", "UNO POR UNO", key="input_sub")
titulo_input = st.text_area("Título Principal", "Escribe el mensaje aquí...", key="input_tit")

st.divider()

# --- PROCESAMIENTO ---
if foto_usuario and titulo_input and plantilla_sel:
    try:
        # 1. Preparar Fondo (Center Crop)
        usuario_img = Image.open(foto_usuario).convert("RGBA")
        fondo = ImageOps.fit(usuario_img, (1080, 1350), method=Image.Resampling.LANCZOS)
        
        # 2. Superponer Plantilla
        plantilla = Image.open(os.path.join(CARPETA_PLANTILLAS, plantilla_sel)).convert("RGBA")
        final_img = Image.alpha_composite(fondo, plantilla)
        draw = ImageDraw.Draw(final_img)

        # 3. CARGAR FUENTES (Lógica de tamaño real)
        try:
            ruta_sub = os.path.join(CARPETA_FUENTES, FUENTE_SUBTITULO)
            ruta_tit = os.path.join(CARPETA_FUENTES, FUENTE_TITULO)
            
            # TAMAÑOS RECUPERADOS
            font_sub = ImageFont.truetype(ruta_sub, 45)
            font_tit = ImageFont.truetype(ruta_tit, 95)
        except:
            st.error("⚠️ No se encontraron las fuentes en /fonts. Las letras se verán pequeñas.")
            font_sub = font_tit = ImageFont.load_default()

        # 4. DIBUJAR
        X_MARGEN = 60
        # Subtítulo
        draw.text((X_MARGEN, 100), subtitulo_input.upper(), font=font_sub, fill=color_texto, anchor="la")
        
        # Título Extra Grande (Ancho corto para evitar desborde)
        titulo_wrapped = textwrap.fill(titulo_input, width=14)
        draw.multiline_text((X_MARGEN, 180), titulo_wrapped, font=font_tit, fill=color_texto, 
                            anchor="la", spacing=15, align="left")

        # --- PASO 4: RESULTADO ---
        st.header("4️⃣ Resultado")
        st.image(final_img, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            buf = BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button("✅ Descargar", buf.getvalue(), "placa_pro.png", "image/png")
        with c2:
            if st.button("🔄 Reiniciar"):
                reiniciar_app()

    except Exception as e:
        st.error(f"Error técnico: {e}")
else:
    st.warning("Sube una foto y escribe un título para generar la placa.")
