# src/peptalk/vector_store.py

import os
import shutil
# We no longer import anything from Doppler
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.peptalk.processing import load_text, chunk_text
from langchain_text_splitters import MarkdownHeaderTextSplitter

# --- Constants ---
DATA_FILE_PATH = "data/mpep_2141-2145.md"
PERSIST_DIRECTORY = "data/chroma_db" 

def get_api_key() -> str:
    """
    Fetches the Google API key directly from the environment variables.
    `doppler run` is responsible for setting this variable.
    """
    try:
        print("Reading GOOGLE_API_KEY from environment...")
        # This is the "normal" way you were talking about
        key = os.environ.get("GOOGLE_API_KEY")
        
        if not key:
            raise ValueError("GOOGLE_API_KEY not found in environment.")
            
        print("Successfully read API key.")
        return key
        
    except Exception as e:
        print(f"Error reading environment variable: {e}")
        print("Please ensure you are running this script using `doppler run`")
        print("and that GOOGLE_API_KEY is set in your Doppler project.")
        raise

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

def create_and_store_embeddings(documents: list, embeddings: GoogleGenerativeAIEmbeddings, persist_dir: str):
    """
    Creates embeddings from md documents and saves them to a Chroma vector store.
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
        
        raw_text = load_text(DATA_FILE_PATH)
        if not raw_text:
            print(f"No text found in {DATA_FILE_PATH}. Run data_ingestion.py first.")
            return

        print("Starting to split text by Markdown headers...")
        # Define the headers we care about. '#' is a good top-level
        # separator for our 'START OF SECTION' tags.
        headers_to_split_on = [
            ("#", "Section")
        ]

        # Initialize the splitter
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on, strip_headers=False
        )

        # Split the text. This creates a list of Document objects.
        # Each document has 'page_content' and 'metadata'.
        docs = markdown_splitter.split_text(raw_text)
        print(f"Successfully split text into {len(docs)} documents.")
        
        embeddings = initialize_embeddings(api_key)
        
        print(f"Clearing old vector store at {PERSIST_DIRECTORY}...")
        if os.path.exists(PERSIST_DIRECTORY):
            shutil.rmtree(PERSIST_DIRECTORY)
        
        create_and_store_embeddings(docs, embeddings, PERSIST_DIRECTORY)
        
    except Exception as e:
        print(f"An error occurred in the main pipeline: {e}")

if __name__ == "__main__":
    # We are back to just using 'python' because 'doppler run'
    # will find the correct 'python' in our activated venv's PATH.
    #
    # Run this file with:
    # doppler run --project docketrocket --config dev -- python src/peptalk/vector_store.py
    main()