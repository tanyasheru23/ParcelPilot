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
                ▼                ▼                ▼
             SQLite           Chroma            SQLite
          Order / Account    PDF documents    Escalations
                │                │                │
                └────────────────┼────────────────┘
                                 ▼
                         Customer Response
```
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
account context. Signed customer agreements take precedence over
general policies when applicable.

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

### 4. Create .env
```text
OPENAI_API_KEY=your_openai_api_key

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=parcelpilot
```

### 5. Run the application
```bash
python main.py
```