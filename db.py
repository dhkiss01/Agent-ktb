"""Small SQLite persistence layer for sessions and messages."""
from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "sessions.db"

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, title TEXT, created_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS messages (session_id TEXT, idx INTEGER, message TEXT)")
    return conn

def create_session(title: str = "새 대화", initial_messages: list[dict] | None = None) -> str:
    session_id = str(uuid.uuid4())
    conn = _connect()
    conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", (session_id, title, datetime.now().isoformat()))
    conn.commit(); conn.close()
    replace_messages(session_id, initial_messages or [])
    return session_id

def list_sessions() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT id, title, created_at FROM sessions ORDER BY created_at DESC").fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]

def load_messages(session_id: str) -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT message FROM messages WHERE session_id = ? ORDER BY idx", (session_id,)).fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]

def replace_messages(session_id: str, messages: list[dict]) -> None:
    conn = _connect()
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.executemany("INSERT INTO messages VALUES (?, ?, ?)", [(session_id, i, json.dumps(m, ensure_ascii=False)) for i, m in enumerate(messages)])
    conn.commit(); conn.close()

def update_title(session_id: str, title: str) -> None:
    conn = _connect()
    conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
    conn.commit(); conn.close()
