import streamlit as st
import streamlit as st
import os
import json
import io
import base64
import requests
from PIL import Image
from openai import OpenAI

# Configuración de página
st.set_page_config(page_title="GIA (OpenAI Edition)", layout="wide", page_icon="🚀")

# Estilos CSS
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2e86c1; }
    .stButton>button {
        background-color: #2e86c1;
        color: white;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# El cliente se inicializa más abajo, después de verificar si el usuario ingresó una clave propia.

def generate_image_gpt5(prompt, style):
    """Genera imagen usando GPT-5 Image Mini (vía OpenRouter Chat API)"""
    try:
        final_prompt = f"Generate an image of: {style} style. {prompt}" if style != "Ninguno" else f"Generate an image of: {prompt}"
        
        # GPT-5 Image Mini se usa vía Chat Completions (Multimodal Output)
        response = client.chat.completions.create(
            model="openai/gpt-5-image-mini",
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            # OpenRouter/OpenAI specific param for output modality
            # Nota: Algunos clientes requieren 'modalities', otros lo infieren.
            # OpenRouter documenta devolver 'message.images' o URLs en el contenido.
            # Verificamos estructura de respuesta.
        )
        
        # GPT-5 Image Mini devuelve la imagen en un campo especial 'images' dentro del mensaje
        # Esto no es estándar en todas las versiones de lib OpenAI, así que accedemos al dict crudo
        response_dict = response.model_dump()
        
        # Buscar en choices[0].message.images
        try:
            message = response_dict.get('choices', [])[0].get('message', {})
            images = message.get('images', [])
            
            if images:
                # Es una lista de objetos {type: 'image_url', image_url: {url: 'data:...'}}
                image_data = images[0]
                if image_data.get('type') == 'image_url':
                    data_url = image_data.get('image_url', {}).get('url', '')
                    
                    if data_url.startswith('data:image'):
                        # Extraer solo el base64 (quitar 'data:image/png;base64,')
                        return data_url.split(',')[1]
                    elif data_url.startswith('http'):
                        # Si es URL normal
                        img_response = requests.get(data_url)
                        if img_response.status_code == 200:
                            return base64.b64encode(img_response.content).decode('utf-8')
        except Exception as e:
            print(f"Debug: Error parseando images: {e}")

        # Fallback: Intentar texto (comportamiento antiguo)
        content = response.choices[0].message.content
        if content:
            # 1. Markdown
            import re
            url_match = re.search(r'\!\[.*?\]\((https?://.*?)\)', content)
            if not url_match:
                url_match = re.search(r'(https?://[^\s\)]+)', content)

            if url_match:
                image_url = url_match.group(1).strip(').,;"\'')
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    return base64.b64encode(img_response.content).decode('utf-8')

        st.warning("⚠️ GPT-5 generó una respuesta, pero no encontré la imagen en el formato esperado.")
        st.write("Estructura recibida (Debug):")
        st.json(response_dict) # Mostrar JSON para que el usuario vea qué llegó
        return None
        
    except Exception as e:
        st.error(f"Error Generación (GPT-5): {e}")
        return None

def edit_text_nemotron(text, instruction):
    """Edita texto usando Nvidia Nemotron (vía OpenRouter)"""
    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free", # Modelo gratuito de Nvidia
            messages=[
                {"role": "system", "content": "Eres un editor experto y creativo."},
                {"role": "user", "content": f"Texto original:\n{text}\n\nInstrucción: {instruction}\n\nDevuelve solo el texto editado."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error Texto (Nemotron): {e}")
        return None

def base64_to_pil(b64_str):
    try:
        return Image.open(io.BytesIO(base64.b64decode(b64_str)))
    except:
        return None

# --- UI ---
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # Opción para que el usuario ponga su propia clave (BYOK - Obligatorio)
    user_key = st.text_input("🔑 Tu API Key de OpenRouter", type="password", help="Introduce tu clave personal de OpenRouter para usar la app.")
    
    st.divider()
    st.success("Proveedor: OpenRouter")
    st.info("Imagen: GPT-5 Image Mini\nTexto: Nvidia Nemotron (Free)")

# Lógica de Selección de Clave
# STRICT BYOK: Solo usamos la clave que el usuario introduce. Sin fallbacks ocultos.
if not user_key:
    st.warning("👈 Para comenzar, por favor ingresa tu API KEY de OpenRouter en la barra lateral.")
    st.info("💡 Si no tienes una, puedes conseguirla en [openrouter.ai/keys](https://openrouter.ai/keys).")
    st.stop()

final_api_key = user_key

# Configurar Cliente con la clave del usuario
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=final_api_key,
)

st.title("🚀 GIA: Edición OpenRouter")
st.caption("Acceso universal a modelos de IA. Sin ataduras.")

tab1, tab2 = st.tabs(["🎨 Generador GPT-5", "📝 Editor Nvidia"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        p_input = st.text_area("Descripción", height=150, placeholder="Un paisaje cyberpunk...")
        style = st.selectbox("Estilo", ["Ninguno", "Cinematic", "Anime", "Photorealistic", "Digital Art"])
        btn_gen = st.button("Generar Imagen", type="primary")
    
    with col2:
        if btn_gen and p_input:
            with st.spinner("GPT-5 está pintando..."):
                b64 = generate_image_gpt5(p_input, style)
                if b64:
                    img = base64_to_pil(b64)
                    if img:
                        st.image(img, caption="Generado por GPT-5 Image Mini", use_container_width=True)
                        
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button("Descargar PNG", buf.getvalue(), "gpt5_image.png", "image/png")
                    else:
                        st.error("Error al decodificar imagen.")

with tab2:
    txt_input = st.text_area("Texto a editar", height=150)
    mode = st.radio("Modo", ["Resumir", "Mejorar redacción", "Cambiar tono", "Personalizado"], horizontal=True)
    custom_inst = st.text_input("Instrucción extra:") if mode == "Personalizado" else ""
    
    if st.button("Procesar Texto"):
        inst = custom_inst if mode == "Personalizado" else f"Aplica: {mode}"
        with st.spinner("Nemotron pensando..."):
            res = edit_text_nemotron(txt_input, inst)
            if res:
                st.info(res)
