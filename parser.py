import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def parse_and_load_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".docx", ".doc"]:
        loader = Docx2txtLoader(file_path)
    elif ext in [".txt", ".md", ".json"]:
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    return loader.load()

def chunk_documents(documents, strategy="recursive"):
    if strategy == "semantic":
        # It automatically finds the key from your terminal variable!
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        splitter = SemanticChunker(
            embeddings, 
            breakpoint_threshold_type="percentile"
        )
        print("🤖 Applying Gemini Semantic Chunking Strategy...")
        
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        print("📝 Applying Recursive Character Chunking Strategy...")

    return splitter.split_documents(documents)