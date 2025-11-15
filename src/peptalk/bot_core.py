# src/peptalk/bot_core.py

import os
import sys
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

# --- Constants ---
PERSIST_DIRECTORY = "data/chroma_db" 

def get_api_key() -> str:
    """
    Fetches the Google API key directly from the environment variables.
    `doppler run` is responsible for setting this variable.
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

def initialize_components(api_key: str):
    """
    Initializes the embedding model, vector store, and chat model.
    """
    # 1. Initialize the Embedding Model (same as vector_store.py)
    print("Initializing Google embedding model (models/text-embedding-004)...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=api_key
    )

    # 2. Load the existing Vector Store from disk
    print(f"Loading vector store from {PERSIST_DIRECTORY}...")
    if not os.path.exists(PERSIST_DIRECTORY):
        print(f"Error: Directory not found at {PERSIST_DIRECTORY}")
        print("Please run vector_store.py first to create the database.")
        sys.exit(1)
        
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )
    
    # Create a retriever interface
    retriever = db.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 chunks
    print("Vector store loaded successfully.")

    # 3. Initialize the Chat Model (Gemini 2.5 Flash)
    print("Initializing Chat Model (Gemini 2.5 Flash)...")
    
    # --- THIS IS THE UPDATED LINE ---
    # We are now using the latest 2.5 model, which my search confirmed.
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key
    )
    print("Chat model initialized.")
    
    return retriever, llm

def create_rag_chain(retriever, llm):
    """
    Creates the main Retrieval-Augmented Generation (RAG) chain.
    """
    template = """
    You are an expert assistant for U.S. Patent Law.
    Your task is to answer the user's question based *only* on the provided
    context from the Manual of Patent Examining Procedure (MPEP).

    Do not use any outside knowledge. If the answer is not in the
    provided context, state that you cannot answer based on the context.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    ANSWER:
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

def main():
    """
    Main function to initialize and run the chat bot in a loop.
    """
    print("Starting PEP-talk Bot POC...")
    try:
        # We only need the one key!
        api_key = get_api_key()
        
        retriever, llm = initialize_components(api_key)
        rag_chain = create_rag_chain(retriever, llm)
        
        print("\n--- PEP-talk Bot is ready! ---")
        print("Ask a question about MPEP 2141-2145 (Obviousness).")
        print("Type 'exit' to quit.\n")
        
        while True:
            question = input("Your question: ")
            if question.lower() == 'exit':
                print("Goodbye!")
                break
                
            print("\nThinking...\n")
            try:
                for chunk in rag_chain.stream(question):
                    print(chunk, end="", flush=True)
                print("\n\n")
            except Exception as e:
                print(f"\nError during model invocation: {e}")
                print("This may be an authentication or API quota issue.\n")

    except Exception as e:
        print(f"\nAn error occurred during startup: {e}")

if __name__ == "__main__":
    # We run this as a module from the root directory
    # doppler run --project docketrocket --config dev -- python -m src.peptalk.bot_core
    main()