import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from PIL import Image
import requests

# Configuración de la página
st.set_page_config(
    page_title="Google AI Chat",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)

# Columna de idioma
lang = 'Español'

# Funciones
def append_message(message):
    st.session_state.chat_session.append({'user': message})

@st.cache_resource
def load_model():
    model = genai.GenerativeModel('gemini-pro')
    return model

@st.cache_resource
def load_modelvision():
    model = genai.GenerativeModel('gemini-pro-vision')
    return model

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = load_model()
vision = load_modelvision()

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

# Chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state or lang != st.session_state.lang:
    st.session_state.lang = lang
    welcome = model.generate_content(f'''
    Da un saludo de bienvenida al usuario y sugiere que puede hacer
    (Puedes describir imágenes, responder preguntas, leer archivos texto, leer tablas, etc.)
    Eres un chatbot en una aplicación de chat creada en Streamlit y Python. Generar la respuesta en {lang}''')
    welcome.resolve()
    st.session_state.welcome = welcome

    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)
else:
    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)

if len(st.session_state.chat_session) > 0:
    for message in st.session_state.chat_session:
        if message['user']['role'] == 'model':
            with st.chat_message('ai'):
                st.write(message['user']['parts'])
                # No hay modo Graphviz en esta versión
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'][0])
                if len(message['user']['parts']) > 1:
                    st.image(message['user']['parts'][1], width=200)

# Opciones de adjuntos
st.write("Opciones de adjuntos:")
cols = st.columns(3)

with cols[0]:
    image_atachment = st.checkbox("Adjuntar imagen", value=False, help="Activa este modo para adjuntar una imagen y que el chatbot pueda leerla")
with cols[1]:
    txt_atachment = st.checkbox("Adjuntar archivo de texto", value=False, help="Activa este modo para adjuntar un archivo de texto y que el chatbot pueda leerlo")
with cols[2]:
    csv_excel_atachment = st.checkbox("Adjuntar CSV o Excel", value=False, help="Activa este modo para adjuntar un archivo CSV o Excel y que el chatbot pueda leerlo")

# Adjunto de imagen
if image_atachment:
    if lang == 'Español':
        image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
        url = st.text_input("O pega la URL de tu imagen")
else:
    image = None
    url = ''

# Adjunto de archivo de texto
if txt_atachment:
    if lang == 'Español':
        txtattachment = st.file_uploader("Sube tu archivo de texto", type=['txt'])
else:
    txtattachment = None

# Adjunto de archivo CSV o Excel
if csv_excel_atachment:
    if lang == 'Español':
        csvexcelattachment = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])
else:
    csvexcelattachment = None

# Entrada de mensaje
if lang == 'Español':
    prompt = st.chat_input("Escribe tu mensaje")

if prompt:
    txt = ''
    if txtattachment:
        txt = txtattachment.getvalue().decode("utf-8")
        if lang == 'Español':
            txt = '   Archivo de texto: \n' + txt

    if csvexcelattachment:
        try:
            df = pd.read_csv(csvexcelattachment)
        except:
            df = pd.read_excel(csvexcelattachment)
        txt += '   Dataframe: \n' + str(df)

    if len(txt) > 5000:
        txt = txt[:5000] + '...'
    
    if image or url != '':
        if url != '':
            img = Image.open(requests.get(url, stream=True).raw)
        else:
            img = Image.open(image)
        prmt = {'role': 'user', 'parts': [prompt+txt, img]}
    else:
        prmt = {'role': 'user', 'parts': [prompt+txt]}

    append_message(prmt)

    if lang == 'Español':
        spinertxt = 'Espera un momento, estoy pensando...'
    with st.spinner(spinertxt):
        if len(prmt['parts']) > 1:
            response = vision.generate_content(prmt['parts'], stream=True, safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
            ])
            response.resolve()
        else:
            response = st.session_state.chat.send_message(prmt['parts'][0])

        try:
            append_message({'role': 'model', 'parts': response.text})
        except Exception as e:
            append_message({'role': 'model', 'parts': f'{type(e).__name__}: {e}'})

        st.rerun()
