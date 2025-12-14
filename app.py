import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Traductor Recetas IA",
    page_icon="💊",
    layout="centered"
)

# --- SEGURIDAD: CONEXIÓN A LA API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        # Si no hay secreto configurado, mostramos aviso amigable
        st.warning("⚠️ Configura tu API Key en los 'Secrets' de Streamlit para empezar.")
        st.stop()
except Exception as e:
    st.error(f"Error de configuración: {e}")

# --- FUNCIONES DEL CEREBRO ---
def analizar_receta(image):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = """
        Eres un farmacéutico experto. Transcribe esta receta médica.
        INSTRUCCIONES:
        1. Extrae: Medicamento, Dosis y Frecuencia.
        2. Corrige abreviaturas.
        3. Formato: Lista clara con emojis.
        4. Añade una nota de seguridad al final.
        """
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error al analizar: {e}"

def crear_pdf(texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "TRADUCCION RECETA MEDICA (IA)", ln=True, align='C')
    pdf.ln(10)
    
    # Contenido
    pdf.set_font("Arial", size=12)
    texto_limpio = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ VISUAL ---
st.title("💊 Traductor de Recetas Médicas")
st.write("Sube la foto y la IA descifrará la letra del médico.")

archivo = st.file_uploader("Sube tu receta aquí", type=["jpg", "png", "jpeg"])

if archivo:
    imagen = Image.open(archivo)
    st.image(imagen, caption='Receta original', use_column_width=True)
    
    if st.button("🔍 Traducir ahora", type="primary"):
        with st.spinner('Analizando caligrafía...'):
            texto_resultado = analizar_receta(imagen)
            
            st.success("¡Análisis completado!")
            st.markdown("### Resultado:")
            st.markdown(texto_resultado)
            
            # Botón de descarga PDF
            pdf_bytes = crear_pdf(texto_resultado)
            st.download_button(
                label="📄 Descargar PDF Oficial",
                data=pdf_bytes,
                file_name="Receta_Traducida.pdf",
                mime="application/pdf"
            )