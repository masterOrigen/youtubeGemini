import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import os
import google.generativeai as genai

load_dotenv()  # Cargar todas las variables de entorno

# Configurar la API de Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt para la generación de resúmenes
prompt = """You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

# Obtener los detalles de la transcripción de los videos de YouTube
def extract_transcript_details(youtube_video_url, language="es"):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        st.warning(f"El video no tiene transcripción disponible: {e}")
        st.stop()

# Generar el contenido utilizando Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Procesar la pregunta y obtener una respuesta
def process_question(question, transcript_text):
    # Aquí puedes agregar la lógica para procesar la pregunta y obtener una respuesta.
    # Por ejemplo, podrías usar técnicas de procesamiento de lenguaje natural.
    # En este ejemplo de demostración, simplemente devolvemos una respuesta aleatoria.
    return "Esta es una respuesta de ejemplo a tu pregunta: " + question

st.title("Transcripción de Videos")
youtube_link = st.text_input("Ingresa link del video Youtube:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        st.markdown("## Transcripción:")
        st.write(transcript_text)

        user_question = st.text_area("Ecribe tu pregunta:")
        if st.button("Enviar pregunta"):
            st.write("Tu Pregunta:", user_question)
            answer = process_question(user_question, transcript_text)
            st.write("Respuesta:", answer)
