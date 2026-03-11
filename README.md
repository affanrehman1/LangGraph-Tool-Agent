# Autonomous LangGraph Tool-Calling Agent

## Introduction
This project provides a robust full-stack architecture for an autonomous AI agent. By tightly integrating LangGraph, FastAPI, Next.js, and the Prisma ORM, this system enables smaller, rapid Large Language Models (LLMs) to securely and deterministically interact with a structured PostgreSQL database and the open web.

Instead of relying solely on pre-trained knowledge, the agent uses strict rule-based tool calling to dynamically write execute database queries, perform programmatic calculations, and stream its execution reasoning back to a premium React frontend via a reactive REST API.

---

## Final Project Architecture

This project is built using a 5-layer architecture to ensure separation of concerns, scalability, and type safety across the entire stack.

1. **Database Layer (Prisma & PostgreSQL):** The foundational data layer. It uses Prisma ORM to provide strict type safety and auto-generated database interaction functions. The schema is normalized for an Inventory Management system involving `Users` and `Items`, as well as conversational memory models `Sessions` and `Messages`.
2. **API Layer (FastAPI):** An asynchronous REST API (`main.py`) that wraps the LangGraph agent, exposing it to the frontend via Server-Sent Events (SSE) streaming connections. Strict input validation is handled by Pydantic (`api_schemas.py`).
3. **Tool/Action Layer (Pydantic & LangChain):** The strict Pydantic models that define the input schemas for our tools. This layer translates our backend API functions into a JSON schema the LLM can understand and interact with deterministically. Includes tools for Live Web Search, Calculator logic, File Inspection, and Database Profile lookups.
4. **Agent Orchestration Layer (LangGraph):** The state-machine orchestrator. It manages the conversation state, routes user queries to the Groq LLM API, evaluates if a tool call is required, executes the tool securely, and routes the response back to the LLM for final generation.
5. **Frontend UI Layer (Next.js 15):** The user-facing application built with React 19, Tailwind CSS v4, and Radix primitives (`shadcn/ui`). It connects to the FastAPI backend, parses the SSE stream in real-time, and renders a dynamic, persistent chat interface.

---

## Technology Stack

### Backend
*   **Language:** Python `3.12` (Required for Pydantic v2 core-schema binaries)
*   **Database:** PostgreSQL (Hosted via Supabase)
*   **ORM:** Prisma Client Python `^0.15.0`
*   **API Framework:** FastAPI `^0.115.0` (with Uvicorn `^0.30.6`)
*   **LLM Inference:** Groq API (`llama-3.1-8b-instant`) — *Optimized via strict system rules to act as a fast, reliable tool-caller.*
*   **Agent Framework:** LangGraph, LangChain Core & Pydantic

### Frontend
*   **Framework:** Next.js `15.2.0` (App Router)
*   **Library:** React `19.0.0` The DOM renderer.
*   **Styling:** Tailwind CSS `4.0.0`
*   **Components:** `shadcn/ui` (Avatar, Button, Card, Input, ScrollArea)
*   **Icons:** `lucide-react`

---

## Step-by-Step Native Setup Guide

Follow these steps to configure the development environment, seed the database, and spin up both the frontend and backend servers.

### 1. Prerequisites
Ensure the following are installed and accessible in your system's PATH:
*   **Python 3.12**
*   **Node.js** (v18+)
*   **Git**

### 2. Clone and Initialize the Backend
Clone the repository and set up an isolated Python virtual environment.

```bash
git clone https://github.com/your-username/langgraph-tool-agent.git
cd "langgraph-tool-agent"

# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate 
# On macOS/Linux:
source .venv/bin/activate

# Install strictly-versioned Python packages
pip install -r requirements.txt
```

### 3. Environment Configuration
The application requires external credentials to function. You must create a `.env` file in the root directory.

Create a file named `.env` and insert your API keys:
```env
# Supabase PostgreSQL Connection String
# Found in Supabase -> Project Settings -> Database -> URI
DATABASE_URL="postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]"

# Groq API Key
# Found in Groq Console -> API Keys
GROQ_API_KEY="gsk_your_key_here"
```

### 4. Database Schema Push & Client Generation
With the `.env` file configured, generate the Prisma Python client and push your schema to the remote PostgreSQL instance.

```bash
# Downloads the customized Python types required to interact with your database
prisma generate

# Applies the schema in schema.prisma to your live Supabase database
prisma db push
```

### 5. Seed the Database
Do not skip this step! The agent needs data to interact with. Run the automated seed script to populate your database with mock users and inventory items.

```bash
python seed.py
```
*You should see a success message indicating users and items were created.*

### 6. Start the FastAPI Backend
Start the high-performance ASGI web server exposing the LangGraph agent to the network. Keep this terminal open.

```bash
uvicorn main:app --reload
```
*The backend is now live on `http://localhost:8000`. You can verify it by visiting `http://localhost:8000/health`.*

### 7. Initialize and Start the Next.js Frontend
Open a **new, separate terminal window**. Navigate to the frontend directory to run the UI.

```bash
# Navigate to the frontend directory
cd "langgraph-tool-agent/frontend"

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev
```

### 8. Use the Project
Open your web browser and navigate to **`http://localhost:3000`**. You are now ready to chat seamlessly with your autonomous, database-aware AI agent!
