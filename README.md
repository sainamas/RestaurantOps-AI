RestoGuide AI

RAG-Based Restaurant Operations Assistant

RestoGuide AI is a local-first AI-powered knowledge assistant designed to help restaurant staff quickly find recipes, kitchen SOPs, policies and operational reference information through natural-language questions.

The project was developed around an operational knowledge-access problem observed through exposure to a restaurant business, where staff may need to repeatedly search for procedures or ask experienced staff for information.

The current version focuses on document ingestion, semantic retrieval, relevance-based routing and source transparency.

⸻

Problem

Restaurant staff may need quick access to:

* Recipes and preparation procedures
* Kitchen SOPs
* Restaurant policies
* Equipment and operational reference guides
* Other internal documentation

Searching through multiple documents or repeatedly asking experienced staff for information can slow down work, particularly for newer staff.

RestoGuide provides a natural-language interface for retrieving relevant operational information from a central knowledge base.

⸻

Solution

RestoGuide combines document ingestion, semantic retrieval and workflow orchestration to locate relevant operational knowledge.

The system first searches the internal restaurant knowledge base. If sufficient internal evidence cannot be found, it can use DuckDuckGo as a fallback and clearly identify the result as external information.

Staff Question
      │
      ▼
Responsive Web Interface
      │
      ▼
FastAPI Backend
      │
      ▼
LangGraph Workflow
      │
      ▼
Internal Knowledge Retrieval
      │
      ├───────────────┐
      │               │
      ▼               ▼
Sentence          FAISS
Transformers      Vector Search
      │               │
      └───────┬───────┘
              ▼
       Relevance Scoring
              │
              ▼
      Evidence Threshold
         │           │
    Sufficient    Insufficient
      Evidence      Evidence
         │              │
         ▼              ▼
   Internal Answer   DuckDuckGo
      + Sources       Search
                         │
                         ▼
                   External Results
                   Clearly Labelled
              │
              ▼
        SQLite Query History

⸻

Phase 1 — Current Implementation

Natural-Language Search

Staff can ask operational questions using natural language instead of manually searching through multiple documents.

Multi-Format Document Ingestion

The ingestion pipeline supports:

* PDF
* DOCX
* TXT
* Markdown

Documents can be uploaded and indexed for retrieval.

Semantic Retrieval

Sentence Transformers convert questions and knowledge-base documents into embeddings.

FAISS performs similarity-based retrieval to identify potentially relevant documents.

Relevance Scoring

Retrieved documents are ranked using semantic similarity combined with title matching.

An evidence threshold determines whether sufficient internal evidence has been found.

LangGraph Workflow

LangGraph orchestrates the retrieval workflow and determines whether the system should use internal knowledge or fall back to external search.

Question
   ↓
Internal Retrieval
   ↓
Evidence Evaluation
   ↓
 ┌───────────────┐
 │               │
 ▼               ▼
Sufficient      Insufficient
Evidence        Evidence
 │               │
 ▼               ▼
Internal        DuckDuckGo
Result          Fallback

External Search Fallback

When sufficient internal evidence cannot be found, the system can query DuckDuckGo.

External results are explicitly labelled and are not treated as approved restaurant procedures.

Source Transparency

Retrieved information includes source information so users can identify where the information came from.

SQLite Query History

Questions and responses are stored in SQLite together with timestamps.

This provides an interaction history that can later be analysed to understand how staff use the knowledge system.

Responsive Web Interface

The application provides a browser-based interface for asking questions and interacting with the knowledge base.

⸻

Architecture

                         ┌─────────────────────┐
                         │      Staff User     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Responsive Web UI  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI        │
                         │     Application      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      LangGraph       │
                         │  Workflow Routing    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Internal Retrieval  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                Sentence Transformers      FAISS
                    Embeddings            Retrieval
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Relevance Scoring   │
                         │ + Evidence Threshold│
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                 Sufficient Evidence       Insufficient
                       │                     Evidence
                       ▼                         ▼
              ┌─────────────────┐      ┌─────────────────┐
              │ Internal Sources │      │  DuckDuckGo     │
              │ + Retrieved Text │      │  Web Search     │
              └────────┬────────┘      └────────┬────────┘
                       │                         │
                       └────────────┬────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │   Answer + Sources  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   SQLite History    │
                         │ Question + Response │
                         │ + Timestamp         │
                         └─────────────────────┘

⸻

Technology Stack

Backend

* Python
* FastAPI
* Pydantic Settings

Retrieval / AI

* Sentence Transformers
* FAISS
* LangGraph

Search

* DuckDuckGo

Database

* SQLite

Document Processing

* PDF
* DOCX
* TXT
* Markdown

Frontend

* HTML
* CSS
* JavaScript
* Jinja2 templates

Testing

* Pytest

⸻

Project Structure

restoguide-ai/
│
├── app/
│   ├── main.py
│   ├── rag/
│   │   └── engine.py
│   ├── services/
│   │   ├── database.py
│   │   └── documents.py
│   ├── templates/
│   └── static/
│
├── data/
│   ├── knowledge_base/
│   └── uploads/
│
├── scripts/
│   └── build_index.py
│
├── tests/
│   └── test_documents.py
│
├── requirements.txt
└── README.md

⸻

Running the Project

Windows / PowerShell

Create a virtual environment:

py -3.11 -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install --upgrade pip
pip install -r requirements.txt

Create the environment file:

Copy-Item .env.example .env

Start the application:

uvicorn app.main:app --reload

Open the application at:

http://127.0.0.1:8000

The first launch downloads the Sentence Transformers embedding model and builds the FAISS index.

Internet access is required for the initial model download and for DuckDuckGo fallback searches.

⸻

Testing

Run the automated tests with:

pytest -q

The project includes automated tests for document-processing functionality.

⸻

Phase 2 — Planned Development

The next development phase will extend RestoGuide from a knowledge-retrieval assistant into a more complete operational learning and staff-support platform.

Phase 2 will build on the existing SQLite interaction history and focus on both operational intelligence and production-ready engineering.

Operational Intelligence

Staff Feedback

Allow staff to indicate whether an answer was useful.

Query Analysis

Analyse frequently repeated staff questions and identify common topics.

Knowledge Gap Detection

Identify areas where staff repeatedly require assistance or where the existing knowledge base may be insufficient.

Training Insights

Convert recurring knowledge gaps into training recommendations for managers.

Manager Dashboard

Provide operational insights such as:

* Most frequently asked questions
* Frequently requested procedures
* Low-feedback responses
* Unanswered questions
* Potential training gaps

Knowledge Review

Introduce knowledge-management states such as:

* Approved
* Needs Review
* Outdated

The planned feedback loop is:

Staff Question
      ↓
Knowledge Retrieval
      ↓
Answer + Sources
      ↓
Staff Feedback
      ↓
Interaction Data
      ↓
Query Analysis
      ↓
Knowledge / Training Gaps
      ↓
Knowledge Base Improvement
      ↓
Improved Staff Assistance

⸻

Production Engineering

As the operational workflow is expanded, Phase 2 will also introduce production-oriented engineering improvements.

Planned improvements include:

* PostgreSQL for persistent application data
* Docker containerisation
* Authentication
* Role-based access control
* Expanded automated testing
* CI/CD with GitHub Actions
* Cloud deployment
* Application logging
* Monitoring and observability

The planned production architecture will evolve toward:

Staff
  ↓
Web Application
  ↓
FastAPI
  ↓
Authentication / RBAC
  ↓
RAG + Knowledge Retrieval
  ↓
PostgreSQL
  ↓
Query Analytics
  ↓
Manager / Training Dashboard

Phase 2 represents planned development and is not represented as implemented functionality in the current version.

⸻

Safety and Limitations

This portfolio prototype uses synthetic restaurant documents.

The current system does not use a generative LLM. Responses are based on retrieved document passages or labelled external search results.

External web information is not treated as approved restaurant procedure.

The system should not be used for food-safety decisions without qualified review and approved procedures.

⸻

Project Direction

RestoGuide is designed to demonstrate how retrieval and AI technologies can be applied to a practical operational knowledge problem.

The project combines:

Natural-language interaction + semantic retrieval + workflow orchestration + backend engineering + operational data

The longer-term direction is to move from simply helping staff find information toward understanding where staff need support and improving the underlying operational knowledge system.
