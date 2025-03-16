import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap
import openai
import json
import time
import speech_recognition as sr
from io import BytesIO
import base64
from PIL import Image
import io

# Load configuration from settings.json
try:
    with open('settings.json', 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    # Default settings in case the file doesn't exist
    settings = {
        'azure_openai': {
            'api_key': 'YOUR_API_KEY',
            'api_version': '2023-12-01-preview',
            'azure_endpoint': 'https://your-resource-name.openai.azure.com/',
            'deployment_name': 'YOUR_DEPLOYMENT_NAME'
        }
    }

# Page configuration
st.set_page_config(
    layout="wide", 
    page_title="Explorador Solar - Latinoamérica",
    page_icon="☀️"
)

# Enhanced custom CSS with animations and modern design
st.markdown("""
<style>
    /* Main styles and colors */
    :root {
        --primary: #1E88E5;
        --primary-dark: #0D47A1;
        --accent: #FFC107;
        --light-bg: #F5F9FF;
        --card-bg: #FFFFFF;
        --success: #4CAF50;
        --warning: #FF9800;
        --danger: #F44336;
    }
    
    /* Modern look for the entire app */
    .main {
        background-color: var(--light-bg);
        padding: 1rem;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: var(--primary);
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--accent);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        color: var(--primary-dark);
        text-align: center;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .card {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    
    /* Info box styling */
    .info-box {
        background-color: var(--light-bg);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Map container */
    .center-map {
        display: flex;
        justify-content: center;
        padding: 0.5rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Divider styling */
    .divider {
        margin: 2rem 0;
        height: 2px;
        background: linear-gradient(90deg, rgba(255,255,255,0), var(--primary), rgba(255,255,255,0));
        border: none;
    }
    
    /* Coordinates box */
    .coordinates-box {
        background: linear-gradient(135deg, #EBF5FF, #E3F2FD);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        border-left: 5px solid var(--primary);
        color: var(--primary-dark);
    }
    
    /* Chat container with fixed height and scrolling */
    .chat-container {
        height: 50vh;  /* Reduce height to make room for input */
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;  /* Reduced margin to bring input closer */
        background-color: #f9f9f9;
    }
    
    .message-container {
        display: flex;
        margin-bottom: 0.8rem;
    }
    
    .user-message {
        background-color: #E3F2FD;
        padding: 0.8rem;
        border-radius: 18px 18px 0 18px;
        margin-left: auto;
        max-width: 80%;
    }
    
    .assistant-message {
        background-color: #F5F5F5;
        padding: 0.8rem;
        border-radius: 18px 18px 18px 0;
        margin-right: auto;
        max-width: 80%;
    }
    
    /* Agent sidebar */
    .agent-sidebar {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Button styling */
    .stButton button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        background-color: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Metrics styling */
    .css-1r6slb0 {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        padding: 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary);
        color: white;
    }
    
    /* Chat input */
    .stChatInput {
        border-radius: 24px;
        padding: 0.3rem 1rem;
        margin-top: 1rem;
    }
    
    /* Add smooth scrolling for the entire app */
    * {
        scroll-behavior: smooth;
    }
    
    /* Sidebar menu styling */
    .sidebar-menu {
        background-color: white;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    
    .menu-option {
        padding: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .menu-option:hover {
        background-color: #F0F7FF;
    }
    
    .menu-option.active {
        background-color: var(--primary);
        color: white;
        font-weight: 600;
    }
    
    /* Improve radio button styling */
    .stRadio > div {
        padding: 0.5rem;
        background-color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Define functions that the LLM can call
def click_on_map(lat, lng):
    """
    Simulate clicking on a specific location on the map
    """
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    
    st.session_state.selected_location = (float(lat), float(lng))
    return f"Clicked on map at latitude {lat}, longitude {lng}"

def change_menu(menu_name):
    """
    Change the active menu section
    """
    if menu_name in ["Mapa Interactivo", "Apartado 2", "Community Hub"]:
        st.session_state.menu = menu_name
        return f"Changed to menu: {menu_name}"
    else:
        return f"Invalid menu name. Available menus: Mapa Interactivo, Apartado 2, Community Hub"
    
# Helper function to auto-scroll chat to bottom
def auto_scroll_chat():
    js = '''
    <script>
        function scrollChatToBottom() {
            var chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }
        // Execute immediately and after a delay to ensure content is rendered
        scrollChatToBottom();
        setTimeout(scrollChatToBottom, 300);
        // Also set a periodic check in case new content is loaded
        setInterval(scrollChatToBottom, 500);
    </script>
    '''
    st.markdown(js, unsafe_allow_html=True)

# The function calling setup for Azure OpenAI
def chat_with_azure_openai(prompt, chat_history):
    # Create Azure OpenAI client
    client = openai.AzureOpenAI(
        api_key=settings['azure_openai']['api_key'],
        api_version=settings['azure_openai']['api_version'],
        azure_endpoint=settings['azure_openai']['azure_endpoint']
    )
    
    # Define function schemas for the LLM to understand
    functions = [
        {
            "name": "click_on_map",
            "description": "Click on a specific location on the map. Use this when the user asks to select or click on a specific city, location, or coordinates on the map.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "The latitude coordinate"
                    },
                    "lng": {
                        "type": "number",
                        "description": "The longitude coordinate"
                    }
                },
                "required": ["lat", "lng"]
            }
        },
        {
            "name": "change_menu",
            "description": "Change to a different menu section in the application",
            "parameters": {
                "type": "object",
                "properties": {
                    "menu_name": {
                        "type": "string",
                        "description": "The name of the menu section to change to",
                        "enum": ["Mapa Interactivo", "Apartado 2", "Community Hub"]
                    }
                },
                "required": ["menu_name"]
            }
        }
    ]
    
    system_message = """
    Eres un asistente experto en instalaciones solares que puede interactuar con un mapa de Latinoamérica. 
    Puedes ayudar a los usuarios a explorar ubicaciones potenciales para instalaciones solares.
    
    Tienes la capacidad de:
    1. Hacer clic en ubicaciones específicas del mapa (usando la función click_on_map)
    2. Cambiar entre diferentes secciones del menú (usando la función change_menu)
    
    Cuando los usuarios te pidan interactuar con el mapa:
    - Si mencionan una ciudad o ubicación específica, usa la función click_on_map con las coordenadas aproximadas de esa ubicación
    - Si piden ver una sección diferente, usa la función change_menu
    
    Datos importantes sobre Latinoamérica y energía solar:
    - México, Chile, Brasil y Colombia son líderes en adopción de energía solar
    - La región ecuatorial tiene alta radiación solar anual
    - Los desiertos de Atacama (Chile) y Sonora (México) tienen condiciones óptimas para energía solar
    
    Proporciona explicaciones claras y concisas sobre las instalaciones solares y cómo las ubicaciones seleccionadas pueden ser adecuadas para proyectos solares.
    """
    
    messages = [
        {"role": "system", "content": system_message}
    ] + chat_history + [{"role": "user", "content": prompt}]
    
    # Call the Azure OpenAI API with function calling capability
    try:
        response = client.chat.completions.create(
            model=settings['azure_openai']['deployment_name'],
            messages=messages,
            temperature=0.5,
            max_tokens=16384,
            functions=functions,
            function_call="auto"  # Let the model decide when to call functions
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to call a function
        if hasattr(response_message, 'function_call') and response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            
            # Execute the appropriate function
            if function_name == "click_on_map":
                result = click_on_map(function_args.get("lat"), function_args.get("lng"))
            elif function_name == "change_menu":
                result = change_menu(function_args.get("menu_name"))
            else:
                result = "Unknown function"
            
            # Add the function response to the conversation
            messages.append({"role": "assistant", "content": None, "function_call": {"name": function_name, "arguments": response_message.function_call.arguments}})
            messages.append({"role": "function", "name": function_name, "content": result})
            
            # Get a new response from the model
            second_response = client.chat.completions.create(
                model=settings['azure_openai']['deployment_name'],
                messages=messages,
                temperature=0.5,
                max_tokens=16384
            )
            
            return second_response.choices[0].message.content
        
        # If no function call, return the response directly
        return response_message.content
    except Exception as e:
        return f"Error al comunicarse con el servicio de OpenAI: {str(e)}"

# Función para obtener información sobre la ubicación
def get_location_info(lat, lon):
    geolocator = Nominatim(user_agent="streamlit_app")
    try:
        location = geolocator.reverse((lat, lon), language="es")
        return location.address if location else "Información no disponible"
    except:
        return "Error al obtener información de ubicación"

# Generar datos aleatorios para el mapa de calor dentro del radio especificado
def generate_heatmap_data_in_radius(center_lat, center_lon, radius_km=2, num_points=200):
    # Radio en grados aproximadamente (1 grado ≈ 111 km en el ecuador)
    radius_degree = radius_km / 111
    
    # Generar puntos aleatorios dentro del radio
    np.random.seed(42)  # Para reproducibilidad
    
    # Generar puntos aleatorios en un círculo usando coordenadas polares
    r = radius_degree * np.sqrt(np.random.uniform(0, 1, num_points))
    theta = np.random.uniform(0, 2 * np.pi, num_points)
    
    # Convertir a coordenadas cartesianas
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # Intensidad de los puntos (más intensos cerca del centro)
    intensity = 1 - (r / radius_degree)
    
    # Crear lista de datos para el mapa de calor
    heat_data = []
    for i in range(num_points):
        lat = center_lat + y[i]
        lon = center_lon + x[i]
        heat_data.append([lat, lon, intensity[i]])
    
    return heat_data

def chat_with_azure_openai_image(prompt, image_data=None):
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
        model=settings['azure_openai']['deployment_name'],
        messages=messages,
        temperature=0.7,
        max_tokens=16384
    )

    return response.choices[0].message.content


# Initialize session state variables
if 'menu' not in st.session_state:
    st.session_state.menu = "Mapa Interactivo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None

# # Initialize session state variables
# if 'menu' not in st.session_state:
#     st.session_state.menu = "Mapa Interactivo"
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if 'selected_location' not in st.session_state:
#     st.session_state.selected_location = None

# Apply custom CSS for fixed chat positioning
st.markdown("""
<style>
    .chat-container {
        height: 50vh;  /* Reduce height to make room for input */
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;  /* Reduced margin to bring input closer */
        background-color: #f9f9f9;
    }
    .message-container {
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #E3F2FD;
        padding: 8px 12px;
        border-radius: 15px 15px 0 15px;
        align-self: flex-end;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #E8F5E9;
        padding: 8px 12px;
        border-radius: 15px 15px 15px 0;
        align-self: flex-start;
        max-width: 80%;
    }
    .agent-sidebar {
        padding: 15px;
        background-color: #f5f5f5;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .main-header {
        font-weight: 600;
    }
    .stChatInputContainer {
        position: fixed;
        bottom: 20px;
        left: 1.5%;  /* Align with column */
        width: 23%;  /* Match approximately column width */
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# Function to ensure chat always scrolls to bottom


# App Header with logo-like design
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <div style="font-size: 3rem; color: #1E88E5; margin-bottom: -0.5rem;">☀️</div>
    <h1 class='main-header'>Explorador de Mapas para Instalaciones Solares</h1>
</div>
""", unsafe_allow_html=True)

# Layout with columns for chat and map
col_chat, col_content = st.columns([1, 3])

# Replace the chat container section with this code
with col_chat:
    st.markdown("<div class='agent-sidebar'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.8rem;">
        <div style="background-color: #4CAF50; width: 40px; height: 40px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 1.5rem;">🤖</div>
        <div>
            <h3 style="margin: 0;">Asistente Solar</h3>
            <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">En línea y listo para ayudar</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write("Haz preguntas sobre instalaciones solares o pide que interactúe con el mapa por ti.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Create a container for the chat messages
    chat_container = st.container()
    
    # Create a container for the input at the bottom
    input_container = st.container()
    
    # Use the input container (this needs to be before displaying messages for layout purposes)
    with input_container:
        user_input = st.chat_input("Pregunta algo o pide interactuar con el mapa...", key="chat_input")
    
    # Display messages in the chat container
    with chat_container:
        st.markdown("<div class='chat-container' id='chat-container'>", unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-container">
                    <div class="user-message">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-container">
                    <div class="assistant-message">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add auto-scroll JavaScript
    auto_scroll_chat()
    
    # Process user input
    if user_input:
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display loading animation
        with st.spinner("Pensando..."):
            # Get response from OpenAI
            response = chat_with_azure_openai(user_input, st.session_state.messages)
            
            # Add assistant response to state
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Force rerun to update the UI
        st.rerun()

if "menu" not in st.session_state:
    st.session_state.menu = "Mapa Interactivo"

tabs = {
    "🗺️ Mapa": "Mapa Interactivo",
    "🤖 Chatbot": "Chatbot",
    "🌍 Comunidad": "Community Hub"
}

with col_content:
    st.markdown("<style>div.stButton > button { width: 100%; }</style>", unsafe_allow_html=True)

    with st.container():
        cols = st.columns(len(tabs))

        for i, (emoji_tab, tab) in enumerate(tabs.items()):
            if cols[i].button(emoji_tab, key=f"tab_{tab}"):
                if st.session_state.menu != tab:  # Avoid unnecessary reruns
                    st.session_state.menu = tab
                    st.rerun()

    st.markdown(f"## {st.session_state.menu}")

    # Apartado 1: Mapa Interactivo
    if st.session_state.menu == "Mapa Interactivo":

        st.markdown("<h2 class='sub-header'>Mapa Interactivo de Latinoamérica</h2>", unsafe_allow_html=True)
        
        # Create a card container for the map and details
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Create columns for the layout
        map_col, info_col = st.columns([7, 5])
        
        # Map center (aproximately center of Latin America)
        center_lat, center_lon = -15.0, -60.0
        
        with map_col:
            st.markdown("<div class='center-map'>", unsafe_allow_html=True)
            # Create base map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=3, control_scale=True)
            
            # Add tile layers with proper attribution
            folium.TileLayer(
                'CartoDB positron',
                attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            ).add_to(m)
            
            folium.TileLayer(
                'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
                attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                name='Stamen Terrain'
            ).add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Show map in Streamlit with click capture
            output = st_folium(m, width=700, height=500)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Process map clicks
            if output["last_clicked"]:
                clicked_lat = output["last_clicked"]["lat"]
                clicked_lng = output["last_clicked"]["lng"]
                st.session_state.selected_location = (clicked_lat, clicked_lng)
        
        with info_col:
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            st.markdown("<h3 class='sub-header'>Detalles de la ubicación</h3>", unsafe_allow_html=True)
            
            if st.session_state.selected_location:
                lat, lng = st.session_state.selected_location
                
                # Show coordinates in a highlighted box
                st.markdown(f"""
                <div class="coordinates-box">
                    <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.3rem;">COORDENADAS</div>
                    Latitud: {lat:.6f}<br>
                    Longitud: {lng:.6f}
                </div>
                """, unsafe_allow_html=True)
                
                # Create map to show 2 km radius area
                detail_map = folium.Map(location=[lat, lng], zoom_start=13)
                
                # Add marker at selected location
                folium.Marker(
                    [lat, lng],
                    popup=f"Lat: {lat:.6f}, Lon: {lng:.6f}",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(detail_map)
                
                # Add circle with 2 km radius
                folium.Circle(
                    location=[lat, lng],
                    radius=2000,  # 2 km in meters
                    color="#3186cc",
                    fill=True,
                    fill_color="#3186cc",
                    fill_opacity=0.2,
                    popup="Radio de 2 km"
                ).add_to(detail_map)
                
                # Show detail map
                st.markdown("<div class='center-map'>", unsafe_allow_html=True)
                folium_static(detail_map, width=400, height=300)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Show location info
                location_info = get_location_info(lat, lng)
                st.markdown("""
                <div style="margin-top: 1rem;">
                    <div style="font-weight: 600; color: #0D47A1; margin-bottom: 0.5rem;">
                        📍 Información de la ubicación:
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write(location_info)
                
                # Add solar potential info (simulated)
                st.markdown("""
                <div style="margin-top: 1rem;">
                    <div style="font-weight: 600; color: #0D47A1; margin-bottom: 0.5rem;">
                        ☀️ Potencial Solar Estimado:
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Simulate solar potential values based on latitude
                solar_potential = abs(lat) * 0.5  # Simulated value
                st.progress(min(solar_potential/10, 1.0))
                
                if solar_potential > 7:
                    st.success(f"Alto potencial solar: {solar_potential:.1f}/10")
                elif solar_potential > 4:
                    st.warning(f"Potencial solar moderado: {solar_potential:.1f}/10")
                else:
                    st.error(f"Bajo potencial solar: {solar_potential:.1f}/10")
            else:
                st.info("Haz clic en el mapa para seleccionar una ubicación y ver los detalles, o pide al asistente que seleccione una ubicación por ti.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # End of card
        
        # Add a divider
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        
        # Section for heat map based on radius
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='sub-header'>Análisis de Radiación Solar - Radio de 2 km</h3>", unsafe_allow_html=True)
        
        if st.session_state.selected_location:
            lat, lng = st.session_state.selected_location
            
            # Generate random data for heat map within 2 km radius
            heat_data = generate_heatmap_data_in_radius(lat, lng, radius_km=2, num_points=300)
            
            # Create heat map
            heatmap = folium.Map(location=[lat, lng], zoom_start=13)
            
            # Add marker at selected location
            folium.Marker(
                [lat, lng],
                popup=f"Lat: {lat:.6f}, Lon: {lng:.6f}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(heatmap)
            
            # Add circle with 2 km radius
            folium.Circle(
                location=[lat, lng],
                radius=2000,  # 2 km en metros
                color="#3186cc",
                fill=False,
                weight=2,
                popup="Radio de 2 km"
            ).add_to(heatmap)
            
            # Add heat map layer
            HeatMap(
                heat_data, 
                radius=15, 
                blur=10, 
                max_zoom=13, 
                gradient={
                    '0.4': '#87CEFA', 
                    '0.65': '#ADD8E6', 
                    '0.8': '#4682B4', 
                    '0.9': '#0000CD', 
                    '1.0': '#00008B'
                }
            ).add_to(heatmap)
            
            # Show heat map
            st.markdown("<div class='center-map'>", unsafe_allow_html=True)
            folium_static(heatmap, width=900, height=400)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align: center; margin-top: 20px; padding: 15px; background-color: #f0f7ff; border-radius: 8px;">
                <h4 style="color: #1E88E5; margin-bottom: 10px;">Interpretación del Mapa de Calor</h4>
                <p>Este mapa de calor muestra la radiación solar estimada dentro del radio de 2 km de la ubicación seleccionada.</p>
                <p>Los colores más intensos indican mayor radiación solar, ideal para la instalación de paneles solares.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Solar installation information with animated cards
            st.markdown("""
            <h4 style="color: #0D47A1; margin: 20px 0 15px 0; text-align: center;">Recomendaciones para Instalación Solar</h4>
            """, unsafe_allow_html=True)
            
            # Use two columns with animated metric cards
            col1, col2 = st.columns(2)
            with col1:
                radiation = np.random.uniform(4.5, 6.5)
                roi = np.random.uniform(3.5, 7.5)
                
                st.markdown(f"""
                <div style="background: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 4px solid #1E88E5;">
                    <div style="font-size: 0.9rem; color: #666;">Radiación Solar Estimada</div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: #0D47A1;">{radiation:.2f} kWh/m²/día</div>
                </div>
                
                <div style="background: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-left: 4px solid #FFC107;">
                    <div style="font-size: 0.9rem; color: #666;">ROI Estimado</div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: #FF9800;">{roi:.1f} años</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                generation = np.random.uniform(1300, 2200)
                co2_savings = np.random.uniform(500, 1200)
                
                st.markdown(f"""
                <div style="background: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 4px solid #4CAF50;">
                    <div style="font-size: 0.9rem; color: #666;">Potencial de Generación</div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: #2E7D32;">{generation:.0f} kWh/kWp/año</div>
                </div>
                
                <div style="background: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-left: 4px solid #9C27B0;">
                    <div style="font-size: 0.9rem; color: #666;">Ahorro CO₂ Estimado</div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: #6A1B9A;">{co2_savings:.0f} kg/año</div>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.info("Selecciona una ubicación en el mapa principal para generar el análisis de radiación solar en el radio de 2 km.")
        st.markdown("</div>", unsafe_allow_html=True)  # End of card
    
    if st.session_state.menu == "Chatbot":
        st.markdown("<h2 class='sub-header'>Análisis Visual de Placas Solares</h2>", unsafe_allow_html=True)
        
        # Create a card container for the image analysis
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 2rem; color: #1E88E5; margin-bottom: 0.5rem;">📷 + 🗣️</div>
            <p>Sube o captura una imagen de paneles solares y describe tu consulta por voz o texto</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                if st.button("🎤 Grabar consulta (10s)", use_container_width=True):
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
        st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
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
                
                # Display loading spinner and analysis
                with st.spinner("Analizando imagen y consulta..."):
                    response = chat_with_azure_openai_image(description, image_data)
                
                # Display result in a nice card
                st.markdown("""
                <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-top: 20px;">
                    <h3 style="color: #1E88E5; margin-bottom: 15px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">Resultado del Análisis</h3>
                """, unsafe_allow_html=True)
                
                # Display the analyzed image
                st.image(image, caption="Imagen analizada", width=400)
                
                # Display the query
                st.markdown(f"""
                <div style="background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <p style="font-weight: 600; margin-bottom: 5px;">Tu consulta:</p>
                    <p style="margin: 0;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the response
                st.markdown(f"""
                <div style="background-color: #F5F5F5; padding: 15px; border-radius: 8px;">
                    <p style="font-weight: 600; margin-bottom: 5px;">Análisis:</p>
                    <p style="margin: 0;">{response}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Clear session variables for next interaction
                if "voice_description_audio" in st.session_state:
                    del st.session_state["voice_description_audio"]
                if "description" in st.session_state:
                    del st.session_state["description"]
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add information about the feature
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 style="color: #0D47A1; margin-bottom: 15px;">Sobre esta funcionalidad</h3>
        <p>Esta herramienta utiliza inteligencia artificial para analizar imágenes de instalaciones solares y proporcionar un diagnóstico experto.</p>
        <p>Puedes utilizar esta función para:</p>
        <ul>
            <li>Identificar problemas en la instalación de paneles solares</li>
            <li>Detectar posibles mejoras en la eficiencia</li>
            <li>Evaluar la orientación y colocación de los paneles</li>
            <li>Identificar daños o deterioro en los equipos</li>
            <li>Recibir recomendaciones para optimizar tu instalación</li>
        </ul>
        <p>Para obtener mejores resultados, intenta proporcionar imágenes claras y bien iluminadas de tus paneles solares.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.menu == "Community Hub":
        st.markdown('<h1 class="main-header">Centro Comunitario</h1>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Intercambio de Conocimiento", "Mercado Laboral", "Desafíos Comunitarios"])
        
        with tab1:
            st.markdown('<h2 class="sub-header">Centro de Intercambio de Conocimiento</h2>', unsafe_allow_html=True)
            
            # Foro de Preguntas y Respuestas moderado por IA
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Foro de Preguntas y Respuestas moderado por IA")
                
                # Ejemplos de preguntas o ingreso de nueva pregunta
                new_question = st.text_area("Haz una pregunta técnica:", 
                                        placeholder="Ej., ¿Cómo reparar un inversor solar?")
                
                if st.button("Enviar Pregunta"):
                    st.success("¡Pregunta enviada! Nuestra IA está generando respuestas iniciales...")
                    # Aquí integrarías con Azure OpenAI
                
                # Muestra de preguntas y respuestas
                st.markdown("### Preguntas Recientes")
                with st.expander("¿Cómo solucionar problemas de voltaje en mi sistema autónomo?"):
                    st.markdown("""
                    **Respuesta IA**: Revisa las conexiones de la batería, verifica la configuración del controlador y asegúrate de tener una correcta conexión a tierra.
                    
                    **Respuestas de la Comunidad**:
                    - **María (Experta en Solar)**: También recomendaría revisar si hay terminales corroídos. [Votos: 12]
                    - **Juan**: En mi experiencia, las conexiones sueltas fueron la causa principal. [Votos: 5]
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Biblioteca de recursos colaborativa
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Biblioteca de Recursos")
                
                # Funcionalidad de carga
                uploaded_file = st.file_uploader("Sube un recurso (guía, plantilla, video)", type=["pdf", "docx", "mp4"], key="resource_uploader")
                resource_type = st.selectbox("Tipo de recurso", ["Guía de Reparación", "Manual de Instalación", "Plantilla de Presupuesto", "Video Tutorial"], key="resource_type")
                tags = st.multiselect("Etiquetas", ["Solar", "Eólico", "Hidro", "Baterías", "Cableado", "Hazlo Tú Mismo", "Profesional"], key="resource_tags")
                
                if st.button("Añadir a la Biblioteca", key="add_to_library"):
                    if uploaded_file is not None:
                        st.success("¡Recurso añadido a la biblioteca y etiquetado automáticamente!")
                
                # Recursos de ejemplo
                st.markdown("### Recursos Populares")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    📄 **Guía de Instalación Solar DIY**  
                    Etiquetas: Solar, DIY, Instalación  
                    Subido por: Carlos  
                    Descargas: 328
                    """)
                
                with col2:
                    st.markdown("""
                    🎬 **Tutorial de Mantenimiento de Banco de Baterías**  
                    Etiquetas: Baterías, Mantenimiento, DIY  
                    Subido por: María  
                    Visualizaciones: 573
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Mapa de Casos de Estudio
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Mapa de Proyectos Comunitarios")
                
                st.markdown('<div class="center-map">', unsafe_allow_html=True)
                # Aquí integrarías un mapa (folium, pydeck, etc.)
                st.image("https://via.placeholder.com/800x400?text=Mapa+Interactivo+de+Proyectos", use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Formulario para añadir proyecto
                st.subheader("Añade Tu Proyecto")
                project_name = st.text_input("Nombre del Proyecto", key="project_name")
                project_type = st.selectbox("Tipo de Proyecto", ["Array Solar", "Turbina Eólica", "Micro-Hidro", "Banco de Baterías", "Sistema Híbrido"], key="project_type")
                location = st.text_input("Ubicación", key="project_location")
                description = st.text_area("Descripción del Proyecto", key="project_description")
                
                col1, col2 = st.columns(2)
                with col1:
                    cost = st.number_input("Costo Total ($USD)", min_value=0, key="project_cost")
                with col2:
                    capacity = st.number_input("Capacidad del Sistema (kW)", min_value=0.0, step=0.1, key="project_capacity")
                
                project_pic = st.file_uploader("Subir Foto del Proyecto", type=["jpg", "png"], key="project_pic")
                
                if st.button("Enviar Proyecto", key="submit_project"):
                    st.success("¡Proyecto añadido al mapa comunitario!")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<h2 class="sub-header">Mercado de Fuerza Laboral y Servicios</h2>', unsafe_allow_html=True)
            
            # Tablón de Empleo
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Tablón de Empleo")
                
                listing_type = st.radio("Quiero:", ["Ofrecer mis servicios", "Encontrar servicios"], key="listing_type")
                
                if listing_type == "Ofrecer mis servicios":
                    st.text_input("Tu Nombre", key="provider_name")
                    st.text_input("Habilidades/Servicios", key="provider_skills")
                    st.number_input("Años de Experiencia", min_value=0, key="provider_experience")
                    st.text_input("Ubicación", key="provider_location")
                    st.slider("Radio de Desplazamiento (km)", 0, 200, 50, key="provider_radius")
                    st.text_area("Descripción de tus servicios", key="provider_description")
                    st.file_uploader("Documentos de Certificación (opcional)", accept_multiple_files=True, key="provider_certifications")
                    
                    if st.button("Publicar Mis Servicios", key="publish_services"):
                        st.success("¡Tu perfil ahora está listado en el mercado!")
                else:
                    st.text_input("Servicio Necesario", key="seeker_service")
                    st.text_input("Ubicación del Proyecto", key="seeker_location")
                    st.slider("Radio de Búsqueda (km)", 0, 200, 50, key="seeker_radius")
                    st.date_input("Fecha Requerida", key="seeker_date")
                    st.text_area("Descripción del Trabajo", key="seeker_description")
                    
                    if st.button("Publicar Trabajo", key="publish_job"):
                        st.success("¡Tu trabajo ha sido publicado! Serás notificado de las coincidencias.")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Sistema de Verificación de Habilidades
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Verificación de Habilidades")
                
                st.markdown("""
                Realiza cuestionarios técnicos para ganar insignias verificadas para tu perfil. ¡Estas te ayudarán a destacar ante posibles empleadores!
                """)
                
                available_quizzes = st.selectbox("Cuestionarios Disponibles", 
                                            ["Seguridad Eléctrica Básica", "Instalación de Paneles Solares", 
                                            "Diseño de Sistemas de Baterías", "Fundamentos de Micro-Hidro",
                                            "Mantenimiento de Turbinas Eólicas"],
                                            key="available_quizzes")
                
                if st.button("Iniciar Cuestionario", key="start_quiz"):
                    st.info("Cargando cuestionario... Tendrás 30 minutos para completar 20 preguntas.")
                
                # Muestra de insignias
                st.subheader("Tus Insignias Obtenidas")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("🔋 **Experto en Baterías**")
                with col2:
                    st.markdown("⚡ **Seguridad Eléctrica**")
                with col3:
                    st.markdown("🛠️ **Instalador Solar**")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Valoraciones y Reseñas
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Valoraciones Comunitarias")
                
                st.markdown("### Profesionales Mejor Valorados")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **Miguel Rodríguez** ⭐⭐⭐⭐⭐  
                    Especialista en Instalación Solar  
                    23 trabajos completados
                    
                    > "Miguel fue profesional y eficiente. ¡Muy recomendable!" - Ana C.
                    """)
                
                with col2:
                    st.markdown("""
                    **Sofía Torres** ⭐⭐⭐⭐⭐  
                    Ingeniera Eléctrica  
                    17 trabajos completados
                    
                    > "Sofía nos ayudó a diseñar nuestro sistema autónomo y tenía un conocimiento increíble." - Marco P.
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<h2 class="sub-header">Desafíos e Incentivos Comunitarios</h2>', unsafe_allow_html=True)
            
            # Desafíos Activos
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Desafíos Activos")
                
                # Barras de progreso de desafíos
                st.markdown("### Desafío 100 Hogares Solares - Guatemala")
                st.progress(65)
                st.markdown("65/100 hogares completados - 15 días restantes")
                
                st.markdown("### Expansión de Energía Eólica - Comunidades Costeras")
                st.progress(30)
                st.markdown("3/10 turbinas comunitarias instaladas - 45 días restantes")
                
                st.markdown("### Desafío de Ahorro de 1000 kWh de Energía")
                st.progress(82)
                st.markdown("820/1000 kWh ahorrados este mes")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Rastreador de Carbono
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Impacto Comunitario")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="CO₂ Reducido", value="523 toneladas", delta="↑ 42 este mes")
                
                with col2:
                    st.metric(label="kWh Renovables Generados", value="87,413", delta="↑ 5,210 este mes")
                
                with col3:
                    st.metric(label="Combustibles Fósiles Evitados", value="$31,265", delta="↑ $2,845 este mes")
                
                # Gráfico de ahorro de carbono
                st.subheader("Ahorro Mensual de Carbono (toneladas CO₂)")
                chart_data = {
                    "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
                    "values": [32, 45, 67, 89, 121, 169]
                }
                
                # Aquí añadirías un gráfico usando plotly, altair, etc.
                st.image("https://via.placeholder.com/800x300?text=Gráfico+de+Ahorro+de+Carbono", use_column_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Recompensas e Incentivos
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Recompensas e Incentivos")
                
                st.markdown("""
                ### Recompensas Disponibles para Participantes de Desafíos
                
                - **10% de Descuento** en paneles solares de Socios SunPower
                - **Evaluación Técnica Gratuita** para tu proyecto de energía renovable
                - **Talleres de Formación** con expertos certificados en energía renovable
                - **Reconocimiento Comunitario** y aparición en nuestro boletín mensual
                
                ### Tus Puntos Actuales: 320
                
                Los puntos se pueden ganar mediante:
                - Contribución a desafíos
                - Compartir conocimientos en el foro
                - Completar proyectos verificados
                - Traer nuevos miembros a la comunidad
                """)
                
                if st.button("Canjear Puntos", key="redeem_points"):
                    st.info("Abriendo catálogo de recompensas...")
                
                st.markdown("</div>", unsafe_allow_html=True)