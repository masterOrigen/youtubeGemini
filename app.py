import streamlit as st
import pandas as pd
from PIL import Image
import requests
import genai

# Configuración de la página
st.set_page_config(
    page_title="Google AI Chat",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide"
)

# Carga del modelo generativo para texto y visión
@st.cache(allow_output_mutation=True)
def load_model(model_name):
    return genai.GenerativeModel(model_name)

model_text = load_model('gemini-pro')
model_vision = load_model('gemini-pro-vision')

# Inicialización de la sesión de chat
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

# Función para añadir mensajes a la sesión de chat
def append_message(message):
    st.session_state.chat_session.append(message)

# Función para extraer bloques de Graphviz de un texto
def extract_graphviz_info(text):
    graphviz_info = text.split('```')
    return [graph for graph in graphviz_info if ('graph' in graph or 'digraph' in graph) and ('{' in graph and '}' in graph)]

# Saludo inicial al usuario
if 'welcome_message' not in st.session_state:
    st.session_state.welcome_message = model_text.generate_content('''
    Da un saludo de bienvenida al usuario y sugiere qué puede hacer.
    Eres un chatbot en una aplicación de chat creada en Streamlit y Python.
    ''')
    st.session_state.welcome_message.resolve()

    st.write(st.session_state.welcome_message.text)

# Columnas para opciones de adjuntos y modo Graphviz
cols = st.columns(4)
lang = 'Español'  # Puedes cambiar el idioma según el contexto de la aplicación

with cols[0]:
    image_attachment = st.toggle("Adjuntar imagen", value=False, help="Activa este modo para adjuntar una imagen y que el chatbot pueda leerla")

with cols[1]:
    text_attachment = st.toggle("Adjuntar archivo de texto", value=False, help="Activa este modo para adjuntar un archivo de texto y que el chatbot pueda leerlo")

with cols[2]:
    csv_excel_attachment = st.toggle("Adjuntar CSV o Excel", value=False, help="Activa este modo para adjuntar un archivo CSV o Excel y que el chatbot pueda leerlo")

with cols[3]:
    graphviz_mode = st.toggle("Modo Graphviz", value=False, help="Activa este modo para generar un grafo con Graphviz en formato .dot a partir de tu mensaje")

# Manejo de adjuntos y entrada de texto del usuario
if text_attachment:
    uploaded_file = st.file_uploader("Sube tu archivo de texto", type=['txt'])
else:
    uploaded_file = None

if csv_excel_attachment:
    uploaded_data = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])
else:
    uploaded_data = None

prompt = st.text_area("Escribe tu mensaje")

# Procesamiento del mensaje del usuario
if st.button("Enviar"):
    if prompt:
        user_message = {'role': 'user', 'parts': [prompt]}
        if uploaded_file:
            text_content = uploaded_file.getvalue().decode("utf-8")
            user_message['parts'].append(f'Archivo de texto:\n{text_content}')

        if uploaded_data:
            try:
                df = pd.read_csv(uploaded_data)
            except Exception as e:
                df = pd.read_excel(uploaded_data)
            user_message['parts'].append(f'Dataframe:\n{df}')

        append_message(user_message)

        if graphviz_mode:
            user_message['parts'].append('Generar un grafo con Graphviz en formato .dot')

        # Respuesta del modelo generativo
        with st.spinner("Espera un momento, estoy pensando..."):
            if image_attachment:
                image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
                if image:
                    img = Image.open(image)
                    user_message['parts'].append(img)

            # Uso del modelo de visión o texto según el contexto
            if any(isinstance(part, Image.Image) for part in user_message['parts']):
                response = model_vision.generate_content(user_message['parts'])
            else:
                response = model_text.send_message(user_message['parts'][0])

            response.resolve()

            append_message({'role': 'model', 'parts': response.text})

    st.experimental_rerun()

# Mostrar el historial del chat
if st.session_state.chat_session:
    for message in st.session_state.chat_session:
        if message['role'] == 'user':
            st.write("Usuario:", message['parts'][0])
            if len(message['parts']) > 1 and isinstance(message['parts'][1], Image.Image):
                st.image(message['parts'][1], caption="Imagen adjunta", use_column_width=True)
        elif message['role'] == 'model':
            st.write("AI:", message['parts'])

# Guardar el estado de la sesión
st.session_state.sync()
