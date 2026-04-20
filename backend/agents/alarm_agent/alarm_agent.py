"""
Alarm Agent
===========
Sets alarms in background threads so Nova stays responsive.
Supports snooze via API. Frontend polls /alarms for status.
"""

import os
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

        hour = result.get("hour")
        minute = result.get("minute", 0)
        label = result.get("label", "Alarm")

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

    def _background_alarm(self, alarm_time, label, alarm_id):
        print(f"[AlarmAgent] Alarm set for {alarm_time.strftime('%H:%M')} — {label}")

        while True:
            now = datetime.datetime.now()

            with _lock:
                entry = next((a for a in active_alarms if a["id"] == alarm_id), None)

            if not entry or entry["status"] == "done":
                return

            # Snooze handling
            if entry["status"] == "snoozed" and entry["snoozed_until"]:
                snooze_time = datetime.datetime.fromisoformat(entry["snoozed_until"])

                if now < snooze_time:
                    time.sleep(1)
                    continue
                else:
                    with _lock:
                        entry["status"] = "ringing"

                    self._play_sound(alarm_id)
                    return

            # Ring
            if now >= alarm_time and entry["status"] == "active":
                with _lock:
                    entry["status"] = "ringing"

                print(f"\n[AlarmAgent] RINGING — {label}")
                self._play_sound(alarm_id)
                return

            time.sleep(1)

    @staticmethod
    def _play_sound(alarm_id):
        end_time = time.time() + 30
        system = platform.system()

        def should_stop():
            with _lock:
                entry = next((a for a in active_alarms if a["id"] == alarm_id), None)
            return not entry or entry["status"] in ["done", "snoozed"]

        # WINDOWS
        if system == "Windows":
            try:
                import winsound
                pattern = [
                    (1500, 300), (1200, 200),
                    (1500, 300), (1200, 200),
                    (1800, 400), (1400, 300),
                ]
                i = 0

                while time.time() < end_time:
                    if should_stop():
                        return

                    freq, dur = pattern[i % len(pattern)]
                    winsound.Beep(freq, dur)
                    time.sleep(0.05)
                    i += 1

            except Exception:
                while time.time() < end_time:
                    if should_stop():
                        return
                    print("\a\a\a", end="", flush=True)
                    time.sleep(0.2)

        # MAC
        elif system == "Darwin":
            import subprocess

            sounds = [
                "/System/Library/Sounds/Sosumi.aiff",
                "/System/Library/Sounds/Glass.aiff",
                "/System/Library/Sounds/Ping.aiff",
            ]

            sound = next((s for s in sounds if os.path.exists(s)), None)

            while time.time() < end_time:
                if should_stop():
                    return

                if sound:
                    try:
                        subprocess.run(["afplay", "-v", "5", sound], timeout=2)
                    except:
                        print("\a\a\a", end="", flush=True)
                else:
                    print("\a\a\a", end="", flush=True)

                time.sleep(0.1)

        # LINUX
        else:
            import subprocess

            linux_sounds = [
                "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
                "/usr/share/sounds/freedesktop/stereo/bell.oga",
                "/usr/share/sounds/ubuntu/stereo/bell.ogg",
            ]

            linux_sound = next((s for s in linux_sounds if os.path.exists(s)), None)

            while time.time() < end_time:
                if should_stop():
                    return

                played = False

                if linux_sound:
                    for player in (["paplay", linux_sound], ["aplay", linux_sound]):
                        try:
                            subprocess.run(player, timeout=3)
                            played = True
                            break
                        except:
                            pass

                if not played:
                    try:
                        subprocess.run(["beep", "-f", "1500", "-l", "300", "-r", "3"], timeout=2)
                        played = True
                    except:
                        pass

                if not played:
                    print("\a\a\a", end="", flush=True)

                time.sleep(0.15)