# clipboard_manager_terminal.py
import sqlite3
import pyperclip
import time
import threading
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

console = Console()

# ── Database Setup ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("clipboard_manager.db")
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

def get_connection():
    return sqlite3.connect("clipboard_manager.db")

# ── Core Functions ───────────────────────────────────────────────
def save_clip(content, category="general"):
    """Save clipboard content to database"""
    if not content or not content.strip():
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Avoid duplicates - check last entry
    cursor.execute(
        "SELECT content FROM clipboard_history ORDER BY id DESC LIMIT 1"
    )
    last = cursor.fetchone()
    
    if last and last[0] == content:
        conn.close()
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO clipboard_history (content, timestamp, category) VALUES (?, ?, ?)",
        (content, timestamp, category)
    )
    conn.commit()
    conn.close()
    console.print(f"[green]✓ Saved:[/green] {content[:50]}...")

def get_history(limit=20, search=None, category=None):
    """Get clipboard history"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, content, timestamp, category, pinned FROM clipboard_history WHERE 1=1"
    params = []
    
    if search:
        query += " AND content LIKE ?"
        params.append(f"%{search}%")
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY pinned DESC, id DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_clip(clip_id):
    """Delete a clipboard entry"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()

def pin_clip(clip_id):
    """Toggle pin on a clipboard entry"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clipboard_history SET pinned = CASE WHEN pinned = 1 THEN 0 ELSE 1 END WHERE id = ?",
        (clip_id,)
    )
    conn.commit()
    conn.close()

def copy_to_clipboard(clip_id):
    """Copy a saved entry back to clipboard"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM clipboard_history WHERE id = ?", (clip_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        pyperclip.copy(row[0])
        console.print(f"[cyan]📋 Copied to clipboard:[/cyan] {row[0][:60]}")
    else:
        console.print("[red]✗ Entry not found[/red]")

def clear_all():
    """Clear all clipboard history"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clipboard_history WHERE pinned = 0")
    conn.commit()
    conn.close()

# ── Display ──────────────────────────────────────────────────────
def display_history(rows):
    """Display history in a rich table"""
    if not rows:
        console.print("[yellow]No clipboard history found[/yellow]")
        return
    
    table = Table(
        title="📋 Clipboard History",
        show_header=True,
        header_style="bold cyan",
        border_style="blue"
    )
    
    table.add_column("ID", style="dim", width=6)
    table.add_column("Content", width=50)
    table.add_column("Category", width=12)
    table.add_column("Timestamp", width=20)
    table.add_column("Pin", width=5)
    
    for row in rows:
        clip_id, content, timestamp, category, pinned = row
        pin_icon = "📌" if pinned else ""
        # Truncate long content
        display_content = content[:47] + "..." if len(content) > 47 else content
        # Color code by category
        cat_colors = {
            "general": "white",
            "code": "green",
            "url": "blue",
            "password": "red",
            "note": "yellow"
        }
        cat_style = cat_colors.get(category, "white")
        
        table.add_row(
            str(clip_id),
            display_content,
            f"[{cat_style}]{category}[/{cat_style}]",
            timestamp,
            pin_icon
        )
    
    console.print(table)

def show_menu():
    """Display main menu"""
    console.print(Panel.fit(
        "[bold cyan]📋 CLIPBOARD MANAGER[/bold cyan]\n"
        "[white]──────────────────────[/white]\n"
        "[green]1[/green] → View History\n"
        "[green]2[/green] → Search Clips\n"
        "[green]3[/green] → Copy Clip to Clipboard\n"
        "[green]4[/green] → Save Manual Clip\n"
        "[green]5[/green] → Delete Clip\n"
        "[green]6[/green] → Pin/Unpin Clip\n"
        "[green]7[/green] → Filter by Category\n"
        "[green]8[/green] → Clear All (unpinned)\n"
        "[green]9[/green] → Start Auto-Monitor\n"
        "[red]0[/red] → Exit",
        border_style="cyan"
    ))

# ── Auto Monitor ─────────────────────────────────────────────────
monitoring = False

def auto_monitor():
    """Background thread to monitor clipboard"""
    global monitoring
    console.print("[yellow]👁  Monitoring clipboard... Press CTRL+C to stop[/yellow]")
    
    last_content = ""
    try:
        while monitoring:
            try:
                current = pyperclip.paste()
                if current != last_content and current.strip():
                    last_content = current
                    save_clip(current)
            except Exception:
                pass
            time.sleep(1)
    except KeyboardInterrupt:
        monitoring = False
        console.print("[red]⏹ Monitoring stopped[/red]")

# ── Main Loop ────────────────────────────────────────────────────
def main():
    global monitoring
    
    init_db()
    console.print("[bold green]✓ Clipboard Manager Started[/bold green]")
    
    while True:
        show_menu()
        choice = Prompt.ask("\n[bold]Enter choice[/bold]")
        
        # ── View History ──
        if choice == "1":
            limit = Prompt.ask("How many entries?", default="20")
            rows = get_history(limit=int(limit))
            display_history(rows)
        
        # ── Search ──
        elif choice == "2":
            query = Prompt.ask("Search term")
            rows = get_history(search=query)
            display_history(rows)
        
        # ── Copy ──
        elif choice == "3":
            rows = get_history()
            display_history(rows)
            clip_id = Prompt.ask("Enter ID to copy")
            copy_to_clipboard(int(clip_id))
        
        # ── Manual Save ──
        elif choice == "4":
            content = Prompt.ask("Enter text to save")
            cats = ["general", "code", "url", "password", "note"]
            console.print(f"Categories: {', '.join(cats)}")
            category = Prompt.ask("Category", default="general")
            save_clip(content, category)
        
        # ── Delete ──
        elif choice == "5":
            rows = get_history()
            display_history(rows)
            clip_id = Prompt.ask("Enter ID to delete")
            delete_clip(int(clip_id))
            console.print("[red]✓ Deleted[/red]")
        
        # ── Pin ──
        elif choice == "6":
            rows = get_history()
            display_history(rows)
            clip_id = Prompt.ask("Enter ID to pin/unpin")
            pin_clip(int(clip_id))
            console.print("[yellow]📌 Toggled pin[/yellow]")
        
        # ── Filter Category ──
        elif choice == "7":
            cats = ["general", "code", "url", "password", "note"]
            console.print(f"[cyan]Categories:[/cyan] {', '.join(cats)}")
            category = Prompt.ask("Enter category")
            rows = get_history(category=category)
            display_history(rows)
        
        # ── Clear All ──
        elif choice == "8":
            confirm = Prompt.ask("[red]Clear all unpinned clips? (yes/no)[/red]")
            if confirm.lower() == "yes":
                clear_all()
                console.print("[red]✓ Cleared all unpinned clips[/red]")
        
        # ── Auto Monitor ──
        elif choice == "9":
            monitoring = True
            monitor_thread = threading.Thread(target=auto_monitor, daemon=True)
            monitor_thread.start()
            
            try:
                while monitoring:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                monitoring = False
                console.print("[red]⏹ Monitoring stopped[/red]")
        
        # ── Exit ──
        elif choice == "0":
            monitoring = False
            console.print("[bold red]👋 Goodbye![/bold red]")
            sys.exit(0)
        
        else:
            console.print("[red]Invalid choice[/red]")
        
        console.print("\n" + "─" * 50 + "\n")

if __name__ == "__main__":
    main()
