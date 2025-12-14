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

st.markdown("<h1>🌈 Traductor de Recetas Médicas con IA 💊</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem; color: #636e72; margin-top: -20px; margin-bottom: 50px; font-weight: 600;'>✨ Convierte la caligrafía médica en texto claro al instante con inteligencia artificial ✨</p>", unsafe_allow_html=True)

# --- BARRA LATERAL MEJORADA ---
with st.sidebar:
    st.markdown("### 🎯 Panel de Control")
    st.markdown("---")
    st.write("🚀 Sube la foto de tu receta y deja que la IA descifre la letra del médico en segundos.")
    
    archivo = st.file_uploader("📤 Arrastra tu receta aquí", type=["jpg", "png", "jpeg"])
    
    st.info("💡 **Tip Profesional:** Asegúrate de que la foto tenga buena iluminación y enfoque nítido para mejores resultados.")
    
    st.markdown("---")
    st.markdown("### ✨ Características Premium")
    st.markdown("✅ Análisis con IA avanzada Gemini")
    st.markdown("✅ Exportación profesional a PDF")
    st.markdown("✅ Resultados instantáneos y precisos")
    st.markdown("✅ Interfaz intuitiva y moderna")

# --- ZONA PRINCIPAL CON COLUMNAS ---
if archivo:
    imagen = Image.open(archivo)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    # COLUMNA IZQUIERDA: IMAGEN
    with col1:
        st.subheader("📸 Receta Original")
        st.image(imagen, caption='📋 Tu imagen cargada correctamente', use_column_width=True)
    
    # COLUMNA DERECHA: RESULTADOS
    with col2:
        st.subheader("🔮 Traducción Inteligente")
        
        if st.button("🚀 Traducir Ahora", type="primary"):
            with st.spinner :
                texto_resultado = analizar_receta(imagen)
                
                st.success("✅ ¡Análisis completado con éxito! Tu receta ha sido traducida.")
                st.markdown("### 📝 Resultado de la Traducción:")
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 50%, #e9ecef 100%); 
                            padding: 30px; 
                            border-radius: 20px; 
                            border-left: 8px solid #667eea;
                            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                            margin: 25px 0;
                            border: 2px solid rgba(102, 126, 234, 0.2);'>
                    <div style='color: #2d3436; font-size: 1.1rem; line-height: 1.9;'>
                        {texto_resultado.replace('\n', '<br>')}
                    </div>
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
    <div style='text-align: center; 
                padding: 80px 40px; 
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%); 
                border-radius: 30px; 
                box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
                border: 3px solid rgba(102, 126, 234, 0.2);
                backdrop-filter: blur(10px);'>
        <div style='font-size: 6rem; margin-bottom: 30px; animation: bounce 2s infinite;'>🏥</div>
        <h2 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   margin-bottom: 25px;
                   font-size: 2.5rem;
                   font-weight: 900;'>
            ¡Bienvenido al Traductor Médico Inteligente!
        </h2>
        <p style='font-size: 1.3rem; 
                  color: #636e72; 
                  max-width: 700px; 
                  margin: 0 auto 40px auto;
                  line-height: 1.8;
                  font-weight: 500;'>
            👈 Sube una imagen de tu receta médica en el panel de la izquierda para comenzar el análisis instantáneo con inteligencia artificial de última generación.
        </p>
        <div style='margin-top: 40px; 
                    padding: 30px; 
                    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%); 
                    border-radius: 20px; 
                    max-width: 600px; 
                    margin-left: auto; 
                    margin-right: auto;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
                    border: 2px solid rgba(102, 126, 234, 0.3);'>
            <p style='margin: 0; 
                      color: #0d47a1; 
                      font-weight: 800;
                      font-size: 1.2rem;'>
                🎯 Formatos soportados: JPG, PNG, JPEG
            </p>
            <p style='margin: 15px 0 0 0; 
                      color: #1565c0; 
                      font-weight: 600;
                      font-size: 1rem;'>
                ⚡ Procesamiento ultrarrápido | 🔒 100% Seguro
            </p>
        </div>
    </div>
    
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
    </style>
    """, unsafe_allow_html=True)
