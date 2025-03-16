import streamlit as st
import openai
import json
import speech_recognition as sr
from io import BytesIO
import base64
from PIL import Image
import io
import os

# Load configuration from settings.json
with open('settings.json', 'r') as f:
    settings = json.load(f)

def chat_with_azure_openai(prompt, image_data=None):
    # Create Azure OpenAI client
    client = openai.AzureOpenAI(
        api_key=settings['azure_openai']['api_key'],
        api_version=settings['azure_openai']['api_version'],
        azure_endpoint=settings['azure_openai']['azure_endpoint']
    )
    
    # Prepare the messages
    messages = [
        {"role": "system", "content": "Eres un experto en instalación de placas solares."},
    ]
    
    # Add image content if provided
    if image_data:
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Add image content to messages
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
    else:
        # Text-only prompt
        messages.append({"role": "user", "content": prompt})
    
    # Make the API call
    response = client.chat.completions.create(
        model=settings['azure_openai']['deployment_name'],  # Get deployment name from settings
        messages=messages,
        temperature=0.7,
        max_tokens=16384
    )

    return response.choices[0].message.content

# Interfaz con Streamlit
st.title("Chatbot Especialista en Placas Solares ☀️")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        # Check if the message contains an image
        if "image" in message:
            st.image(message["image"], caption="Imagen analizada")
        st.write(message["content"])

# Integrated photo and voice interaction
st.header("Consulta Visual + Voz")
st.write("Sube una foto de paneles solares y describe tu consulta por voz o texto")

# Layout with two columns for better organization
col1, col2 = st.columns([3, 2])

with col1:
    # Image upload section
    st.subheader("1. Sube o captura una imagen")
    image_source = st.radio(
        "Fuente de imagen:",
        ["Subir archivo", "Usar cámara"],
        horizontal=True
    )
    
    image_data = None
    image = None
    
    if image_source == "Subir archivo":
        image_file = st.file_uploader("Selecciona una imagen", type=["jpg", "jpeg", "png"])
        
        if image_file is not None:
            image = Image.open(image_file)
            st.image(image, caption="Imagen cargada", use_column_width=True)
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            image_data = img_byte_arr.getvalue()
            
            # Store in session state
            st.session_state["image_data"] = image_data
            st.session_state["image"] = image
    else:
        camera_image = st.camera_input("Toma una foto")
        
        if camera_image is not None:
            image = Image.open(camera_image)
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            image_data = img_byte_arr.getvalue()
            
            # Store in session state
            st.session_state["image_data"] = image_data
            st.session_state["image"] = image

with col2:
    # Description input section
    st.subheader("2. Describe tu consulta")
    
    description_method = st.radio(
        "Método de descripción:",
        ["Usar voz", "Escribir texto"],
        horizontal=True
    )
    
    if description_method == "Usar voz":
        if st.button("🎤 Grabar consulta (10s)"):
            with st.spinner("Grabando durante 10 segundos..."):
                try:
                    r = sr.Recognizer()
                    
                    with sr.Microphone() as source:
                        st.write("Ajustando al ruido ambiente...")
                        r.adjust_for_ambient_noise(source)
                        st.write("¡Grabando! Habla ahora...")
                        audio = r.listen(source, timeout=10)
                        st.success("¡Grabación completada!")
                        
                        st.session_state["voice_description_audio"] = audio
                        
                        # Try to transcribe immediately
                        try:
                            text = r.recognize_google(audio, language="es-ES")
                            st.session_state["description"] = text
                            st.success(f"Transcripción: {text}")
                        except Exception as e:
                            st.warning("No se pudo transcribir automáticamente. Se intentará al analizar.")
                except Exception as e:
                    st.error(f"Error al grabar: {e}")
    else:
        text_input = st.text_area(
            "Escribe tu consulta:",
            placeholder="Ej: Analiza estos paneles solares y dime si hay problemas de instalación",
            value="",
            height=100
        )
        if text_input:
            st.session_state["description"] = text_input

# Submit button - below both columns
if st.button("📤 Analizar", type="primary", use_container_width=True):
    if "image_data" not in st.session_state or st.session_state["image_data"] is None:
        st.warning("⚠️ Por favor, sube o captura una imagen primero.")
    else:
        # Get image data
        image_data = st.session_state["image_data"]
        image = st.session_state["image"]
        
        # Get description
        description = None
        
        # Try to get from stored transcription
        if "description" in st.session_state:
            description = st.session_state["description"]
        
        # If no stored description but we have audio, try to transcribe
        elif "voice_description_audio" in st.session_state:
            r = sr.Recognizer()
            try:
                with st.spinner("Transcribiendo audio..."):
                    audio_data = st.session_state["voice_description_audio"]
                    description = r.recognize_google(audio_data, language="es-ES")
                    st.success(f"Transcripción: {description}")
            except Exception as e:
                st.error(f"Error al transcribir: {e}")
                description = "Analiza esta imagen de paneles solares e identifica posibles problemas o mejoras."
        
        # Default description
        if not description:
            description = "Analiza esta imagen de paneles solares e identifica posibles problemas o mejoras."
        
        # Add to chat history
        st.session_state["messages"].append({
            "role": "user",
            "content": description,
            "image": image
        })
        
        with st.chat_message("user"):
            st.image(image, caption="Imagen analizada")
            st.write(description)
        
        # Send to API with image
        with st.spinner("Analizando imagen y consulta..."):
            response = chat_with_azure_openai(description, image_data)
        
        # Display response
        st.session_state["messages"].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
        
        # Clear session variables for next interaction
        if "voice_description_audio" in st.session_state:
            del st.session_state["voice_description_audio"]
        if "description" in st.session_state:
            del st.session_state["description"]

# Regular text chat option
st.divider()
st.subheader("O simplemente haz una pregunta:")
user_input = st.chat_input("Escribe tu consulta sobre placas solares...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.spinner("Pensando..."):
        response = chat_with_azure_openai(user_input)
    
    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)