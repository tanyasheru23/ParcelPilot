import os
import sys

# Ensure project root is on sys.path so `src` and top-level modules import reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from src.data.vectorstore import get_vectorstore


@pytest.fixture(scope="module")
def vectorstore():
    """
    Load the existing Chroma vector store.

    The vector store must already have been built before
    running these tests.
    """
    return get_vectorstore()


def get_account_ids(documents):
    """Return the account IDs present in retrieved documents."""
    return {
        document.metadata.get("account_id")
        for document in documents
    }


def test_vectorstore_has_account_metadata(vectorstore):
    """
    Every indexed document should have an account_id.

    Expected values:
        GENERAL
        ACCT-001
        ACCT-002
        ACCT-004
    """

    results = vectorstore.similarity_search(
        "cancellation policy",
        k=20,
    )

    assert len(results) > 0

    for document in results:
        assert "account_id" in document.metadata
        assert document.metadata["account_id"] is not None


def test_general_documents_are_marked_general(vectorstore):
    """
    General documents should use account_id='GENERAL'.
    """

    results = vectorstore.similarity_search(
        "support policy service credit cancellation",
        k=20,
    )

    general_documents = [
        document
        for document in results
        if document.metadata.get("authority") != "signed_customer_agreement"
    ]

    assert len(general_documents) > 0

    for document in general_documents:
        assert document.metadata.get("account_id") == "GENERAL"


def test_customer_agreement_has_account_id(vectorstore):
    """
    Customer-specific agreements must have a real account ID
    rather than GENERAL.
    """

    results = vectorstore.similarity_search(
        "customer agreement cancellation service credit",
        k=20,
    )

    customer_documents = [
        document
        for document in results
        if document.metadata.get("authority") == "signed_customer_agreement"
    ]

    assert len(customer_documents) > 0

    for document in customer_documents:
        account_id = document.metadata.get("account_id")

        assert account_id is not None
        assert account_id != "GENERAL"


def test_northstar_filter_returns_only_northstar_documents(
    vectorstore,
):
    """
    Verify Chroma can retrieve Northstar-specific documents
    using account_id metadata.
    """

    results = vectorstore.similarity_search(
        "cancellation policy",
        k=10,
        filter={
            "account_id": "ACCT-001"
        },
    )

    assert len(results) > 0

    account_ids = get_account_ids(results)

    assert account_ids == {"ACCT-001"}


def test_lumenworks_filter_returns_only_lumenworks_documents(
    vectorstore,
):
    """
    Verify Chroma can retrieve LumenWorks-specific documents
    using account_id metadata.
    """

    results = vectorstore.similarity_search(
        "cancellation policy",
        k=10,
        filter={
            "account_id": "ACCT-002"
        },
    )

    assert len(results) > 0

    account_ids = get_account_ids(results)

    assert account_ids == {"ACCT-002"}


def test_general_filter_returns_only_general_documents(
    vectorstore,
):
    """
    Verify general documents can be retrieved separately.
    """

    results = vectorstore.similarity_search(
        "support policy",
        k=10,
        filter={
            "account_id": "GENERAL"
        },
    )

    assert len(results) > 0

    account_ids = get_account_ids(results)

    assert account_ids == {"GENERAL"}


def test_northstar_cannot_retrieve_lumenworks_documents(
    vectorstore,
):
    """
    Basic isolation test.

    A search explicitly scoped to Northstar must never
    return LumenWorks documents.
    """

    results = vectorstore.similarity_search(
        "customer agreement",
        k=20,
        filter={
            "account_id": "ACCT-001"
        },
    )

    for document in results:
        assert document.metadata.get("account_id") != "ACCT-002"


def test_lumenworks_cannot_retrieve_northstar_documents(
    vectorstore,
):
    """
    Reverse isolation test.
    """

    results = vectorstore.similarity_search(
        "customer agreement",
        k=20,
        filter={
            "account_id": "ACCT-002"
        },
    )

    for document in results:
        assert document.metadata.get("account_id") != "ACCT-001"