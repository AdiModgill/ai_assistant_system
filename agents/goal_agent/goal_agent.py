# agents/goal_agent/goal_agent.py
"""
GoalAgent - Tracks daily goals via chat.
Commands:
  "goal: study 2, gym 1"     -> set goals
  "done: 1 study, 1 gym"     -> update progress
  "progress"                 -> show today status
"""

import re
from datetime import date
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME

_mongo = MongoClient(MONGO_URI)
_db = _mongo[DB_NAME]
goals_col = _db["goals"]


def _today():
    return date.today().strftime("%Y-%m-%d")


class GoalAgent:
    name = "GoalAgent"

    def handle(self, user_input: str, memory=None) -> str:
        text = user_input.lower().strip()

        if "progress" in text:
            return self._show_progress()

        if text.startswith("done:") or text.startswith("done "):
            return self._update_goals(user_input)

        if text.startswith("goal:") or text.startswith("goal "):
            return self._set_goals(user_input)

        return (
            "Goal commands:\n"
            "  goal: study 2, gym 1  -> set goals\n"
            "  done: 1 study         -> update progress\n"
            "  progress              -> show today status"
        )

    def _set_goals(self, text: str) -> str:
        # parse "goal: study 2, gym 1"
        raw = re.sub(r"(?i)^goal[:\s]+", "", text).strip()
        items = [i.strip() for i in raw.split(",") if i.strip()]

        added = []
        for item in items:
            parts = item.rsplit(" ", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                try:
                    target = int(parts[1])
                except ValueError:
                    continue
            else:
                name = parts[0].strip()
                target = 1

            goals_col.update_one(
                {"goal": name, "date": _today()},
                {"$setOnInsert": {"goal": name, "target": target, "done": 0, "date": _today()}},
                upsert=True
            )
            added.append(f"{name} x{target}")

        if not added:
            return "Could not parse goals. Try: goal: study 2, gym 1"

        return f"Goals set for today: {', '.join(added)}"

    def _update_goals(self, text: str) -> str:
        # parse "done: 1 study, 2 gym"
        raw = re.sub(r"(?i)^done[:\s]+", "", text).strip()
        items = [i.strip() for i in raw.split(",") if i.strip()]

        updated = []
        for item in items:
            parts = item.strip().split(" ", 1)
            if len(parts) == 2:
                try:
                    count = int(parts[0])
                    name = parts[1].strip()
                except ValueError:
                    try:
                        count = int(parts[1])
                        name = parts[0].strip()
                    except ValueError:
                        continue
            else:
                continue

            result = goals_col.update_one(
                {"goal": name, "date": _today()},
                {"$inc": {"done": count}}
            )
            if result.matched_count:
                updated.append(f"{name} +{count}")

        if not updated:
            return "No matching goals found for today. Set goals first with: goal: study 2"

        return f"Updated: {', '.join(updated)}\n" + self._show_progress()

    def _show_progress(self) -> str:
        goals = list(goals_col.find({"date": _today()}, {"_id": 0}))
        if not goals:
            return "No goals set for today. Try: goal: study 2, gym 1"

        lines = ["Today's Goals:"]
        for g in goals:
            done = g.get("done", 0)
            target = g.get("target", 1)
            remaining = max(0, target - done)
            status = "Done!" if remaining == 0 else f"Remaining: {remaining}"
            lines.append(f"  {g['goal']}: {done}/{target} ({status})")

        return "\n".join(lines)
