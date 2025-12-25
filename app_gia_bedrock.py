import boto3
import streamlit as st
import json
import base64
import io
import time
import random
from PIL import Image
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

# --- 1. Configuración Inicial y UI ---
st.set_page_config(page_title="GIA: Mugen", layout="wide", page_icon="♾️")

# Cargar entorno (fallback)
load_dotenv(override=True)

# Estilos
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2c3e50; }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        border: none;
    }
    .stButton>button:hover { background-color: #45a049; }
</style>
""", unsafe_allow_html=True)

# --- 2. Gestión de Credenciales y Cliente (BYOK) ---
def get_bedrock_runtime(aws_access_key, aws_secret_key, aws_session_token, region):
    """
    Crea un cliente bedrock-runtime usando las credenciales proporcionadas.
    Prioriza inputs de UI, luego variables de entorno.
    """
    try:
        if aws_access_key and aws_secret_key:
            # Uso de credenciales explícitas (BYOK)
            session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                aws_session_token=aws_session_token if aws_session_token else None,
                region_name=region
            )
            return session.client("bedrock-runtime")
        else:
            # Fallback a entorno local (si existe)
            return boto3.client("bedrock-runtime", region_name=region)
    except Exception as e:
        return None

# --- UI de Configuración Lateral ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/900/900782.png", width=60)
    st.title("⚙️ Configuración AWS")
    
    st.info("Ingrese sus credenciales de AWS para habilitar la generación.")
    
    aws_access_key = st.text_input("AWS Access Key ID", type="password")
    aws_secret_key = st.text_input("AWS Secret Access Key", type="password")
    aws_session_token = st.text_input("AWS Session Token (Opcional)", type="password")
    
    region = st.selectbox("Región AWS", ["us-west-2", "us-east-1"], index=0)
    
    st.markdown("---")
    st.subheader("Modelos Seleccionados")
    st.caption("🖼️ Titan Image V2")
    st.caption("🎨 Stable Image Core")
    st.caption("📝 Claude 3 Sonnet")

# Inicializar Cliente
client = get_bedrock_runtime(aws_access_key, aws_secret_key, aws_session_token, region)

# Verificar conexión básica (opcional, solo visual)
connection_status = st.empty()
if aws_access_key and aws_secret_key:
    connection_status.success(f"✅ Credenciales cargadas para {region}")
else:
    # Intentar detectar si hay credenciales de entorno para mensaje amigable
    if os.getenv("AWS_ACCESS_KEY_ID"):
        connection_status.info(f"ℹ️ Usando credenciales de entorno (.env) en {region}")
    else:
        connection_status.warning("⚠️ Sin credenciales. Por favor ingréselas en el panel lateral.")

# --- 3. Lógica de Generación ---

def generate_titan_v2(prompt, width=1024, height=1024):
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": "standard",
            "height": height,
            "width": width,
            "cfgScale": 8.0,
            "seed": random.randint(0, 2147483647)
        }
    })
    
    try:
        response = client.invoke_model(
            modelId="amazon.titan-image-generator-v2:0",
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        return base64.b64decode(response_body['images'][0])
    except Exception as e:
        raise e

def generate_stable_core(prompt, aspect_ratio="1:1"):
    # Mapeo de aspect ratio a ancho para simplificar, Stable Core usa aspect_ratio string
    body = json.dumps({
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": "png"
    })
    
    try:
        response = client.invoke_model(
            modelId="stability.stable-image-core-v1:0",
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        # Stable Core suele devolver 'image' (base64) directamente o en 'images'
        if 'image' in response_body:
            return base64.b64decode(response_body['image'])
        elif 'images' in response_body:
            return base64.b64decode(response_body['images'][0])
        else:
            raise Exception(f"Formato desconocido: {response_body.keys()}")
    except Exception as e:
        raise e

def edit_text_sonnet(text, instruction):
    user_message = f"Instrucción: {instruction}\n\nTexto a procesar:\n{text}\n\nSalida editada:"
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": user_message}]
    })
    
    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        raise e

# --- 4. Interfaz Principal ---

st.title("GIA: Mugen")
st.caption("Infinite Possibilities • Creative AI")

tab_img, tab_txt = st.tabs(["🖼️ Generador de Imágenes", "📝 Editor de Texto"])

with tab_img:
    col_input, col_preview = st.columns([1, 1.2])
    
    with col_input:
        st.markdown("### 1. Define tu Visión")
        
        # Estado para el prompt para permitir actualizaciones
        if 'current_prompt' not in st.session_state:
            st.session_state.current_prompt = ""
            
        # Text Area vinculado al session state
        img_prompt = st.text_area("Descripción (Prompt)", value=st.session_state.current_prompt, placeholder="Ej: Un paisaje futurista...", height=120, key="prompt_input")
        
        # Botón para mejorar prompt usando Claude
        if st.button("✨ Mejorar Prompt (Claude)", type="secondary", help="Usa IA para detallar tu descripción"):
            if client and img_prompt:
                with st.spinner("Claude está imaginando detalles..."):
                    try:
                        mejora_prompt = edit_text_sonnet(img_prompt, "Mejora este prompt para generación de imágenes (Stable Diffusion/Titan). Hazlo detallado, descriptivo, visual y en inglés. Devuelve SOLO el prompt mejorado sin comillas ni texto extra.")
                        # Actualizar el prompt en la caja (rerun necesario para ver cambio visual inmediato a veces, pero st.text_area con key se actualiza)
                        st.session_state.current_prompt = mejora_prompt
                        st.session_state.prompt_input = mejora_prompt # Hack para forzar update visual
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Error mejorando prompt: {e}")
            elif not client:
                st.error("Configura las credenciales AWS primero.")
            else:
                st.warning("Escribe algo para mejorar.")

        st.markdown("### 2. Elige tu Artista")
        img_model = st.radio("Modelo de Generación", ["Amazon Titan V2", "Stable Image Core"], horizontal=True)

        st.markdown("### 3. Crear")
        if st.button("🎨 Generar Obra Maestra", type="primary", use_container_width=True):
            current_prompt_val = st.session_state.get("prompt_input", img_prompt)
            if not client:
                st.error("Error: Cliente AWS no inicializado. Verifique credenciales.")
            elif not current_prompt_val:
                st.warning("Escribe un prompt primero.")
            else:
                with st.spinner(f"Renderizando con {img_model}..."):
                    try:
                        if img_model == "Amazon Titan V2":
                            img_bytes = generate_titan_v2(current_prompt_val)
                        else:
                            img_bytes = generate_stable_core(current_prompt_val)
                        
                        # Guardar en session state para persistencia
                        st.session_state['last_img'] = img_bytes
                        st.session_state['last_prompt'] = current_prompt_val
                        st.success("¡Imagen generada!")
                    except Exception as e:
                        st.error(f"Fallo en generación: {e}")

    with col_preview:
        st.markdown("### 4. Resultado")
        if 'last_img' in st.session_state:
            st.image(io.BytesIO(st.session_state['last_img']), caption=st.session_state.get('last_prompt', ''))
            
            # Botones de acción
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Descargar", st.session_state['last_img'], file_name=f"mugen_art_{int(time.time())}.png", mime="image/png", use_container_width=True)
            with c2:
                if st.button("🗑️ Limpiar", use_container_width=True):
                    del st.session_state['last_img']
                    del st.session_state['last_prompt']
                    st.rerun()
        else:
            st.info("La imagen generada aparecerá aquí.")
            st.markdown("""
            <div style="text-align: center; color: #aaa; margin-top: 50px;">
                <h1>♾️</h1>
                <p>Waiting for inspiration...</p>
            </div>
            """, unsafe_allow_html=True)

with tab_txt:
    st.subheader("Editor Inteligente (Claude 3 Sonnet)")
    txt_input = st.text_area("Texto Original", height=150)
    txt_instr = st.text_input("Instrucción de Edición", placeholder="Mejora el tono para que sea más profesional...")
    
    if st.button("Procesar Texto"):
        if not client:
             st.error("Error: Cliente AWS no inicializado.")
        elif not txt_input:
            st.warning("Ingresa un texto.")
        else:
            with st.spinner("Claude trabajando..."):
                try:
                    res = edit_text_sonnet(txt_input, txt_instr)
                    st.text_area("Resultado", value=res, height=200)
                except Exception as e:
                    st.error(f"Error: {e}")
