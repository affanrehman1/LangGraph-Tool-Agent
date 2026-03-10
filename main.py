import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
import uuid

from agent import app as graph_app
from api_schemas import ChatRequest
from database import get_session_messages, save_message

app = FastAPI(
    title="LangGraph Agent API",
    description="Streaming REST API for an autonomous tool-calling LangGraph agent."
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

async def generate_chat_stream(message: str, session_id: str):
    """Generates an SSE stream of AI agent events and persists memory."""
    
    # 1. Load historical messages from DB
    history = await get_session_messages(session_id)
    langchain_messages = []
    for msg in history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_messages.append(AIMessage(content=msg["content"]))
            
    # 2. Append the specific new human message
    langchain_messages.append(HumanMessage(content=message))
    await save_message(session_id, "user", message)
    
    state = {"messages": langchain_messages}
    ai_full_response = ""
    
    # Stream granular updates (v2)
    async for event in graph_app.astream_events(state, version="v2"):
        kind = event["event"]
        
        # 1. Stream text chunks
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                ai_full_response += content
                yield f"data: {json.dumps({'type': 'content', 'data': content})}\n\n"
                
        # 2. Alert tool execution start
        elif kind == "on_tool_start":
            tool_name = event["name"]
            tool_input = event["data"].get("input", {})
            yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name, 'input': tool_input})}\n\n"
            
        # 3. Alert tool execution end
        elif kind == "on_tool_end":
            tool_name = event["name"]
            yield f"data: {json.dumps({'type': 'tool_end', 'tool': tool_name})}\n\n"
            
    # 4. Save the full AI response to the DB
    if ai_full_response:
        await save_message(session_id, "ai", ai_full_response)
        
    # Send termination signal
    yield "data: [DONE]\n\n"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handles streaming chat requests."""
    # Ensure a session ID exists
    session_id = request.session_id or str(uuid.uuid4())
    
    return StreamingResponse(
        generate_chat_stream(request.message, session_id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
