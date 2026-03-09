# Autonomous LangGraph Tool-Calling Agent

An advanced, autonomous AI agent backend architecture built with LangGraph, FastAPI, and Prisma ORM. This project demonstrates how to connect powerful Large Language Models (LLMs) directly to structured relational databases through automated, deterministic tool calling.

## Architecture Overview

This project is built using a layered architecture to ensure separation of concerns, scalability, and type safety across the entire stack. 

1. **Database Layer (Prisma & PostgreSQL):** The foundational data layer. It uses Prisma ORM to provide strict type safety and auto-generated database interaction functions. The schema is currently normalized for an Inventory Management system involving `Users` and `Items`.
2. **API Layer (FastAPI):** An asynchronous REST API that wraps the Prisma database functions, exposing them to the internal network.
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
    *   `User`: Primary actor in the system.
    *   `Item`: A cataloged entity managed by the User in a one-to-many relationship with cascading deletes.
*   **`database.py`**: Contains highly optimized, asynchronous interaction functions:
    *   `get_user_by_id`: Fetches a user record and performs a SQL JOIN to pull relational inventory data.
    *   `update_item_quantity`: Updates specific tracking variables inside the Item table.

### Layer 2: Agent Tool Interface
We've established the strict protocols and interfaces for LLM interactions.
*   **`tools.py`**: Defines the actions the agent can take, strictly typed with Pydantic:
    *   `fetch_user_information`: LangChain `@tool` wrapping the database query, converting the Prisma model response to an LLM-friendly JSON format. 
    *   `simple_calculator`: A secondary tool demonstrating how to offload non-deterministic LLM math to a structured, deterministic Python execution engine.

### Layer 3: Agent Orchestration
We have integrated a LangGraph state machine to manage the loop between deterministic tool calling and LLM generation.
*   **`agent.py`**: The core graph architecture defining nodes and edges:
    *   **LLM Node:** An `agent` node that processes conversational state through the `llama-3.3-70b-versatile` model, analyzing whether standard text or a tool execution is required.
    *   **Tool Node:** A `tools` node that maps the LLM's requested tool securely to our underlying Python functions.
    *   **Conditional Routing:** Automated edge routing that loops execution between the LLM and the Tool Node until the agent synthesizes a cohesive final response.

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

### 5. Generate Database Client
With the `.env` file configured, generate the Prisma Python client. This process reads your schema and downloads the customized Python types required to interact with your specific database structure.

```bash
prisma generate
```

*(Note: Pushing the schema to the live Supabase database via `prisma db push` is scheduled for Phase 2).*
