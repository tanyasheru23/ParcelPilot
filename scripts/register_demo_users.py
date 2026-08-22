from getpass import getpass
import os
import sys

# Ensure project root is on sys.path so `src` and top-level modules import reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.auth import init_users_table, register_user


def main():

    init_users_table()

    print("=== ParcelPilot Demo User Registration ===")
    print()

    email = input("Email: ").strip()
    name = input("Name: ").strip()
    account_id = input("Account ID (e.g. ACCT-001): ").strip()
    password = getpass("Password: ")

    try:

        user = register_user(
            email=email,
            password=password,
            name=name,
            account_id=account_id,
        )

        print("\nUser registered successfully!")
        print(f"User ID:      {user['user_id']}")
        print(f"Name:         {user['name']}")
        print(f"Email:        {user['email']}")
        print(f"Account:      {user['account_name']}")
        print(f"Account ID:   {user['account_id']}")
        print(f"Plan:         {user['plan']}")
        print(f"Role:         {user['role']}")

    except ValueError as e:

        print(f"\nRegistration failed: {e}")


if __name__ == "__main__":
    main()