#
# REPLACE THIS FILE
# File: peptalk/backend/src/peptalk/vector_store.py
#
import os
import shutil
import glob 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter

# --- THIS IS THE CORRECTED IMPORT ---
from langchain_core.documents import Document

# --- Constants ---
DATA_FILE_PATH_PATTERN = "data/mpep_*.md" 
PERSIST_DIRECTORY = "data/chroma_db" 

def get_api_key() -> str:
    """
    Fetches the Google API key directly from the environment variables.
    """
    try:
        print("Reading GOOGLE_API_KEY from environment...")
        key = os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY not found in environment.")
        print("Successfully read API key.")
        return key
    except Exception as e:
        print(f"Error reading environment variable: {e}")
        print("Please ensure GOOGLE_API_KEY is set in your Doppler project.")
        raise

def load_and_split_markdown_files(file_pattern: str) -> list[Document]:
    """
    Loads all markdown files matching the pattern and splits them by headers.
    """
    all_documents = []
    
    headers_to_split_on = [
        ("#", "H1"),
        ("##", "H2"),
        ("###", "H3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )

    markdown_files = glob.glob(file_pattern)
    if not markdown_files:
        print(f"Warning: No files found matching pattern {file_pattern}")
        return []
        
    print(f"Found {len(markdown_files)} markdown files to process...")

    for filepath in markdown_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            docs = markdown_splitter.split_text(raw_text)
            
            for doc in docs:
                doc.metadata['source_file'] = filepath.split('/')[-1]
                
            all_documents.extend(docs)
            print(f"Processed {filepath}, added {len(docs)} documents.")
            
        except IOError as e:
            print(f"ERROR: Could not read file {filepath}. Error: {e}")

    return all_documents


def initialize_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """
    Initializes the Google embedding model.
    """
    print("Initializing Google embedding model...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=api_key
    )
    print("Google embedding model initialized.")
    return embeddings

def create_and_store_embeddings(documents: list[Document], embeddings: GoogleGenerativeAIEmbeddings, persist_dir: str):
    """
    Creates embeddings from text chunks and saves them to a Chroma vector store.
    """
    if not documents:
        print("No documents to process. Exiting.")
        return

    print(f"Creating vector store from {len(documents)} documents...")
    
    db = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory=persist_dir
    )
    
    print(f"Vector store successfully created and saved to {persist_dir}")

def main():
    """
    Main pipeline: Load secret, load text, chunk text, create vector store.
    """
    try:
        api_key = get_api_key()
        
        print(f"Loading and splitting markdown files from {DATA_FILE_PATH_PATTERN}...")
        documents = load_and_split_markdown_files(DATA_FILE_PATH_PATTERN)
        
        if not documents:
            print(f"No documents found. Run data_ingestion.py first.")
            return
        
        embeddings = initialize_embeddings(api_key)
        
        print(f"Clearing old vector store at {PERSIST_DIRECTORY}...")
        if os.path.exists(PERSIST_DIRECTORY):
            shutil.rmtree(PERSIST_DIRECTORY)
        
        create_and_store_embeddings(documents, embeddings, PERSIST_DIRECTORY)
        
    except Exception as e:
        print(f"An error occurred in the main pipeline: {e}")

if __name__ == "__main__":
    main()