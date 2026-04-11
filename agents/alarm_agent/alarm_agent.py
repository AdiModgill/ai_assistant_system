import datetime
import time
import platform
import json
import re

try:
    import ollama
except ImportError:
    print("ERROR: Please install ollama")
    print("Run: pip install ollama")
    exit(1)


def play_sound():
    """Play alarm sound for exactly 30 seconds"""
    system = platform.system()
    
    # Calculate end time (30 seconds from now)
    end_time = time.time() + 30
    
    print(" Alarm ringing for 30 seconds...")
    
    if system == "Windows":
        try:
            import winsound
            # Keep beeping until 30 seconds are up
            while time.time() < end_time:
                winsound.Beep(1000, 400)  # 400ms beep
                time.sleep(0.1)  # Short pause
                winsound.Beep(800, 400)   # Different tone
                time.sleep(0.1)
        except:
            # Fallback: terminal beep
            while time.time() < end_time:
                print("\a", end='', flush=True)
                time.sleep(0.3)
    else:
        # Mac/Linux - terminal beep for 30 seconds
        while time.time() < end_time:
            print("\a", end='', flush=True)
            time.sleep(0.3)
    
    print("\n✓ Alarm sound finished (30 seconds completed)")


def ask_llm_for_time(user_input, model_name="llama3:8b"):
    """
    Ask Llama 3 to extract time from user's instruction
    """
    system_prompt = """You are a time extraction assistant. Extract the alarm time from the user's message.
Respond ONLY with a JSON object in this EXACT format, nothing else:
{"hour": 7, "minute": 30, "label": "wake up"}

Examples:
- "set alarm 7:30 AM" -> {"hour": 7, "minute": 30, "label": "alarm"}
- "wake me at 6 PM" -> {"hour": 18, "minute": 0, "label": "wake up"}
- "remind me at 14:45 to take medicine" -> {"hour": 14, "minute": 45, "label": "take medicine"}
- "alarm 9:15" -> {"hour": 9, "minute": 15, "label": "alarm"}

Use 24-hour format (0-23). If no label is mentioned, use "alarm".
If you cannot find a time, respond with: {"error": "no time found"}"""

    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        
        # Extract JSON from response
        llm_text = response['message']['content']
        
        # Find JSON in the response
        start = llm_text.find('{')
        end = llm_text.rfind('}') + 1
        
        if start != -1 and end > start:
            json_str = llm_text[start:end]
            data = json.loads(json_str)
            return data
        
        return {"error": "Could not parse response"}
        
    except Exception as e:
        return {"error": f"LLM error: {str(e)}"}


def run_alarm(hour, minute, label="Alarm"):
    """Run the alarm and wait for trigger time"""
    print()
    print("=" * 60)
    print(f"✓ Alarm set for {hour:02d}:{minute:02d} - {label}")
    print("=" * 60)
    print()
    
    now = datetime.datetime.now()
    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print("Monitoring... (Press Ctrl+C to cancel)")
    print()
    
    alarm_has_rung = False
    
    try:
        while True:
            now = datetime.datetime.now()
            
            status = f"\rNow: {now.hour:02d}:{now.minute:02d}:{now.second:02d} | Alarm: {hour:02d}:{minute:02d}:00"
            print(status, end='', flush=True)
            
            if now.hour == hour and now.minute == minute and not alarm_has_rung:
                alarm_has_rung = True
                
                print("\n" * 2)
                print("=" * 60)
                print(" " * 10)
                print(" " * 20 + "ALARM RINGING!")
                print(" " * 10)
                print("=" * 60)
                print(f"Time: {now.strftime('%H:%M:%S')}")
                print(f"Label: {label}")
                print("=" * 60)
                print()
                
                print("Playing alarm sound...")
                play_sound()
                
                print()
                print("✓ Alarm completed!")
                return True
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nAlarm cancelled!")
        return False


def main():
    """Main program loop"""
    print("=" * 60)
    print("AI-POWERED ONE-LINE ALARM - Llama 3 Edition")
    print("=" * 60)
    print()
    print("Just type naturally! Examples:")
    print("  - wake me up at 7:30 AM")
    print("  - set alarm for 2:15 PM")
    print("  - remind me at 18:00 to call mom")
    print("  - alarm 6:45")
    print()
    print("Commands:")
    print("  - 'quit' or 'exit' to close")
    print("=" * 60)
    print()
    
    # Check if Ollama is running — split into two separate try/except blocks
    # so a successful connection is never mistaken for a failure.
    print("Checking Ollama connection...")
    try:
        test = ollama.list()
        print("✓ Ollama connected!")
    except Exception as e:
        print("✗ Cannot connect to Ollama!")
        print("Please make sure Ollama is running.")
        print("Open another terminal and run: ollama serve")
        print(f"  (Error: {e})")
        return

    # Check if llama3:8b is available — separate block so any KeyError/
    # AttributeError in model-list parsing never triggers the connection error.
    try:
        # ollama >= 0.2 returns an object with a .models attribute;
        # older versions returned a plain dict — handle both.
        model_list = test.models if hasattr(test, 'models') else test.get('models', [])
        models = [
            (m.model if hasattr(m, 'model') else m.get('model', m.get('name', '')))
            for m in model_list
        ]
        if not any('llama3' in m for m in models):
            print("\n⚠ Warning: llama3:8b not found in Ollama!")
            print("Available models:", models)
            print("\nTo download llama3:8b, run:")
            print("  ollama pull llama3:8b")
            response = input("\nContinue anyway? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                return
        else:
            print("✓ Llama 3 8B model found!")
    except Exception as e:
        print(f"⚠ Could not check available models: {e}")
        print("Continuing anyway...")

    print()
    
    while True:
        # Get user instruction
        user_input = input("What time? ").strip()
        
        if not user_input:
            continue
        
        # Check for exit
        if user_input.lower() in ['quit', 'exit', 'bye', 'stop']:
            print("Goodbye!")
            break
        
        # Ask Llama 3 to extract time
        print("🤖 Llama 3 is thinking...")
        result = ask_llm_for_time(user_input)
        
        if "error" in result:
            print(f"✗ {result['error']}")
            print("Try being more specific with the time, like '7:30 AM'")
            print()
            continue
        
        # Get hour, minute, label
        hour = result.get('hour')
        minute = result.get('minute', 0)
        label = result.get('label', 'Alarm')
        
        # Validate
        if hour is None or not (0 <= hour <= 23) or not (0 <= minute <= 59):
            print("✗ Invalid time extracted. Please try again.")
            print()
            continue
        
        # Check if time is in the future
        now = datetime.datetime.now()
        alarm_time = datetime.datetime(now.year, now.month, now.day, hour, minute, 0)
        
        if alarm_time <= now:
            print(f"⚠ Warning: {hour:02d}:{minute:02d} is in the past or right now!")
            print("Setting anyway...")
        
        # Run the alarm
        run_alarm(hour, minute, label)
        
        # Ask if they want another
        print()
        response = input("Set another alarm? (press Enter or type 'quit'): ").strip()
        if response.lower() in ['quit', 'exit', 'no', 'n']:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
