import os
import sys
import uuid

# Ensure project root is on sys.path so `src` imports reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import uuid

from src.agent import graph
from src.auth import authenticate_user


def login(email: str, password: str):
    """Authenticate a user and create their session."""

    user_context = authenticate_user(
        email=email,
        password=password,
    )

    if user_context is None:
        return None

    session = {
        "session_id": str(uuid.uuid4()),
        "user_context": user_context,
    }

    return session


def chat(session: dict):
    """Run the interactive customer chat for an authenticated session."""

    config = {
        "configurable": {
            "thread_id": session["session_id"],
        }
    }

    print("\nLogged in successfully!")
    print(f"Account: {session['user_context'].account_name}")
    print(f"User: {session['user_context'].name}")

    while True:

        user_input = input("\nCustomer: ")

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                "user_context": session["user_context"],
            },
            config=config,
        )

        print(
            "\nParcelPilot:",
            result["messages"][-1].content,
        )


def main():

    print("=== ParcelPilot ===")

    email = input("Email: ").strip()
    password = input("Password: ")

    session = login(email, password)

    if session is None:
        print("\nInvalid email or password.")
        return

    chat(session)


if __name__ == "__main__":
    main()