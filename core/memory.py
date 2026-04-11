"""
MemoryManager - Clean abstraction for all conversation memory.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rules:
  - Nova and agents NEVER call the database directly.
  - All memory reads/writes go through this class only.
  - Session buffer = fast in-memory cache for current session.
  - DB = persistent storage across sessions.
"""

from typing import List, Dict
from database.db import Database


class MemoryManager:
    def __init__(self):
        self.db = Database()
        self._session: List[Dict] = []  # In-memory buffer for current session

    # ──────────────────────────────────────────────
    # Write
    # ──────────────────────────────────────────────

    def add(self, role: str, content: str) -> None:
        """
        Add a message to both the session buffer and the database.
        role: "user" or "assistant"
        """
        message = {"role": role, "content": content}
        self._session.append(message)
        self.db.save_message(role, content)

    def load_into_session(self, messages: List[Dict]) -> None:
        """
        Pre-load messages (from DB history) into the session buffer.
        Called once on startup so Nova has context from past conversations.
        Does NOT re-save them to DB.
        """
        self._session = list(messages)

    # ──────────────────────────────────────────────
    # Read
    # ──────────────────────────────────────────────

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get the last N messages from the current session buffer."""
        return self._session[-limit:]

    def get_history(self, limit: int = 50) -> List[Dict]:
        """Fetch past messages from the database (cross-session)."""
        return self.db.get_messages(limit=limit)

    def search(self, keyword: str) -> List[Dict]:
        """Search past conversations in the DB by keyword."""
        return self.db.search_messages(keyword)

    # ──────────────────────────────────────────────
    # Clear
    # ──────────────────────────────────────────────

    def clear_session(self) -> None:
        """Clear only the in-memory session buffer. DB records are kept."""
        self._session = []

    def clear_all(self) -> None:
        """Wipe everything: session buffer + all database records."""
        self._session = []
        self.db.clear_all()