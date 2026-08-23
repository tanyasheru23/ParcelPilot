# 📦 ParcelPilot

ParcelPilot is a customer-facing AI support agent for logistics companies.

It helps authenticated customers answer questions about:

- Orders and shipments
- Cancellation policies
- Customer-specific agreements
- Service-credit eligibility
- Support issues
- Escalations

The agent uses structured operational data together with document retrieval
and is orchestrated using LangGraph.

---
## Hosted Demo

[Launch ParcelPilot](https://parcelpilot-application.streamlit.app/)

The hosted application uses demo customer accounts for evaluation.

## Architecture

```text
                         ┌──────────────────┐
                         │     Customer     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Authentication │
                         └────────┬─────────┘
                                  │
                             UserContext
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │     ParcelPilot Agent    │
                    │   LangGraph + OpenAI LLM │
                    └────────────┬─────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
         lookup_order    search_documents   create_escalation
                │                │                │
                │                │            INTERRUPT
                │                │                │
                │                │        Customer confirmation
                │                │                │
                ▼                ▼                ▼
             SQLite           Chroma            SQLite
          Order / Account    PDF documents    Escalations
                │                │                │
                └────────────────┼────────────────┘
                                 ▼
                         Customer Response
```

The agent can perform sequential tool calls when answering questions that
require both operational order data and document-based policy information.
Escalation requests use a human-in-the-loop interrupt and require customer
confirmation before the escalation is created.


## Document Retrieval

```text
PDF Documents
     │
     ▼
PyPDFLoader
     │
     ▼
Text Splitting
     │
     ▼
OpenAI Embeddings
     │
     ▼
Chroma
     │
     ▼
Account + Authority Filtering
     │
     ▼
Relevant Document Chunks
```

Customer-specific documents are filtered using the authenticated
account context. General policies and account-specific agreements
are retrieved based on the query, with signed customer agreements
taking precedence over general policies when applicable.

## Setup

### 1. Clone the repo
```bash
git clone <repository-url>
cd ParcelPilot
```

### 2. Create and activate a virtual env
Windows: 
```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/MacOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Register Users

The hosted demo already contains pre-populated demo users.

If running the application locally without the hosted demo:

Register the required users using the registration script:

```bash
python scripts/register_users.py
```

### 5. Create Streamlit Secrets

Create:

`.streamlit/secrets.toml`

Example:

```toml
OPENAI_API_KEY = "your_openai_api_key"
LANGSMITH_TRACING = "true"
LANGSMITH_API_KEY = "your_langsmith_api_key"
LANGSMITH_PROJECT = "parcelpilot"

[DEMO_PASSWORDS]
"ops@northstar.com" = "your_password"
"ops@lumenworks.com" = "your_password"
"ops@beaconretail.com" = "your_password"
"ops@axislabs.com" = "your_password"
```
The passwords in DEMO_PASSWORDS must match the passwords used during
registration.

### 6. Run the application
```bash
streamlit run app.py
```

### Demo Accounts

The application supports the following demo accounts:

- Northstar Logistics
- LumenWorks
- Beacon Retail
- Axis Labs

Demo credentials are configured through Streamlit Secrets and should not
be committed to the repository.

### Demo Data

The repository contains the pre-populated SQLite database used by the
assessment demo. No manual database setup or user registration is required
to use the hosted application.

For a fresh local setup, use the registration script described above.

### Streamlit Cloud

For deployment, configure the same values from
`.streamlit/secrets.toml` in the application's Streamlit Cloud Secrets
settings.

The database and document/vector-store data required for the demo are
included in the repository.

---

## Assessment Documentation

- [Evaluation Prompts](docs/try_these_prompts.md) — Natural test prompts for each
  demo account, including authorization and escalation scenarios.
- [Design Decisions & Safety Controls](docs/Design_Decisions.md) — Authentication,
  account isolation, tool design, document authority, sequential workflows,
  human-in-the-loop actions, and data privacy.
- [AI Tools Usage](docs/AI_Tool_Usage.md) — How AI development tools were used
  during the assessment.
- [Future Improvements](docs/Improvements.md) — Potential production,
  scalability, security, observability, and agent improvements.
