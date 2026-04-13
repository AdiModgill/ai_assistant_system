"""
Nova AI Assistant - Single Entry Point
Run this file to start the assistant.
"""

from core.nova import Nova


def main():
    nova = Nova()
    nova.run()


if __name__ == "__main__":
    main()