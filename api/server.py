"""
Nova API Server
================
Connects the React frontend to Nova backend.
Run with: uvicorn api.server:app --reload --port 8000
"""

import datetime
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.nova import Nova
from agents.alarm_agent.alarm_agent import active_alarms, _lock



def start_whatsapp_bot():
    """Start WhatsApp bot in background thread so it shares the same process as Nova."""
    try:
        from agents.whatsapp_agent.whatsapp_agent import start_whatsapp_agent
        t = threading.Thread(target=start_whatsapp_agent, daemon=True)
        t.start()
        print("[Nova] WhatsApp bot started in background!")
    except Exception as e:
        print(f"[Nova] WhatsApp bot failed to start: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_whatsapp_bot()
    threading.Thread(target=goal_reminder_loop, daemon=True).start()
    print('[Nova] Goal reminder started!')
    yield
    # Shutdown (nothing needed)


app = FastAPI(title="Nova API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



nova = Nova()


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agent: str


@app.get("/")
def root():
    return {"status": "Nova API is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_input = request.message.strip()
    if not user_input:
        return ChatResponse(response="Please say something!", agent="Nova")

    try:
        agent = nova.router.route(user_input)
        agent_name = type(agent).__name__ if agent else "Nova"
        response = nova.process(user_input)
        return ChatResponse(response=response, agent=agent_name)

    except Exception as e:
        return ChatResponse(
            response=f"Sorry, something went wrong: {str(e)}",
            agent="Nova"
        )


@app.get("/alarms")
def get_alarms():
    """Return all alarms so frontend can display them."""
    return {"alarms": active_alarms}


@app.post("/alarms/{alarm_id}/snooze")
def snooze_alarm(alarm_id: str, minutes: int = 5):
    """Snooze a ringing alarm by X minutes (default 5)."""
    with _lock:
        entry = next((a for a in active_alarms if a["id"] == alarm_id), None)
        if not entry:
            raise HTTPException(status_code=404, detail="Alarm not found")

        snooze_until = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        entry["status"] = "snoozed"
        entry["snoozed_until"] = snooze_until.isoformat()

        from agents.alarm_agent.alarm_agent import AlarmAgent
        agent = AlarmAgent()
        thread = threading.Thread(
            target=agent._background_alarm,
            args=(snooze_until, entry["label"], alarm_id),
            daemon=True
        )
        thread.start()

    return {"status": "snoozed", "until": snooze_until.strftime("%H:%M")}


@app.post("/alarms/{alarm_id}/dismiss")
def dismiss_alarm(alarm_id: str):
    """Dismiss an alarm."""
    with _lock:
        entry = next((a for a in active_alarms if a["id"] == alarm_id), None)
        if not entry:
            raise HTTPException(status_code=404, detail="Alarm not found")
        entry["status"] = "done"

    return {"status": "dismissed"}


@app.get("/agents")
def get_agents():
    capabilities = nova.router.list_capabilities()
    return {"agents": capabilities}


@app.get("/history")
def get_history():
    messages = nova.memory.get_recent(limit=20)
    return {"history": messages}


@app.delete("/history")
def clear_history():
    nova.memory.clear_all()
    return {"status": "History cleared!"}


# ── Goals API ────────────────────────────────────────────────────────────────
from pymongo import MongoClient as _MC
from datetime import date as _date
from config.settings import MONGO_URI as _MURI, DB_NAME as _DBN

_gclient = _MC(_MURI)
_gdb = _gclient[_DBN]
_goals_col = _gdb["goals"]


def _today():
    return _date.today().strftime("%Y-%m-%d")


class GoalIn(BaseModel):
    name: str
    target: int

class GoalUpdate(BaseModel):
    name: str
    done: int


@app.post("/goals")
def create_goals(goals: list[GoalIn]):
    for g in goals:
        _goals_col.update_one(
            {"goal": g.name, "date": _today()},
            {"$setOnInsert": {"goal": g.name, "target": g.target, "done": 0, "date": _today()}},
            upsert=True
        )
    return {"status": "Goals created!"}


@app.get("/goals")
def get_goals():
    goals = list(_goals_col.find({"date": _today()}, {"_id": 0}))
    return {"goals": goals}


@app.post("/goals/update")
def update_goals(updates: list[GoalUpdate]):
    for u in updates:
        _goals_col.update_one(
            {"goal": u.name, "date": _today()},
            {"$inc": {"done": u.done}}
        )
    return {"status": "Updated!"}


@app.get("/goals/reminder")
def get_reminder():
    goals = list(_goals_col.find({"date": _today()}, {"_id": 0}))
    if not goals:
        return {"reminder": "No goals set for today!"}
    lines = []
    for g in goals:
        remaining = max(0, g["target"] - g.get("done", 0))
        if remaining > 0:
            lines.append(f"{g['goal']} -> {remaining} remaining")
    if not lines:
        return {"reminder": "All goals completed for today!"}
    return {"reminder": "Reminder: " + ", ".join(lines)}


# ── Goal Reminder Background Thread ──────────────────────────────────────────
import time as _time

def goal_reminder_loop():
    """Runs every 60 min, prints reminder if goals incomplete."""
    while True:
        try:
            _time.sleep(3600)  # wait 1 hour
            goals = list(_goals_col.find({"date": _today()}, {"_id": 0}))
            pending = [g for g in goals if g.get("done", 0) < g.get("target", 1)]
            if pending:
                print("\n[Goal Reminder]")
                for g in pending:
                    remaining = g["target"] - g.get("done", 0)
                    print(f"  {g['goal']}: {remaining} remaining")
        except Exception as e:
            print(f"Goal reminder error: {e}")
