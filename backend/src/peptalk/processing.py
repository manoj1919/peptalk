# src/pep_talk/processing.py

from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Splits a large text into smaller chunks using a recursive splitter.
    """
    if not text:
        return []
        
    print(f"Starting to chunk text... Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    
    chunks = text_splitter.split_text(text)
    
    print(f"Successfully split text into {len(chunks)} chunks.")
    return chunks

def load_text(file_path: str) -> str:
    """Loads raw text from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        print(f"ERROR: Could not read file {file_path}. Error: {e}")
        return ""

if __name__ == "__main__":
    # This block lets us test this module directly
    text_content = load_text('data/mpep_2141-2145.txt')
    
    if text_content:
        chunks = chunk_text(text_content)
        print("\n--- Example Chunk (First 500 chars) ---")
        if chunks:
            print(chunks[0][:500] + "...")
    else:
        print("No text content found. Run data_ingestion.py first.")