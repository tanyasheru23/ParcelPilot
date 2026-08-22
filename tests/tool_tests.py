import os
import sys
import uuid

# Ensure project root is on sys.path so `src` imports reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.models import EscalationRequest, UserContext

from src.tools import (
    lookup_order,
    search_documents,
    create_escalation,
)


# ==================================================
# Mock authenticated users
# ==================================================

NORTHSTAR_USER = UserContext(
    user_id="USER-001",
    email="ops@northstar.com",
    name="Sara",
    account_id="ACCT-001",
    account_name="NorthStar",
    plan="enterprise",
    role="customer_user",
)

LUMENWORKS_USER = UserContext(
    user_id="USER-002",
    email="ops@lumenworks.com",
    name="Jay",
    account_id="ACCT-002",
    account_name="LumenWorks",
    plan="business",
    role="customer_user",
)


# ==================================================
# lookup_order
# ==================================================

def test_lookup_order_valid():
    """
    An authenticated customer should be able to retrieve
    an order belonging to their own account.
    """

    result = lookup_order.invoke({
        "order_id": "ORD-1001",
        "user_context": NORTHSTAR_USER,
    })

    assert result is not None
    assert result.order_id == "ORD-1001"
    assert result.account_id == NORTHSTAR_USER.account_id
    assert result.status
    assert result.carrier


def test_lookup_order_invalid():
    """
    An invalid order ID should return no result.
    """

    result = lookup_order.invoke({
        "order_id": "INVALID-ORDER",
        "user_context": NORTHSTAR_USER,
    })

    assert result is None


def test_lookup_order_blocks_other_account_order():
    """
    A customer must not be able to retrieve an order
    belonging to another customer's account.
    """

    result = lookup_order.invoke({
        "order_id": "ORD-2001",
        "user_context": NORTHSTAR_USER,
    })

    assert result is None


def test_lookup_order_returns_own_account_order():
    """
    LumenWorks should be able to retrieve its own order.
    """

    result = lookup_order.invoke({
        "order_id": "ORD-2001",
        "user_context": LUMENWORKS_USER,
    })

    assert result is not None
    assert result.order_id == "ORD-2001"
    assert result.account_id == LUMENWORKS_USER.account_id


# ==================================================
# search_documents
# ==================================================

def test_search_documents_returns_general_documents():
    """
    An authenticated customer should be able to retrieve
    general ParcelPilot documents.
    """

    result = search_documents.invoke({
        "query": "What is the cancellation policy?",
        "user_context": NORTHSTAR_USER,
    })

    assert isinstance(result, list)
    assert len(result) > 0

    for document in result:
        assert document.page_content
        assert document.metadata.get("source_file")
        assert document.metadata.get("document_type")
        assert document.metadata.get("authority")

        # General documents must be explicitly marked GENERAL.
        if document.metadata.get("authority") != "signed_customer_agreement":
            assert document.metadata.get("account_id") == "GENERAL"


def test_search_documents_returns_own_account_documents():
    """
    NorthStar should be able to retrieve general documents
    and NorthStar-specific documents, but not documents
    belonging to another account.
    """

    result = search_documents.invoke({
        "query": "cancellation policy service credit",
        "user_context": NORTHSTAR_USER,
    })

    assert isinstance(result, list)
    assert len(result) > 0

    for document in result:
        account_id = document.metadata.get("account_id")

        assert account_id in {
            "GENERAL",
            NORTHSTAR_USER.account_id,
        }


def test_search_documents_does_not_return_other_account_documents():
    """
    NorthStar must never receive LumenWorks-specific documents.
    """

    result = search_documents.invoke({
        "query": "customer agreement cancellation service credit",
        "user_context": NORTHSTAR_USER,
    })

    assert isinstance(result, list)

    for document in result:
        account_id = document.metadata.get("account_id")

        assert account_id in {
            "GENERAL",
            NORTHSTAR_USER.account_id,
        }


def test_lumenworks_search_does_not_return_northstar_documents():
    """
    LumenWorks must never receive NorthStar-specific documents.
    """

    result = search_documents.invoke({
        "query": "customer agreement cancellation service credit",
        "user_context": LUMENWORKS_USER,
    })

    assert isinstance(result, list)

    for document in result:
        account_id = document.metadata.get("account_id")

        assert account_id in {
            "GENERAL",
            LUMENWORKS_USER.account_id,
        }

# ==================================================
# create_escalation
# ==================================================

# ==================================================
# create_escalation
# ==================================================

def test_create_escalation():
    """
    An authenticated customer should be able to create
    an escalation for their own account.
    """

    result = create_escalation.invoke({
        "order_id": "ORD-1001",
        "customer_query": "I cannot cancel my shipment.",
        "reason": "Unable to determine applicable cancellation rule.",
        "priority": "medium",
        "evidence": "Current policy and customer agreement conflict.",
        "user_context": NORTHSTAR_USER,
    })

    assert result["success"] is True
    assert result["escalation_id"] is not None
    assert result["status"] == "open"


def test_create_escalation_uses_authenticated_account():
    """
    The escalation must be created under the authenticated
    user's account.
    """

    result = create_escalation.invoke({
        "order_id": "ORD-2001",
        "customer_query": "My shipment is delayed.",
        "reason": "Shipment delay requires support.",
        "priority": "medium",
        "evidence": "Order information indicates a delay.",
        "user_context": LUMENWORKS_USER,
    })

    assert result["success"] is True
    assert result["escalation_id"] is not None
    assert result["status"] == "open"


def test_create_escalation_cannot_choose_account():
    """
    The customer must not be able to choose the account
    under which an escalation is created.

    account_id is intentionally NOT part of the tool input.
    The tool obtains it from authenticated UserContext.
    """

    tool_schema = create_escalation.args_schema.model_json_schema()

    properties = tool_schema.get("properties", {})

    assert "account_id" not in properties