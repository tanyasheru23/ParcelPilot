# AI Tools Usage

Used AI coding assistants during the development of ParcelPilot as
development aids, particularly for debugging, implementation suggestions,
documentation, and UI refinement.

## Tools Used

### ChatGPT

Used for:

- Understanding the problem statement and product needs.
- Discussing agent architecture and LangGraph workflows.
- Reasoning about tool sequencing and human-in-the-loop interrupts.
- Debugging authentication, checkpointing, and Streamlit integration issues.
- Designing evaluation scenarios and test prompts.
- Reviewing system-prompt behaviour.
- README and project documentation drafting.
- Deployment planning and troubleshooting.

### Claude

Used for:

- Reviewing and refining the Streamlit interface.
- Debugging the escalation confirmation UI.
- Suggesting improvements to Streamlit session-state handling.
- Helping restructure UI rendering around LangGraph interrupts.

### LangSmith

Used for:

- Inspecting LangGraph traces.
- Verifying tool calls and execution order.
- Debugging sequential tool execution.
- Observing agent behaviour during evaluation.

## Development Approach

Treated AI-generated suggestions as development assistance rather than
as a substitute for testing or engineering decisions.

Reviewed code suggestions, adapted to the existing codebase, and tested
locally and through the hosted application.

Particular attention was given to:

- Authorization boundaries.
- Customer-specific document access.
- Sequential tool execution.
- Human confirmation before escalation.
- Persistent conversation state.
- Correctness of policy precedence.

## Verification

The final behaviour was verified through manual test conversations,
LangSmith traces, local Streamlit testing, and testing of the deployed
application.

AI assistance was therefore used as part of the development workflow, while
implementation choices and final validation remained the developer's
responsibility.
