# Future Improvements

ParcelPilot was designed as an assessment-ready prototype. The following
improvements would be appropriate for a production deployment.

## 1. Persistent Production Storage

The current prototype uses SQLite for operational data and LangGraph
checkpointing.

A production system should use a managed database such as PostgreSQL for:

- Customer accounts
- Orders
- Escalations
- Conversation/checkpoint state

This would provide better concurrency, reliability, backup, and scaling.

## 2. Production Vector Store

The current document retrieval pipeline uses Chroma.

For larger document collections and distributed deployments, a managed or
server-based vector database could provide better scalability and persistence.

## 3. Stronger Authentication

The prototype uses application-level authentication for the assessment.

A production implementation should integrate with an identity provider and
use:

- Secure password hashing
- Session/token management
- Role-based access control
- Account-level authorization middleware

## 4. Better Document Governance

The retrieval layer could be extended with:

- Document versioning
- Effective/expiry dates
- Document approval status
- More granular tenant-level access control
- Audit trails for retrieved contractual information

## 5. Automated Evaluation

A production-quality agent should have an evaluation suite covering:

- Tool selection accuracy
- Sequential tool execution
- Retrieval relevance
- Authorization violations
- Policy precedence
- Escalation correctness
- Response quality

These tests could be integrated into CI/CD.

## 6. Observability

LangSmith provides useful tracing during development.

A production system could additionally track:

- Tool latency
- LLM latency and token usage
- Retrieval latency
- Escalation frequency
- Failure rates
- User feedback

## 7. Resilience and Scalability

Additional improvements would include:

- Retry policies for external services
- Rate limiting
- Timeouts
- Graceful failure handling
- Background document ingestion
- Caching where appropriate

## 8. UI Improvements

The current interface exposes useful tool activity and escalation
confirmation.

Future versions could provide:

- More polished tool execution indicators
- Better error states
- Conversation history
- Admin/support views for escalations
- Accessibility improvements
- Mobile-friendly layouts

## 9. Security Hardening

For production use:

- Secrets should remain outside source control.
- Database access should use least-privilege credentials.
- Customer data should be encrypted in transit and at rest.
- Sensitive information should be excluded from logs.
- Authorization should be enforced independently of the LLM.

## 10. Human-in-the-Loop Expansion

The current interrupt is used for escalation confirmation.

The same pattern could be extended to other high-impact actions such as:

- Cancelling shipments
- Issuing refunds
- Modifying orders
- Changing customer information

The agent should explain the proposed action and obtain explicit user
confirmation before executing such operations.
