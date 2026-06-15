from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Note Schemas
class NoteBase(BaseModel):
    title: Optional[str] = ""
    content: Optional[str] = ""
    category: Optional[str] = "quick"
    font_style: Optional[str] = "sans"

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    review_interval: Optional[int] = None
    repetitions: Optional[int] = None
    ease_factor: Optional[float] = None
    next_review: Optional[datetime] = None

class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    review_interval: int
    repetitions: int
    ease_factor: float
    next_review: datetime

    class Config:
        from_attributes = True

# Spaced Repetition Review Request Schema
class ReviewRequest(BaseModel):
    quality: int  # 0 to 5 rating

# Canvas Schemas
class CanvasStateBase(BaseModel):
    name: Optional[str] = "default"
    room_id: Optional[str] = "default"
    data: Optional[str] = '{"paths": [], "stickies": []}'

class CanvasStateUpdate(CanvasStateBase):
    pass

class CanvasStateResponse(CanvasStateBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# Page Schemas
class PageBase(BaseModel):
    page_number: int
    title: Optional[str] = ""
    content: Optional[str] = ""
    font_style: Optional[str] = "caveat"

class PageCreate(PageBase):
    pass

class PageUpdate(PageBase):
    title: Optional[str] = None
    content: Optional[str] = None
    font_style: Optional[str] = None
    review_interval: Optional[int] = None
    repetitions: Optional[int] = None
    ease_factor: Optional[float] = None
    next_review: Optional[datetime] = None

class PageResponse(PageBase):
    id: int
    book_id: int
    created_at: datetime
    updated_at: datetime
    review_interval: int
    repetitions: int
    ease_factor: float
    next_review: datetime

    class Config:
        from_attributes = True


# Book Schemas
class BookBase(BaseModel):
    name: str

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessage(BaseModel):
    role: str  # "system", "user", or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]



