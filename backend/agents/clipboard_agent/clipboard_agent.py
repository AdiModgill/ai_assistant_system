"""
Clipboard Agent (Fixed + Reliable)
=================================
Nova calls: agent.handle(user_input, memory)

Features:
✔ Copy text to clipboard
✔ Always save to DB (even if clipboard fails)
✔ Read clipboard (with DB fallback)
✔ Clipboard history
✔ Restore last saved item
"""

import sqlite3
import pyperclip
from datetime import datetime

DB_PATH = "clipboard_manager.db"


class ClipboardAgent:
    name = "ClipboardAgent"

    def __init__(self):
        self._init_db()

    # ── Nova Entry ─────────────────────────────────────────

    def handle(self, user_input: str, memory=None) -> str:
        text = user_input.lower()

        # READ CLIPBOARD
        if any(w in text for w in ["read", "what's in", "whats in", "show clipboard", "paste"]):
            if "history" in text:
                return self._get_history()
            return self._read_clipboard()

        # HISTORY
        if "history" in text:
            return self._get_history()

        # RESTORE LAST
        if "last" in text or "restore" in text:
            return self._restore_last()

        # COPY
        if any(w in text for w in ["copy", "save", "add to clipboard"]):
            content = self._extract_content(user_input)
            if content:
                return self._copy_to_clipboard(content)
            return "✗ What should I copy?\nTry: copy this to clipboard: Hello World"

        return "I can copy, read clipboard, show history, or restore last item."

    # ── CORE ACTIONS ──────────────────────────────────────

    def _copy_to_clipboard(self, content: str) -> str:
        """Copy + always save to DB"""
        copied = False

        try:
            pyperclip.copy(content)
            check = pyperclip.paste()
            if check == content:
                copied = True
        except Exception:
            copied = False

        # ALWAYS SAVE
        self._save_to_db(content)

        if copied:
            return f"✅ Copied & saved:\n\"{content}\""
        else:
            return f"⚠ Saved but clipboard failed:\n\"{content}\""

    def _read_clipboard(self) -> str:
        """Read clipboard, fallback to DB"""
        try:
            content = pyperclip.paste()
            if content and content.strip():
                return f"📋 Clipboard:\n\n{content}"
        except Exception:
            pass

        # fallback
        return "📋 Clipboard empty. Showing last saved:\n\n" + self._get_last_only()

    def _restore_last(self) -> str:
        """Restore last DB entry to clipboard"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM clipboard_history ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()

            if row:
                try:
                    pyperclip.copy(row[0])
                    return f"📋 Restored to clipboard:\n{row[0]}"
                except:
                    return f"⚠ Found but could not copy:\n{row[0]}"
            return "No saved content."
        except Exception as e:
            return f"✗ Error: {e}"

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
                return "📋 No history."

            output = ["📋 Clipboard History:\n"]
            for i, (cid, content, ts) in enumerate(rows, 1):
                preview = content[:60] + "..." if len(content) > 60 else content
                output.append(f"{i}. [{ts}] {preview}")

            return "\n".join(output)

        except Exception as e:
            return f"✗ Error: {e}"

    def _get_last_only(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM clipboard_history ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else "Nothing saved yet."
        except:
            return "Error reading DB."

    # ── HELPERS ───────────────────────────────────────────

    def _extract_content(self, user_input: str) -> str:
        if ":" in user_input:
            return user_input.split(":", 1)[1].strip()

        commands = [
            "copy this to clipboard", "copy to clipboard",
            "save to clipboard", "add to clipboard",
            "copy this", "copy", "save"
        ]

        lower = user_input.lower()

        for cmd in commands:
            if cmd in lower:
                idx = lower.find(cmd) + len(cmd)
                return user_input[idx:].strip()

        return ""

    def _save_to_db(self, content: str):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO clipboard_history (content, timestamp)
                VALUES (?, ?)
            """, (content, timestamp))

            conn.commit()
            conn.close()
        except Exception:
            pass

    def _init_db(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()
            conn.close()
        except Exception:
            pass