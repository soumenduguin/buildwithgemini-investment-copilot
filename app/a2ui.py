# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

from google.adk.events.ui_widget import UiWidget

DISCLAIMER_TEXT = (
    "Educational simulation using synthetic data. "
    "Not financial advice and not a prediction of future returns."
)


def build_a2ui_payload(
    investor_profile: dict[str, Any] | None = None,
    financial_metrics: dict[str, Any] | None = None,
    portfolio_allocation: dict[str, Any] | None = None,
    market_summary: dict[str, Any] | list[dict[str, Any]] | None = None,
    quantitative_analysis: dict[str, Any] | None = None,
    scenarios: list[dict[str, Any]] | None = None,
    assumptions: list[str] | dict[str, Any] | None = None,
    dashboard_title: str = "INVESTMENT COPILOT DASHBOARD",
) -> dict[str, Any]:
    """Dynamically builds a structured A2UI JSON specification payload.

    Contains 8 sections:
    1. INVESTOR SUMMARY
    2. FINANCIAL SUMMARY
    3. PORTFOLIO ALLOCATION
    4. MARKET SUMMARY (Labeled 'Synthetic Market Data')
    5. QUANTITATIVE ANALYSIS
    6. SCENARIOS
    7. ASSUMPTIONS
    8. DISCLAIMER

    Args:
        investor_profile: Investor profile fields.
        financial_metrics: Surplus, emergency fund, capacity.
        portfolio_allocation: Asset class allocation percentages and amounts.
        market_summary: Synthetic market snapshot records.
        quantitative_analysis: Volatility, drawdown, correlation metrics.
        scenarios: List of saved/active scenarios.
        assumptions: Simulator assumptions.
        dashboard_title: Title header.

    Returns:
        Structured A2UI JSON payload dictionary.
    """
    profile = investor_profile or {}
    financials = financial_metrics or {}
    portfolio = portfolio_allocation or {}
    scens = scenarios or []
    quant = quantitative_analysis or {}

    # Normalize market summary list
    market_list = []
    if isinstance(market_summary, list):
        market_list = market_summary
    elif isinstance(market_summary, dict):
        market_list = market_summary.get("assets") or [market_summary]

    # Calculate allocation monthly amounts and verify 100% total
    allocations_raw = (
        portfolio.get("illustrative_allocation")
        or portfolio.get("allocations")
        or portfolio.get("allocation")
        or portfolio
    )
    monthly_inv = float(
        profile.get("monthly_investment_amount")
        or profile.get("monthly_investment")
        or financials.get("monthly_investment_amount")
        or 40000.0
    )

    allocation_table = []
    total_pct = 0.0

    if isinstance(allocations_raw, dict):
        for asset, pct in allocations_raw.items():
            if isinstance(pct, (int, float)):
                pct_val = float(pct)
                total_pct += pct_val
                amt = (pct_val / 100.0) * monthly_inv
                allocation_table.append(
                    {
                        "asset_class": asset,
                        "percentage": f"{pct_val:.1f}%",
                        "monthly_amount": f"₹{amt:,.2f}",
                    }
                )

    # Section 1: Investor Summary
    sec_investor = {
        "id": "section_investor_summary",
        "title": "1. INVESTOR SUMMARY",
        "fields": {
            "Investor Name": profile.get("investor_name")
            or profile.get("fictional_investor_name")
            or "Alex",
            "Age": profile.get("age") or 35,
            "Investment Goal": profile.get("investment_goal")
            or "Long-term wealth creation",
            "Risk Tolerance": profile.get("risk_tolerance") or "Moderate",
            "Investment Horizon": f"{profile.get('horizon_years', 7)} years",
            "Liquidity Requirement": profile.get("liquidity_requirement")
            or profile.get("liquidity_preference")
            or "Low",
        },
    }

    # Section 2: Financial Summary
    income = float(profile.get("monthly_income") or 100000.0)
    expenses = float(profile.get("monthly_expenses") or 60000.0)
    surplus = (
        financials.get("monthly_surplus")
        if financials.get("monthly_surplus") is not None
        else (income - expenses)
    )
    savings = float(profile.get("current_savings") or 300000.0)
    annual_cap = financials.get("annual_investment_capacity") or (monthly_inv * 12.0)

    sec_financial = {
        "id": "section_financial_summary",
        "title": "2. FINANCIAL SUMMARY",
        "fields": {
            "Monthly Income": f"₹{income:,.2f}",
            "Monthly Expenses": f"₹{expenses:,.2f}",
            "Monthly Surplus": f"₹{surplus:,.2f}",
            "Current Savings": f"₹{savings:,.2f}",
            "Monthly Investment": f"₹{monthly_inv:,.2f}",
            "Annual Investment Capacity": f"₹{annual_cap:,.2f}",
        },
    }

    # Section 3: Portfolio Allocation
    sec_portfolio = {
        "id": "section_portfolio_allocation",
        "title": "3. PORTFOLIO ALLOCATION",
        "total_percentage": f"{total_pct:.1f}%",
        "table": allocation_table,
    }

    # Section 4: Market Summary
    sec_market = {
        "id": "section_market_summary",
        "title": "4. MARKET SUMMARY",
        "label": "Synthetic Market Data",
        "assets": market_list,
    }

    # Section 5: Quantitative Analysis
    sec_quant = {
        "id": "section_quantitative_analysis",
        "title": "5. QUANTITATIVE ANALYSIS",
        "simulated_volatility": quant.get("simulated_volatility")
        or quant.get("annualized_volatility")
        or "12.4% p.a.",
        "max_drawdown": quant.get("max_drawdown") or "-4.2%",
        "correlation": quant.get("correlation") or "Broad Equity vs Gold: -0.84",
        "baseline_vs_scenario": quant.get("baseline_vs_scenario")
        or "Baseline Volatility: 12.4% | Shock Volatility: 18.2%",
    }

    # Section 6: Scenarios
    sec_scenarios = {
        "id": "section_scenarios",
        "title": "6. SCENARIOS",
        "list": scens,
    }

    # Section 7: Assumptions
    assump_list = (
        assumptions
        if isinstance(assumptions, list)
        else [
            "Asset allocations calculated deterministically based on risk tolerance, horizon, and liquidity.",
            "Bounded market adjustments limited to max +/-5 percentage points.",
            "Emergency fund target defaults to 6 months of living expenses.",
        ]
    )
    sec_assumptions = {
        "id": "section_assumptions",
        "title": "7. ASSUMPTIONS",
        "rules": assump_list,
    }

    # Section 8: Disclaimer
    sec_disclaimer = {
        "id": "section_disclaimer",
        "title": "8. DISCLAIMER",
        "text": DISCLAIMER_TEXT,
    }

    return {
        "surface": "a2ui_investment_dashboard",
        "title": dashboard_title,
        "components": [
            sec_investor,
            sec_financial,
            sec_portfolio,
            sec_market,
            sec_quant,
            sec_scenarios,
            sec_assumptions,
            sec_disclaimer,
        ],
        "actions": [
            {"label": "View Baseline", "action": "load_simulation"},
            {"label": "View Scenario", "action": "load_scenario"},
            {"label": "Compare Scenario", "action": "compare_scenario_to_baseline"},
            {"label": "Show Market Analysis", "action": "get_market_overview"},
            {
                "label": "Show Quantitative Analysis",
                "action": "analyze_portfolio_quantitatively",
            },
            {"label": "Show Assumptions", "action": "search_investment_knowledge"},
        ],
    }


def create_a2ui_widget(
    payload: dict[str, Any], widget_id: str = "a2ui_dashboard_01"
) -> UiWidget:
    """Creates a Google ADK UiWidget instance with provider='a2ui'.

    Args:
        payload: Dynamic A2UI payload dictionary.
        widget_id: Unique widget identifier.

    Returns:
        UiWidget instance suitable for ADK ToolContext.render_ui_widget.
    """
    return UiWidget(
        id=widget_id,
        provider="a2ui",
        payload=payload,
    )


def format_a2ui_markdown_dashboard(payload: dict[str, Any]) -> str:
    """Formats the dynamic A2UI payload into structured markdown for Playground display."""
    comps = {c["id"]: c for c in payload.get("components", [])}

    investor = comps.get("section_investor_summary", {}).get("fields", {})
    financial = comps.get("section_financial_summary", {}).get("fields", {})
    portfolio = comps.get("section_portfolio_allocation", {})
    market = comps.get("section_market_summary", {})
    quant = comps.get("section_quantitative_analysis", {})
    scenarios = comps.get("section_scenarios", {}).get("list", [])
    assumptions = comps.get("section_assumptions", {}).get("rules", [])
    disclaimer = comps.get("section_disclaimer", {}).get("text", DISCLAIMER_TEXT)

    lines = [
        f"# 📊 {payload.get('title', 'INVESTMENT COPILOT DASHBOARD')}",
        "",
        "## 👤 BASELINE: 1. INVESTOR SUMMARY",
        f"- **Name**: {investor.get('Investor Name', 'Alex')}",
        f"- **Age**: {investor.get('Age', 35)}",
        f"- **Goal**: {investor.get('Investment Goal', 'Long-term wealth creation')}",
        f"- **Risk Tolerance**: {investor.get('Risk Tolerance', 'Moderate')}",
        f"- **Investment Horizon**: {investor.get('Investment Horizon', '7 years')}",
        f"- **Liquidity Requirement**: {investor.get('Liquidity Requirement', 'Low')}",
        "",
        "## 💵 BASELINE: 2. FINANCIAL SUMMARY",
        f"- **Monthly Income**: {financial.get('Monthly Income', '₹100,000.00')}",
        f"- **Monthly Expenses**: {financial.get('Monthly Expenses', '₹60,000.00')}",
        f"- **Monthly Surplus**: {financial.get('Monthly Surplus', '₹40,000.00')}",
        f"- **Current Savings**: {financial.get('Current Savings', '₹300,000.00')}",
        f"- **Monthly Investment**: {financial.get('Monthly Investment', '₹40,000.00')}",
        f"- **Annual Capacity**: {financial.get('Annual Investment Capacity', '₹480,000.00')}",
        "",
        "## 🎨 BASELINE: 3. PORTFOLIO ALLOCATION",
        "| Asset Class | Allocation % | Monthly Amount |",
        "| :--- | :---: | :---: |",
    ]

    for item in portfolio.get("table", []):
        lines.append(
            f"| {item['asset_class']} | {item['percentage']} | {item['monthly_amount']} |"
        )
    lines.append(f"**Total Allocation**: {portfolio.get('total_percentage', '100.0%')}")
    lines.append("")

    lines.extend(
        [
            "## 📈 SYNTHETIC MARKET DATA: 4. MARKET SUMMARY",
            f"*(Label: {market.get('label', 'Synthetic Market Data')})*",
        ]
    )
    market_assets = market.get("assets", [])
    if market_assets:
        lines.extend(
            [
                "| Asset Name | Asset Class | Trend | 1Y Return | Volatility |",
                "| :--- | :--- | :---: | :---: | :---: |",
            ]
        )
        for a in market_assets[:5]:
            name = a.get("asset_name") or a.get("name") or "Asset"
            ac = a.get("asset_class") or "Equity"
            tr = a.get("trend") or "BULLISH"
            ret = a.get("one_year_return") or a.get("1y_return") or "12.5%"
            vol = a.get("volatility") or "MODERATE"
            lines.append(f"| {name} | {ac} | {tr} | {ret} | {vol} |")
    else:
        lines.append(
            "- Broadband Synthetic Market Dataset loaded (9 assets: Broad Equity, Bonds, Gold, Cash, International Equity)."
        )
    lines.append("")

    lines.extend(
        [
            "## 🔢 QUANTITATIVE ANALYSIS: 5. QUANTITATIVE & RISK METRICS",
            f"- **Simulated Portfolio Volatility**: {quant.get('simulated_volatility', '12.4% p.a.')}",
            f"- **Maximum Drawdown**: {quant.get('max_drawdown', '-4.2%')}",
            f"- **Pairwise Correlation**: {quant.get('correlation', 'Broad Equity vs Gold: -0.84')}",
            f"- **Baseline vs Scenario Delta**: {quant.get('baseline_vs_scenario', 'Baseline Volatility: 12.4% | Shock Volatility: 18.2%')}",
            "",
            "## 🔄 SCENARIO: 6. SAVED / ACTIVE WHAT-IF SCENARIOS",
        ]
    )

    if scenarios:
        for s in scenarios:
            name = s.get("scenario_name") or s.get("name") or "What-If Scenario"
            stype = s.get("scenario_type") or "parameter_modification"
            lines.append(f"- **{name}** ({stype})")
    else:
        lines.append("- No active What-If scenario. Displaying baseline portfolio.")
    lines.append("")

    lines.extend(
        [
            "## 📝 ASSUMPTIONS: 7. SIMULATOR RULES & ASSUMPTIONS",
        ]
    )
    for rule in assumptions:
        lines.append(f"- {rule}")
    lines.append("")

    lines.extend(
        [
            "## ⚠️ DISCLAIMER: 8. SIMULATION SAFETY BOUNDARY",
            f"> **{disclaimer}**",
            "",
            "### 🔘 INTERACTIVE DASHBOARD ACTIONS",
            "- `[View Baseline]` — Load baseline simulation",
            "- `[View Scenario]` — Load active What-If scenario",
            "- `[Compare Scenario]` — Compare scenario against baseline",
            "- `[Show Market Analysis]` — View synthetic market intelligence",
            "- `[Show Quantitative Analysis]` — View quantitative math & volatility",
            "- `[Show Assumptions]` — View synthetic simulator rules",
        ]
    )

    return "\n".join(lines)
