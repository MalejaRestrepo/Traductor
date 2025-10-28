import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from deep_translator import GoogleTranslator  # ✅ Reemplazo moderno y compatible

# CONFIGURACIÓN GENERAL
st.set_page_config(
    page_title="Traductor de Voz",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🎨 ESTILOS VISUALES — Paleta lavanda-celeste con contraste mejorado
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #e6e4ff 0%, #d9f4ff 100%);
        color: #1f244b;
        font-family: 'Poppins', sans-serif;
    }
    .block-container {
        background: #f9faff;
        border: 1px solid #c0d3ff;
        border-radius: 16px;
        padding: 2rem 2.2rem;
        box-shadow: 0 10px 24px rgba(31, 36, 75, 0.12);
    }
    h1, h2, h3 {
        color: #1f244b;
        text-align: center;
        font-weight: 700;
    }
    p, label, span, div { color: #1f244b; }
    section[data-testid="stSidebar"] {
        background: #eaf3ff;
        border-right: 2px solid #bcd6ff;
        color: #1e1c3a;
    }
    section[data-testid="stSidebar"] * { color: #1e1c3a !important; }
    div.stButton > button, .bk-root .bk-btn {
        background: linear-gradient(90deg, #b9a6ff 0%, #9be4ff 100%) !important;
        color: #1f244b !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #9fcaff !important;
        box-shadow: 0 6px 14px rgba(31, 36, 75, 0.18) !important;
        font-size: 16px !important;
        padding: 9px 24px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover, .bk-root .bk-btn:hover {
        background: linear-gradient(90deg, #a694ff 0%, #8fd8ff 100%) !important;
        transform: translateY(-1px);
    }
    audio {
        border-radius: 10px;
        border: 2px solid #8db8ff;
    }
    [data-testid="stHeader"] {
        background: linear-gradient(90deg, #7c9eff 0%, #b0c3ff 100%) !important;
        color: white !important;
        height: 3.5rem;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.25);
    }
    </style>
""", unsafe_allow_html=True)


# TÍTULOS PRINCIPALES
st.title("🎧 Traductor de Voz")
st.subheader("Escucho lo que dices, lo traduzco y te lo leo en voz alta.")

# IMAGEN PRINCIPAL
if os.path.exists("OIG7.jpg"):
    image = Image.open("OIG7.jpg")
    st.image(image, width=320)
else:
    st.info("Sube una imagen llamada **OIG7.jpg** para personalizar el diseño.")

# SIDEBAR
with st.sidebar:
    st.subheader("🪄 Instrucciones")
    st.write("Presiona el botón de **Escuchar**, habla lo que quieras traducir y luego selecciona los idiomas y acento para generar el audio traducido.")

# BOTÓN DE ESCUCHA
st.markdown("### 🎙️ Pulsa el botón y habla lo que quieras traducir")
stt_button = Button(label="🎤 Escuchar", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.markdown("### 📝 Texto detectado:")
        texto_original = result.get("GET_TEXT")
        st.success(texto_original)

        # Crear carpeta temporal si no existe
        try:
            os.mkdir("temp")
        except:
            pass

        # --- CONFIGURACIÓN DE TRADUCCIÓN ---
        st.markdown("### 🌐 Configuración de traducción")

        in_lang = st.selectbox(
            "Lenguaje de entrada",
            ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
        )
        lang_map = {
            "Inglés": "en", "Español": "es", "Bengali": "bn",
            "Coreano": "ko", "Mandarín": "zh-CN", "Japonés": "ja"
        }
        input_language = lang_map.get(in_lang, "en")

        out_lang = st.selectbox(
            "Lenguaje de salida",
            ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
        )
        output_language = lang_map.get(out_lang, "es")

        english_accent = st.selectbox(
            "Acento del audio",
            (
                "Defecto",
                "Español",
                "Reino Unido",
                "Estados Unidos",
                "Canadá",
                "Australia",
                "Irlanda",
                "Sudáfrica",
            ),
        )

        accent_map = {
            "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
            "Estados Unidos": "com", "Canadá": "ca", "Australia": "com.au",
            "Irlanda": "ie", "Sudáfrica": "co.za"
        }
        tld = accent_map.get(english_accent, "com")

        display_output_text = st.checkbox("Mostrar texto traducido")

        # ✅ Nueva función de traducción con deep-translator
        def text_to_speech(input_language, output_language, text, tld):
            translated_text = GoogleTranslator(source=input_language, target=output_language).translate(text)
            tts = gTTS(translated_text, lang=output_language, tld=tld, slow=False)
            file_name = text[:20] if text else "audio"
            path = f"temp/{file_name}.mp3"
            tts.save(path)
            return file_name, translated_text

        # --- BOTÓN DE CONVERSIÓN ---
        if st.button("✨ Convertir a Audio"):
            result_name, translated_text = text_to_speech(input_language, output_language, texto_original, tld)
            audio_file = open(f"temp/{result_name}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown("#### 🎧 Audio generado:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown("#### 💬 Texto traducido:")
                st.info(translated_text)

        # --- Limpieza de archivos viejos ---
        def remove_files(n):
            mp3_files = glob.glob("temp/*.mp3")
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

        remove_files(7)
