import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from PIL import Image
import requests

#Je t'aime plus que les mots,
#Plus que les sentiments,
#Plus que la vie elle-même

st.set_page_config(
    page_title="Google AI Chat",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)
# Path: Main.py
#Author: Sergio Demis Lopez Martinez
#------------------------------------------------------------
#HEADER
st.markdown('''
GEMINI AI  <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
 BY GPT MEDIOS''', unsafe_allow_html=True)

#------------------------------------------------------------
#LANGUAGE
# Columna de idioma
lang = 'Español'
st.divider()

#------------------------------------------------------------
#FUNCTIONS


def append_message(message: dict) -> None:
    """
    The function appends a message to a chat session.

    :param message: The `message` parameter is a dictionary that represents a chat message. It typically contains
    information such as the user who sent the message and the content of the message
    :type message: dict
    :return: The function is not returning anything.
    """
    st.session_state.chat_session.append({'user': message})
    return

@st.cache_resource
def load_model() -> genai.GenerativeModel:
    """
    The function `load_model()` returns an instance of the `genai.GenerativeModel` class initialized with the model name
    'gemini-pro'.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro')
    return model

@st.cache_resource
def load_modelvision() -> genai.GenerativeModel:
    """
    The function `load_modelvision` loads a generative model for vision tasks using the `gemini-pro-vision` model.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro-vision')
    return model



#------------------------------------------------------------
#CONFIGURATION
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = load_model()

vision = load_modelvision()

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

#st.session_state.chat_session

#------------------------------------------------------------
#CHAT

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state or lang != st.session_state.lang:
    st.session_state.lang = lang
    welcome  = model.generate_content(f'''
    Da un saludo de bienvenida al usuario y sugiere que puede hacer
    (Puedes describir imágenes, responder preguntas, leer archivos texto, leer tablas,generar gráficos con graphviz, etc)
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
                graphs = extract_graphviz_info(message['user']['parts'])
                if len(graphs) > 0:
                    for graph in graphs:
                        st.graphviz_chart(graph,use_container_width=False)
                        if lang == 'Español':
                          view = "Ver texto"
                        else:
                          view = "View text"
                        with st.expander(view):
                          st.code(graph, language='dot')
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'][0])
                if len(message['user']['parts']) > 1:
                    st.image(message['user']['parts'][1], width=200)
        count += 1



#st.session_state.chat.history

cols=st.columns(4)

with cols[0]:
    if lang == 'Español':
      image_atachment = st.toggle("Adjuntar imagen", value=False, help="Activa este modo para adjuntar una imagen y que el chatbot pueda leerla")
    else:
      image_atachment = st.toggle("Attach image", value=False, help="Activate this mode to attach an image and let the chatbot read it")

with cols[1]:
    if lang == 'Español':
      txt_atachment = st.toggle("Adjuntar archivo de texto", value=False, help="Activa este modo para adjuntar un archivo de texto y que el chatbot pueda leerlo")
    else:
      txt_atachment = st.toggle("Attach text file", value=False, help="Activate this mode to attach a text file and let the chatbot read it")
with cols[2]:
    if lang == 'Español':
      csv_excel_atachment = st.toggle("Adjuntar CSV o Excel", value=False, help="Activa este modo para adjuntar un archivo CSV o Excel y que el chatbot pueda leerlo")
    else:
      csv_excel_atachment = st.toggle("Attach CSV or Excel", value=False, help="Activate this mode to attach a CSV or Excel file and let the chatbot read it")

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

    if graphviz_mode:
        if lang == 'Español':
          txt += '   Genera un grafo con graphviz en .dot \n'
        else:
          txt += '   Generate a graph with graphviz in .dot \n'

    if len(txt) > 5000:
        txt = txt[:5000] + '...'
    if image or url != '':
        if url != '':
            img = Image.open(requests.get(url, stream=True).raw)
        else:
            img = Image.open(image)
        prmt  = {'role': 'user', 'parts':[prompt+txt, img]}
    else:
        prmt  = {'role': 'user', 'parts':[prompt+txt]}

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



#st.session_state.chat_session
