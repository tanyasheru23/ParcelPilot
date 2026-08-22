from pydantic import BaseModel
from datetime import datetime

# =========================
# Data Models
# =========================

class Account(BaseModel):
    account_id: str
    account_name: str
    plan: str
    status: str
    csm: str
    contract_file: str | None = None
    premium_support: bool
    notes: str | None = None

class Order(BaseModel):
    order_id: str
    account_id: str
    carrier: str
    status: str
    booked_at: datetime

    pickup_window_start: datetime
    pickup_window_end: datetime
    pickup_actual_at: datetime | None = None

    shipment_fee_inr: float

    carrier_fault: bool
    customer_fault: bool

    cancellation_requested_at: datetime | None = None
    notes: str | None = None

class Ticket(BaseModel):
    ticket_id: str
    account_id: str
    created_at: datetime
    subject: str
    status: str
    description: str
    channel: str
    assigned_to: str
    last_customer_message_at: datetime | None = None
    historical_resolution: str | None = None

class DocumentChunk(BaseModel):
    content: str
    source_file: str
    document_type: str
    status: str
    authority: str
    authority_rank: int
    account_id: str | None = None

# =========================
# Tool schemas
# =========================

class LookupOrderInput(BaseModel):
    order_id: str

class SearchDocumentsInput(BaseModel):
    query: str
    account_id: str | None = None

class SearchDocumentsOutput(BaseModel):
    results: list[DocumentChunk]

class EscalationRequest(BaseModel):
    order_id : str | None = None
    customer_query : str
    reason : str
    priority : str
    evidence : str
    status : str

class CreateEscalationOutput(BaseModel):
    success: bool
    escalation_id: str
    status: str

# =========================
# User Context
# =========================
class UserContext(BaseModel):
    user_id: str
    email: str
    name: str
    account_id: str
    account_name: str
    plan: str
    role: str