import os
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

from database import get_user_by_id, get_all_users

class WebSearchSchema(BaseModel):
    query: str = Field(..., description="The exact search query to look up on the internet.")

@tool(args_schema=WebSearchSchema)
def web_search_tool(query: str) -> str:
    """Search the live internet for current events, facts, or any information not in your training data. Use this whenever the user asks about recent news, live data, or anything you are uncertain about."""
    try:
        # Wraps search execution to limit output payload and manage API rate limits.
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
        search = DuckDuckGoSearchResults(api_wrapper=wrapper)
        return search.run(query)
    except Exception as e:
        return f"Warning: Search engine is currently unavailable due to errors or rate limits. Try answering without it if possible. (Error: {e})"


# 2. DB Tool
class GetUserSchema(BaseModel):
    user_id: str = Field(
        default="",
        description=(
            "The UUID of a specific user to look up. "
            "Leave this field EMPTY (do not fill it in) when the user asks for multiple users, "
            "all users, any users, or does not specify a particular ID. "
            "Only provide a UUID here if the user gives you a specific ID."
        )
    )

@tool(args_schema=GetUserSchema)
async def fetch_user_information(user_id: str = "") -> list | dict:
    """
    Fetch user profiles and their inventory items from the database.
    IMPORTANT: If the user asks for 'all users', 'some users', 'a list of users', 'users you know',
    or any number of users without specifying IDs, call this tool with an EMPTY user_id.
    Only pass a specific UUID if the user explicitly provides one.
    """
    if not user_id or user_id.lower() == "all":
        users = await get_all_users()
        return [u.model_dump() for u in users]

    user_record = await get_user_by_id(user_id)
    if user_record:
        return user_record.model_dump()
    return {"error": f"No user found with ID: {user_id}"}


# 3. Calculator
class CalculatorSchema(BaseModel):
    a: float = Field(..., description="First number.")
    b: float = Field(..., description="Second number.")
    operation: str = Field(
        ..., 
        description="Operation: 'add', 'subtract', 'multiply', 'divide'"
    )

@tool(args_schema=CalculatorSchema)
def simple_calculator(a: float, b: float, operation: str) -> float | str:
    """Perform exact arithmetic. Use this for ANY math calculation instead of computing it yourself."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero."
        return a / b
    return f"Error: Unknown operation '{operation}'."


# 4. File Tool
class FileReaderSchema(BaseModel):
    filepath: str = Field(
        ...,
        description="File name in local directory."
    )

@tool(args_schema=FileReaderSchema)
def read_local_file(filepath: str) -> str:
    """Read the contents of a local text or markdown file. Use this when the user asks to read, open, or inspect a file by name."""
    # Prevent directory traversal
    base_dir = os.getcwd()
    safe_path = os.path.abspath(os.path.join(base_dir, filepath))
    
    if not safe_path.startswith(base_dir):
        return f"Error: Unauthorized access. Cannot read files outside of {base_dir}"
        
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found in the current directory."
    except Exception as e:
        return f"Error reading file: {str(e)}"
