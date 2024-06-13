import os
import streamlit as st
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key de Gemini desde las variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Funciones para obtener la transcripción de un video de YouTube y hacer preguntas sobre la transcripción
def get_transcript_from_youtube_video(youtube_url):
    gemini_api_url = "https://api.gemini.com/transcribe-youtube-video"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {"youtube_url": youtube_url}
    response = requests.post(gemini_api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["transcript"]
    else:
        return None

def ask_question_about_transcript(question, transcript):
    gemini_api_url = "https://api.gemini.com/ask-question"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {"question": question, "transcript": transcript}
    response = requests.post(gemini_api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["answer"]
    else:
        return None

# Configuración de la página
st.set_page_config(page_title="Gemini AI - YouTube Transcript", layout="wide")

# Título de la aplicación
st.title("Gemini AI - YouTube Transcript")

# Input para ingresar la URL del video de YouTube
youtube_url = st.text_input("Ingresa la URL del video de YouTube:")

# Botón para obtener la transcripción del video
if st.button("Obtener Transcripción"):
    if youtube_url:
        transcript = get_transcript_from_youtube_video(youtube_url)
        if transcript:
            st.header("Transcripción del Video:")
            st.write(transcript)
        else:
            st.error("Ocurrió un error al obtener la transcripción del video.")
    else:
        st.warning("Por favor ingresa la URL del video de YouTube.")

# Input para realizar preguntas sobre la transcripción
question = st.text_input("Haz una pregunta sobre la transcripción del video:")

# Botón para obtener la respuesta a la pregunta
if st.button("Obtener Respuesta"):
    if question:
        if transcript:
            answer = ask_question_about_transcript(question, transcript)
            if answer:
                st.header("Respuesta:")
                st.write(answer)
            else:
                st.error("Ocurrió un error al obtener la respuesta.")
        else:
            st.warning("Primero obtén la transcripción del video antes de hacer una pregunta.")
    else:
        st.warning("Por favor ingresa una pregunta.")
