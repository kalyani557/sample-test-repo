import streamlit as st
import tempfile
import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Import our parser functions
from parser import parse_and_load_document, chunk_documents

# --- 1. Page Configuration & UI Theme Styling ---
st.set_page_config(page_title="AuditTrail AI", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Light-Themed CSS UI Tweaks
st.markdown("""
    <style>
        /* Main background area configuration */
        .stApp {
            background-color: #FAFAFA;
        }
        /* Top app header bar styling */
        header[data-testid="stHeader"] {
            background-color: #FAFAFA;
        }
        /* Make the main headings clean and corporate */
        h1 {
            color: #1E293B !important;
            font-weight: 700 !important;
            font-family: 'Inter', sans-serif;
        }
        /* Style the Sidebar panel with soft gray */
        section[data-testid="stSidebar"] {
            background-color: #F1F5F9 !important;
            border-right: 1px solid #E2E8F0;
        }
        /* Soft, card-styled file uploader box */
        div[data-testid="stFileUploadDropzone"] {
            background-color: #FFFFFF !important;
            border: 2px dashed #CBD5E1 !important;
            border-radius: 8px !important;
        }
        /* Audit response window layout */
        .response-container {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-top: 15px;
            color: #334155;
        }
    </style>
""", unsafe_allow_html=True)

# Title Layout
st.markdown("# 🛡️ AuditTrail AI")
st.markdown("<p style='color: #64748B; font-size: 1.1rem; margin-top: -15px;'>Professional Automated Compliance & RFP Intelligence Panel</p>", unsafe_allow_html=True)
st.divider()

# --- 2. Sidebar Configuration ---
with st.sidebar:
    st.markdown("<h3 style='color: #0F172A;'>Control Center</h3>", unsafe_allow_html=True)
    chunk_strategy = st.selectbox(
        "Chunking Strategy", 
        ["recursive", "semantic"],
        help="'Recursive' splits by fixed text window sizes. 'Semantic' optimizes text layout boundaries using Gemini."
    )
    st.markdown("---")
    st.markdown("<small style='color: #94A3B8;'>Status: Connected via Terminal Env Key</small>", unsafe_allow_html=True)

# --- 3. File Upload Logic ---
uploaded_files = st.file_uploader(
    "Upload Compliance Docs (PDF, DOCX, TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    file_hashes = "".join([f.name for f in uploaded_files]) + chunk_strategy
    
    if "current_files" not in st.session_state or st.session_state.current_files != file_hashes:
        all_chunks = []
        
        with st.spinner("Parsing internal document structures..."):
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    docs = parse_and_load_document(tmp_path)
                    for doc in docs:
                        doc.metadata["source_file"] = uploaded_file.name
                        
                    chunks = chunk_documents(docs, strategy=chunk_strategy)
                    all_chunks.extend(chunks)
                finally:
                    os.remove(tmp_path)
            
            embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
            vector_db = Chroma.from_documents(all_chunks, embeddings)
            st.session_state.retriever = vector_db.as_retriever(search_kwargs={"k": 4})
            st.session_state.current_files = file_hashes
            st.success(f"Successfully vectorized {len(all_chunks)} compliance text fragments!")

    # --- 4. Query & RAG Chain Interface ---
    user_question = st.text_input("📝 Run Audit Query (e.g., 'What are the technical SLA uptime requirements?')")
    
    if user_question and "retriever" in st.session_state:
        with st.spinner("Gemini is auditing document context arrays..."):
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                temperature=0
            )
            
            system_prompt = (
                "You are an expert compliance auditor assistant. Answer the user's question using exclusively the provided context.\n"
                "If you do not know the answer or if it's not present in the context text, say exactly: 'I cannot find the answer in the document.'\n\n"
                "Context:\n{context}\n\nQuestion: {input}"
            )
            prompt = ChatPromptTemplate.from_template(system_prompt)

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            rag_chain = (
                {"context": st.session_state.retriever | format_docs, "input": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            retrieved_chunks = st.session_state.retriever.invoke(user_question)
            response_text = rag_chain.invoke(user_question)

            # Elegant card component wrapper for output data
            st.markdown(f"""
                <div class="response-container">
                    <h3 style="margin-top: 0; color: #0F172A;">⚖️ Verified Audit Response</h3>
                    <p style="line-height: 1.6; color: #334155;">{response_text}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("") # Margin spacer
            with st.expander("🔍 Inspect Verified Context Sources"):
                for i, doc in enumerate(retrieved_chunks):
                    st.markdown(f"📄 **Chunk {i+1}** — Source File: `{doc.metadata.get('source_file')}`")
                    st.info(doc.page_content)