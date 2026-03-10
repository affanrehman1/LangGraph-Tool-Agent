# Autonomous LangGraph Tool-Calling Agent

## Introduction
This project provides a robust backend architecture for an autonomous AI agent. By integrating LangGraph, FastAPI, and the Prisma ORM, this system enables Large Language Models (LLMs) to securely and deterministically interact with a structured PostgreSQL database. 

Instead of relying solely on pre-trained knowledge to generate text, the agent dynamically writes and executes database queries, performs programmatic calculations, and streams its execution reasoning back to external client applications via a reactive REST API.

## Architecture Overview

This project is built using a layered architecture to ensure separation of concerns, scalability, and type safety across the entire stack. 

1. **Database Layer (Prisma & PostgreSQL):** The foundational data layer. It uses Prisma ORM to provide strict type safety and auto-generated database interaction functions. The schema is currently normalized for an Inventory Management system involving `Users` and `Items`.
2. **API Layer (FastAPI):** An asynchronous REST API (`main.py`) that wraps the LangGraph agent, exposing it to the internal network via Server-Sent Events (SSE) streaming connections. Strict input validation is handled by Pydantic (`api_schemas.py`).
3. **Tool/Action Layer (Pydantic & LangChain):** The strict Pydantic models that define the input schemas for our tools. This layer translates our backend API functions into a JSON schema the LLM can understand and interact with deterministically.
4. **Agent Orchestration Layer (LangGraph):** The state-machine orchestrator. It manages the conversation state, routes user queries to the Groq LLM API, evaluates if a tool call is required, executes the tool, and routes the database response back to the LLM for final generation.

## Technology Stack

### Core Technologies
*   **Language:** Python `^3.10`
*   **Database:** PostgreSQL (Hosted via Supabase)
*   **ORM:** Prisma Client Python `^0.15.0`
*   **API Framework:** FastAPI `^0.115.0` (with Uvicorn `^0.30.6`)
*   **LLM Inference:** Groq API (`llama-3.3-70b-versatile`)
*   **Agent Framework:** LangGraph, LangChain Core & Pydantic `(Installed)`

## Current System Capabilities

### Layer 1: Database Architecture
The foundational relational database architecture has been deployed and configured.
*   **`schema.prisma`**: Defines the core relational data models:
    *   **Inventory Models:** `User` and `Item` for catalog management with cascading deletes.
    *   **Memory Models:** `Session` and `Message` to persistently store Agent conversational history.
*   **`database.py`**: Contains highly optimized, asynchronous interaction functions:
    *   `get_user_by_id` & `update_item_quantity`: Custom queries for inventory manipulation.
    *   `get_session_messages` & `save_message`: Queries handling the fetching and storing of LLM chat sequences.

### Layer 2: Agent Tool Interface
We've established the strict protocols and interfaces for LLM interactions.
*   **`tools.py`**: Defines the capabilities the agent has access to, strictly typed with Pydantic:
    *   **Preset Tools**: Integration with Langchain Community (`DuckDuckGoSearchRun`) giving the agent live internet access.
    *   **Custom Database Tools**: `fetch_user_information` translates natural language into deterministic Prisma database queries.
    *   **Custom Logic Tools**: `simple_calculator` offloads non-deterministic LLM math to a structured Python execution engine, and `read_local_file` allows secure text/markdown file inspection.

### Layer 3: Agent Orchestration
We have integrated a LangGraph state machine to manage the loop between deterministic tool calling and LLM generation.
*   **`agent.py`**: The core graph architecture defining nodes and edges:
    *   **LLM Node:** An `agent` node that processes conversational state through the `llama-3.3-70b-versatile` model, analyzing whether standard text or a tool execution is required.
    *   **Tool Node:** A `tools` node that maps the LLM's requested tool securely to our underlying Python functions.
    *   **Conditional Routing:** Automated edge routing that loops execution between the LLM and the Tool Node until the agent synthesizes a cohesive final response.

### Layer 4: API & Streaming Server
The agent is exposed via a high-performance ASGI web server, allowing external frontends to communicate with the Python logic.
*   **`api_schemas.py`**: Defines strict Pydantic models (like `ChatRequest`) ensuring frontend payloads are validated before reaching the agent. Crucially, handles `session_id` payload ingestion to tie incoming text to persistent histories.
*   **`main.py`**: A FastAPI application featuring a `/chat` POST endpoint. 
    *   **Context Rehydration:** The endpoint fetches historical `HumanMessage` and `AIMessage` models from the database dynamically based on the requested session.
    *   **SSE Streaming:** It uses LangGraph's `astream_events` (v2) to generate a Server-Sent Events (SSE) stream, delivering granular real-time updates of tool executions and LLM text generation back to the client.

## Local Development & Setup Guide

Follow these steps to configure the development environment and connect to the database.

### 1. Prerequisites
Ensure the following are installed on your local machine:
*   Python 3.10 or higher.
*   Node.js (Required strictly for the Prisma CLI engine).
*   Git.

### 2. Clone and Initialize
Clone the repository and set up an isolated Python virtual environment.

```bash
git clone https://github.com/your-username/langgraph-tool-agent.git
cd langgraph-tool-agent

# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate 
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
Install the required packages from the requirements file.

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
The application requires external credentials to function. You must create a `.env` file in the root directory.

1.  Create a file named `.env`.
2.  Add the following variables, replacing the bracketed sections with your actual credentials:

```env
# Supabase PostgreSQL Connection String
# Found in Supabase -> Project Settings -> Database -> URI
DATABASE_URL="postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]"

# Groq API Key
# Found in Groq Console -> API Keys
GROQ_API_KEY="gsk_your_key_here"
```

### 5. Generate and Push Database Client
With the `.env` file configured, generate the Prisma Python client. This process reads your schema and downloads the customized Python types required to interact with your specific database structure.

```bash
prisma generate
```

After generating the client, you must push your local schema over to your live Supabase database so the tables are actually created:

```bash
prisma db push
```

### 6. Run the API Server
Start the FastAPI server using Uvicorn. This will expose the LangGraph agent and begin listening for incoming requests.

```bash
uvicorn main:app --reload
```
You can verify the backend is running by navigating to `http://localhost:8000/health` in your browser.
