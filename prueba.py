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

# Initialize session state variables
if 'menu' not in st.session_state:
    st.session_state.menu = "Mapa Interactivo"
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None

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

with col_content:
    # Modern menu design with icons
    st.markdown("<div class='sidebar-menu'>", unsafe_allow_html=True)
    
    # Update menu options to include Community Hub
    menu_options = {
        "Mapa Interactivo": "🗺️",
        "Apartado 2": "📷",
        "Community Hub": "🌐"
    }

    # Initialize if not in session state
    if 'menu' not in st.session_state:
        st.session_state.menu = "Mapa Interactivo"

    # Update radio button to include Community Hub
    menu = st.radio("", 
                    ["Mapa Interactivo", "Apartado 2", "Community Hub"],
                    index=["Mapa Interactivo", "Apartado 2", "Community Hub"].index(st.session_state.menu),
                    label_visibility="collapsed",
                    key="menu_selection")

    # Update session state when radio changes
    st.session_state.menu = menu
    
    # Custom menu UI
    for option, icon in menu_options.items():
        active_class = "active" if st.session_state.menu == option else ""
        if st.markdown(f"""
        <div class="menu-option {active_class}" onclick="
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: '{option}'
            }}, '*')
        ">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span>{option}</span>
        </div>
        """, unsafe_allow_html=True):
            st.session_state.menu = option
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Hidden radio button that's controlled by the custom menu
    # menu = st.radio("", ["Mapa Interactivo", "Apartado 2", "Apartado 3"], 
    #                index=["Mapa Interactivo", "Apartado 2", "Apartado 3"].index(st.session_state.menu),
    #                label_visibility="collapsed",
    #                key="menu_selection")

        # First, make sure the menu options list contains all possibilities
    menu_options_list = ["Mapa Interactivo", "Apartado 2"]

    # Then, check if the current menu selection is in this list; if not, default to the first option
    if st.session_state.menu not in menu_options_list:
        st.session_state.menu = menu_options_list[0]

    # # Now use the radio button with the correct index
    # menu = st.radio("", menu_options_list,
    #             index=menu_options_list.index(st.session_state.menu),
    #             label_visibility="collapsed",
    #             key="menu_selection_alternate")

    
    # Update the menu state if changed manually
    if menu != st.session_state.menu:
        st.session_state.menu = menu

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
    
    if st.session_state.menu == "Apartado 2":
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
        st.markdown('<h1 class="main-header">Community Hub</h1>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Knowledge Sharing", "Workforce Marketplace", "Community Challenges"])
        
        with tab1:
            st.markdown('<h2 class="sub-header">Knowledge Sharing Hub</h2>', unsafe_allow_html=True)
            
            # AI-Moderated Q&A Forum
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("AI-Moderated Q&A Forum")
                
                # Sample questions or new question input
                new_question = st.text_area("Ask a technical question:", 
                                        placeholder="E.g., How to fix a solar inverter?")
                
                if st.button("Submit Question"):
                    st.success("Question submitted! Our AI is generating initial answers...")
                    # Here you would integrate with Azure OpenAI
                
                # Sample Q&A display
                st.markdown("### Recent Questions")
                with st.expander("How to troubleshoot voltage issues in my off-grid system?"):
                    st.markdown("""
                    **AI Response**: Check battery connections, verify controller settings, and ensure proper grounding.
                    
                    **Community Answers**:
                    - **Maria (Solar Expert)**: I'd also recommend checking for corroded terminals. [Upvote: 12]
                    - **John**: In my experience, loose connections were the main cause. [Upvote: 5]
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Crowdsourced Resource Library
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Resource Library")
                
                # Upload functionality
                uploaded_file = st.file_uploader("Upload a resource (guide, template, video)", type=["pdf", "docx", "mp4"])
                resource_type = st.selectbox("Resource type", ["Repair Guide", "Installation Manual", "Budget Template", "Tutorial Video"])
                tags = st.multiselect("Tags", ["Solar", "Wind", "Hydro", "Batteries", "Wiring", "DIY", "Professional"])
                
                if st.button("Add to Library"):
                    if uploaded_file is not None:
                        st.success("Resource added to the library and automatically tagged!")
                
                # Sample resources
                st.markdown("### Popular Resources")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    📄 **DIY Solar Installation Guide**  
                    Tags: Solar, DIY, Installation  
                    Uploaded by: Carlos  
                    Downloads: 328
                    """)
                
                with col2:
                    st.markdown("""
                    🎬 **Battery Bank Maintenance Tutorial**  
                    Tags: Batteries, Maintenance, DIY  
                    Uploaded by: Maria  
                    Views: 573
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Case Study Map
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Community Projects Map")
                
                st.markdown('<div class="center-map">', unsafe_allow_html=True)
                # Here you would integrate a map (folium, pydeck, etc.)
                st.image("https://via.placeholder.com/800x400?text=Interactive+Map+of+Projects", use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add project form
                st.subheader("Add Your Project")
                project_name = st.text_input("Project Name")
                project_type = st.selectbox("Project Type", ["Solar Array", "Wind Turbine", "Micro-Hydro", "Battery Bank", "Hybrid System"])
                location = st.text_input("Location")
                description = st.text_area("Project Description")
                
                col1, col2 = st.columns(2)
                with col1:
                    cost = st.number_input("Total Cost ($USD)", min_value=0)
                with col2:
                    capacity = st.number_input("System Capacity (kW)", min_value=0.0, step=0.1)
                
                project_pic = st.file_uploader("Upload Project Photo", type=["jpg", "png"])
                
                if st.button("Submit Project"):
                    st.success("Project added to the community map!")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<h2 class="sub-header">Workforce & Services Marketplace</h2>', unsafe_allow_html=True)
            
            # Job Board
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Job Board")
                
                listing_type = st.radio("I want to:", ["Offer my services", "Find services"])
                
                if listing_type == "Offer my services":
                    st.text_input("Your Name")
                    st.text_input("Skills/Services")
                    st.number_input("Years of Experience", min_value=0)
                    st.text_input("Location")
                    st.slider("Travel Radius (km)", 0, 200, 50)
                    st.text_area("Description of your services")
                    st.file_uploader("Certification Documents (optional)", accept_multiple_files=True)
                    
                    if st.button("List My Services"):
                        st.success("Your profile is now listed in the marketplace!")
                else:
                    st.text_input("Service Needed")
                    st.text_input("Project Location")
                    st.slider("Search Radius (km)", 0, 200, 50)
                    st.date_input("Required By Date")
                    st.text_area("Job Description")
                    
                    if st.button("Post Job"):
                        st.success("Your job has been posted! You'll be notified of matches.")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Skills Verification System
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Skills Verification")
                
                st.markdown("""
                Take technical quizzes to earn verified badges for your profile. These will help you stand out to potential employers!
                """)
                
                available_quizzes = st.selectbox("Available Quizzes", 
                                            ["Basic Electrical Safety", "Solar Panel Installation", 
                                            "Battery System Design", "Micro-Hydro Basics",
                                            "Wind Turbine Maintenance"])
                
                if st.button("Start Quiz"):
                    st.info("Quiz loading... You'll have 30 minutes to complete 20 questions.")
                
                # Sample badges display
                st.subheader("Your Earned Badges")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("🔋 **Battery Expert**")
                with col2:
                    st.markdown("⚡ **Electrical Safety**")
                with col3:
                    st.markdown("🛠️ **Solar Installer**")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Ratings & Reviews
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Community Ratings")
                
                st.markdown("### Top Rated Professionals")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **Miguel Rodriguez** ⭐⭐⭐⭐⭐  
                    Solar Installation Specialist  
                    23 completed jobs
                    
                    > "Miguel was professional and efficient. Highly recommended!" - Ana C.
                    """)
                
                with col2:
                    st.markdown("""
                    **Sofia Torres** ⭐⭐⭐⭐⭐  
                    Electrical Engineer  
                    17 completed jobs
                    
                    > "Sofia helped design our off-grid system and was incredibly knowledgeable." - Marco P.
                    """)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<h2 class="sub-header">Community Challenges & Incentives</h2>', unsafe_allow_html=True)
            
            # Active Challenges
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Active Challenges")
                
                # Challenge progress bars
                st.markdown("### 100 Solar Homes Challenge - Guatemala")
                st.progress(65)
                st.markdown("65/100 homes completed - 15 days remaining")
                
                st.markdown("### Wind Power Expansion - Coastal Communities")
                st.progress(30)
                st.markdown("3/10 community turbines installed - 45 days remaining")
                
                st.markdown("### 1000 kWh Energy Savings Challenge")
                st.progress(82)
                st.markdown("820/1000 kWh saved this month")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Carbon Tracker
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Community Impact")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="CO₂ Reduced", value="523 tonnes", delta="↑ 42 this month")
                
                with col2:
                    st.metric(label="Renewable kWh Generated", value="87,413", delta="↑ 5,210 this month")
                
                with col3:
                    st.metric(label="Fossil Fuels Avoided", value="$31,265", delta="↑ $2,845 this month")
                
                # Carbon savings chart
                st.subheader("Monthly Carbon Savings (tonnes CO₂)")
                chart_data = {
                    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "values": [32, 45, 67, 89, 121, 169]
                }
                
                # Here you would add a chart using plotly, altair, etc.
                st.image("https://via.placeholder.com/800x300?text=Carbon+Savings+Chart", use_column_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Rewards & Incentives
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Rewards & Incentives")
                
                st.markdown("""
                ### Available Rewards for Challenge Participants
                
                - **10% Discount** on solar panels from SunPower Partners
                - **Free Technical Assessment** for your renewable energy project
                - **Training Workshops** with certified renewable energy experts
                - **Community Recognition** and feature in our monthly newsletter
                
                ### Your Current Points: 320
                
                Points can be earned by:
                - Contributing to challenges
                - Sharing knowledge in the forum
                - Completing verified projects
                - Bringing new members to the community
                """)
                
                if st.button("Redeem Points"):
                    st.info("Opening rewards catalog...")
                
                st.markdown("</div>", unsafe_allow_html=True)

    # Update the sidebar to include the new menu option
    # In your app's initialization section, add:
    # if "menu" not in st.session_state:
    #     st.session_state.menu = "Dashboard"

    # Then in your sidebar code:
    # st.sidebar.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
    # for option in ["Dashboard", "Apartado 2", "Community Hub"]:
    #     if st.sidebar.button(option, key=option):
    #         st.session_state.menu = option
    # st.sidebar.markdown('</div>', unsafe_allow_html=True)