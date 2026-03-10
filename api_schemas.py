from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="User text input."
    )
    session_id: str | None = Field(
        default=None,
        description="The unique UUID of the chat session. If not provided, a new session is created."
    )
