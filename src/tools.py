import sqlite3
import os
import sys
import uuid

from langchain_core.tools import tool

# Ensure project root is on sys.path so `src` and top-level modules import reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data.sqlite_loader import query_db
from src.data.vectorstore import get_vectorstore
from src.models import (
    Order,
    DocumentChunk,
    EscalationRequest,
)
from src.models import UserContext

from typing import Annotated
from langgraph.prebuilt import InjectedState

from config import DB_PATH

@tool
def lookup_order(order_id: str, user_context: Annotated[UserContext, InjectedState("user_context")]) -> Order | None:
    """
    Look up an order by order ID and return its details.
    """
    account_id = user_context.account_id
    query = """
        SELECT *
        FROM orders
        WHERE order_id = ?
        AND account_id = ?
    """

    # query_db currently accepts a query string,
    # so parameterized SQL is handled directly here.
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            query,
            (order_id, account_id),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Order(**dict(row))

    finally:
        connection.close()


@tool
def search_documents(
    query: str,
    user_context: Annotated[
        UserContext,
        InjectedState("user_context")
    ],
):
    """
    Search documents available to the authenticated customer account.
    Searches both account-specific documents and general policies.
    """

    account_id = user_context.account_id

    vectorstore = get_vectorstore()

    account_docs = vectorstore.similarity_search(
        query,
        k=4,
        filter={
            "account_id": account_id
        }
    )

    general_docs = vectorstore.similarity_search(
        query,
        k=4,
        filter={
            "account_id": "GENERAL"
        }
    )

    results = account_docs + general_docs

    return results

@tool
def create_escalation(
    order_id: str | None,
    customer_query: str,
    reason: str,
    priority: str,
    evidence: str,
    user_context: Annotated[
        UserContext,
        InjectedState("user_context")
    ],
):
    """
    Create an escalation for a customer issue that
    cannot be safely resolved by the customer-facing agent.
    """
    
    account_id = user_context.account_id

    escalation_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"

    conn = sqlite3.connect("data/processed/parcelpilot.db")

    conn.execute(
        """
        INSERT INTO escalations (
            escalation_id,
            account_id,
            order_id,
            customer_query,
            reason,
            priority,
            evidence,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            escalation_id,
            account_id,
            order_id,
            customer_query,
            reason,
            priority,
            evidence,
            "open",
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "escalation_id": escalation_id,
        "status": "open"
    }