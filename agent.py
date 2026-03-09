import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict

from tools import fetch_user_information, simple_calculator

load_dotenv()

# Define LangGraph state schema for tracking conversation history
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize LLM and bind external tools
llm = ChatGroq(model="llama-3.3-70b-versatile")
tools = [fetch_user_information, simple_calculator]
llm_with_tools = llm.bind_tools(tools)

# Define agent node for invoking LLM
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Define node for executing python tools requested by LLM
tool_executor = ToolNode(tools)

# Compile LangGraph framework
graph_builder = StateGraph(State)
graph_builder.add_node("agent", chatbot)
graph_builder.add_node("tools", tool_executor)

# Configure graph routing edges
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", tools_condition)
graph_builder.add_edge("tools", "agent")

app = graph_builder.compile()
