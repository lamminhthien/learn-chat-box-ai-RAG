from pydantic import BaseModel
from datetime import datetime

class Note(BaseModel):
    id: int
    text: str
    created_at: datetime

class Event(BaseModel):
    id: int
    title: str
    datetime: datetime
    created_at: datetime 