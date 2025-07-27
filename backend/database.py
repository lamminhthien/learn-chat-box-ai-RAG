import psycopg2
from models import Note, Event
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Function to create tables if they do not exist
# Call this function once at startup or manually to ensure tables are present
# You can also add this to your app startup logic if desired

def init_db_tables():
    conn = get_pg_conn()
    cur = conn.cursor()
    # Create notes table if not exists
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    # Create events table if not exists
    cur.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            datetime TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Hàm tiện ích kết nối PostgreSQL
def get_pg_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT"))
    )

# CRUD Note

def create_note(text: str) -> Note:
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (text, created_at) VALUES (%s, %s) RETURNING id, text, created_at",
        (text, datetime.utcnow())
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return Note(id=row[0], text=row[1], created_at=row[2])

def get_notes() -> List[Note]:
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, text, created_at FROM notes ORDER BY created_at DESC")
    notes = [Note(id=row[0], text=row[1], created_at=row[2]) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return notes

def update_note(note_id: int, text: str) -> Optional[Note]:
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET text = %s WHERE id = %s RETURNING id, text, created_at", (text, note_id))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row:
        return Note(id=row[0], text=row[1], created_at=row[2])
    return None

def delete_note(note_id: int) -> bool:
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return deleted

# CRUD Event

def create_event(title: str, datetime_: str) -> Event:
    dt = datetime.fromisoformat(datetime_)
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (title, datetime, created_at) VALUES (%s, %s, %s) RETURNING id, title, datetime, created_at",
        (title, dt, datetime.utcnow())
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return Event(id=row[0], title=row[1], datetime=row[2], created_at=row[3])

def get_events() -> List[Event]:
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, datetime, created_at FROM events ORDER BY datetime")
    events = [Event(id=row[0], title=row[1], datetime=row[2], created_at=row[3]) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return events

def update_event(event_id: int, title: str, datetime_: str) -> Optional[Event]:
    dt = datetime.fromisoformat(datetime_)
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("UPDATE events SET title = %s, datetime = %s WHERE id = %s RETURNING id, title, datetime, created_at", (title, dt, event_id))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row:
        return Event(id=row[0], title=row[1], datetime=row[2], created_at=row[3])
    return None

def delete_event(event_id: int) -> bool:
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return deleted 

def init_db():
    conn = get_pg_conn()
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()