#
# REPLACE THIS FILE
# File: peptalk/backend/main.py
#

import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# (No more CORS imports)

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
        api_key = get_api_key()
        retriever, llm = initialize_components(api_key)
        rag_chain = create_rag_chain(retriever, llm)
        bot_state["rag_chain"] = rag_chain
        print("--- RAG Bot Loaded Successfully. Server is Ready. ---")
    except Exception as e:
        print(f"!!! CRITICAL STARTUP ERROR: {e} !!!")
        print("!!! Server will start, but /chat/stream will fail. !!!")
        bot_state["rag_chain"] = None
    
    yield
    
    print("--- Server Shutdown ---")
    bot_state.clear()


# --- FastAPI Application ---

app = FastAPI(
    title="PEP-talk API",
    description="API for the PEP-talk RAG bot.",
    lifespan=lifespan
)

# (CORS Middleware section is REMOVED)

# --- API Endpoints ---

@app.get("/")
def get_root():
    return {"message": "PEP-talk API is running. Post to /api/chat/stream to interact."}

async def stream_rag_response(rag_chain, question: str) -> AsyncGenerator[str, None]:
    """
    Asynchronously streams the RAG chain's response.
    """
    try:
        async for chunk in rag_chain.astream(question):
            yield chunk
            await asyncio.sleep(0) 
    except Exception as e:
        print(f"Error during RAG stream: {e}")
        yield f"\n\nSERVER_ERROR: An error occurred while processing your request: {e}"

# --- IMPORTANT URL CHANGE ---
# The URL is now /api/chat/stream to work with the frontend's proxy.
@app.post("/api/chat/stream")
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
    print("--- Starting Uvicorn server for development ---")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=8000, 
        reload=True
    )