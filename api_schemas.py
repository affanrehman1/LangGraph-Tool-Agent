from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="The natural language message sent by the user to the agent."
    )
