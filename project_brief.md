# Project Brief: Investment Copilot

## Overview
**Investment Copilot** is an educational AI Portfolio Simulator built using the Google Agent Development Kit (ADK) and Google Gemini. The application interviews a fictional investor, builds a structured investor profile, detects missing data and financial inconsistencies, and will eventually analyze synthetic market data to simulate illustrative investment allocations.

> **IMPORTANT DISCLAIMER**
> **Investment Copilot is an educational training project.** It does **NOT** use real financial data, real user financial information, real brokerage accounts, trading systems, or real-money transactions. All data, profiles, and scenarios are strictly fictitious simulations for learning and demonstration purposes.

---

## Application Goals & Roadmap

### Current Focus (First Version)
- **Investor Profiler Agent**: A conversational AI agent that interviews a fictional investor to gather a complete investor profile.
- **State Management & Validation**: Session-scoped tracking of collected profile fields, missing field detection, and financial/logical inconsistency checks.
- **Structured Profile Output**: Generates a standardized JSON/Pydantic `InvestorProfile` object upon complete data collection.
- **Playground & CLI Compatibility**: Runnable locally with `agents-cli run` and standard ADK Playground (`agents-cli playground`).

### Step 2 (Completed): Financial Analysis Tools
- **`calculate_monthly_surplus`**: Calculates `monthly_income - monthly_expenses`, returns net cash flow status (`POSITIVE`, `BREAK_EVEN`, `NEGATIVE`).
- **`calculate_emergency_fund`**: Calculates target emergency fund (`monthly_expenses * number_of_months`, defaulting to 6 months).
- **`calculate_annual_investment_capacity`**: Calculates annual investment capacity (`monthly_investment * 12`).
- **Safety Boundary**: Strict rule prohibiting specific product, stock, ETF, or cryptocurrency recommendations.

### Step 3 (Completed): Market Intelligence & Analytics
- **Synthetic Market Dataset (`app/data/synthetic_market_data.csv`)**: 9 fictional asset records across broad equity, large-cap, mid-cap, bonds, gold, international equity, cash, tech sector, and real estate.
- **`get_market_snapshot`**: Filters synthetic asset records by name or asset class.
- **`analyze_asset_trend`**: Deterministic trend analysis (`BULLISH_POSITIVE`, `BEARISH_NEGATIVE`, `NEUTRAL_MIXED`), momentum, volatility, and 52-week price range position.
- **`compare_assets`**: Side-by-side comparative metrics for multiple requested asset names.
- **`get_market_overview`**: High-level summary of dataset counts, asset classes, trend tallies, and extreme return/volatility assets.
- **Safety Boundary**: Strict rule prohibiting security buy/sell recommendations, portfolio allocation percentages, or brokerage execution.

### Step 4 (Completed): Portfolio Architect & Allocation Engine
- **`calculate_illustrative_allocation`**: Deterministic asset allocation across Equity, Debt, Gold, International Equity, and Cash/Liquid based on risk tolerance, horizon, liquidity, and monthly investment amount.
- **`adjust_allocation_for_market_conditions`**: Bounded deterministic market adjustments (max +-5 percentage points per asset class) based on synthetic market indicators.
- **`analyze_illustrative_portfolio`**: Evaluates growth vs defensive balance, monthly currency breakdown, and multi-asset diversification metrics.
- **Safety Boundary**: Strict prohibition of personalized financial advice, stock ticker recommendations, or return guarantees.

### Step 5 (Completed): What-If Scenario Simulator
- **`create_scenario`**: Non-destructively evaluates hypothetical investor parameter changes (monthly investment, income, expenses, horizon, risk, liquidity) without mutating stored baseline profile.
- **`simulate_market_shock`**: Simulates hypothetical asset class price/volatility shocks (e.g. -25% equity crash, +10% gold surge).
- **`compare_scenario_to_baseline` & `compare_scenarios`**: Side-by-side comparison of baseline vs scenario metrics, allocations, and parameter deltas.
- **`list_scenarios`**: Summarizes active session scenarios.

### Step 6 (Completed): RAG / Investment Knowledge Layer
- **Knowledge Base (`app/knowledge_base/`)**: 5 synthetic reference documents (`risk_profiles.md`, `asset_classes.md`, `liquidity_guidelines.md`, `portfolio_assumptions.md`, `scenario_assumptions.md`).
- **`search_investment_knowledge`**: ADK FunctionTool retrieving source document passages for explanation grounding, labeled as *"Synthetic Educational Investment Simulation Knowledge"*.
- **Conflict Handling**: Explicitly state when a rule is undefined without hallucinating external rules.
- **Strict Isolation**: RAG provides explanations without overriding deterministic Python allocations or scenario calculations.

### Step 7 (Completed): Quantitative Analysis with Code Execution
- **`app/quant.py`**: Math engine & sandboxed Python execution context pre-loaded with synthetic market return series and portfolio data.
- **Quantitative Tools (`app/quant_tools.py`)**:
  - `execute_quantitative_analysis`: Dynamic sandboxed Python execution tool.
  - `analyze_historical_returns`: Average, cumulative, and monthly return analysis.
  - `analyze_volatility`: Standard deviation, relative volatility, weighted portfolio volatility.
  - `analyze_drawdowns`: Peak-to-trough price series and maximum drawdown %.
  - `analyze_correlations`: Pairwise asset correlation matrix.
  - `analyze_portfolio_quantitatively`: Weighted returns, volatilities, asset class contribution %, diversification ratio.
  - `compare_scenarios_quantitatively`: Baseline vs scenario quantitative delta comparison.
- **Safety & Disclaimers**: Operating strictly on synthetic simulation data with mandatory `LIMITATION` disclaimers.

### Step 8 (Completed): Cross-Session Memory
- **File-Backed Memory Service (`app/memory.py`)**: Implements Google ADK `BaseMemoryService` persisting stable investor facts as JSON in `app/data/investor_memory.json` across session and server restarts.
- **ADK Memory Tools (`app/memory_tools.py`)**:
  - `save_investor_memory`: Tool to explicitly save stable investor contextual facts (name, goal, risk tolerance, horizon years, liquidity preference, simulation preferences).
  - `recall_investor_memory`: Tool to query and retrieve remembered investor facts across sessions.
  - `load_memory` & `preload_memory`: Standard ADK memory tools integrated on `root_agent`.
- **Memory Boundaries**: Memory retains strictly stable contextual parameters and does NOT store temporary What-If scenario changes, calculated portfolios, market datasets, bank details, or real personal financial data.
- **Precedence**: Active current session inputs take precedence over remembered facts for current calculations.

### Step 9 (Completed): Persistent Simulation Storage
- **Dual-Mode Persistence Engine (`app/storage.py`)**:
  - Primary: Cloud Firestore database client (`google.cloud.firestore`) when a Firestore database instance is provisioned.
  - Fallback: Local persistent JSON file store (`app/data/simulations_store.json`) when Firestore is unprovisioned, offline, or returns authentication/connection errors.
- **Data Models**:
  - `InvestorSimulation`: Structured record containing `simulation_id`, `fictional_investor_name`, `created_at`, `updated_at`, `investor_profile`, `baseline_financial_metrics`, `baseline_portfolio`, and `assumptions`.
  - `ScenarioRecord`: Structured record containing `scenario_id`, `simulation_id`, `scenario_name`, `scenario_type`, `changed_parameters`, `baseline_values`, `scenario_values`, `scenario_allocation`, `allocation_differences`, and `created_at`.
- **ADK Storage Tools (`app/storage_tools.py`)**:
  - `save_simulation`: Persists complete fictional investor simulation records.
  - `load_simulation`: Retrieves stored simulations by `simulation_id` or investor name across sessions.
  - `list_simulations`: Returns summaries of all saved simulations.
  - `save_scenario`: Persists What-If scenarios linked to a simulation ID.
  - `load_scenario`: Retrieves stored scenarios by `scenario_id`.
  - `list_scenarios`: Returns stored scenarios linked to a simulation ID.
  - `delete_simulation`: Safely deletes simulation records and associated scenarios.
- **Memory vs Firestore Distinction**:
### Step 10 (Completed): A2UI Investment Dashboard
- **A2UI Payload Generator (`app/a2ui.py`)**:
  - Dynamically builds structured A2UI specifications rendered visually in ADK Playground and CLI environments.
  - Consists of 8 distinct sections:
    1. `INVESTOR SUMMARY` (Name, Age, Goal, Risk Tolerance, Horizon, Liquidity)
    2. `FINANCIAL SUMMARY` (Income, Expenses, Surplus, Savings, Investment Amount, Annual Capacity)
    3. `PORTFOLIO ALLOCATION` (Table of asset classes, percentages, monthly currency amounts, 100% total validation)
    4. `MARKET SUMMARY` (Asset overview explicitly labeled *"Synthetic Market Data"*)
    5. `QUANTITATIVE ANALYSIS` (Volatility, Max Drawdown, Correlations, Baseline vs Scenario Delta)
    6. `SCENARIOS` (Active and saved What-If scenarios)
    7. `ASSUMPTIONS` (Deterministic allocation and simulator rules)
    8. `DISCLAIMER` (*"Educational simulation using synthetic data. Not financial advice and not a prediction of future returns."*)
- **ADK A2UI Dashboard Tools (`app/a2ui_tools.py`)**:
  - `render_investment_dashboard`: Main tool rendering 8-section baseline simulation dashboard with `UiWidget(provider="a2ui")`.
  - `render_scenario_dashboard`: Dashboard rendering baseline vs scenario comparison.
  - `render_market_dashboard`: Synthetic market intelligence visual dashboard.
  - `render_quantitative_dashboard`: Quantitative risk analysis visual dashboard.
- **Interactive Control Buttons**: Built-in A2UI action triggers mapped to backend agent tools (`View Baseline`, `View Scenario`, `Compare Scenario`, `Show Market Analysis`, `Show Quantitative Analysis`, `Show Assumptions`).
- **Visual Separation**: Clear visual distinctions between Baseline, Scenario, Synthetic Market Data, Quantitative Analysis, and Assumptions.
- **Regression Tested**: 100% test coverage with **102 / 102 passing unit tests**.

---

## Schema & Profile Fields

The `Investor Profiler Agent` collects and validates 10 core fields:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `investor_name` | String | Fictional investor name |
| `age` | Integer | Investor age in years (18–120) |
| `monthly_income` | Float | Monthly income in USD |
| `monthly_expenses` | Float | Monthly living expenses in USD |
| `current_savings` | Float | Current liquid savings / emergency fund in USD |
| `monthly_investment_amount` | Float | Monthly amount available for investment in USD |
| `investment_goal` | String | Financial/investment goal (e.g. Retirement, Home Purchase) |
| `horizon_years` | Integer | Investment time horizon in years (> 0) |
| `risk_tolerance` | String | Risk tolerance level (Low, Moderate, High) |
| `liquidity_requirement` | String | Liquidity requirement level (Low, Moderate, High) |

---

## Validation & Inconsistency Rules

The profiler automatically detects:
1. **Deficit spending**: Monthly expenses > Monthly income
2. **Excessive investment**: Monthly investment amount > Net monthly surplus (`monthly_income - monthly_expenses`)
3. **Invalid numerical values**: Negative values for financial metrics, age < 18 or > 120, horizon_years <= 0.
4. **Missing fields**: Identifies incomplete profiles and prompts the user conversationally.

---

## Project Directory Structure

```text
investment-copilot/
├── app/
│   ├── __init__.py         # App and root_agent export
│   ├── agent.py            # Investor Profiler root_agent & ADK App definition
│   ├── tools.py            # Step 1 ADK FunctionTools (save, check, finalize profile)
│   ├── schema.py           # Pydantic schema & inconsistency validation logic
│   ├── market.py           # Step 3 Synthetic market dataset engine
│   ├── market_tools.py     # Step 3 ADK Market Intelligence tools
│   ├── portfolio.py        # Step 4 Portfolio Architect allocation engine
│   ├── portfolio_tools.py  # Step 4 ADK Portfolio Architect tools
│   ├── scenarios.py        # Step 5 What-If Scenario Simulator engine
│   ├── scenario_tools.py   # Step 5 ADK Scenario tools
│   ├── knowledge.py        # Step 6 Synthetic RAG search engine
│   ├── rag_tools.py        # Step 6 ADK RAG search tool
│   ├── quant.py            # Step 7 Quantitative math & sandboxed Python engine
│   ├── quant_tools.py      # Step 7 ADK Quantitative tools
│   ├── memory.py           # Step 8 File-backed ADK BaseMemoryService engine
│   ├── memory_tools.py     # Step 8 ADK Memory tools
│   ├── storage.py          # Step 9 Dual-mode persistent storage engine (Firestore / JSON)
│   ├── storage_tools.py    # Step 9 ADK Storage tools
│   ├── data/               # Persistent data directory
│   │   ├── synthetic_market_data.csv  # Synthetic market dataset (9 assets)
│   │   ├── investor_memory.json       # Step 8 persistent memory store
│   │   └── simulations_store.json     # Step 9 persistent simulation store
│   └── knowledge_base/     # Step 6 Synthetic reference documents
├── tests/unit/             # Comprehensive unit test suite (92 tests passing)
├── project_brief.md        # Comprehensive project documentation (this file)
├── README.md               # User guide and getting started instructions
├── pyproject.toml          # Dependencies and Python tool configuration
└── agents-cli-manifest.yaml# Agents CLI manifest metadata
```


---

## Running Locally & ADK Playground

### 1. Execute single prompt / CLI turn
```bash
agents-cli run "Hi, I want to create a profile for an investor named Alex, age 35."
```

### 2. Multi-turn session resumption
```bash
agents-cli run "Monthly income is 8000 and expenses are 4000." --session-id <SESSION_ID>
```

### 3. Launch ADK Playground
```bash
agents-cli playground
```
This opens the web interface to interact conversationally with the `Investor Profiler Agent`.
