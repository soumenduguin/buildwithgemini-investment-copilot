# Investment Copilot — Educational AI Portfolio Simulator

![Investment Copilot Demo](docs/demo.gif)

**Investment Copilot** is an educational AI Portfolio Simulator built using **Google Agent Development Kit (ADK)** and **Google Gemini 2.5 Flash**. It provides conversational investor profiling, financial health analysis, synthetic market intelligence, deterministic illustrative portfolio allocation, grounded RAG knowledge explanations, sandboxed quantitative risk analysis, non-destructive What-If scenario simulation, cross-session ADK memory, persistent simulation storage, and dynamic A2UI visual dashboard rendering.

> [!IMPORTANT]
> **EDUCATIONAL SIMULATION ONLY**
> This project is designed strictly for educational, research, and training purposes. It operates exclusively on fictional investor profiles and synthetic market datasets. It does **NOT** provide personalized real-world financial advice, recommend actual stock/ETF tickers, guarantee investment returns, connect to live financial APIs, or execute real-money transactions.
>
> *"Educational simulation using synthetic data. Not financial advice and not a prediction of future returns."*

---

## **Key Features & Capabilities**

1. **Conversational Investor Profiler**
   - Natural language interview to collect 10 core profile fields: name, age, monthly income, monthly expenses, current savings, monthly investment amount, investment goal, horizon in years, risk tolerance, and liquidity requirement.
   - Pydantic schema validation (`app/schema.py`) with real-time inconsistency detection (cash flow deficits, excessive investment capacity).

2. **Financial Health Analysis Tools**
   - `calculate_monthly_surplus`: Evaluates cash flow surplus/deficit status.
   - `calculate_emergency_fund`: Computes 6-month target liquid reserves.
   - `calculate_annual_investment_capacity`: Evaluates 12-month total investment capacity.

3. **Synthetic Market Intelligence Layer**
   - Controlled synthetic dataset (`app/data/synthetic_market_data.csv`) covering 9 asset classes (Broad Equity, Large Cap, Mid Cap, Fixed Income, Gold, International, Cash/Liquid, REIT, Commodities).
   - Tools: `get_market_overview`, `get_market_snapshot`, `analyze_asset_trend`, `compare_assets`.

4. **Deterministic Portfolio Architect**
   - Generates illustrative asset-class allocation weights using deterministic Python rules based on risk profile, horizon, and liquidity.
   - Applies market-based adjustments (`adjust_allocation_for_market_conditions`) and guarantees that allocations strictly sum to **100.0%**.

5. **Grounded RAG Knowledge Layer**
   - Search engine (`app/knowledge.py`) over synthetic Markdown reference documents (`app/knowledge_base/`).
   - Grounds educational explanations and cites document sources (`risk_profiles.md`, `asset_classes.md`, `portfolio_assumptions.md`). Grounded non-hallucination guarantee on unsupported rules.

6. **Sandboxed Quantitative Analysis**
   - Quantitative engine (`app/quant.py`) and tools (`analyze_volatility`, `analyze_drawdowns`, `analyze_correlations`, `analyze_portfolio_quantitatively`, `compare_scenarios_quantitatively`).
   - Sandboxed Python code execution (`execute_quantitative_analysis`) running math over synthetic data.

7. **What-If Scenario Simulator**
   - Non-destructive scenario modeling (`create_scenario`, `simulate_market_shock`, `compare_scenario_to_baseline`).
   - Guarantees baseline profile isolation — baseline profile remains untouched when testing hypothetical parameter or market shock variations.

8. **Cross-Session ADK Memory & Persistent Storage**
   - ADK Memory (`save_investor_memory`, `recall_investor_memory`) stores stable contextual facts across sessions.
   - Structured Storage Service (`storage.py`, `storage_tools.py`) with GCP Firestore primary engine and local persistent JSON fallback (`app/data/simulations_store.json`).

9. **Dynamic A2UI Visual Dashboard**
   - Payload spec builder (`app/a2ui.py`) and tools (`render_investment_dashboard`, `render_scenario_dashboard`, `render_market_dashboard`, `render_quantitative_dashboard`).
   - Renders an 8-section dynamic UI tree (Investor Summary, Financial Summary, Portfolio Allocation, Market Summary, Quantitative Analysis, Scenarios, Assumptions, Disclaimer).

---

## **Wired Google Cloud & ADK Services**

The project codebase (`app/` and `agents-cli-manifest.yaml`) implements and integrates the following core Google Cloud & ADK services:

- **Vertex AI Agent Engine (Reasoning Engine)**: Deployed backend hosting the ADK root agent powered by `gemini-2.5-flash`.
- **Google ADK Memory Service**: Cross-session memory system for investor context persistence (`app/memory_tools.py`).
- **Google Cloud Firestore & Local JSON Persistence**: Structured simulation document persistence (`app/storage_tools.py`).
- **Grounding RAG Layer**: File-based RAG search indexer over educational reference documents (`app/rag_tools.py`).
- **Controlled Code Execution Engine**: Sandboxed Python math execution engine for quantitative risk analysis (`app/quant_tools.py`).
- **A2UI Interactive Presentation**: UI Widget spec renderer (`app/a2ui_tools.py`).

*(Note: Live market APIs, image generation, and live brokerage transactions are explicitly excluded per safety guidelines.)*

---

## **Project Architecture & Flow**

```text
User Input ──► ADK Root Agent (gemini-2.5-flash)
                   │
                   ├──► Profiler & Financial Analysis Engine (Pydantic / Python)
                   ├──► Synthetic Market Intelligence (CSV / Trend Math)
                   ├──► Portfolio Architect Engine (Deterministic Allocation)
                   ├──► Grounded RAG Layer (Markdown Search / Grounded Explanations)
                   ├──► Quantitative Execution (Sandboxed Math Sandbox)
                   ├──► What-If Scenario Simulator (Baseline Isolation Engine)
                   ├──► ADK Memory & Firestore Persistent Storage
                   └──► A2UI Dashboard Generator (UiWidget Spec Builder)
```

For detailed architecture diagrams and deterministic vs. generative matrix details, see [docs/architecture.md](docs/architecture.md).

---

## **Project Structure**

```text
investment-copilot/
├── app/
│   ├── __init__.py         # App and root_agent export
│   ├── agent.py            # Root Agent system prompt & tool declarations
│   ├── a2ui.py             # A2UI payload builder & UiWidget generator
│   ├── a2ui_tools.py       # FunctionTools for A2UI rendering
│   ├── tools.py            # Financial analysis & profiling tools
│   ├── profiler.py         # Profile extraction & state manager
│   ├── market.py           # Synthetic market data loader & trend math
│   ├── market_tools.py     # FunctionTools for market analysis
│   ├── portfolio.py        # Deterministic portfolio allocation engine
│   ├── portfolio_tools.py  # FunctionTools for portfolio architect
│   ├── scenarios.py        # Scenario creation & market shock engine
│   ├── scenario_tools.py   # FunctionTools for What-If simulator
│   ├── knowledge.py        # RAG search engine & document indexer
│   ├── rag_tools.py        # FunctionTools for RAG search
│   ├── quant.py            # Sandboxed Python execution & quantitative math engine
│   ├── quant_tools.py      # FunctionTools for quantitative risk analysis
│   ├── memory.py           # ADK Memory engine
│   ├── memory_tools.py     # FunctionTools for cross-session memory
│   ├── storage.py          # Firestore / local persistent JSON storage engine
│   ├── storage_tools.py    # FunctionTools for simulation persistence
│   ├── schema.py           # Pydantic schemas & inconsistency validator
│   ├── knowledge_base/     # Synthetic educational Markdown reference docs
│   └── data/               # Synthetic market CSVs & storage files
├── docs/
│   ├── architecture.md     # System architecture documentation
│   ├── demo_script.md      # Presentation script walkthrough
│   ├── demo_recording.webm # Raw WebM video recording
│   └── demo.gif            # Optimized looping GIF demo
├── tests/
│   ├── integration/        # Server, agent, and evaluation integration tests
│   └── unit/               # Unit tests across all engine components
├── pyproject.toml          # uv / Python project configuration
├── agents-cli-manifest.yaml# ADK agent manifest
└── README.md               # Quickstart & system documentation
```

---

## **Setup & Local Execution**

### **1. Install Dependencies**
```bash
agents-cli install
```
Or using `uv`:
```bash
uv sync
```

### **2. Environment Variables**
Ensure `.env` contains valid GCP project settings for Gemini API and ADK:
```env
GOOGLE_GENAI_USE_VERTEXAI="true"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-east1"
```

### **3. Run ADK Development Server & Playground**
Launch local ADK development server:
```bash
agents-cli playground
```
Access the ADK Web UI via the local server address displayed in the terminal output to converse interactively with **Investment Copilot**.

---

## **Running Tests & Quality Checks**

Run the complete 118-test automated suite:
```bash
uv run pytest tests/
```

Run comprehensive linter & quality checks:
```bash
agents-cli lint
```
(Executes `ruff check .`, `ruff format . --check`, `codespell`, and `ty check .`).

---

## **Demonstration & Presentation**

To review the 5–10 minute presentation script featuring fictional investor Alex, see [docs/demo_script.md](docs/demo_script.md).

---

## **Educational Limitations & Safety**

- **Educational Simulation Scope**: Designed strictly as an educational tool demonstrating AI agent capabilities.
- **No Real Advice**: Percentages and returns do NOT constitute real-world financial, tax, or investment advice.
- **No Real Execution**: No live market data feeds, stock ticker recommendations, or brokerage account integrations are included.
- **Synthetic Data**: All prices, returns, and volatilities are derived from synthetic reference files.
