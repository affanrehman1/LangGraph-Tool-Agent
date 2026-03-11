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
# Apply system prompt to ensure strict JSON tool calling schema compliance.
system_message = {
    "role": "system",
    "content": "You are a helpful AI assistant with access to tools. ALWAYS use the provided tool JSON schema to execute tools. NEVER output raw strings like `<|python_tag|>` or markdown code blocks for tool calls."
}
llm_with_tools = llm.bind_tools(tools).bind_messages([system_message])

# LLM node
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

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
