import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Traductor Recetas IA",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CARGA DE ESTILOS ---
def cargar_estilo(nombre_archivo):
    try:
        with open(nombre_archivo) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

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
        model = genai.GenerativeModel('gemini-2.5-flash')
        
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

# --- INTERFAZ VISUAL REDISEÑADA ---

st.markdown("<h1>💊 Traductor de Recetas Médicas con IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #636e72; margin-top: -20px; margin-bottom: 40px;'>Convierte la caligrafía médica en texto claro al instante</p>", unsafe_allow_html=True)

# --- BARRA LATERAL MEJORADA ---
with st.sidebar:
    st.markdown("### 📂 Panel de Control")
    st.markdown("---")
    st.write("🎯 Sube la foto de tu receta y deja que la IA descifre la letra del médico.")
    
    archivo = st.file_uploader("📤 Arrastra tu receta aquí", type=["jpg", "png", "jpeg"])
    
    st.info("💡 **Tip Profesional:** Asegúrate de que la foto tenga buena iluminación y enfoque nítido para mejores resultados.")
    
    st.markdown("---")
    st.markdown("### ✨ Características")
    st.markdown("✅ Análisis con IA avanzada")
    st.markdown("✅ Exportación a PDF")
    st.markdown("✅ Resultados instantáneos")

# --- ZONA PRINCIPAL CON COLUMNAS ---
if archivo:
    imagen = Image.open(archivo)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    # COLUMNA IZQUIERDA: IMAGEN
    with col1:
        st.subheader("📸 Receta Original")
        st.image(imagen, caption='📋 Tu imagen cargada', use_column_width=True)
    
    # COLUMNA DERECHA: RESULTADOS
    with col2:
        st.subheader("🔮 Traducción Inteligente")
        
        if st.button("🚀 Traducir Ahora", type="primary"):
            with st.spinner('🧠 Analizando caligrafía médica...'):
                texto_resultado = analizar_receta(imagen)
                
                st.success("✅ ¡Análisis completado con éxito!")
                st.markdown("### 📝 Resultado:")
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                            padding: 25px; 
                            border-radius: 15px; 
                            border-left: 5px solid #667eea;
                            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                            margin: 20px 0;'>
                    {texto_resultado.replace('\n', '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # Botón de descarga PDF
                pdf_bytes = crear_pdf(texto_resultado)
                st.download_button(
                    label="📄 Descargar PDF Oficial",
                    data=pdf_bytes,
                    file_name="Receta_Traducida.pdf",
                    mime="application/pdf"
                )
else:
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.08);'>
        <div style='font-size: 5rem; margin-bottom: 20px;'>🏥</div>
        <h2 style='color: #667eea; margin-bottom: 15px;'>¡Bienvenido al Traductor Médico!</h2>
        <p style='font-size: 1.2rem; color: #636e72; max-width: 600px; margin: 0 auto;'>
            👈 Sube una imagen de tu receta médica en el panel de la izquierda para comenzar el análisis con inteligencia artificial.
        </p>
        <div style='margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 15px; max-width: 500px; margin-left: auto; margin-right: auto;'>
            <p style='margin: 0; color: #1e3a8a; font-weight: 600;'>
                🎯 Formatos soportados: JPG, PNG, JPEG
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
