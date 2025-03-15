import streamlit as st
import openai

def chat_with_azure_openai(prompt):
    client = openai.AzureOpenAI(
        api_key="6evUUU8hO6Z13XrWLqupolcAtbxiOdCiw0LBeu2prfMuqEd33BwUJQQJ99BCACYeBjFXJ3w3AAAAACOGQmQt",
        api_version="2023-12-01-preview",  # Usa la última versión
        azure_endpoint="https://ai-hackathonuabpayretailers082809715538.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-10-21",
    )

    response = client.chat.completions.create(
        model="YOUR_DEPLOYMENT_NAME",  # Nombre del modelo desplegado
        messages=[
            {"role": "system", "content": "Eres un experto en instalación de placas solares."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=16384
    )

    return response.choices[0].message.content

# Interfaz con Streamlit
st.title("Chatbot Especialista en Placas Solares ☀️")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Haz una pregunta sobre instalación de placas solares...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    response = chat_with_azure_openai(user_input)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    
    with st.chat_message("assistant"):
        st.write(response)
