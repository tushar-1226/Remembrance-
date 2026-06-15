import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="")
    content = Column(Text, default="")
    category = Column(String, default="quick")  # "quick" or "structured"
    font_style = Column(String, default="sans")  # "sans", "serif", or "mono"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Spaced Repetition (SuperMemo-2 Algorithm) fields
    review_interval = Column(Integer, default=0)  # in days
    repetitions = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    next_review = Column(DateTime, default=datetime.datetime.utcnow)

class CanvasState(Base):
    __tablename__ = "canvas_states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="default")
    room_id = Column(String, default="default", index=True)
    data = Column(Text, default='{"paths": [], "stickies": []}')  # JSON blob of canvas data
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    pages = relationship("Page", back_populates="book", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), index=True)
    page_number = Column(Integer, default=1, index=True)
    title = Column(String, default="")
    content = Column(Text, default="")
    font_style = Column(String, default="caveat")  # handwriting font
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Spaced repetition parameters per page
    review_interval = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    next_review = Column(DateTime, default=datetime.datetime.utcnow)

    book = relationship("Book", back_populates="pages")


