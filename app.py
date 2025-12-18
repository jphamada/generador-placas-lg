import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps  # Añadimos ImageOps
import os
import textwrap

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador de Placas LG", layout="centered")
st.title("🎨 Creador de Placas LG")

CARPETA_FUENTES = "fonts"
CARPETA_PLANTILLAS = "templates"
FUENTE_SUBTITULO_BOLD = "Roboto-Bold.ttf"
FUENTE_TITULO_BOLD = "Merriweather_24pt-Black.ttf"

# --- INTERFAZ ---
with st.sidebar:
    st.header("Configuración de la Placa")
    
    # 1. Inputs de Texto
    subtitulo_input = st.text_input("Subtítulo", "ESCRIBE EL SUBTÍTULO")
    titulo_input = st.text_area("Título", "Escribe aquí el título principal...")
    
    st.divider() # Línea divisoria para organizar mejor
    
    # 2. Lógica de Colores
    st.subheader("Color del Texto")
    
    # Definimos los colores básicos en un diccionario para fácil acceso
    colores_predefinidos = {
        "Azul LG": "#005CC3",
        "Rojo": "#C30000",
        "Verde": "#0A920E",
        "Personalizado": "CUSTOM"
    }
    
    # El usuario elige entre los nombres de los colores
    seleccion_color = st.radio(
        "Elige un color o usa uno propio:",
        options=list(colores_predefinidos.keys())
    )
    
    # Si elige "Personalizado", mostramos el Color Picker
    if seleccion_color == "Personalizado":
        color_texto = st.color_picker("Selecciona tu color", "#005b9f")
    else:
        # Si elige uno básico, asignamos el código Hexadecimal correspondiente
        color_texto = colores_predefinidos[seleccion_color]

    st.divider()

foto_usuario = st.file_uploader("1. Sube tu foto", type=["jpg", "png", "jpeg"])

if os.path.exists(CARPETA_PLANTILLAS):
    templates = [f for f in os.listdir(CARPETA_PLANTILLAS) if f.endswith(('.png', '.jpg'))]
    plantilla_sel = st.selectbox("2. Elige la plantilla", templates) if templates else None
else:
    st.error("Carpeta 'templates' no encontrada.")
    plantilla_sel = None

# --- MOTOR DE PROCESAMIENTO ---
if st.button("Generar Placa"):
    if foto_usuario and titulo_input and plantilla_sel:
        try:
            # A. CARGAR Y AJUSTAR FOTO (SIN DEFORMAR)
            usuario_img = Image.open(foto_usuario).convert("RGBA")
            
            # ImageOps.fit escala y recorta al centro automáticamente para llenar 1080x1350
            fondo = ImageOps.fit(usuario_img, (1080, 1350), method=Image.Resampling.LANCZOS)
            
            # B. CARGAR PLANTILLA
            plantilla = Image.open(os.path.join(CARPETA_PLANTILLAS, plantilla_sel)).convert("RGBA")
            
            # Unir (Fondo + Plantilla)
            final_img = Image.alpha_composite(fondo, plantilla)
            draw = ImageDraw.Draw(final_img)

            # C. CARGAR FUENTES BOLD
            try:
                font_sub = ImageFont.truetype(os.path.join(CARPETA_FUENTES, FUENTE_SUBTITULO_BOLD), 35)
                font_tit = ImageFont.truetype(os.path.join(CARPETA_FUENTES, FUENTE_TITULO_BOLD), 65)
            except:
                font_sub = font_tit = ImageFont.load_default()

            # D. DIBUJAR TEXTO (Mismos márgenes que el ejemplo)
            X_MARGEN = 60
            draw.text((X_MARGEN, 100), subtitulo_input.upper(), font=font_sub, fill=color_texto, anchor="la")
            
            titulo_wrapped = textwrap.fill(titulo_input, width=26)
            draw.multiline_text((X_MARGEN, 180), titulo_wrapped, font=font_tit, fill=color_texto, 
                                anchor="la", spacing=15, align="left")

            # E. RESULTADO
            st.success("¡Placa generada correctamente!")
            st.image(final_img, use_container_width=True)

            from io import BytesIO
            buf = BytesIO()
            final_img.save(buf, format="PNG")
            st.download_button("Descargar Imagen", buf.getvalue(), "placa_proporcional.png", "image/png")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Falta subir la foto o completar el título.")
