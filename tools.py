import os
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from database import get_user_by_id, get_all_users

class WebSearchSchema(BaseModel):
    query: str = Field(..., description="The search query.")

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

@tool(args_schema=WebSearchSchema)
def web_search_tool(query: str) -> str:
    """Use this tool to search the live internet for information you don't already know."""
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
        description="User UUID string. Leave empty or use 'all' to get all users."
    )

@tool(args_schema=GetUserSchema)
async def fetch_user_information(user_id: str = "") -> list | dict:
    """Fetch user and inventory. Leave user_id empty to fetch ALL users."""
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
    """Compute exact math logic."""
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
    """Read local text files securely."""
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
