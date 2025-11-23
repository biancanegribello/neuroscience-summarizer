import streamlit as st 
import fitz  # PyMuPDF 
from google import genai 
import os 
import json 
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        st.error("❌ API Key not found. Please set GEMINI_API_KEY in .env or Streamlit Secrets.")
        st.stop()

client = genai.Client(api_key=api_key)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ResearchMate",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE SETUP ---
# Inicializamos variáveis para controlar o arquivo atual
if 'summary_data' not in st.session_state:
    st.session_state.summary_data = None
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

# --- STYLE FUNCTION (Para limpar o código principal) ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        /* General App Styling */
        .stApp { background-color: #0f0e17; font-family: 'Outfit', sans-serif; color: #fffffe; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif; color: #fffffe; }
        p, li, div { color: #a7a9be; }

        /* Hero Section */
        .hero-container { text-align: center; padding: 3rem 0 2rem 0; margin-bottom: 2rem; }
        .hero-title { font-size: 3.5rem; font-weight: 700; background: -webkit-linear-gradient(45deg, #7f5af0, #2cb67d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }
        .hero-subtitle { font-size: 1.2rem; color: #94a1b2; font-weight: 400; }
        .hero-badge { background-color: rgba(127, 90, 240, 0.2); color: #7f5af0; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 1rem; }

        /* Containers & Cards */
        [data-testid="stBorderContainer"] { background-color: #16161a; border: 1px solid #242629; border-radius: 16px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        
        /* Buttons */
        .stButton > button { width: 100%; border-radius: 8px; font-weight: 600; background: linear-gradient(90deg, #7f5af0 0%, #6246ea 100%); color: white; border: none; padding: 0.6rem 1rem; transition: all 0.3s ease; margin-top: 1rem; }
        .stButton > button:hover { box-shadow: 0 4px 15px rgba(127, 90, 240, 0.4); transform: translateY(-2px); color: white; }

        /* Fix Streamlit Inputs colors */
        .stSelectbox label { color: #fffffe; }
        div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: black !important; -webkit-text-fill-color: black !important; }
        ul[data-baseweb="menu"] li span { color: black !important; }

        /* Summary Cards */
        .summary-card { background-color: #fffffe; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); color: #2b2c34; }
        .summary-card h3 { color: #2b2c34; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem; }
        .summary-card p, .summary-card li { color: #4a4e69; font-size: 1rem; line-height: 1.6; }
        .tag { display: inline-block; background-color: #eaddff; color: #21005d; padding: 0.2rem 0.6rem; border-radius: 16px; font-size: 0.85rem; font-weight: 500; margin-right: 0.5rem; margin-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# Injeta o CSS
inject_custom_css() 

# --- CORE LOGIC FUNCTIONS ---

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf") # Abre o PDF
    text = "" # Inicializa a string de texto
    for page in doc: # Percorre as páginas
        text += page.get_text() # Extrai o texto de cada página
    doc.close() # Fecha o PDF
    return text # Retorna o texto extraído

def get_summary_from_gemini(full_text, detail_level, target_audience):
    try:
        # Instrução para garantir JSON limpo
        prompt = f"""
        As an expert academic researcher, analyze the provided scientific paper text and generate a comprehensive summary in valid JSON format.
        
        **Configuration:**
        - **Detail Level:** {detail_level}
        - **Target Audience:** {target_audience}
        
        Required JSON Structure (Do not include Markdown formatting like ```json at the start):
        {{
            "title": "Paper Title",
            "authors": ["Author 1", "Author 2"],
            "publication_year": "Year",
            "journal": "Journal Name",
            "keywords": ["Keyword 1", "Keyword 2"],
            "main_subject": "One sentence summary",
            "abstract_summary": "Summary text...",
            "introduction_summary": "Summary text...",
            "objective_hypotheses": "Objective text...",
            "methodology_summary": "Methods text...",
            "results_summary": "Key findings text...",
            "discussion_summary": "Discussion text...",
            "main_conclusions": ["Concl 1", "Concl 2"]
        }}
        
        Paper Text:
        {full_text}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'} # Garante que a resposta seja JSON
        )
        
        # Parsing seguro
        return json.loads(response.text) # Retorna o JSON

    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def generate_markdown_report(data):
    """Converts the JSON analysis data into a full Markdown report string."""
    
    # Formata listas (como autores e conclusões) para texto
    authors = ", ".join(data.get('authors', []))
    keywords = ", ".join(data.get('keywords', []))
    
    # Cria a lista de conclusões com bolinhas (bullet points)
    conclusions_list = "\n".join([f"- {item}" for item in data.get('main_conclusions', [])])

    # Monta o texto final usando f-strings (f"...")
    markdown_text = f"""# {data.get('title', 'Untitled Paper')}

    *Authors:* {authors}
    *Journal:* {data.get('journal', 'N/A')} ({data.get('publication_year', 'N/A')})
    *Main Subject:* {data.get('main_subject', 'N/A')}
    *Keywords:* {keywords}

    ---

    ## 📖 Abstract Summary
    {data.get('abstract_summary', 'N/A')}

    ## 🔦 Introduction
    {data.get('introduction_summary', 'N/A')}

    ## 🎯 Objective & Hypotheses
    {data.get('objective_hypotheses', 'N/A')}

    ## 🧪 Methodology
    {data.get('methodology_summary', 'N/A')}

    ## 📊 Results
    {data.get('results_summary', 'N/A')}

    ## 💬 Discussion
    {data.get('discussion_summary', 'N/A')}

    ## 💡 Main Conclusions
    {conclusions_list}

    ---
    *Analysis generated by ResearchMate (Powered by Gemini 2.0 Flash)*
    """
    return markdown_text


def render_summary_cards(data):
    # 1. General Info
    st.markdown(f"""
    <div class="summary-card">
        <h3>📄 {data.get('title', 'Untitled')}</h3>
        <p><strong>👥 Authors:</strong> {', '.join(data.get('authors', ['Unknown']))}</p>
        <p><strong>🗓️ Publication:</strong> {data.get('journal', 'N/A')} ({data.get('publication_year', 'N/A')})</p>
        <p><strong>🔖 Subject:</strong> {data.get('main_subject', '')}</p>
        <div style="margin-top: 10px;">
            {''.join([f'<span class="tag">{k}</span>' for k in data.get('keywords', [])])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Grid Layout for Main Sections
    sections = [
        ("📖 Abstract", "abstract_summary"),
        ("🔦 Introduction", "introduction_summary"),
        ("🎯 Objective", "objective_hypotheses"),
        ("🧪 Methodology", "methodology_summary"),
        ("📊 Results", "results_summary"),
        ("💬 Discussion", "discussion_summary"),
    ]
    
    c1, c2 = st.columns(2)
    for i, (title, key) in enumerate(sections):
        content = data.get(key, "Not provided.")
        html = f"""<div class="summary-card"><h3>{title}</h3><p>{content}</p></div>"""
        (c1 if i % 2 == 0 else c2).markdown(html, unsafe_allow_html=True)

    # 3. Conclusions
    conclusions = "".join([f"<li>{c}</li>" for c in data.get('main_conclusions', [])])
    st.markdown(f"""<div class="summary-card"><h3>💡 Main Conclusions</h3><ul>{conclusions}</ul></div>""", unsafe_allow_html=True)

# --- UI LAYOUT ---

st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">BETA v1.0</div>
        <div class="hero-title">ResearchMate</div>
        <div class="hero-subtitle">Understand Research Faster with AI-Powered Summaries</div>
    </div>
""", unsafe_allow_html=True)

# Container Central de Controle
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.container(border=True):
        st.markdown("### ⚙️ Configuration")
        c1, c2 = st.columns(2)
        detail_level = c1.selectbox("Detail Level", ["Concise", "Balanced", "Comprehensive"], index=1)
        target_audience = c2.selectbox("Target Audience", ["Student", "Researcher", "Expert"], index=1)
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader("Upload PDF Paper", type="pdf")
        
        # LOGICA DE ESTADO INTELIGENTE
        if uploaded_file:
            # Criamos um ID único baseado no nome e tamanho do arquivo
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            
            # Se o arquivo mudou desde a última vez, limpamos o resumo anterior
            if st.session_state.current_file_id != file_id:
                st.session_state.summary_data = None
                st.session_state.current_file_id = file_id
            
            if st.button("✨ Summarize Paper"):
                with st.spinner('🧠 Analyzing paper structure...'):
                    text = extract_text_from_pdf(uploaded_file)
                    if text:
                        data = get_summary_from_gemini(text, detail_level, target_audience)
                        if data:
                            st.session_state.summary_data = data
                            st.rerun() # Recarrega a página para exibir os dados limpamente
        else:
            # Se o usuário removeu o arquivo, limpa tudo
            st.session_state.summary_data = None
            st.session_state.current_file_id = None

# --- DISPLAY RESULTS ---
if st.session_state.summary_data:
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    render_summary_cards(st.session_state.summary_data)
    
    # 1. Gera o texto completo usando a função nova
    full_report = generate_markdown_report(st.session_state.summary_data)
    
    # 2. Cria um nome de arquivo baseado no título do artigo (substituindo espaços por _)
    safe_filename = st.session_state.summary_data.get('title', 'summary').replace(' ', '_') + "_Analysis.md"
    
    # 3. O botão de download agora entrega o relatório completo
    st.download_button(
        label="📥 Download Full Report",
        data=full_report,
        file_name=safe_filename,
        mime="text/markdown"
    )