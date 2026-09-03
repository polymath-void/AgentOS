import socket
from fastapi import FastAPI
import sqlite3
import uvicorn
import os

app = FastAPI()

# Database connection stays open in RAM
db_path = '/data/data/com.termux/files/home/.polymath_agent/memory.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
db = sqlite3.connect(db_path, check_same_thread=False)

@app.get("/search")
def search_context(query: str):
    cursor = db.execute("SELECT content FROM facts WHERE content LIKE ? LIMIT 5", (f"%{query}%",))
    results = [row[0] for row in cursor.fetchall()]
    return {"status": "success", "data": results}

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    port = 8080
    try:
        # Try to bind to 8080
        uvicorn.run(app, host="127.0.0.1", port=port)
    except Exception:
        # If 8080 fails, find a free one
        port = get_free_port()
        print(f"8080 busy, running on {port}")
        uvicorn.run(app, host="127.0.0.1", port=port)
