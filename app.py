import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# Título y descripción
st.title("📝 Analizador de Texto con TextBlob")
st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:
- Análisis de sentimiento y subjetividad
- Extracción de palabras clave
- Análisis de frecuencia de palabras
""")

# Barra lateral
st.sidebar.title("Opciones")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# Función para contar palabras sin depender de NLTK
def contar_palabras(texto):
    stop_words = set([
        # Lista combinada español/inglés...
        "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
        "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella",
        "ellas", "ellos", "en", "entre", "era", "eras", "es", "esa", "esas", "ese",
        "eso", "esos", "esta", "estas", "este", "esto", "estos", "ha", "había", "han",
        "has", "hasta", "he", "la", "las", "le", "les", "lo", "los", "me", "mi", "mía",
        "mías", "mío", "míos", "mis", "mucho", "muchos", "muy", "nada", "ni", "no", "nos",
        "nosotras", "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "o", "os", 
        "otra", "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "que", 
        "quien", "quienes", "qué", "se", "sea", "sean", "según", "si", "sido", "sin", 
        "sobre", "sois", "somos", "son", "soy", "su", "sus", "suya", "suyas", "suyo", 
        "suyos", "también", "tanto", "te", "tenéis", "tenemos", "tener", "tengo", "ti", 
        "tiene", "tienen", "todo", "todos", "tu", "tus", "tuya", "tuyas", "tuyo", "tuyos", 
        "tú", "un", "una", "uno", "unos", "vosotras", "vosotros", "vuestra", "vuestras", 
        "vuestro", "vuestros", "y", "ya", "yo",
        # Inglés
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", 
        "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", 
        "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
        "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", 
        "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
        "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", 
        "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", 
        "the", "their", "theirs", "them", "themselves", "then", "there", "there's", 
        "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", 
        "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
        "we'd", "we'll", "we're", "we've", "were",         "weren't", "what", "what's", "when", 
        "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", 
        "why's", "with", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    ])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

# Traductor
translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity

    frases_originales = [f.strip() for f in re.split(r'[.!?]+', texto) if f.strip()]
    frases_traducidas = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    frases_combinadas = []
    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases_combinadas.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })

    contador_palabras, palabras = contar_palabras(texto_ingles)

    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto,
        "texto_traducido": texto_ingles
    }

# Cargar archivo Lottie
def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        st.error(f"No se pudo cargar la animación: {filepath}")
        return None

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)

        if resultados["sentimiento"] > 0.05:
            st.success(f"📈 Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"📉 Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"📊 Neutral ({resultados['sentimiento']:.2f})")

        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")

    with col2:
        st.subheader("Palabras más frecuentes")
        if resultados["contador_palabras"]:
            top_words = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(top_words)

    st.subheader("Texto Traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Texto Original (Español):**")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])

    st.subheader("Frases detectadas")
    for i, frase_dict in enumerate(resultados["frases"][:10], 1):
        frase_original = frase_dict["original"]
        frase_traducida = frase_dict["traducido"]
        blob_frase = TextBlob(frase_traducida)
        polarity = blob_frase.sentiment.polarity

        st.markdown(f"**Frase {i}:** {frase_original}")
        if polarity >= 0.5:
            st.success("😊 Sentimiento Positivo")
            anim = load_lottiefile("positivo.json")
            if anim: st_lottie(anim, height=200)
        elif polarity <= -0.5:
            st.error("😔 Sentimiento Negativo")
            anim = load_lottiefile("negativo.json")
            if anim: st_lottie(anim, height=200)
        else:
            st.info("😐 Sentimiento Neutral")
            anim = load_lottiefile("neutral.json")
            if anim: st_lottie(anim, height=200)

# Entrada de texto o archivo
if modo == "Texto directo":
    texto_input = st.text_area("Escribe o pega el texto aquí:", height=200)
elif modo == "Archivo de texto":
    archivo = st.file_uploader("Sube un archivo .txt", type=["txt"])
    texto_input = archivo.read().decode("utf-8") if archivo else ""

# Botón de análisis
if st.button("🔍 Analizar texto") and texto_input.strip():
    resultados = procesar_texto(texto_input)
    crear_visualizaciones(resultados)
