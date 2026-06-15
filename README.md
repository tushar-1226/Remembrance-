# 📖 Remembrance

Remembrance is an immersive, skeuomorphic study assistant and digital library designed to combine the classic aesthetic of physical notebooks with modern, AI-enhanced learning techniques. 

Explore your books in a custom-designed digital study library, write notes on double-page vintage ledger sheets with realistic typewriter sounds, review auto-generated active recall study cards scheduled using the **SM-2 Spaced Repetition Algorithm**, sketch on an interactive canvas whiteboard, or study alongside a **Groq-powered AI revision companion**.

---

## ✨ Features

### 🚪 Animated Library Entrance Gates
* Grand double-pane entrance doors swing open in 3D perspective to reveal your workspace.
* Session storage caching keeps doors unlocked on page refreshes for fluid navigation.

### 📚 2D Skeuomorphic Library Layout
* **Cabinet Bookshelf Rack**: Contains your digital books. Custom color-coded book spines with drag-and-drop support.
* **Study Table Desk**: Drag a book spine from the shelf and drop it onto the desk to slide open the vintage ledger.
* **Recall Chalkboard**: Real-time listing of due study reviews. Click on any due card to instantly open that book page spread.
* **Whiteboard Wall Frame**: Click on the framed slate to transition the library room into a full interactive canvas drawing board.

### ✍️ Writable Side-by-Side Ledger Book
* **Dual Writable Sheets**: Writable lined-paper surfaces on both the left page (Page $N$) and right page (Page $N+1$).
* **Independent Auto-Saver**: Separate background-saving debounce timers keep both page changes synced with the backend without UI delay.
* **Handwriting Font Styles**: Select between multiple fonts including *Architects Daughter*, *Patrick Hand*, *Caveat*, *Sacramento*, *Courier Typewriter*, and *Georgia*.
* **Typewriter Sounds**: Realistic typewriter click sounds trigger as you type on the pages (can be toggled on/off).
* **3D Page Flip Transitions**: Smooth page turn leaf animations as you step through pages.

### 🧠 Spaced Repetition & Active Recall
* **Auto Card Parsing**: Bullet points written in the format `- Question? Answer` or `* Question? Answer` on either page are parsed automatically into review cards.
* **SM-2 Study Deck**: Rate your recall accuracy from `1` (complete blackout) to `5` (perfect response) to automatically calculate ease factors, repetitions, and next review intervals.

### 🤖 Groq AI Revision Companion
* **Note Reference Sidebar**: Displays a read-only side-by-side preview of your written page spread so you can review notes while chatting.
* **Smart Suggestion Chips**: Auto-quiz your notes, summarize the book, or suggest new active recall cards to write.
* **Custom Chat**: Type custom prompts to converse directly with the LLM.

### 🎨 Whiteboard Canvas
* Adjustable pen stroke size.
* Eraser and clear-canvas capabilities.
* Floating return button to transition back to the library room.

---

## 🛠️ Technology Stack

* **Frontend**: Next.js (TypeScript, Tailwind CSS, Lucide icons)
* **Backend**: FastAPI (Python 3.10+, SQLite database)
* **AI Model API**: Groq API
* **Libraries**: Lucide-React, Uvicorn, SQLAlchemy

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following installed:
* **Node.js** (v18+)
* **Python** (3.10+)

### 2. Setup Configuration
To enable the AI Companion chatbot, set your Groq API key in the backend environment.
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Servers
You can launch both the FastAPI backend and Next.js frontend concurrently using the dev startup script at the root:

```bash
# Make script executable (first time only)
chmod +x start.sh

# Start dev environment
./start.sh
```

This will automatically:
1. Boot up the FastAPI server on [http://localhost:8000](http://localhost:8000).
2. Start the Next.js server on [http://localhost:1947](http://localhost:1947).
3. Attempt to open `http://localhost:1947` in your browser.

Press `Ctrl+C` in the terminal to stop both servers cleanly.
