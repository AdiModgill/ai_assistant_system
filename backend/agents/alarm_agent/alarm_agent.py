"""
Alarm Agent
===========
Sets alarms in background threads so Nova stays responsive.
Supports snooze via API. Frontend polls /alarms for status.
"""

import datetime
import time
import threading
import platform
import json
import ollama

# Shared alarm list — frontend polls GET /alarms
active_alarms = []
_lock = threading.Lock()


class AlarmAgent:
    name = "AlarmAgent"

    def handle(self, user_input: str) -> str:
        result = self._extract_time(user_input)

        if "error" in result:
            return "I couldn't find a time in that. Try: 'set alarm for 5 minutes' or 'remind me at 7:30 AM'"

        hour   = result.get("hour")
        minute = result.get("minute", 0)
        label  = result.get("label", "Alarm")

        if hour is None or not (0 <= hour <= 23) or not (0 <= minute <= 59):
            return "That doesn't look like a valid time. Please try again."

        now = datetime.datetime.now()
        alarm_time = datetime.datetime(now.year, now.month, now.day, hour, minute)
        if alarm_time <= now:
            alarm_time += datetime.timedelta(days=1)

        alarm_id = str(int(time.time()))
        alarm_entry = {
            "id": alarm_id,
            "label": label,
            "time": f"{hour:02d}:{minute:02d}",
            "status": "active",
            "snoozed_until": None
        }

        with _lock:
            active_alarms.append(alarm_entry)

        thread = threading.Thread(
            target=self._background_alarm,
            args=(alarm_time, label, alarm_id),
            daemon=True
        )
        thread.start()

        diff = alarm_time - now
        total_seconds = int(diff.total_seconds())
        minutes_away = total_seconds // 60
        seconds_away = total_seconds % 60

        if minutes_away == 0:
            time_msg = f"in {seconds_away} seconds"
        elif minutes_away < 60:
            time_msg = f"in {minutes_away} minute{'s' if minutes_away != 1 else ''}"
        else:
            time_msg = f"at {hour:02d}:{minute:02d}"

        return f"⏰ Got it! I'll remind you about '{label}' {time_msg}. Feel free to keep chatting!"

    def _extract_time(self, user_input: str) -> dict:
        now = datetime.datetime.now()
        system_prompt = f"""Extract alarm time from the user message.
Current time is {now.strftime('%H:%M')}.
If user says "in X minutes", add X minutes to current time and give the result.
Reply ONLY with JSON, nothing else:
{{"hour": 7, "minute": 30, "label": "wake up"}}
Use 24-hour format. If no time found: {{"error": "no time found"}}"""

        try:
            response = ollama.chat(
                model="llama3:latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            llm_text = response["message"]["content"]
            start = llm_text.find("{")
            end = llm_text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(llm_text[start:end])
            return {"error": "Could not parse response"}
        except Exception as e:
            return {"error": str(e)}

    def _background_alarm(self, alarm_time: datetime.datetime, label: str, alarm_id: str):
        print(f"[AlarmAgent] Alarm set for {alarm_time.strftime('%H:%M')} — {label}")

        while True:
            now = datetime.datetime.now()

            with _lock:
                entry = next((a for a in active_alarms if a["id"] == alarm_id), None)

            if not entry or entry["status"] == "done":
                return

            # Handle snoozed state
            if entry["status"] == "snoozed" and entry["snoozed_until"]:
                snooze_time = datetime.datetime.fromisoformat(entry["snoozed_until"])
                if now < snooze_time:
                    time.sleep(1)
                    continue
                else:
                    with _lock:
                        entry["status"] = "ringing"
                    self._play_sound()
                    return

            # Ring when time reached
            if now >= alarm_time and entry["status"] == "active":
                with _lock:
                    entry["status"] = "ringing"
                print(f"\n[AlarmAgent] RINGING — {label}")
                self._play_sound()
                return

            time.sleep(1)

    @staticmethod
    def _play_sound():
        end_time = time.time() + 10
        if platform.system() == "Windows":
            try:
                import winsound
                while time.time() < end_time:
                    winsound.Beep(1000, 400)
                    time.sleep(0.1)
                    winsound.Beep(800, 400)
                    time.sleep(0.1)
            except Exception:
                while time.time() < end_time:
                    print("\a", end="", flush=True)
                    time.sleep(0.3)
        else:
            while time.time() < end_time:
                print("\a", end="", flush=True)
                time.sleep(0.3)