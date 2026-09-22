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

from app.a2ui import DISCLAIMER_TEXT, build_a2ui_payload
from app.a2ui_tools import (
    render_investment_dashboard,
    render_market_dashboard,
    render_quantitative_dashboard,
    render_scenario_dashboard,
)


def test_dashboard_renders_alex_baseline():
    """1. Verify dashboard renders with Alex's baseline investor summary."""
    res = render_investment_dashboard()
    assert res["status"] == "success"
    assert res["surface"] == "a2ui_investment_dashboard"
    payload = res["a2ui_payload"]

    investor_sec = next(
        c for c in payload["components"] if c["id"] == "section_investor_summary"
    )
    assert investor_sec["fields"]["Investor Name"] == "Alex"
    assert investor_sec["fields"]["Age"] == 35
    assert investor_sec["fields"]["Risk Tolerance"] == "Moderate"


def test_financial_summary_correctness():
    """2. Verify financial summary numbers match income, expenses, surplus, savings."""
    profile = {
        "monthly_income": 120000.0,
        "monthly_expenses": 70000.0,
        "monthly_investment_amount": 50000.0,
        "current_savings": 500000.0,
    }
    financials = {
        "monthly_surplus": 50000.0,
        "annual_investment_capacity": 600000.0,
    }

    res = render_investment_dashboard(
        investor_profile=profile, financial_metrics=financials
    )
    payload = res["a2ui_payload"]
    fin_sec = next(
        c for c in payload["components"] if c["id"] == "section_financial_summary"
    )

    assert fin_sec["fields"]["Monthly Income"] == "₹120,000.00"
    assert fin_sec["fields"]["Monthly Expenses"] == "₹70,000.00"
    assert fin_sec["fields"]["Monthly Surplus"] == "₹50,000.00"
    assert fin_sec["fields"]["Annual Investment Capacity"] == "₹600,000.00"


def test_portfolio_totals_100_percent():
    """3. Verify portfolio allocation percentages total exactly 100%."""
    res = render_investment_dashboard()
    payload = res["a2ui_payload"]
    port_sec = next(
        c for c in payload["components"] if c["id"] == "section_portfolio_allocation"
    )

    table = port_sec["table"]
    sum_pct = sum(float(item["percentage"].replace("%", "")) for item in table)
    assert abs(sum_pct - 100.0) < 0.01
    assert port_sec["total_percentage"] == "100.0%"


def test_market_summary_synthetic_data_label():
    """4. Verify market summary displays synthetic data labeled correctly."""
    res = render_market_dashboard()
    payload = res["a2ui_payload"]
    mkt_sec = next(
        c for c in payload["components"] if c["id"] == "section_market_summary"
    )

    assert mkt_sec["label"] == "Synthetic Market Data"
    assert len(mkt_sec["assets"]) > 0


def test_scenario_appears_in_ui():
    """5. Verify scenario details appear in the A2UI dashboard payload."""
    scenarios = [
        {
            "scenario_name": "₹60,000 Monthly Investment",
            "scenario_type": "parameter_modification",
            "changed_parameters": {"monthly_investment_amount": 60000.0},
        }
    ]

    res = render_investment_dashboard(scenarios=scenarios)
    payload = res["a2ui_payload"]
    scen_sec = next(c for c in payload["components"] if c["id"] == "section_scenarios")

    assert len(scen_sec["list"]) == 1
    assert scen_sec["list"][0]["scenario_name"] == "₹60,000 Monthly Investment"


def test_scenario_changes_update_ui():
    """6. Verify scenario dashboard updates allocations and quantitative delta."""
    baseline = {"investor_name": "Alex", "risk_tolerance": "Moderate"}
    scenario_data = {
        "scenario_name": "Equity Market Shock (-25%)",
        "baseline_values": {"Equity": "55.0%"},
    }
    scenario_alloc = {"allocations": {"Equity": 40.0, "Debt": 45.0, "Gold": 15.0}}

    res = render_scenario_dashboard(
        baseline_profile=baseline,
        scenario_data=scenario_data,
        scenario_allocation=scenario_alloc,
    )
    payload = res["a2ui_payload"]
    port_sec = next(
        c for c in payload["components"] if c["id"] == "section_portfolio_allocation"
    )

    equity_item = next(
        item for item in port_sec["table"] if item["asset_class"] == "Equity"
    )
    assert equity_item["percentage"] == "40.0%"


def test_quantitative_analysis_inclusion():
    """7. Verify quantitative analysis parameters (volatility, max drawdown) appear."""
    res = render_quantitative_dashboard()
    payload = res["a2ui_payload"]
    quant_sec = next(
        c for c in payload["components"] if c["id"] == "section_quantitative_analysis"
    )

    assert "simulated_volatility" in quant_sec
    assert "max_drawdown" in quant_sec
    assert "correlation" in quant_sec


def test_saved_simulation_restored_dashboard():
    """8. Verify saved simulation payload renders properly on restored dashboard."""
    sim_record = {
        "fictional_investor_name": "Alex",
        "investor_profile": {
            "investor_name": "Alex",
            "age": 35,
            "monthly_income": 100000.0,
        },
        "baseline_financial_metrics": {"monthly_surplus": 40000.0},
        "baseline_portfolio": {
            "allocations": {"Equity": 55.0, "Debt": 35.0, "Cash": 10.0}
        },
    }

    res = render_investment_dashboard(
        investor_profile=sim_record["investor_profile"],
        financial_metrics=sim_record["baseline_financial_metrics"],
        portfolio_allocation=sim_record["baseline_portfolio"],
    )

    formatted = res["formatted_dashboard"]
    assert "Alex" in formatted
    assert "Equity" in formatted
    assert DISCLAIMER_TEXT in formatted


def test_missing_data_handled_gracefully():
    """9. Verify empty/missing input data defaults gracefully without crashing."""
    payload = build_a2ui_payload()
    assert payload["surface"] == "a2ui_investment_dashboard"
    comps = {c["id"]: c for c in payload["components"]}

    assert comps["section_investor_summary"]["fields"]["Investor Name"] == "Alex"
    assert comps["section_disclaimer"]["text"] == DISCLAIMER_TEXT


def test_disclaimer_and_interactive_actions():
    """10. Verify educational disclaimer and action buttons are present."""
    payload = build_a2ui_payload()
    actions = [a["label"] for a in payload["actions"]]

    assert "View Baseline" in actions
    assert "View Scenario" in actions
    assert "Compare Scenario" in actions
    assert "Show Market Analysis" in actions
    assert "Show Quantitative Analysis" in actions
    assert "Show Assumptions" in actions
