import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE PÁGINA (MODIFICADO: AHORA ES WIDE) ---
st.set_page_config(
    page_title="Traductor Recetas IA",
    page_icon="💊",
    layout="wide", # Cambiado a wide para que quepan las columnas
    initial_sidebar_state="expanded"
)

# --- 2. CARGA DE ESTILOS (NUEVO) ---
def cargar_estilo(nombre_archivo):
    try:
        with open(nombre_archivo) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Si no encuentra el estilo, sigue funcionando sin él

# Cargamos tu archivo style.css
cargar_estilo("style.css")

# --- SEGURIDAD: CONEXIÓN A LA API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.warning("⚠️ Configura tu API Key en los 'Secrets' de Streamlit para empezar.")
        st.stop()
except Exception as e:
    st.error(f"Error de configuración: {e}")

# --- FUNCIONES DEL CEREBRO ---
def analizar_receta(image):
    try:
        # Usamos 2.5-flash para asegurar estabilidad (el 2.5 a veces da error de cuota)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # --- TU PROMPT ORIGINAL INTACTO ---
        prompt = """
        Transcribe esta receta médica.
        primero todo los datos del doctor y luego todos del paciente
        Extrae: Medicamento, Dosis, Frecuencia e Instrucciones.
        Si hay abreviaturas, complétalas y si hay observaciones se lo mas exacto en lo escrito. Responde en español claro.
        """
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error al analizar: {e}"

def crear_pdf(texto):
    # --- TU FUNCIÓN PDF ORIGINAL INTACTA ---
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

# --- INTERFAZ VISUAL (RE-ESTRUCTURADA) ---

# Título principal
st.title("💊 Traductor de Recetas Médicas")

# --- BARRA LATERAL (NUEVO LUGAR PARA SUBIR ARCHIVO) ---
with st.sidebar:
    st.header("📂 Panel de Control")
    st.write("Sube la foto y la IA descifrará la letra del médico.")
    archivo = st.file_uploader("Sube tu receta aquí", type=["jpg", "png", "jpeg"])
    st.info("💡 Tip: Asegúrate de que la foto tenga buena luz.")

# --- ZONA PRINCIPAL CON COLUMNAS ---
if archivo:
    imagen = Image.open(archivo)
    
    # DIVIDIMOS LA PANTALLA EN 2
    col1, col2 = st.columns([1, 1], gap="large")
    
    # COLUMNA IZQUIERDA: IMAGEN
    with col1:
        st.subheader("📸 Receta Original")
        st.image(imagen, caption='Tu imagen cargada', use_column_width=True)
    
    # COLUMNA DERECHA: RESULTADOS
    with col2:
        st.subheader("📝 Traducción")
        
        # Botón grande
        if st.button("🔍 Traducir ahora", type="primary"):
            with st.spinner('Analizando caligrafía...'):
                texto_resultado = analizar_receta(imagen)
                
                st.success("¡Análisis completado!")
                st.markdown("### Resultado:")
                st.markdown(texto_resultado)
                
                # Botón de descarga PDF (TU LÓGICA ORIGINAL)
                pdf_bytes = crear_pdf(texto_resultado)
                st.download_button(
                    label="📄 Descargar PDF Oficial",
                    data=pdf_bytes,
                    file_name="Receta_Traducida.pdf",
                    mime="application/pdf"
                )
else:
    # Mensaje de bienvenida si no hay foto
    st.info("👈 Por favor, sube una imagen en el menú de la izquierda para comenzar.")