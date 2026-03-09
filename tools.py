from pydantic import BaseModel, Field
from langchain_core.tools import tool

from database import get_user_by_id


# Input schema for database lookup tool
class GetUserSchema(BaseModel):
    user_id: str = Field(
        ...,
        description="The unique UUID string of the User to look up in the database."
    )


# Langchain tool for fetching user profile and inventory
@tool(args_schema=GetUserSchema)
async def fetch_user_information(user_id: str) -> dict:
    """Fetches user profile details and inventory from the database."""
    user_record = await get_user_by_id(user_id)
    if user_record:
        return user_record.model_dump() 
    return {"error": f"No user found with ID: {user_id}"}


# Input schema for arithmetic calculator
class CalculatorSchema(BaseModel):
    a: float = Field(..., description="The first numerical value.")
    b: float = Field(..., description="The second numerical value.")
    operation: str = Field(
        ..., 
        description="The mathematical operation to perform. MUST be one of: 'add', 'subtract', 'multiply', 'divide'"
    )


# Langchain calculator tool for deterministic math logic
@tool(args_schema=CalculatorSchema)
def simple_calculator(a: float, b: float, operation: str) -> float | str:
    """Performs exact mathematical calculations routing around LLM math limitations."""
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
