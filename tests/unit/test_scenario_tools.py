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

from unittest.mock import MagicMock

from app.scenario_tools import (
    compare_scenario_to_baseline,
    compare_scenarios,
    create_scenario,
    list_scenarios,
    simulate_market_shock,
)

BASE_PROFILE = {
    "investor_name": "Alex",
    "age": 32,
    "monthly_income": 150000.0,
    "monthly_expenses": 70000.0,
    "current_savings": 800000.0,
    "monthly_investment_amount": 40000.0,
    "investment_goal": "Long-term wealth creation",
    "horizon_years": 7,
    "risk_tolerance": "Moderate",
    "liquidity_requirement": "Low",
}


def _mock_context():
    ctx = MagicMock()
    ctx.state = {
        "investor_profile_data": dict(BASE_PROFILE),
        "scenarios": {},
    }
    return ctx


def test_increasing_monthly_investment():
    ctx = _mock_context()
    res = create_scenario(
        monthly_investment=60000.0,
        scenario_name="Increase Investment",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["scenario_values"]["monthly_investment_amount"] == 60000.0
    assert res["financial_metric_changes"]["annual_investment_capacity"] == 240000.0
    assert sum(res["scenario_allocation"].values()) == 100.0


def test_decreasing_monthly_investment():
    ctx = _mock_context()
    res = create_scenario(
        monthly_investment=20000.0,
        scenario_name="Decrease Investment",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["scenario_values"]["monthly_investment_amount"] == 20000.0
    assert res["financial_metric_changes"]["annual_investment_capacity"] == -240000.0


def test_changing_investment_horizon():
    ctx = _mock_context()
    res = create_scenario(
        investment_horizon_years=3,
        scenario_name="Shorter Horizon",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["scenario_values"]["horizon_years"] == 3
    # Short horizon reduces equity allocation compared to baseline long horizon
    assert res["scenario_allocation"]["Equity"] < res["baseline_allocation"]["Equity"]
    assert sum(res["scenario_allocation"].values()) == 100.0


def test_changing_risk_tolerance():
    ctx = _mock_context()
    res = create_scenario(
        risk_tolerance="Conservative",
        scenario_name="Conservative Shift",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["scenario_values"]["risk_tolerance"] == "Conservative"
    assert res["scenario_allocation"]["Equity"] < res["baseline_allocation"]["Equity"]
    assert sum(res["scenario_allocation"].values()) == 100.0


def test_changing_liquidity_requirement():
    ctx = _mock_context()
    res = create_scenario(
        liquidity_requirement="High",
        scenario_name="High Liquidity",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["scenario_values"]["liquidity_requirement"] == "High"
    assert (
        res["scenario_allocation"]["Cash/Liquid"]
        > res["baseline_allocation"]["Cash/Liquid"]
    )
    assert sum(res["scenario_allocation"].values()) == 100.0


def test_changing_income():
    ctx = _mock_context()
    res = create_scenario(
        monthly_income=200000.0,
        scenario_name="Income Raise",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["financial_metric_changes"]["monthly_surplus"] == 50000.0


def test_changing_expenses():
    ctx = _mock_context()
    res = create_scenario(
        monthly_expenses=90000.0,
        scenario_name="Expense Spike",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert res["financial_metric_changes"]["monthly_surplus"] == -20000.0
    assert res["financial_metric_changes"]["emergency_fund_target"] == 120000.0


def test_equity_market_shock():
    ctx = _mock_context()
    res = simulate_market_shock(
        asset_class="Equity",
        percentage_change=-25.0,
        scenario_name="Equity Crash",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert sum(res["scenario_allocation"].values()) == 100.0
    assert res["scenario_allocation"]["Debt"] >= res["baseline_allocation"]["Debt"]


def test_positive_market_shock():
    ctx = _mock_context()
    res = simulate_market_shock(
        asset_class="Gold",
        percentage_change=10.0,
        scenario_name="Gold Surge",
        tool_context=ctx,
    )
    assert res["status"] == "success"
    assert sum(res["scenario_allocation"].values()) == 100.0


def test_multiple_independent_scenarios():
    ctx = _mock_context()
    res1 = create_scenario(
        monthly_investment=60000.0, scenario_name="Scen 1", tool_context=ctx
    )
    res2 = create_scenario(
        risk_tolerance="Conservative", scenario_name="Scen 2", tool_context=ctx
    )

    list_res = list_scenarios(tool_context=ctx)
    assert list_res["scenarios_count"] == 2
    assert res1["scenario_id"] == "scenario_1"
    assert res2["scenario_id"] == "scenario_2"


def test_baseline_remains_unchanged():
    ctx = _mock_context()
    initial_base = dict(ctx.state["investor_profile_data"])

    create_scenario(
        monthly_investment=90000.0,
        risk_tolerance="Conservative",
        tool_context=ctx,
    )
    simulate_market_shock(
        asset_class="Equity", percentage_change=-30.0, tool_context=ctx
    )

    # State base profile must remain identical
    assert ctx.state["investor_profile_data"] == initial_base


def test_invalid_scenario_parameters():
    ctx = _mock_context()
    res = create_scenario(
        monthly_investment=-5000.0,
        risk_tolerance="InvalidRisk",
        tool_context=ctx,
    )
    assert res["status"] == "error"
    assert "validation failed" in res["message"]


def test_scenario_comparison():
    ctx = _mock_context()
    create_scenario(
        monthly_investment=60000.0, scenario_name="High Invest", tool_context=ctx
    )
    comp_res = compare_scenario_to_baseline(scenario_id="scenario_1", tool_context=ctx)
    assert comp_res["status"] == "success"
    assert comp_res["scenario_values"]["monthly_investment_amount"] == 60000.0


def test_scenario_created_from_baseline():
    ctx = _mock_context()
    _ = create_scenario(
        monthly_investment=60000.0, scenario_name="Scen 1", tool_context=ctx
    )
    res2 = create_scenario(
        investment_horizon_years=3, scenario_name="Scen 2", tool_context=ctx
    )

    # Scen 2 should use baseline investment amount (40000), not Scen 1's 60000
    assert res2["baseline_values"]["horizon_years"] == 7
    assert res2["base_profile_reference"]["monthly_investment_amount"] == 40000.0


def test_compare_scenarios_tool():
    ctx = _mock_context()
    create_scenario(
        monthly_investment=60000.0, scenario_name="Scen 1", tool_context=ctx
    )
    create_scenario(
        risk_tolerance="Conservative", scenario_name="Scen 2", tool_context=ctx
    )

    comp = compare_scenarios(scenario_id_1="1", scenario_id_2="2", tool_context=ctx)
    assert comp["status"] == "success"
    assert "scenario_1" in comp
    assert "scenario_2" in comp
    assert "allocation_differences_2_minus_1" in comp
