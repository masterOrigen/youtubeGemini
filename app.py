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
    initial_sidebar_state="expanded",
)

# CSS personalizado con texto negro y toggles personalizados
st.markdown("""
    <style>
    body {
        color: black;
        background-color: white;
    }
    .stApp {
        background-color: white;
    }
    .stTextInput > div > div > input {
        color: black;
        background-color: white;
    }
    .stTextArea textarea {
        color: black;
        background-color: white;
    }
    .stSelectbox > div > div > select {
        color: black;
    }
    .stMarkdown {
        color: black;
    }
    /* Estilo para nuestro toggle personalizado */
    .custom-toggle {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .custom-toggle .toggle-label {
        margin-right: 10px;
    }
    .custom-toggle .stCheckbox {
        height: 26px;
    }
    .custom-toggle .stCheckbox > label {
        display: flex;
        align-items: center;
    }
    .custom-toggle .stCheckbox > label > span {
        background-color: #f0f0f0;
        border: 1px solid black;
        border-radius: 20px;
        width: 50px;
        height: 26px;
        position: relative;
        transition: all 0.3s ease;
    }
    .custom-toggle .stCheckbox > label > span::before {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        background-color: black;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        transition: all 0.3s ease;
    }
    .custom-toggle .stCheckbox > label > input:checked + span {
        background-color: black;
    }
    .custom-toggle .stCheckbox > label > input:checked + span::before {
        background-color: white;
        transform: translateX(24px);
    }
    .custom-toggle .stCheckbox > label > div {
        display: none;
    }
    /* Estilo para el nombre de la imagen y el texto de la URL */
    .uploadedFileName {
        color: black !important;
    }
    .stFileUploader > div > div > div {
        color: black !important;
    }
    /* Estilo para el área de texto */
    .stTextInput > div {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para crear un toggle personalizado
def custom_toggle(label, key):
    with st.container():
        st.markdown(f'<div class="custom-toggle"><span class="toggle-label">{label}</span>', unsafe_allow_html=True)
        value = st.checkbox("", key=key, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    return value

# HEADER
st.markdown('''
GEMINI AI  <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
 BY GPT MEDIOS''', unsafe_allow_html=True)

# LANGUAGE
lang = 'Español'
st.divider()

# FUNCTIONS
def append_message(message: dict) -> None:
    st.session_state.chat_session.append({'user': message})
    return

@st.cache_resource
def load_model() -> genai.GenerativeModel:
    model = genai.GenerativeModel('gemini-pro')
    return model

@st.cache_resource
def load_modelvision() -> genai.GenerativeModel:
    model = genai.GenerativeModel('gemini-pro-vision')
    return model

# CONFIGURATION
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = load_model()
vision = load_modelvision()

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

# CHAT
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state or lang != st.session_state.lang:
    st.session_state.lang = lang
    welcome = model.generate_content(f'''
    Da un saludo de bienvenida al usuario y sugiere que puede hacer
    (Puedes describir imágenes, responder preguntas, leer archivos texto, leer tablas, etc)
    eres un chatbot en una aplicación de chat creada en streamlit y python. generate the answer in {lang}''')
    welcome.resolve()
    st.session_state.welcome = welcome

    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)
else:
    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)

if len(st.session_state.chat_session) > 0:
    count = 0
    for message in st.session_state.chat_session:
        if message['user']['role'] == 'model':
            with st.chat_message('ai'):
                st.write(message['user']['parts'])
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'][0])
                if len(message['user']['parts']) > 1:
                    st.image(message['user']['parts'][1], width=200)
        count += 1

cols = st.columns(3)

with cols[0]:
    if lang == 'Español':
        image_atachment = custom_toggle("Adjuntar imagen", "image_toggle")
    else:
        image_atachment = custom_toggle("Attach image", "image_toggle")

with cols[1]:
    if lang == 'Español':
        txt_atachment = custom_toggle("Adjuntar archivo de texto", "txt_toggle")
    else:
        txt_atachment = custom_toggle("Attach text file", "txt_toggle")

with cols[2]:
    if lang == 'Español':
        csv_excel_atachment = custom_toggle("Adjuntar CSV o Excel", "csv_excel_toggle")
    else:
        csv_excel_atachment = custom_toggle("Attach CSV or Excel", "csv_excel_toggle")

if image_atachment:
    if lang == 'Español':
      image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
      url = st.text_input("O pega la url de tu imagen")
    else:
      image = st.file_uploader("Upload your image", type=['png', 'jpg', 'jpeg'])
      url = st.text_input("Or paste your image url")
else:
    image = None
    url = ''

if txt_atachment:
    if lang == 'Español':
      txtattachment = st.file_uploader("Sube tu archivo de texto", type=['txt'])
    else:
      txtattachment = st.file_uploader("Upload your text file", type=['txt'])
else:
    txtattachment = None

if csv_excel_atachment:
    if lang == 'Español':
      csvexcelattachment = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])
    else:
      csvexcelattachment = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])
else:
    csvexcelattachment = None

if lang == 'Español':
  prompt = st.chat_input("Escribe tu mensaje")
else:
  prompt = st.chat_input("Write your message")

if prompt:
    txt = ''
    if txtattachment:
        txt = txtattachment.getvalue().decode("utf-8")
        if lang == 'Español':
          txt = '   Archivo de texto: \n' + txt
        else:
          txt = '   Text file: \n' + txt

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
        prmt = {'role': 'user', 'parts':[prompt+txt, img]}
    else:
        prmt = {'role': 'user', 'parts':[prompt+txt]}

    append_message(prmt)

    if lang == 'Español':
      spinertxt = 'Espera un momento, estoy pensando...'
    else:
      spinertxt = 'Wait a moment, I am thinking...'
    with st.spinner(spinertxt):
        if len(prmt['parts']) > 1:
            response = vision.generate_content(prmt['parts'],stream=True,safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
    ]
)
            response.resolve()
        else:
            response = st.session_state.chat.send_message(prmt['parts'][0])

        try:
          append_message({'role': 'model', 'parts':response.text})
        except Exception as e:
          append_message({'role': 'model', 'parts':f'{type(e).__name__}: {e}'})

        st.rerun()
