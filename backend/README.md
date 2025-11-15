#
# REPLACE THIS FILE
# File: peptalk/README.md
#

# PEP-talk: A Vertical-Slice Implementation

This project is a proof-of-concept (POC) implementation of the "PEP-talk" platform, a RAG-based AI assistant for studying complex legal texts.

This implementation is strictly scoped to MPEP Chapters 2141-2145 (Obviousness) and demonstrates the core "Living Text" feature.

## Project Structure

-   `data/`: Holds the raw and processed data.
    -   `mpep_2141-2145.md`: The *structured* Markdown file scraped from the USPTO.
    -   `chroma_db/`: The vector database.
-   `src/peptalk/`: The core Python source code.
    -   `data_ingestion.py`: Scrapes the USPTO website and saves as Markdown.
    -   `vector_store.py`: Reads the Markdown, splits it by headers, and builds the vector DB.
    -   `bot_core.py`: Contains the core logic for the RAG chain.
-   `main.py`: The FastAPI web server that exposes the bot as an API.
-   `requirements.txt`: Python dependencies.
-   `tests/`: Unit tests.

## Setup Instructions

These instructions are for a Linux server environment.

### 1. Clone the Repository

```bash
git clone [your-repo-url]
cd peptalk