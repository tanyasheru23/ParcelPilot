import sqlite3
import uuid

import bcrypt

from src.models import UserContext


from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)


def init_users_table():
    """
    Create the users table if it does not already exist.
    """

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            account_id TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer_user',
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (account_id)
                REFERENCES accounts(account_id)
        )
        """
    )

    conn.commit()
    conn.close()


def register_user(
    email: str,
    password: str,
    name: str,
    account_id: str,
    role: str = "customer_user",
):
    """
    Register a user under an existing ParcelPilot account.

    The account must already exist and be ACTIVE.
    """

    conn = get_connection()

    # Check that the account already exists
    account = conn.execute(
        """
        SELECT account_id, account_name, plan, status
        FROM accounts
        WHERE account_id = ?
        """,
        (account_id,),
    ).fetchone()

    if account is None:
        conn.close()
        raise ValueError(
            f"Account '{account_id}' does not exist."
        )

    account_id_db, account_name, plan, status = account

    if status.upper() != "ACTIVE":
        conn.close()
        raise ValueError(
            f"Account '{account_id}' is not active."
        )

    # Check duplicate email
    existing_user = conn.execute(
        """
        SELECT user_id
        FROM users
        WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if existing_user is not None:
        conn.close()
        raise ValueError(
            f"A user with email '{email}' already exists."
        )

    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    user_id = f"USER-{uuid.uuid4().hex[:8].upper()}"

    conn.execute(
        """
        INSERT INTO users (
            user_id,
            email,
            password_hash,
            name,
            account_id,
            role,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            email,
            password_hash,
            name,
            account_id_db,
            role,
            "active",
        ),
    )

    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "email": email,
        "name": name,
        "account_id": account_id_db,
        "account_name": account_name,
        "plan": plan,
        "role": role,
    }


def authenticate_user(
    email: str,
    password: str,
) -> UserContext | None:
    """
    Authenticate a user and return their trusted UserContext.

    Returns None if authentication fails.
    """

    conn = get_connection()

    user = conn.execute(
        """
        SELECT
            u.user_id,
            u.email,
            u.password_hash,
            u.name,
            u.account_id,
            u.role,
            u.status,
            a.account_name,
            a.plan,
            a.status
        FROM users u
        JOIN accounts a
            ON u.account_id = a.account_id
        WHERE u.email = ?
        """,
        (email,),
    ).fetchone()

    conn.close()

    if user is None:
        return None

    (
        user_id,
        email_db,
        password_hash,
        name,
        account_id,
        role,
        user_status,
        account_name,
        plan,
        account_status,
    ) = user

    # User must be active
    if user_status.lower() != "active":
        return None

    # Account must be active
    if account_status.upper() != "ACTIVE":
        return None

    # Verify password
    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )

    if not password_valid:
        return None

    return UserContext(
        user_id=user_id,
        email=email_db,
        name=name,
        account_id=account_id,
        account_name=account_name,
        plan=plan,
        role=role,
    )