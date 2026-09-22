# Investment Copilot — System Architecture Documentation

This document describes the technical architecture, component flow, data schemas, and design principles of **Investment Copilot**, an educational AI portfolio simulator built with Google ADK (Agent Development Kit).

---

## **1. High-Level Architecture Flow**

```
                       ┌──────────────────────────────┐
                       │          USER INPUT          │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │     ADK ROOT AGENT           │
                       │    (gemini-2.5-flash)        │
                       └──────────────┬───────────────┘
                                      │
     ┌────────────────────────────────┼────────────────────────────────┐
     │                                │                                │
     ▼                                ▼                                ▼
┌───────────────┐           ┌───────────────────┐            ┌──────────────────┐
│ PROFILE ENGINE│           │ FINANCIAL ENGINE  │            │ SYNTHETIC MARKET │
│ (app/profiler)│           │ (app/tools.py)    │            │ (app/market.py)  │
└───────┬───────┘           └─────────┬─────────┘            └────────┬─────────┘
        │                             │                               │
        └─────────────────────────────┼───────────────────────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  PORTFOLIO ARCHITECT ENGINE  │
                       │     (app/portfolio.py)       │
                       └──────────────┬───────────────┘
                                      │
     ┌────────────────────────────────┼────────────────────────────────┐
     │                                │                                │
     ▼                                ▼                                ▼
┌───────────────┐           ┌───────────────────┐            ┌──────────────────┐
│SCENARIO ENGINE│           │  RAG KNOWLEDGE    │            │ QUANT MATH CODES │
│(app/scenarios)│           │  (app/knowledge)  │            │ (app/quant.py)   │
└───────┬───────┘           └─────────┬─────────┘            └────────┬─────────┘
        │                             │                               │
        └─────────────────────────────┼───────────────────────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │   STORAGE & MEMORY LAYER     │
                       │(ADK Memory & Firestore/Local)│
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  A2UI DASHBOARD GENERATOR    │
                       │   (app/a2ui.py & tools)      │
                       └──────────────────────────────┘
```

---

## **2. Component Layer Breakdown**

### **A. Root Agent & Controller (`app/agent.py`)**
- **Model**: `gemini-2.5-flash` with Vertex AI backend.
- **Role**: Orchestrates conversational state, tool invocations, session context reuse, user input precedence, and response synthesis.
- **Function Tools**: Registers 30+ dedicated tools across profiling, financial calculations, market analysis, deterministic allocation, scenario modeling, RAG document search, quantitative math execution, ADK memory, persistent storage, and A2UI dashboard rendering.

### **B. Investor Profiler (`app/schema.py`, `app/profiler.py`)**
- **Validation**: Enforces strict Pydantic model validation (`InvestorProfile`).
- **Inconsistency Engine**: `check_inconsistencies()` detects cash flow deficits, investment over-allocation, and invalid ranges before finalizing profiles.

### **C. Financial Analysis Engine (`app/tools.py`)**
- **Surplus Calculator**: Computes monthly income minus expenses.
- **Emergency Fund Sizing**: Computes target liquid reserves (e.g. 6x monthly expenses).
- **Annual Capacity**: Evaluates annual investment capacity based on monthly contributions.

### **D. Synthetic Market Data Layer (`app/market.py`, `app/data/`)**
- **Dataset**: Stores fictional reference price histories across 9 asset classes (`broad_equity`, `large_cap`, `mid_cap`, `fixed_income`, `gold`, `international`, `cash_liquid`, `reit`, `commodities`).
- **Trend Analyzer**: Computes 1-month / 1-year returns, annual volatility, and trend classification without live external API dependencies.

### **E. Illustrative Portfolio Engine (`app/portfolio.py`)**
- **Deterministic Asset Allocation**: Maps risk tolerance (`Low`, `Moderate`, `High`), horizon years, and liquidity requirements to asset weights via explicit Python rules.
- **Mathematical Integrity**: Enforces that all generated allocations strictly sum to **100.0%**.

### **F. What-If Scenario Engine (`app/scenarios.py`)**
- **Isolation Principle**: Creates scenario objects that copy baseline profiles without overwriting stored baseline records.
- **Market Shocks**: Applies hypothetical percentage movements (e.g., -25% equity decline) to observe defensive asset behavior.

### **G. Grounded RAG Knowledge Layer (`app/knowledge.py`, `app/knowledge_base/`)**
- **Reference Corpus**: Markdown documents covering `risk_profiles.md`, `asset_classes.md`, `liquidity_guidelines.md`, `portfolio_assumptions.md`, and `scenario_mechanics.md`.
- **Search Engine**: Simple TF-IDF / keyword similarity matcher returning exact text excerpts and source document citations.

### **H. Quantitative Analysis & Code Execution (`app/quant.py`)**
- **Calculations**: Asset-weighted returns, portfolio volatility, maximum drawdown, and pairwise Pearson correlation matrices.
- **Sandboxed Execution**: `run_sandboxed_python()` runs custom mathematical code in an isolated environment with restricted `__builtins__`.

### **I. Memory & Persistent Storage (`app/memory_tools.py`, `app/storage.py`)**
- **ADK Cross-Session Memory**: Stores stable investor facts across sessions.
- **Firestore / File Persistence**: `storage_service` persists structured simulation records, baseline profiles, and scenarios with JSON fallback when GCP Firestore is unconfigured.

### **J. A2UI Dashboard Visual Generator (`app/a2ui.py`, `app/a2ui_tools.py`)**
- **Payload Spec**: Constructs an 8-section dynamic JSON specification.
- **Visual Sections**: Investor Summary, Financial Summary, Portfolio Allocation, Market Overview, Quantitative Analysis, Scenarios, Assumptions, Educational Disclaimer.

---

## **3. Deterministic vs. Generative Logic Matrix**

To ensure absolute safety and mathematical accuracy, Investment Copilot strictly separates deterministic logic from generative LLM functions:

| System Layer | Implementation Type | Responsibilities & Guarantees |
| :--- | :--- | :--- |
| **Conversational Flow** | **Generative (LLM)** | Natural language dialogue, intent extraction, synthesis of tool results. |
| **Profile Validation** | **Deterministic (Python)** | Pydantic type checks, range validation, inconsistency detection. |
| **Financial Analysis** | **Deterministic (Python)** | Surplus calculation, emergency fund math, annual investment capacity. |
| **Portfolio Allocation** | **Deterministic (Python)** | Asset-weight lookup tables, normalization ensuring total = 100.0%. |
| **Scenario Engine** | **Deterministic (Python)** | Copying baseline objects, applying parameter/market deltas in isolation. |
| **Knowledge Retrieval** | **Deterministic (Python)** | Document lookup & matching; explicit fallback when rule is missing. |
| **Quantitative Analysis** | **Deterministic (Python)** | Matrix math for returns, standard deviation, drawdown, correlation. |
| **Memory & Storage** | **Deterministic (Python)** | CRUD operations for ADK memory keys and Firestore simulation records. |
| **A2UI Payload Generation** | **Deterministic (Python)** | Constructing structured UI JSON trees from verified backend state. |

---

## **4. Safety & Educational Boundaries**

1. **Non-Advisory Guardrail**: All outputs carry explicit educational disclaimers.
2. **Synthetic Data Scoping**: All market prices, returns, and volatilities are derived from synthetic CSVs (`app/data/synthetic_market.csv`).
3. **No External Execution**: No live market APIs, brokerage connections, or trade execution capabilities are included.
