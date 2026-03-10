import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from agent import app as graph_app
from api_schemas import ChatRequest

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

async def generate_chat_stream(message: str):
    """Generates an SSE stream of AI agent events."""
    state = {"messages": [HumanMessage(content=message)]}
    
    # Stream granular updates (v2)
    async for event in graph_app.astream_events(state, version="v2"):
        kind = event["event"]
        
        # 1. Stream text chunks
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
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
            
    # Send termination signal
    yield "data: [DONE]\n\n"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handles streaming chat requests."""
    return StreamingResponse(
        generate_chat_stream(request.message),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
