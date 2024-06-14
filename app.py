import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from PIL import Image
import requests
import PyPDF2

# HEADER
st.markdown('''
Desarrollado por Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
, Streamlit y Python''', unsafe_allow_html=True)
st.caption("Por Sergio Demis Lopez Martinez")

# CONFIGURACIÓN
st.set_page_config(
    page_title="Chat de Google AI",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)

# FUNCIÓN PARA EXTRAER INFORMACIÓN DE GRAPHVIZ
def extract_graphviz_info(text: str) -> list[str]:
    graphviz_info = text.split('```')
    return [graph for graph in graphviz_info if ('graph' in graph or 'digraph' in graph) and ('{' in graph and '}' in graph)]

# FUNCIÓN PARA AGREGAR UN MENSAJE A LA SESIÓN DE CHAT
def append_message(message: dict) -> None:
    st.session_state.chat_session.append({'user': message})
    return

# FUNCIÓN PARA CARGAR EL MODELO DE GOOGLE AI
@st.cache_resource
def load_model() -> genai.GenerativeModel:
    model = genai.GenerativeModel('gemini-pro')
    return model

# FUNCIÓN PARA CARGAR EL MODELO DE VISIÓN
@st.cache_resource
def load_modelvision() -> genai.GenerativeModel:
    model = genai.GenerativeModel('gemini-pro-vision')
    return model

# CONFIGURACIÓN INICIAL
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = load_model()
vision = load_modelvision()

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

# MENSAJE DE BIENVENIDA
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state:
    welcome = model.generate_content('¡Bienvenido a este chat! ¿En qué puedo ayudarte?')
    welcome.resolve()
    st.session_state.welcome = welcome

    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)
else:
    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)

# HISTORIAL DEL CHAT
if len(st.session_state.chat_session) > 0:
    for message in st.session_state.chat_session:
        if message['user']['role'] == 'model':
            with st.chat_message('ai'):
                st.write(message['user']['parts'])
                graphs = extract_graphviz_info(message['user']['parts'])
                if len(graphs) > 0:
                    for graph in graphs:
                        st.graphviz_chart(graph, use_container_width=False)
                        with st.expander("Ver texto"):
                            st.code(graph, language='dot')
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'])

# MENÚ DE OPCIONES
cols = st.columns(4)

with cols[0]:
    image_atachment = st.toggle("Adjuntar imagen", value=False, help="Activa este modo para adjuntar una imagen y que el chatbot pueda leerla")

with cols[1]:
    txt_atachment = st.toggle("Adjuntar archivo PDF", value=False, help="Activa este modo para adjuntar un archivo PDF y que el chatbot pueda leerlo")

with cols[2]:
    csv_excel_atachment = st.toggle("Adjuntar CSV o Excel", value=False, help="Activa este modo para adjuntar un archivo CSV o Excel y que el chatbot pueda leerlo")

with cols[3]:
    graphviz_mode = st.toggle("Modo graphviz", value=False, help="Activa este modo para generar un grafo con graphviz en .dot a partir de tu mensaje")

# MANEJO DE ADJUNTOS
if image_atachment:
    image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
    url = st.text_input("O pega la URL de tu imagen")
else:
    image = None
    url = ''

if txt_atachment:
    pdf_file = st.file_uploader("Sube tu archivo PDF", type=['pdf'])
else:
    pdf_file = None

if csv_excel_atachment:
    csvexcelattachment = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])
else:
    csvexcelattachment = None

# ENTRADA DE TEXTO
prompt = st.chat_input("Escribe tu mensaje")

if prompt:
    txt = ''
    if pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        num_pages = pdf_reader.numPages
        txt += f"El archivo PDF contiene {num_pages} páginas."
        page_num = st.number_input("Ingresa el número de página que deseas extraer:", min_value=1, max_value=num_pages)
        page = pdf_reader.getPage(page_num - 1)
        page_text = page.extractText()
        txt += page_text

    if csvexcelattachment:
        try:
            df = pd.read_csv(csvexcelattachment)
        except:
            df = pd.read_excel(csvexcelattachment)
        txt += '   Dataframe: \n' + str(df)

    if graphviz_mode:
        txt += '   Genera un grafo con graphviz en .dot \n'

    if len(txt) > 5000:
        txt = txt[:5000] + '...'
    if image or url != '':
        if url != '':
            img = Image.open(requests.get(url, stream=True).raw)
        else:
            img = Image.open(image)
        prmt = {'role': 'user', 'parts': [prompt + txt, img]}
    else:
        prmt = {'role': 'user', 'parts': [prompt + txt]}

    append_message(prmt)

    with st.spinner('Espera un momento, estoy pensando...'):
        if len(prmt['parts']) > 1:
            response = vision.generate_content(prmt['parts'], stream=True, safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
            ])
            response.resolve()
        else:
            response = st.session_state.chat.send_message(prmt['parts'][0])

        try:
            append_message({'role': 'model', 'parts': response.text})
        except Exception as e:
            append_message({'role': 'model', 'parts': f'{type(e).__name__}: {e}'})

        st.rerun()
