#
# REPLACE THIS FILE
# File: peptalk/README.md
#

# PEP-talk: A Vertical-Slice Implementation (Monorepo)

This is the PEP-talk project, a RAG-based AI assistant for studying complex legal texts. It is structured as a **monorepo** containing two main applications:

-   `backend/`: The Python/FastAPI application that runs the RAG chain.
-   `frontend/`: The React/Nginx application that provides the user interface.

The entire stack is managed and run using **Docker Compose**.

## Setup

### 1. Environment & API Keys

This project uses Doppler to manage the `GOOGLE_API_KEY`.

```bash
# Log in to your Doppler account
doppler login

# Set up the project in this directory
doppler setup --project docketrocket --config dev

# Add your Google AI API key (get one from Google AI Studio)
doppler secrets set GOOGLE_API_KEY=YOUR_API_KEY_HERE