from pydantic import BaseModel, Field
from langchain_core.tools import tool

from database import get_user_by_id


# Define the input schema for the database lookup tool
class GetUserSchema(BaseModel):
    user_id: str = Field(
        ...,
        description="The unique UUID string of the User to look up in the database."
    )


# Register the function as a LangChain tool with strict input validation
@tool(args_schema=GetUserSchema)
async def fetch_user_information(user_id: str) -> dict:
    """Fetches user profile details and inventory from the database."""
    
    # Execute the asynchronous query against PostgreSQL
    user_record = await get_user_by_id(user_id)
    
    # Return a serialized dictionary if found, otherwise return an error dictionary
    if user_record:
        return user_record.model_dump() 
    else:
        return {"error": f"No user found with ID: {user_id}"}


# Define the input schema for the arithmetic calculator tool
class CalculatorSchema(BaseModel):
    a: float = Field(..., description="The first numerical value.")
    b: float = Field(..., description="The second numerical value.")
    operation: str = Field(
        ..., 
        description="The mathematical operation to perform. MUST be one of: 'add', 'subtract', 'multiply', 'divide'"
    )


# Register the calculator function to prevent LLM hallucination on math
@tool(args_schema=CalculatorSchema)
def simple_calculator(a: float, b: float, operation: str) -> float | str:
    """Performs exact mathematical calculations routing around LLM math limitations."""
    
    # Route the execution based on the requested operation
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        # Prevent division by zero runtime errors
        if b == 0:
            return "Error: Cannot divide by zero."
        return a / b
    else:
        return f"Error: Unknown operation '{operation}'."
