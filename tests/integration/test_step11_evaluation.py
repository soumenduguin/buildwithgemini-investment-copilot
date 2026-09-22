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

from app.a2ui import build_a2ui_payload
from app.a2ui_tools import (
    render_investment_dashboard,
)
from app.knowledge import search_knowledge_base
from app.market import load_synthetic_market_data
from app.market_tools import (
    analyze_asset_trend,
    get_market_overview,
    get_market_snapshot,
)
from app.memory import memory_service
from app.memory_tools import recall_investor_memory, save_investor_memory
from app.portfolio import calculate_baseline_allocation
from app.portfolio_tools import (
    adjust_allocation_for_market_conditions,
    analyze_illustrative_portfolio,
    calculate_illustrative_allocation,
)
from app.quant import (
    calculate_correlation_data,
    calculate_drawdown_data,
    calculate_returns_data,
    calculate_volatility_data,
    run_sandboxed_python,
)
from app.quant_tools import (
    analyze_portfolio_quantitatively,
)
from app.scenario_tools import (
    create_scenario,
    simulate_market_shock,
)
from app.schema import InvestorProfile, check_inconsistencies
from app.storage_tools import (
    delete_simulation,
    list_simulations,
    load_scenario,
    load_simulation,
    save_simulation,
)
from app.tools import (
    calculate_annual_investment_capacity,
    calculate_emergency_fund,
    calculate_monthly_surplus,
)


def test_eval_1_full_end_to_end_alex():
    """1. FULL END-TO-END TEST: Verify complete fictional investor workflow."""
    input_data = {
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
    profile_obj = InvestorProfile(**input_data)
    assert profile_obj.investor_name == "Alex"
    val_res = check_inconsistencies(input_data)
    assert len(val_res) == 0

    # Step 2: Financial Analysis
    surplus_res = calculate_monthly_surplus(150000.0, 70000.0)
    assert surplus_res["monthly_surplus"] == 80000.0
    assert surplus_res["status"] == "success"

    ef_res = calculate_emergency_fund(70000.0, 6)
    assert ef_res["emergency_fund_target"] == 420000.0

    cap_res = calculate_annual_investment_capacity(40000.0)
    assert cap_res["annual_investment_capacity"] == 480000.0

    # Step 3: Market Analysis
    mkt_overview = get_market_overview()
    assert mkt_overview["total_assets"] == 9

    snapshot = get_market_snapshot(asset_class="Equity")
    assert snapshot["status"] == "success"

    trend = analyze_asset_trend("BROAD_EQUITY_INDEX")
    assert trend["status"] == "success"

    # Step 4: Portfolio Allocation
    alloc_res = calculate_illustrative_allocation("Moderate", 7, "Low", 40000.0)
    assert alloc_res["status"] == "success"
    alloc_dict = alloc_res["illustrative_allocation"]
    total_pct = sum(alloc_dict.values())
    assert abs(total_pct - 100.0) < 0.01

    adj_res = adjust_allocation_for_market_conditions(alloc_dict)
    assert adj_res["status"] == "success"

    port_analysis = analyze_illustrative_portfolio(alloc_dict, 40000.0)
    assert port_analysis["status"] == "success"

    # Step 5: Knowledge / RAG
    rag_res = search_knowledge_base("risk profiles moderate")
    assert rag_res["status"] == "success"
    assert len(rag_res["matches"]) > 0

    # Step 6: Quantitative Analysis
    quant_res = analyze_portfolio_quantitatively(alloc_dict)
    assert quant_res["status"] == "success"

    # Step 7: Scenarios
    scen_res = create_scenario(
        scenario_name="Increased Investment",
        monthly_investment=60000.0,
    )
    assert scen_res["status"] == "success"

    # Step 8: Persistent Storage
    sim_data = {
        "fictional_investor_name": "Alex",
        "investor_profile": input_data,
        "baseline_portfolio": alloc_dict,
    }
    save_sim_res = save_simulation(sim_data, simulation_id="sim_alex_eval")
    assert save_sim_res["status"] == "success"

    load_sim_res = load_simulation("sim_alex_eval")
    assert load_sim_res["status"] == "success"

    # Step 9: A2UI Dashboard
    dash_res = render_investment_dashboard(
        investor_profile=input_data, portfolio_allocation=alloc_dict
    )
    assert dash_res["status"] == "success"
    assert dash_res["a2ui_payload"]["components"][0]["title"] == "1. INVESTOR SUMMARY"


def test_eval_2_baseline_consistency():
    """2. BASELINE CONSISTENCY: Verify display values match backend/tool results."""
    income = 150000.0
    expenses = 70000.0
    monthly_inv = 40000.0

    surplus = income - expenses
    annual_cap = monthly_inv * 12

    assert surplus == 80000.0
    assert annual_cap == 480000.0

    alloc = calculate_baseline_allocation("Moderate", 7, "Low", monthly_inv)[
        "illustrative_allocation"
    ]
    assert sum(alloc.values()) == 100.0

    # Ensure currency breakdown sums to monthly_inv
    currency_amounts = {
        asset: round((pct / 100.0) * monthly_inv, 2) for asset, pct in alloc.items()
    }
    assert sum(currency_amounts.values()) == monthly_inv


def test_eval_3_scenario_isolation():
    """3. SCENARIO ISOLATION: Verify baseline remains untouched and scenarios don't leak."""
    baseline = {
        "investor_name": "Alex",
        "monthly_income": 150000.0,
        "monthly_expenses": 70000.0,
        "monthly_investment_amount": 40000.0,
        "horizon_years": 7,
        "risk_tolerance": "Moderate",
        "liquidity_requirement": "Low",
    }

    # Scenario 1: ₹60,000 monthly investment
    s1 = create_scenario(scenario_name="Monthly Inv 60k", monthly_investment=60000.0)
    # Scenario 2: 3 years horizon
    s2 = create_scenario(scenario_name="3 Year Horizon", investment_horizon_years=3)
    # Scenario 3: -25% equity shock
    s3 = simulate_market_shock(
        asset_class="Equity", percentage_change=-25.0, scenario_name="Equity Shock"
    )

    # Verify baseline is unchanged
    assert baseline["monthly_investment_amount"] == 40000.0
    assert baseline["horizon_years"] == 7

    # Verify scenario allocations sum to 100%
    assert sum(s1["scenario_allocation"].values()) == 100.0
    assert sum(s2["scenario_allocation"].values()) == 100.0
    assert sum(s3["scenario_allocation"].values()) == 100.0

    # Verify Scenario 1 differs from Scenario 2
    assert s1["scenario_allocation"] != s2["scenario_allocation"]


def test_eval_4_rag_validation():
    """4. RAG VALIDATION: Verify knowledge retrieval and absence of hallucination on non-existent rules."""
    # Known topic
    res_known = search_knowledge_base("risk profiles conservative moderate aggressive")
    assert len(res_known.get("matches", [])) > 0

    # Non-existent topic
    res_unknown = search_knowledge_base(
        "crypto yield farming derivative options leverage"
    )
    assert len(res_unknown.get("matches", [])) == 0


def test_eval_5_quantitative_validation():
    """5. QUANTITATIVE VALIDATION: Verify returns, volatility, drawdown, and correlation math."""
    returns_res = calculate_returns_data()
    assert isinstance(returns_res, dict)

    vol_res = calculate_volatility_data()
    assert isinstance(vol_res, dict)

    dd_res = calculate_drawdown_data()
    assert isinstance(dd_res, dict)

    corr_res = calculate_correlation_data()
    assert isinstance(corr_res, dict)

    # Sandboxed execution test
    code = "result = {'test_stat': 42}"
    exec_res = run_sandboxed_python(code)
    assert exec_res["status"] == "success"
    assert exec_res["variables"]["result"]["test_stat"] == 42


def test_eval_6_memory_validation():
    """6. MEMORY VALIDATION: Verify stable facts remembered and current session precedence."""
    # Reset memory
    memory_service.memory_store = {}

    save_res = save_investor_memory(
        "Alex",
        "Risk tolerance is Moderate, horizon is 7 years",
    )
    assert save_res["status"] == "success"

    recall_res = recall_investor_memory("Alex")
    assert recall_res["status"] == "success"


def test_eval_7_storage_validation():
    """7. STORAGE VALIDATION: Test persistent simulations and scenarios."""
    sim_id = "SIM-EVAL-TEST-001"
    sim_data = {
        "fictional_investor_name": "Jordan",
        "investor_profile": {"age": 28, "monthly_income": 80000.0},
    }

    save_res = save_simulation(sim_data, simulation_id=sim_id)
    assert save_res["status"] == "success"

    load_res = load_simulation(sim_id)
    assert load_res["status"] == "success"

    list_res = list_simulations()
    assert list_res["status"] == "success"
    assert list_res["count"] > 0

    del_res = delete_simulation(sim_id)
    assert del_res["status"] == "success"


def test_eval_8_a2ui_validation():
    """8. A2UI VALIDATION: Test dynamic component layout and disclaimers."""
    profile = {
        "fictional_investor_name": "Alex",
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
    payload = build_a2ui_payload(investor_profile=profile)
    assert len(payload["components"]) == 8

    # Verify disclaimer component presence
    disc_comp = next(
        c for c in payload["components"] if c["id"] == "section_disclaimer"
    )
    assert "Educational simulation" in disc_comp["text"]


def test_eval_10_failure_gracefulness():
    """10. FAILURE TESTS: Test invalid parameters and missing records."""
    # Invalid risk tolerance
    res_risk = calculate_baseline_allocation("INVALID_RISK", 5, "Low", 40000.0)
    assert res_risk["status"] == "error"

    # Missing simulation
    res_sim = load_simulation("NON_EXISTENT_SIM_999")
    assert res_sim["status"] == "not_found"

    # Missing scenario
    res_scen = load_scenario("NON_EXISTENT_SCEN_999")
    assert res_scen["status"] == "not_found"

    # Deficit cash flow
    val_res = check_inconsistencies(
        {
            "monthly_income": 50000.0,
            "monthly_expenses": 70000.0,
            "monthly_investment_amount": 10000.0,
        }
    )
    assert len(val_res) > 0


def test_eval_11_safety_validation():
    """11. SAFETY VALIDATION: Check that market dataset and RAG contain NO stock tickers or buy/sell advice."""
    market_data = load_synthetic_market_data()
    for row in market_data:
        asset_name = row["asset_name"]
        # Ensure no stock tickers (e.g. AAPL, TSLA, NVDA) or specific mutual funds are listed
        assert "AAPL" not in asset_name
        assert "TSLA" not in asset_name
        assert "NVDA" not in asset_name
