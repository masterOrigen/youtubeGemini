import os
import streamlit as st
from dotenv import load_dotenv
import requests

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key de Gemini desde las variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Función para obtener la transcripción de un video de YouTube utilizando la API de Gemini
def obtener_transcripcion_youtube(url):
    try:
        # Endpoint de la API de Gemini para obtener la transcripción de un video de YouTube
        url_api_gemini = "https://api.gemini.com/transcripcion"

        # Parámetros de la solicitud
        params = {
            "apikey": GEMINI_API_KEY,
            "url": url
        }

        # Realizar la solicitud a la API de Gemini
        response = requests.get(url_api_gemini, params=params)
        response_data = response.json()

        if response.status_code == 200:
            transcripcion = response_data.get("transcripcion")
            return transcripcion
        else:
            st.error("Ocurrió un error al obtener la transcripción del video.")
            return None
    except Exception as e:
        st.error("Error de conexión: {}".format(e))
        return None

# Configurar la página de Streamlit
st.set_page_config(
    page_title="Obtener Transcripción de Video de YouTube",
    layout="centered"
)

# Título de la aplicación
st.title("Obtener Transcripción de Video de YouTube")

# Entrada de texto para ingresar la URL del video de YouTube
url_video_youtube = st.text_input("Ingresa la URL del video de YouTube:")

# Botón para obtener la transcripción del video
if st.button("Obtener Transcripción"):
    if url_video_youtube:
        transcripcion = obtener_transcripcion_youtube(url_video_youtube)
        if transcripcion:
            st.write("Transcripción del video:")
            st.write(transcripcion)
    else:
        st.warning("Por favor ingresa la URL del video de YouTube.")
