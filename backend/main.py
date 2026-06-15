import datetime
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Set
import json
import os
import httpx

import models
import schemas
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Remembrance Notes API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development, Next.js can connect directly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/notes", response_model=List[schemas.NoteResponse])
def get_notes(
    category: Optional[str] = None, 
    due_only: Optional[bool] = False, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Note)
    if category:
        query = query.filter(models.Note.category == category)
    
    if due_only:
        now = datetime.datetime.utcnow()
        query = query.filter(models.Note.next_review <= now)
        
    # Order by updated_at descending
    return query.order_by(models.Note.updated_at.desc()).all()

@app.post("/api/notes", response_model=schemas.NoteResponse)
def create_note(note_in: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = models.Note(
        title=note_in.title,
        content=note_in.content,
        category=note_in.category,
        font_style=note_in.font_style,
        next_review=datetime.datetime.utcnow()
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/api/notes/{note_id}", response_model=schemas.NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/api/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(note_id: int, note_in: schemas.NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    
    db.commit()
    db.refresh(note)
    return note

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"status": "success", "message": f"Note {note_id} deleted"}

@app.post("/api/notes/{note_id}/review", response_model=schemas.NoteResponse)
def review_note(note_id: int, review: schemas.ReviewRequest, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    q = review.quality
    if q < 0 or q > 5:
        raise HTTPException(status_code=400, detail="Quality score must be between 0 and 5")
    
    # SM-2 Algorithm implementation
    if q >= 3:
        if note.repetitions == 0:
            note.review_interval = 1
        elif note.repetitions == 1:
            note.review_interval = 6
        else:
            note.review_interval = round(note.review_interval * note.ease_factor)
        note.repetitions += 1
    else:
        note.repetitions = 0
        note.review_interval = 1
        
    note.ease_factor = note.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if note.ease_factor < 1.3:
        note.ease_factor = 1.3
        
    note.next_review = datetime.datetime.utcnow() + datetime.timedelta(days=note.review_interval)
    db.commit()
    db.refresh(note)
    return note

# WebSocket Connection Manager for collaborative canvas rooms
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: str, sender: WebSocket):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != sender:
                    try:
                        await connection.send_text(message)
                    except Exception:
                        pass

manager = ConnectionManager()

# Canvas endpoints
@app.get("/api/canvas", response_model=schemas.CanvasStateResponse)
def get_canvas_state(room: Optional[str] = "default", db: Session = Depends(get_db)):
    canvas = db.query(models.CanvasState).filter(models.CanvasState.room_id == room).first()
    if not canvas:
        # Create canvas state for this room if it doesn't exist
        canvas = models.CanvasState(name=room, room_id=room, data='{"image": "", "stickies": []}')
        db.add(canvas)
        db.commit()
        db.refresh(canvas)
    return canvas

@app.post("/api/canvas", response_model=schemas.CanvasStateResponse)
def save_canvas_state(
    canvas_in: schemas.CanvasStateUpdate, 
    room: Optional[str] = "default", 
    db: Session = Depends(get_db)
):
    canvas = db.query(models.CanvasState).filter(models.CanvasState.room_id == room).first()
    if not canvas:
        canvas = models.CanvasState(name=room, room_id=room, data=canvas_in.data)
        db.add(canvas)
    else:
        canvas.data = canvas_in.data
    db.commit()
    db.refresh(canvas)
    return canvas

@app.websocket("/api/canvas/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            # Receive text data (broadcast drawing paths/cursors/stickies actions)
            data = await websocket.receive_text()
            await manager.broadcast(data, room_id, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
    except Exception:
        manager.disconnect(websocket, room_id)


# Bookshelf and Paginated Pages Endpoints
@app.get("/api/books", response_model=List[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).order_by(models.Book.name).all()

@app.post("/api/books", response_model=schemas.BookResponse)
def create_book(book_in: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.name == book_in.name).first()
    if db_book:
        return db_book
    
    new_book = models.Book(name=book_in.name)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    # Auto-generate page 1 as default
    first_page = models.Page(book_id=new_book.id, page_number=1, title="Page 1", content="")
    db.add(first_page)
    db.commit()
    
    return new_book

@app.delete("/api/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"status": "success", "message": f"Book {book_id} deleted"}

@app.get("/api/books/{book_id}/pages", response_model=List[schemas.PageResponse])
def get_book_pages(book_id: int, db: Session = Depends(get_db)):
    return db.query(models.Page).filter(models.Page.book_id == book_id).order_by(models.Page.page_number).all()

@app.get("/api/books/{book_id}/pages/{page_num}", response_model=schemas.PageResponse)
def get_book_page(book_id: int, page_num: int, db: Session = Depends(get_db)):
    page = db.query(models.Page).filter(
        models.Page.book_id == book_id, 
        models.Page.page_number == page_num
    ).first()
    if not page:
        page = models.Page(
            book_id=book_id, 
            page_number=page_num, 
            title=f"Page {page_num}", 
            content="",
            next_review=datetime.datetime.utcnow()
        )
        db.add(page)
        db.commit()
        db.refresh(page)
    return page

@app.post("/api/books/{book_id}/pages", response_model=schemas.PageResponse)
def save_book_page(book_id: int, page_in: schemas.PageCreate, db: Session = Depends(get_db)):
    page = db.query(models.Page).filter(
        models.Page.book_id == book_id, 
        models.Page.page_number == page_in.page_number
    ).first()
    
    if not page:
        page = models.Page(
            book_id=book_id,
            page_number=page_in.page_number,
            title=page_in.title,
            content=page_in.content,
            font_style=page_in.font_style,
            next_review=datetime.datetime.utcnow()
        )
        db.add(page)
    else:
        page.title = page_in.title
        page.content = page_in.content
        page.font_style = page_in.font_style
    
    db.commit()
    db.refresh(page)
    return page

@app.get("/api/pages/due", response_model=List[schemas.PageResponse])
def get_due_pages(db: Session = Depends(get_db)):
    now = datetime.datetime.utcnow()
    return db.query(models.Page).filter(models.Page.next_review <= now).all()

@app.post("/api/books/{book_id}/pages/{page_num}/review", response_model=schemas.PageResponse)
def review_book_page(book_id: int, page_num: int, review: schemas.ReviewRequest, db: Session = Depends(get_db)):
    page = db.query(models.Page).filter(models.Page.book_id == book_id, models.Page.page_number == page_num).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    q = review.quality
    if q < 0 or q > 5:
        raise HTTPException(status_code=400, detail="Quality score must be between 0 and 5")
    
    # SM-2 Algorithm implementation
    if q >= 3:
        if page.repetitions == 0:
            page.review_interval = 1
        elif page.repetitions == 1:
            page.review_interval = 6
        else:
            page.review_interval = round(page.review_interval * page.ease_factor)
        page.repetitions += 1
    else:
        page.repetitions = 0
        page.review_interval = 1
        
    page.ease_factor = page.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if page.ease_factor < 1.3:
        page.ease_factor = 1.3
        
    page.next_review = datetime.datetime.utcnow() + datetime.timedelta(days=page.review_interval)
    db.commit()
    db.refresh(page)
    return page


@app.post("/api/books/{book_id}/chat")
async def chat_book(book_id: int, chat_in: schemas.ChatRequest, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    pages = db.query(models.Page).filter(models.Page.book_id == book_id).order_by(models.Page.page_number).all()
    
    # 1. Compile pages context
    context_text = ""
    for p in pages:
        context_text += f"\n--- Page {p.page_number}: {p.title} ---\n{p.content or 'Empty content...'}\n"
        
    # 2. Get Groq API Key
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_api_key:
        from dotenv import load_dotenv
        load_dotenv()
        groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured on the server")
        
    # 3. Build system instruction
    system_prompt = (
        f"You are the AI Revision Companion for the study book titled '{book.name}'.\n"
        "Your mission is to help the user revise and study the notes they have written in this book.\n"
        "Quiz them, ask them active recall questions, clarify their doubts, or summarize page contents.\n"
        "Adopt a helpful, encouraging, and retro-intelligent persona. Be concise but deep in your explanations.\n\n"
        "Here is the complete, current content of the book's pages:\n"
        "=========================================\n"
        f"{context_text}\n"
        "=========================================\n\n"
        "Ensure all your answers are directly grounded in the notes above. If the user asks about something "
        "not mentioned in the notes, answer it but connect it back to their notes!"
    )
    
    # 4. Construct messages payload
    groq_messages = [{"role": "system", "content": system_prompt}]
    for m in chat_in.messages:
        groq_messages.append({"role": m.role, "content": m.content})
        
    # 5. Send HTTP request to Groq API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": groq_messages,
                    "temperature": 0.7,
                    "max_tokens": 1024
                },
                timeout=30.0
            )
            if response.status_code != 200:
                error_detail = response.text
                print(f"Groq API Error: {error_detail}")
                raise HTTPException(status_code=response.status_code, detail=f"Groq API responded with error: {error_detail}")
                
            res_json = response.json()
            reply = res_json["choices"][0]["message"]["content"]
            return {"role": "assistant", "content": reply}
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Request to Groq API failed: {exc}")


