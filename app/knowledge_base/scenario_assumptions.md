# What-If Scenario Assumptions in Investment Copilot

> **DISCLAIMER:** *Synthetic Educational Investment Simulation Knowledge ONLY. This document describes the exact implementation rules for the Step 5 What-If Scenario Simulator.*

## Principles of What-If Scenario Simulation

The Step 5 What-If Scenario Simulator provides a non-destructive sandbox for users to evaluate hypothetical parameter modifications and market shocks without altering stored baseline data.

---

## 1. Non-Destructive Baseline Preservation

- **Immutability:** The stored baseline investor profile (`tool_context.state["investor_profile_data"]`) and baseline synthetic market dataset are **NEVER** modified, overwritten, or mutated by scenario tools.
- **Reference Copying:** Each scenario makes a deep copy of baseline parameters, applies requested changes, and evaluates the scenario independently.

---

## 2. Scenario Isolation & Storage

- **Session State Storage:** Scenarios are indexed in session state (`tool_context.state["scenarios"]`) as independent objects (`scenario_1`, `scenario_2`, etc.).
- **Independent Baseline Origin:** By default, every scenario evaluates parameter changes relative to the active baseline profile, preventing unintended error propagation across hypothetical tests.

---

## 3. Supported Scenario Parameter Modifications

The scenario simulator supports modifications to any combination of the following parameters:
- `monthly_income` (Hypothetical monthly income)
- `monthly_expenses` (Hypothetical monthly expenses)
- `monthly_investment` (Hypothetical monthly investment contribution)
- `investment_horizon_years` (Hypothetical investment horizon in years)
- `risk_tolerance` ('Conservative', 'Moderate', 'Aggressive')
- `liquidity_requirement` ('Low', 'Medium', 'High')

---

## 4. Market Shock Simulation Rules

The simulator evaluates hypothetical asset-class shocks via `simulate_market_shock`:
- **Equity Shock (e.g. -25% Equity Crash):** Simulates acute equity drawdowns by elevating market volatility indicators ($> 20\%$), triggering defensive deterministic shifts (+3% to Debt from Equity).
- **Gold Shock (e.g. +10% Gold Surge):** Simulates commodity upside by activating bullish trend indicators, triggering a +2% shift to Gold from Cash/Liquid.
- **Baseline Market Isolation:** Underlying CSV market data files are never overwritten; shocks modify only transient indicators for the target scenario.

---

## 5. Scenario Comparison Mechanics

- **Baseline vs Scenario (`compare_scenario_to_baseline`):** Compares parameter values, financial metrics (surplus, emergency fund, annual capacity), asset allocations, and explicitly calculates deltas ($+ / -$).
- **Scenario vs Scenario (`compare_scenarios`):** Evaluates side-by-side asset allocation deltas between any two created scenarios (`scenario_2` minus `scenario_1`).

---

## 6. Limitations of Hypothetical Scenarios

- **Educational Projections:** Scenarios evaluate deterministic model shifts and do not predict future market prices, economic cycles, or real inflation.
- **No Brokerage Execution:** Scenarios are conceptual models for financial literacy and decision-making education only.
