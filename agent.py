import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict

from tools import fetch_user_information, simple_calculator, web_search_tool, read_local_file

load_dotenv()

# State tracking schema
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Setup LLM and tools
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
tools = [fetch_user_information, simple_calculator, web_search_tool, read_local_file]
# Apply explicit tool-calling rules optimised for llama-3.1-8b-instant.
system_message = {
    "role": "system",
    "content": (
        "You are an autonomous AI assistant. You have access to tools and MUST use them when relevant. "
        "Follow these rules strictly:\n"
        "1. NEVER output raw text like `<function=...>` or markdown code blocks as tool calls. "
        "Always use the structured tool-calling interface.\n"
        "2. USER QUERIES: If a user asks about users, people, or inventory in ANY way "
        "(e.g. 'show me users', 'list people', 'give me 5 users', 'who do you know'), "
        "you MUST immediately call `fetch_user_information` with an empty `user_id`. "
        "Do NOT ask for IDs. Do NOT explain yourself. Just call the tool.\n"
        "3. MATH: For any arithmetic, always call `simple_calculator`.\n"
        "4. LIVE INFO: For any current events or facts you are unsure about, call `web_search_tool`.\n"
        "5. FILES: To read a local file, call `read_local_file`.\n"
        "6. After a tool returns data, summarise it clearly for the user."
    )
}
llm_with_tools = llm.bind_tools(tools)

# LLM node
def chatbot(state: State):
    messages = [system_message] + state["messages"]
    return {"messages": [llm_with_tools.invoke(messages)]}

# Tool execution node
tool_executor = ToolNode(tools)

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("agent", chatbot)
graph_builder.add_node("tools", tool_executor)

# Configure edges
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", tools_condition)
graph_builder.add_edge("tools", "agent")

app = graph_builder.compile()
