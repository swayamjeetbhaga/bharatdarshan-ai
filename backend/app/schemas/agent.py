from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    place_name: str | None = None
    district: str | None = None
    attraction_id: int | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
