import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import os
import google.generativeai as genai
import spacy

load_dotenv()  # Cargar todas las variables de entorno

# Configurar la API de Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Cargar el modelo de procesamiento de lenguaje natural (en este caso, spaCy en español)
nlp = spacy.load("es_core_news_sm")

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

# Procesar la pregunta y obtener una respuesta basada en el contenido del video
def process_question(input_text, transcript_text):
    # Analizar la pregunta utilizando spaCy
    doc = nlp(input_text)
    
    # Extraer entidades nombradas relevantes de la pregunta
    relevant_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "WORK_OF_ART"]]
    
    # Realizar búsqueda de las entidades en la transcripción
    relevant_sentences = []
    for sentence in transcript_text.split("."):
        for entity in relevant_entities:
            if entity.lower() in sentence.lower():
                relevant_sentences.append(sentence.strip())
                break
    
    # Devolver la respuesta como un resumen de las oraciones relevantes
    if relevant_sentences:
        return ". ".join(relevant_sentences)
    else:
        return "Lo siento, no pude encontrar información relevante en el video para responder a tu pregunta."

st.title("Transcripción de Videos")
youtube_link = st.text_input("Ingresa link del video Youtube:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Procesar"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        st.markdown("## Transcripción:")
        st.write(transcript_text)

        user_question = st.text_area("Escribe tu pregunta:")
        if st.button("Enviar pregunta"):
            st.write("Tu Pregunta:", user_question)
            answer = process_question(user_question, transcript_text)
            st.write("Respuesta:", answer)
