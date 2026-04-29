import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.main_graph import app
from memory.memory_store import load_history, clear_history


def run_cli():
    print("\nFinancial AI Agent\n")
    print("=" * 60)

    username = input("Enter your username to start (or press Enter for 'guest'): ").strip()
    if not username:
        username = "guest"

    history = load_history(username)
    if history:
        print(f"\nWelcome back, {username}. You have {len(history) // 2} previous conversation(s) on record.")
    else:
        print(f"\nWelcome, {username}. Starting a new session.")

    print("\nType 'exit' to quit | 'clear memory' to reset your history\n")
    print("=" * 60 + "\n")

    while True:
        query = input(f"[{username}] Ask: ").strip()

        if not query:
            continue
        if query.lower() in ["exit", "quit"]:
            print(f"Goodbye, {username}.")
            break
        if query.lower() == "clear memory":
            clear_history(username)
            print("Your conversation history has been cleared.\n")
            continue

        print(f"\nProcessing: {query}\n")
        start_time = time.time()
        final_output = None

        try:
            for chunk in app.stream({"query": query, "username": username}):
                for key in chunk:
                    print(f"[{key.upper()}] updated")
                for value in chunk.values():
                    if isinstance(value, dict) and "final" in value:
                        final_output = value["final"]

            print("\nFINAL OUTPUT:\n")
            print(final_output if final_output else "No final output generated.")
            print(f"\nExecution Time: {time.time() - start_time:.2f} seconds")
            print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    run_cli()
