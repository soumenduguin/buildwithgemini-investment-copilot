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

from google.adk.tools import ToolContext

from app.scenarios import (
    ASSET_CLASSES,
    EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    build_market_shock_data,
    build_scenario_data,
)

DEFAULT_BASELINE_FALLBACK = {
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


def _get_base_profile(tool_context: ToolContext | None) -> dict[str, Any]:
    """Retrieves current baseline profile from session state or fallback."""
    if tool_context and hasattr(tool_context, "state"):
        profile = tool_context.state.get("investor_profile_data")
        if profile and isinstance(profile, dict) and profile.get("investor_name"):
            return profile
    return DEFAULT_BASELINE_FALLBACK


def _get_scenarios_store(tool_context: ToolContext | None) -> dict[str, Any]:
    """Retrieves or initializes the scenario store in session state."""
    if tool_context and hasattr(tool_context, "state"):
        if "scenarios" not in tool_context.state:
            tool_context.state["scenarios"] = {}
        return tool_context.state["scenarios"]
    return {}


def create_scenario(
    scenario_name: str | None = None,
    monthly_income: float | None = None,
    monthly_expenses: float | None = None,
    monthly_investment: float | None = None,
    investment_horizon_years: int | None = None,
    risk_tolerance: str | None = None,
    liquidity_requirement: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Creates a non-destructive hypothetical What-If scenario by modifying one or more baseline investor parameters.

    EDUCATIONAL SIMULATION ONLY: Evaluates parameter changes without altering stored baseline profile.

    Args:
        scenario_name: Optional descriptive label for the scenario (e.g., 'Higher Monthly Investment').
        monthly_income: Hypothetical monthly income.
        monthly_expenses: Hypothetical monthly expenses.
        monthly_investment: Hypothetical monthly investment contribution.
        investment_horizon_years: Hypothetical investment horizon in years.
        risk_tolerance: Hypothetical risk tolerance ('Conservative', 'Moderate', 'Aggressive').
        liquidity_requirement: Hypothetical liquidity requirement ('Low', 'Medium', 'High').
        tool_context: ADK ToolContext for session state.

    Returns:
        Dict comparing Baseline vs Scenario parameters, metrics, allocations, and diffs.
    """
    base_profile = _get_base_profile(tool_context)
    store = _get_scenarios_store(tool_context)

    scen_id = f"scenario_{len(store) + 1}"

    changed_params = {}
    if monthly_income is not None:
        changed_params["monthly_income"] = monthly_income
    if monthly_expenses is not None:
        changed_params["monthly_expenses"] = monthly_expenses
    if monthly_investment is not None:
        changed_params["monthly_investment"] = monthly_investment
    if investment_horizon_years is not None:
        changed_params["investment_horizon_years"] = investment_horizon_years
    if risk_tolerance is not None:
        changed_params["risk_tolerance"] = risk_tolerance
    if liquidity_requirement is not None:
        changed_params["liquidity_requirement"] = liquidity_requirement

    scenario_res = build_scenario_data(
        base_profile=base_profile,
        changed_params=changed_params,
        scenario_id=scen_id,
        scenario_name=scenario_name,
    )

    if scenario_res.get("status") == "success":
        store[scen_id] = scenario_res

    return scenario_res


def simulate_market_shock(
    asset_class: str,
    percentage_change: float,
    scenario_name: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Simulates a hypothetical synthetic market shock on an asset class without altering baseline data.

    EDUCATIONAL SIMULATION ONLY: Evaluates portfolio reaction under hypothetical synthetic market shocks.

    Args:
        asset_class: Asset class to shock (e.g. 'Equity', 'Gold', 'Debt').
        percentage_change: Percentage movement (e.g. -25.0, +10.0).
        scenario_name: Optional descriptive label for the shock scenario.
        tool_context: ADK ToolContext for session state.

    Returns:
        Dict comparing Baseline vs Shocked Scenario allocations and market reaction notes.
    """
    base_profile = _get_base_profile(tool_context)
    store = _get_scenarios_store(tool_context)

    scen_id = f"scenario_{len(store) + 1}"

    shock_res = build_market_shock_data(
        base_profile=base_profile,
        asset_class=asset_class,
        percentage_change=percentage_change,
        scenario_id=scen_id,
        scenario_name=scenario_name,
    )

    if shock_res.get("status") == "success":
        store[scen_id] = shock_res

    return shock_res


def compare_scenario_to_baseline(
    scenario_id: str,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Compares a specific stored scenario against the current baseline profile and allocation.

    Args:
        scenario_id: Identifier or index of the scenario (e.g., 'scenario_1' or '1').
        tool_context: ADK ToolContext for session state.

    Returns:
        Structured breakdown of Baseline vs Scenario parameters, financial metrics, allocations, and diffs.
    """
    store = _get_scenarios_store(tool_context)
    scen_key = scenario_id.strip()

    if scen_key not in store and f"scenario_{scen_key}" in store:
        scen_key = f"scenario_{scen_key}"

    if scen_key not in store:
        available = list(store.keys())
        return {
            "status": "error",
            "message": f"Scenario '{scenario_id}' not found. Available scenarios: {available if available else 'None'}",
        }

    scen = store[scen_key]
    return {
        "status": "success",
        "scenario_id": scen["scenario_id"],
        "scenario_name": scen["scenario_name"],
        "baseline_values": scen.get("baseline_values", {}),
        "scenario_values": scen.get("scenario_values", {}),
        "baseline_allocation": scen.get("baseline_allocation", {}),
        "scenario_allocation": scen.get("scenario_allocation", {}),
        "allocation_differences": scen.get("allocation_differences", {}),
        "financial_metric_changes": scen.get("financial_metric_changes", {}),
        "explanation": scen.get("explanation", []),
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }


def list_scenarios(
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Lists all created What-If scenarios in the current session.

    Args:
        tool_context: ADK ToolContext for session state.

    Returns:
        Summary list of all stored scenarios.
    """
    store = _get_scenarios_store(tool_context)
    if not store:
        return {
            "status": "success",
            "scenarios_count": 0,
            "scenarios": [],
            "message": "No scenarios have been created in this session yet. The baseline profile remains active.",
        }

    summary_list = []
    for sid, sdata in store.items():
        summary_list.append(
            {
                "scenario_id": sid,
                "scenario_name": sdata.get("scenario_name"),
                "changed_parameters": sdata.get(
                    "changed_parameters", sdata.get("shock_details", {})
                ),
                "created_at": sdata.get("created_at"),
            }
        )

    return {
        "status": "success",
        "scenarios_count": len(summary_list),
        "scenarios": summary_list,
    }


def compare_scenarios(
    scenario_id_1: str,
    scenario_id_2: str,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Compares two stored What-If scenarios side-by-side.

    Args:
        scenario_id_1: First scenario ID (e.g. 'scenario_1' or '1').
        scenario_id_2: Second scenario ID (e.g. 'scenario_2' or '2').
        tool_context: ADK ToolContext for session state.

    Returns:
        Side-by-side comparison of allocations, parameter changes, and differences.
    """
    store = _get_scenarios_store(tool_context)
    key1 = scenario_id_1.strip()
    key2 = scenario_id_2.strip()

    if key1 not in store and f"scenario_{key1}" in store:
        key1 = f"scenario_{key1}"
    if key2 not in store and f"scenario_{key2}" in store:
        key2 = f"scenario_{key2}"

    if key1 not in store or key2 not in store:
        missing = []
        if key1 not in store:
            missing.append(scenario_id_1)
        if key2 not in store:
            missing.append(scenario_id_2)
        return {
            "status": "error",
            "message": f"Scenario(s) not found: {', '.join(missing)}. Available: {list(store.keys())}",
        }

    s1 = store[key1]
    s2 = store[key2]

    alloc1 = s1.get("scenario_allocation", {})
    alloc2 = s2.get("scenario_allocation", {})

    diff_1_vs_2 = {
        ac: round(alloc2.get(ac, 0.0) - alloc1.get(ac, 0.0), 2) for ac in ASSET_CLASSES
    }

    return {
        "status": "success",
        "scenario_1": {
            "scenario_id": s1["scenario_id"],
            "scenario_name": s1["scenario_name"],
            "allocation": alloc1,
        },
        "scenario_2": {
            "scenario_id": s2["scenario_id"],
            "scenario_name": s2["scenario_name"],
            "allocation": alloc2,
        },
        "allocation_differences_2_minus_1": diff_1_vs_2,
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }
