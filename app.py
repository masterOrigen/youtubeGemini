import os
import streamlit as st
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key de YouTube desde las variables de entorno
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Función para obtener la transcripción de un video de YouTube utilizando la API de Google
def obtener_transcripcion_youtube(url_video):
    try:
        # Extraer el ID del video de la URL
        video_id = obtener_video_id(url_video)
        
        # Construir el servicio de la API de YouTube
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        
        # Obtener detalles del video
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        # Extraer el título del video
        video_title = video_response["items"][0]["snippet"]["title"]

        # Obtener subtítulos (si están disponibles)
        captions_response = youtube.captions().list(
            part="id",
            videoId=video_id
        ).execute()

        if captions_response["items"]:
            # Obtener el ID del subtítulo
            caption_id = captions_response["items"][0]["id"]

            # Descargar la transcripción del subtítulo
            transcript_response = youtube.captions().download(
                id=caption_id,
                tfmt="vtt"
            ).execute()

            # Convertir la transcripción a texto plano
            transcript_text = convertir_transcripcion(transcript_response)

            return transcript_text, video_title
        else:
            return None, video_title
    except Exception as e:
        st.error("Error al obtener la transcripción del video: {}".format(e))
        return None, None

# Función para extraer el ID del video de una URL de YouTube
def obtener_video_id(url):
    if "youtube.com" in url:
        video_id = url.split("v=")[1]
        return video_id
    elif "youtu.be" in url:
        video_id = url.split("/")[-1]
        return video_id
    else:
        return None

# Función para convertir la transcripción en formato WebVTT a texto plano
def convertir_transcripcion(transcript_response):
    # Extraer el texto de la transcripción en formato WebVTT
    vtt_text = transcript_response.decode("utf-8")
    
    # Eliminar las etiquetas HTML y los timestamps
    lines = vtt_text.split("\n")
    text = ""
    for line in lines:
        if not line.strip().isdigit():
            text += line.strip() + " "
    
    return text

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
        transcripcion, titulo_video = obtener_transcripcion_youtube(url_video_youtube)
        if transcripcion:
            st.write("Transcripción del video '{}'".format(titulo_video))
            st.write(transcripcion)
        else:
            st.warning("No se encontraron subtítulos para el video.")
    else:
        st.warning("Por favor ingresa la URL del video de YouTube.")
