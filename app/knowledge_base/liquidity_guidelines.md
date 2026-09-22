# Liquidity Guidelines in Investment Copilot Simulation

> **DISCLAIMER:** *Synthetic Educational Investment Simulation Knowledge ONLY. This document defines internal simulation rules for liquidity requirements. It does NOT constitute personalized financial planning advice.*

## Overview of Liquidity Requirements

In the Investment Copilot simulation, liquidity requirement reflects an investor's need for access to cash over short-to-medium time horizons. The simulator supports three liquidity requirement levels:
1. Low
2. Medium / Moderate
3. High

---

## 1. Low Liquidity Requirement

### Definition
The investor has sufficient separate emergency savings or stable short-term cash flow, allowing the vast majority of contributions to remain committed to long-term investment assets.

### Simulator Rule
- **Adjustment:** No additional shift toward liquid assets (0.0% adjustment).
- **Cash/Liquid Allocation:** Retains standard baseline allocation (5.0% for Moderate/Aggressive, 10.0% for Conservative).

---

## 2. Medium / Moderate Liquidity Requirement

### Definition
The investor may require periodic access to capital or foresees potential short-to-medium-term expenditures within 1–3 years.

### Simulator Rule
- **Adjustment:** +5.0% shift to **Cash/Liquid**.
- **Offset:** Derived by deducting 5.0% from **Debt**.
- **Effect:** Increases liquid buffer to 10.0% (for Moderate/Aggressive) or 15.0% (for Conservative) while preserving full growth equity exposure.

---

## 3. High Liquidity Requirement

### Definition
The investor anticipates significant capital withdrawals, upcoming large expenditures (e.g. house purchase, education tuition), or maintains a elevated preference for liquid cash safety.

### Simulator Rule
- **Adjustment:** +10.0% shift to **Cash/Liquid**.
- **Offset:** Derived by deducting 5.0% from **Debt** and 5.0% from **Equity**.
- **Effect:** Significantly elevates immediate cash/liquid allocation to 15.0% (for Moderate/Aggressive) or 20.0% (for Conservative), reducing both growth and fixed-income exposure proportionally.

---

## Liquidity Adjustment Summary Table

| Liquidity Requirement | Cash/Liquid Shift | Shift Source (Deducted From) | Impact on Portfolio |
| :--- | :--- | :--- | :--- |
| **Low** | +0.0% | None | Standard baseline cash allocation maintained |
| **Medium** | +5.0% | -5.0% Debt | Moderate liquidity buffer added without reducing Equity |
| **High** | +10.0% | -5.0% Debt, -5.0% Equity | High liquidity buffer added; defensive and growth assets reduced |
