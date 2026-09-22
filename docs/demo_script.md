# Investment Copilot — 5-10 Minute Demonstration Script

This document provides a complete, step-by-step walkthrough script for presenting the **Investment Copilot** — an educational AI portfolio simulator built with Google ADK (Agent Development Kit).

> [!IMPORTANT]
> **EDUCATIONAL BOUNDARY REMINDER**:
> Investment Copilot is strictly an educational simulation operating on synthetic reference datasets. It does **NOT** provide real-world personalized financial advice, recommend actual stock/ETF tickers, guarantee investment returns, or connect to brokerage accounts.

---

## **Demo Overview & Fictional Persona**

- **Target Persona**: **Alex** (32 years old, Tech Professional)
- **Monthly Income**: ₹150,000
- **Monthly Expenses**: ₹70,000
- **Current Emergency Savings**: ₹800,000
- **Monthly Investment Amount**: ₹40,000
- **Investment Goal**: Long-Term Wealth Creation
- **Investment Horizon**: 7 Years
- **Risk Tolerance**: Moderate
- **Liquidity Requirement**: Low

---

## **Step-by-Step Demonstration Flow**

### **Phase 1: Introduction & Educational Boundary (30 Seconds)**

**Presenter Prompt to Audience / Evaluators**:
> *"Welcome to Investment Copilot! Built on Google ADK with Gemini 2.5 Flash, Investment Copilot is an educational AI portfolio simulator designed to teach investor profiling, deterministic portfolio construction, quantitative risk analysis, and scenario testing over controlled synthetic market datasets."*

---

### **Phase 2: Conversational Investor Profiling & Financial Health (1.5 Minutes)**

**Step 1: Start Conversation & Provide Alex's Details**
- **User Prompt**:
  ```text
  Hi! I want to set up an investment simulation for a 32-year-old tech professional named Alex. Alex earns ₹150,000 per month, spends ₹70,000, has ₹800,000 in savings, wants to invest ₹40,000 monthly for long-term wealth creation over 7 years, has a Moderate risk tolerance, and low liquidity needs.
  ```
- **What the Agent Does**:
  1. Calls `save_profile_fields` to register Alex's details.
  2. Runs `check_inconsistencies` (verifying income > expenses and investment capacity <= surplus).
  3. Executes `calculate_monthly_surplus`, `calculate_emergency_fund`, and `calculate_annual_investment_capacity`.
  4. Calls `finalize_investor_profile`.
- **Expected Important Outputs**:
  - Net monthly cash flow surplus: **₹80,000**
  - Target 6-month emergency fund: **₹420,000** (Current savings of ₹800,000 exceeds target by ₹380,000)
  - Annual investment capacity: **₹480,000**
  - Confirmation of complete profile with zero financial inconsistencies.

---

### **Phase 3: Synthetic Market Intelligence (1 Minute)**

- **User Prompt**:
  ```text
  Can you show me the current synthetic market overview and analyze the trend for the broad equity index?
  ```
- **What the Agent Does**:
  1. Calls `get_market_overview` to fetch synthetic performance across 9 assets.
  2. Calls `analyze_asset_trend("BROAD_EQUITY_INDEX")` to extract 1-month/1-year returns, volatility, and trend classification.
- **Expected Important Outputs**:
  - Synthetic asset count: **9 assets** across Broad Equity, Large Cap, Mid Cap, Fixed Income, Gold, International, Cash/Liquid.
  - `BROAD_EQUITY_INDEX` classification: Bullish / Growth (1-year synthetic return ~12.5%, annual volatility ~15.2%).
  - Synthetic data label clearly displayed.

---

### **Phase 4: Deterministic Illustrative Portfolio Allocation (1 Minute)**

- **User Prompt**:
  ```text
  Generate an illustrative asset-class allocation for Alex based on this moderate risk profile and 7-year horizon.
  ```
- **What the Agent Does**:
  1. Calls `calculate_illustrative_allocation("Moderate", horizon_years=7, liquidity="Low", monthly_amount=40000)`.
  2. Applies `adjust_allocation_for_market_conditions`.
  3. Runs `analyze_illustrative_portfolio` to compute defensive vs growth breakdown.
- **Expected Important Outputs**:
  - **Equity (Broad/Large Cap)**: 45% (₹18,000/mo)
  - **Fixed Income (Bonds)**: 30% (₹12,000/mo)
  - **Gold**: 10% (₹4,000/mo)
  - **International Equity**: 10% (₹4,000/mo)
  - **Cash / Liquid**: 5% (₹2,000/mo)
  - **Total**: Exactly **100.0%** (₹40,000/mo).

---

### **Phase 5: Grounded RAG Educational Explanation (1 Minute)**

- **User Prompt**:
  ```text
  Why did the simulator allocate 45% to equity and 10% to gold for a moderate profile with a 7-year horizon?
  ```
- **What the Agent Does**:
  1. Calls `search_investment_knowledge("risk profiles moderate gold allocation 7 year horizon")`.
  2. Grounds response strictly on retrieved reference documents (`risk_profiles.md`, `asset_classes.md`, `portfolio_assumptions.md`).
  3. Cites exact Markdown document filenames.
- **Expected Important Outputs**:
  - Grounded explanation citing `risk_profiles.md` (Moderate balance between growth and capital preservation) and `asset_classes.md` (Gold acts as a non-correlated inflation hedge).
  - Explicit non-hallucination guarantee.

---

### **Phase 6: Sandboxed Quantitative Risk Analysis (1 Minute)**

- **User Prompt**:
  ```text
  Run a quantitative risk analysis on Alex's portfolio allocation, including expected return, volatility, max drawdown, and asset correlations.
  ```
- **What the Agent Does**:
  1. Calls `analyze_portfolio_quantitatively` or `execute_quantitative_analysis`.
  2. Runs sandboxed Python code over synthetic return matrices.
- **Expected Important Outputs**:
  - Asset-weighted synthetic return: **~8.72%**
  - Asset-weighted synthetic volatility: **~11.45%**
  - Max drawdown: **-21.50%**
  - Low correlation between Fixed Income (Bonds) and Broad Equity (0.15), confirming asset diversification.

---

### **Phase 7: Non-Destructive What-If Scenarios & Isolation (1.5 Minutes)**

- **User Prompt**:
  ```text
  What if Alex increases monthly investment from ₹40,000 to ₹60,000? Also, simulate a hypothetical 25% drop in equity markets. Compare this scenario to Alex's baseline.
  ```
- **What the Agent Does**:
  1. Calls `create_scenario("Alex_Higher_Inv", {"monthly_investment_amount": 60000})`.
  2. Calls `simulate_market_shock("Alex_Equity_Drop", shock_asset_class="Equity", shock_percentage=-25)`.
  3. Calls `compare_scenario_to_baseline`.
- **Expected Important Outputs**:
  - **Baseline Untouched**: Baseline remains ₹40,000/mo, 45% Equity, Moderate risk.
  - **Scenario Allocation**: Shows updated monthly currency breakdowns (e.g. ₹60,000/mo allocation totaling 100%).
  - **Side-by-side Comparison**: Highlights surplus utilization and defensive tilt under synthetic market shock.

---

### **Phase 8: Persistence, Cross-Session Memory & A2UI Dashboard (1.5 Minutes)**

- **User Prompt**:
  ```text
  Save this simulation as Alex_Baseline and render the complete A2UI Investment Dashboard.
  ```
- **What the Agent Does**:
  1. Calls `save_simulation("sim_alex_baseline", profile, portfolio, financials)`.
  2. Calls `save_investor_memory` for cross-session facts (`Alex`, `Moderate`, `7 years`).
  3. Calls `render_investment_dashboard`.
- **Expected Important Outputs**:
  - Structured storage saved confirmation in Firestore/local storage.
  - Full 8-Section A2UI JSON specification rendering Investor Summary, Financial Summary, Illustrative Allocation (100%), Synthetic Market Overview, Quantitative Risk Metrics, Scenarios, Assumptions, and Safety Disclaimer.

---

## **Key Feature Demonstration Checklist**

| Feature Area | Demonstration Command / Question | Key Assertion / Verification |
| :--- | :--- | :--- |
| **Deterministic Engine** | `Generate portfolio allocation` | Allocations derived via Python matrix math; percentages sum to 100%. |
| **Scenario Isolation** | `What if monthly investment is ₹60,000?` | Baseline profile remains untouched at ₹40,000. |
| **RAG Grounding** | `Why did the simulator select this asset mix?` | Answers cite synthetic `.md` docs; zero hallucinated stock tickers. |
| **Quant Sandbox** | `Run quantitative portfolio analysis` | Executes safe sandboxed Python returns, volatility, drawdown calculations. |
| **ADK Cross-Session Memory** | `Load Alex simulation` | Recalls stable investor facts and stored baseline simulations. |
| **A2UI Visual Dashboard** | `Show A2UI dashboard` | Renders dynamic 8-section visual UI component payload. |
| **Safety Guardrails** | All prompts | Educational disclaimers present; strictly no real-money or ticker recommendations. |

---

## **Frequently Asked Questions for Presenters**

1. **Q: Is Investment Copilot giving real financial advice?**
   - *A: No. Investment Copilot is strictly an educational simulation built for demonstrating AI agent capabilities with ADK. It uses synthetic market data and deterministic allocation models.*
2. **Q: How does the deterministic allocation engine work?**
   - *A: Rather than allowing the LLM to invent percentages, Python code maps risk tolerance, horizon, and liquidity parameters to fixed asset-class weights, ensuring 100% mathematical integrity.*
3. **Q: How does RAG prevent hallucinations?**
   - *A: The agent searches controlled Markdown documentation files (`app/knowledge_base/`). If a rule is absent, the agent explicitly states that the concept is undefined in the knowledge base.*
