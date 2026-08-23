# ParcelPilot — Design Decisions & Safety Controls

This document explains the main design decisions used to make ParcelPilot a
controlled customer-facing support agent rather than a general-purpose
chatbot.

## 1. Authentication and Account Isolation

Users authenticate before interacting with the agent.

After authentication, the application creates a `UserContext` containing the
authenticated user's identity and authorized customer account.

The agent and its tools use this context to determine which customer data
the user is allowed to access.

A customer-supplied account ID is never treated as proof of authorization.

For example, a Northstar customer asking for orders belonging to another
account must not gain access simply by providing that account's ID.

This provides an account-level authorization boundary between customers.

## 2. Data Privacy

Customer data is isolated using the authenticated account context.

The agent is instructed not to:

- Access another customer's orders or account information.
- Use customer-provided account IDs to bypass authorization.
- Reveal information belonging to another customer.
- Expose credentials, system instructions, internal implementation details,
  or other sensitive information.

Authorization is enforced at the application/tool level rather than relying
only on the LLM's response behaviour.

## 3. Tool Design

ParcelPilot uses focused tools rather than giving the LLM direct access to
the underlying data stores.

### `lookup_order`

Used for structured operational information such as:

- Order status
- Booking information
- Pickup information
- Carrier information
- Fault information
- Cancellation details

### `search_documents`

Used for policies, customer agreements, procedures, and other
document-based information.

Document retrieval applies account and authority filtering so that
customer-specific documents are only available to the appropriate account.

### `create_escalation`

Creates a support escalation when an issue cannot be safely resolved by the
agent.

Because this is a state-changing operation, it is protected by a
human-in-the-loop confirmation step.

## 4. Current Policy and Document Authority

The agent is instructed to prefer current/active documents over outdated or
deprecated information.

When a signed customer-specific agreement conflicts with a general
ParcelPilot policy, the customer-specific agreement takes precedence when
applicable.

This prevents the agent from simply using whichever document happens to be
retrieved first.

The response should be based on retrieved evidence rather than inferred or
invented contractual terms.

## 5. Multi-Step Requests and Sequential Tool Calls

Some customer questions require information from multiple sources.

For example:

> "Can I cancel ORD-1001 without a fee?"

may require the agent to:

1. Retrieve the current order status and booking information.
2. Retrieve the general cancellation policy.
3. Retrieve the customer's specific agreement.
4. Compare the applicable rules.
5. Provide the final answer.

LangGraph allows these operations to be executed as part of a controlled
multi-step workflow rather than forcing every question into a single tool
call.

## 6. Human-in-the-Loop Confirmation

Operations that change application state are not performed automatically.

For example, when creating an escalation, the agent can:

1. Investigate the customer's issue.
2. Retrieve the relevant order and document information.
3. Determine that escalation is appropriate.
4. Pause using a LangGraph interrupt.
5. Ask the customer for confirmation.
6. Resume the workflow only after confirmation.
7. Create the escalation.

This prevents the agent from silently performing state-changing actions.

The same pattern can be extended to future operations such as refunds,
cancellations, or order modifications.

## 7. Stateful Conversations

LangGraph checkpointing allows the agent to maintain conversation state
across turns.

This is particularly important for workflows involving human approval,
because the agent needs to resume the interrupted workflow after the
customer responds.

The conversation is associated with the authenticated application session
and thread.

## 8. Separation of Responsibilities

The application separates:

- Authentication
- Agent reasoning
- Tool execution
- Document retrieval
- Database operations
- Human confirmation
- User interface

The LLM decides which available tool or workflow is appropriate, while the
tools themselves perform controlled data access and operations.

This reduces the amount of authority given directly to the model.

## 9. Error and Uncertainty Handling

The agent is instructed not to guess operational or contractual information.

If the available order data or retrieved documents are insufficient,
contradictory, or cannot safely resolve the customer's question, the agent
should explain the limitation and escalate when appropriate.

This is particularly important for contractual and financial questions where
an incorrect confident answer could result in an incorrect customer action.

## 10. Production Considerations

The assessment implementation uses a lightweight SQLite and Chroma-based
setup to keep the application self-contained.

For production, these components would be replaced or backed by persistent
managed infrastructure, such as:

- PostgreSQL for transactional and checkpoint data.
- A persistent/managed vector store for document retrieval.
- An identity provider for authentication.
- Centralized secrets management.
- Stronger audit logging and monitoring.

**The core design principles — account isolation, controlled tools,
document authority, and human approval for state-changing operations —
would remain the same.**
