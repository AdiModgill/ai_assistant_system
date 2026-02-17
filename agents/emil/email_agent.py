from agent import AIAgent


def main():
    print("\n" + "=" * 60)
    print("🤖 AI EMAIL AGENT (Local LLM - Qwen2.5)")
    print("=" * 60)
    print("Type something like:")
    print("Send an email to john@example.com saying hello")
    print("Type 'exit' to quit\n")

    agent = AIAgent()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("👋 Bye!")
                break

            if not user_input:
                print("Please type something 🙂")
                continue

            response = agent.process_user_input(user_input)
            print("\nAgent:", response)

        except KeyboardInterrupt:
            print("\n👋 Stopped")
            break

        except Exception as e:
            print("❌ Error:", e)


if __name__ == "__main__":
    main()
