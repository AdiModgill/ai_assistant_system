"""
Clipboard Agent
================
Nova calls: agent.handle(user_input, memory)

What it does:
1. "copy this text to clipboard: Hello World"  -> saves text to clipboard
2. "read my clipboard" / "what's in clipboard" -> returns current clipboard content
3. "show clipboard history"                    -> returns last 10 saved clips
"""

import sqlite3
import pyperclip
from datetime import datetime

try:
    import ollama
except ImportError:
    ollama = None

DB_PATH = "clipboard_manager.db"


class ClipboardAgent:
    name = "ClipboardAgent"

    def __init__(self):
        self._init_db()

    # ── Nova entry point ────────────────────────────────────

    def handle(self, user_input: str, memory=None) -> str:
        text = user_input.lower()

        # read clipboard
        if any(w in text for w in ["read", "what's in", "whats in", "show clipboard", "get clipboard", "paste"]):
            if "history" in text:
                return self._get_history()
            return self._read_clipboard()

        # show history
        if "history" in text:
            return self._get_history()

        # copy text to clipboard
        if any(w in text for w in ["copy", "save to clipboard", "add to clipboard"]):
            # extract the text after ":" or "copy"
            content = self._extract_content(user_input)
            if content:
                return self._copy_to_clipboard(content)
            else:
                return "✗ What should I copy? Try: 'copy this to clipboard: Hello World'"

        return "I can: read clipboard, show clipboard history, or copy text. Try 'read my clipboard'."

    # ── Actions ─────────────────────────────────────────────

    def _read_clipboard(self) -> str:
        try:
            content = pyperclip.paste()
            if not content or not content.strip():
                return "📋 Clipboard is empty."
            return f"📋 Clipboard contains:\n\n{content}"
        except Exception as e:
            return f"✗ Could not read clipboard: {e}"

    def _copy_to_clipboard(self, content: str) -> str:
        try:
            pyperclip.copy(content)
            self._save_to_db(content)
            return f"✅ Copied to clipboard:\n\"{content}\""
        except Exception as e:
            return f"✗ Could not copy to clipboard: {e}"

    def _get_history(self, limit: int = 10) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, timestamp FROM clipboard_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return "📋 No clipboard history found."

            lines = ["📋 Last clipboard entries:\n"]
            for i, (clip_id, content, timestamp) in enumerate(rows, 1):
                preview = content[:60] + "..." if len(content) > 60 else content
                lines.append(f"{i}. [{timestamp}] {preview}")

            return "\n".join(lines)

        except Exception as e:
            return f"✗ Could not fetch history: {e}"

    # ── Helpers ─────────────────────────────────────────────

    def _extract_content(self, user_input: str) -> str:
        """Extract the text to copy — everything after ':' if present."""
        if ":" in user_input:
            return user_input.split(":", 1)[1].strip()

        # try removing command words
        for phrase in ["copy this to clipboard", "copy to clipboard", "save to clipboard",
                       "add to clipboard", "copy this", "copy"]:
            if phrase in user_input.lower():
                idx = user_input.lower().find(phrase) + len(phrase)
                remainder = user_input[idx:].strip()
                if remainder:
                    return remainder

        return ""

    def _save_to_db(self, content: str):
        """Save to clipboard history DB."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    pinned INTEGER DEFAULT 0
                )
            """)
            # avoid duplicate of last entry
            cursor.execute(
                "SELECT content FROM clipboard_history ORDER BY id DESC LIMIT 1"
            )
            last = cursor.fetchone()
            if last and last[0] == content:
                conn.close()
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO clipboard_history (content, timestamp) VALUES (?, ?)",
                (content, timestamp)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _init_db(self):
        """Create DB table if not exists."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    pinned INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass