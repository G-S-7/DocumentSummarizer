import streamlit as st
from core.extractor import DocumentExtractor
from dotenv import load_dotenv
from core.summarizer import TransformerSummarizer
from services.orchestrator import DocumentOrchestrator

load_dotenv()
# --- DEPRECIATION/INITIALIZATION CACHE ---
@st.cache_resource
def init_orchestrator():
    extractor = DocumentExtractor()
    summarizer = TransformerSummarizer(model_name="google/flan-t5-large")
    return DocumentOrchestrator(extractor, summarizer)

orchestrator = init_orchestrator()

# --- UI SETUP ---
st.set_page_config(page_title="IntellectExtract Enterprise", page_icon="📝", layout="wide")
st.title("📝 Intelligent Document Summarizer")

with st.sidebar:
    st.header("📥 Upload Zone")
    uploaded_files = st.file_uploader(
        label="Upload documents", 
        type=["pdf", "png", "jpg", "jpeg", "webp", "txt"], 
        accept_multiple_files=True
    )
    
    st.markdown("---")
    st.header("⚙️ Summary Generation Settings")
    
    # User Dynamic Controls
    user_prompt = st.text_area(
        label="Custom Prompt / Suggestions",
        placeholder="e.g., Summarize the technical stack in bullet points...",
        help="Leave blank to use the default automated bullet-point template."
    )
    
    col_min, col_max = st.columns(2)
    with col_min:
        min_length = st.number_input("Minimum Tokens", min_value=5, max_value=100, value=20, step=5)
    with col_max:
        max_length = st.number_input("Maximum Tokens", min_value=50, max_value=512, value=180, step=10)

    # Bundle configurations to pass cleanly through pipeline
    summary_settings = {
        "prompt": user_prompt,
        "min_len": int(min_length),
        "max_len": int(max_length)
    }

# --- PROCESSING ---
if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.container():
            st.markdown(f"### 📄 Processing: `{uploaded_file.name}`")
            
            file_bytes = uploaded_file.read()
            
            with st.spinner("Analyzing document structure & generating summary..."):
                doc_data = orchestrator.process_document(
                    file_name=uploaded_file.name,
                    file_type=uploaded_file.type,
                    file_bytes=file_bytes,
                    summary_settings=summary_settings # Passing user variables
                )
                
            # --- PRESENT VARIATION BY TYPE ---
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🤖 AI Summary")
                # Used st.markdown instead of st.info so bullet breaks display accurately
                st.markdown(doc_data["summary"])
                
            with col2:
                st.subheader("📑 Extracted Structural Text")
                if doc_data["type"] == "application/pdf" :
                    tabs = st.tabs([f"Page {i+1}" for i in range(len(doc_data["pages"]))])
                    for idx, page_content in enumerate(doc_data["pages"]):
                        with tabs[idx]:
                            if page_content:
                                st.code(page_content, language="text")
                            else:
                                st.warning("Empty page or structural elements missed.")
                elif doc_data["type"] == "text/plain":
                    st.text_area("Text File Content", value=doc_data["pages"][0], height=300)
                else:
                    st.text_area("OCR Text Output", value=doc_data["pages"][0], height=300)
            st.markdown("---")
else:
    st.info("💡 Upload standard documents or images via the sidebar to initiate analysis pipeline.")
