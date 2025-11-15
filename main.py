#
# ADD THIS NEW FILE
# File: peptalk/main.py
#

import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Import the logic from your existing bot_core
from src.peptalk.bot_core import (
    get_api_key,
    initialize_components,
    create_rag_chain
)

# --- Pydantic Models for API Validation ---

class ChatRequest(BaseModel):
    """The request model for a user's question."""
    question: str

# --- Global Bot State ---

# This dictionary will hold our loaded RAG chain.
# We use a dict so it can be modified by the lifespan event.
bot_state = {}

# --- Lifespan Event Handler (Startup/Shutdown) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    On startup, it loads the RAG model.
    """
    print("--- Server Startup: Loading RAG Bot ---")
    try:
        # Load all the components, just like bot_core.py's main()
        api_key = get_api_key()
        retriever, llm = initialize_components(api_key)
        rag_chain = create_rag_chain(retriever, llm)
        
        # Store the chain in our global state
        bot_state["rag_chain"] = rag_chain
        print("--- RAG Bot Loaded Successfully. Server is Ready. ---")
    except Exception as e:
        print(f"!!! CRITICAL STARTUP ERROR: {e} !!!")
        print("!!! Server will start, but /chat/stream will fail. !!!")
        bot_state["rag_chain"] = None # Set to None so we can check
    
    yield
    
    # --- Shutdown ---
    print("--- Server Shutdown ---")
    bot_state.clear()


# --- FastAPI Application ---

app = FastAPI(
    title="PEP-talk API",
    description="API for the PEP-talk RAG bot.",
    lifespan=lifespan
)

# --- API Endpoints ---

@app.get("/")
def get_root():
    return {"message": "PEP-talk API is running. Post to /chat/stream to interact."}

async def stream_rag_response(rag_chain, question: str) -> AsyncGenerator[str, None]:
    """
    Asynchronously streams the RAG chain's response.
    """
    # astream() is the async version of stream()
    try:
        async for chunk in rag_chain.astream(question):
            yield chunk
            # Add a tiny sleep to allow other requests to be processed
            await asyncio.sleep(0) 
    except Exception as e:
        print(f"Error during RAG stream: {e}")
        yield f"\n\nSERVER_ERROR: An error occurred while processing your request: {e}"

@app.post("/chat/stream")
async def post_chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Receives a user's question and streams back the RAG bot's response.
    """
    rag_chain = bot_state.get("rag_chain")
    
    if rag_chain is None:
        return StreamingResponse(
            iter(["Error: Bot not initialized. Check server logs."]), 
            media_type="text/plain", 
            status_code=500
        )
        
    print(f"Streaming response for question: {request.question}")
    
    return StreamingResponse(
        stream_rag_response(rag_chain, request.question),
        media_type="text/plain"
    )

if __name__ == "__main__":
    """
    This allows you to run the server directly for development.
    However, you should use the `uvicorn` command for production
    or when running with Doppler.
    """
    print("--- Starting Uvicorn server for development (use `doppler run` for proper env) ---")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000, 
        reload=True      # Reloads server on code changes
    )