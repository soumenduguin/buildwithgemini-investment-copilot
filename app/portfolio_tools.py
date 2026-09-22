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

from app.market import get_market_overview_data
from app.portfolio import (
    adjust_allocation_for_market,
    analyze_portfolio_data,
    calculate_baseline_allocation,
)


def calculate_illustrative_allocation(
    risk_tolerance: str | None = None,
    investment_horizon_years: int | None = None,
    liquidity_requirement: str | None = None,
    monthly_investment_amount: float | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates a deterministic illustrative asset allocation across Equity, Debt, Gold, International Equity, and Cash.

    EDUCATIONAL SIMULATION ONLY: Computes an illustrative asset class breakdown based on deterministic simulation rules.

    Args:
        risk_tolerance: Investor risk tolerance ('Conservative', 'Moderate', 'Aggressive').
        investment_horizon_years: Time horizon in years (e.g., 5, 7, 10).
        liquidity_requirement: Liquidity requirement ('Low', 'Medium', 'High').
        monthly_investment_amount: Monthly investment contribution in currency units.
        tool_context: ADK ToolContext for automatic state fallback.

    Returns:
        A dict containing normalized percentage allocations, deterministic assumptions, and educational disclaimer.
    """
    profile_data = {}
    if tool_context and hasattr(tool_context, "state"):
        profile_data = tool_context.state.get("investor_profile_data", {})

    final_risk = risk_tolerance or profile_data.get("risk_tolerance")
    final_horizon = (
        investment_horizon_years
        if investment_horizon_years is not None
        else profile_data.get("horizon_years")
    )
    final_liq = liquidity_requirement or profile_data.get("liquidity_requirement")
    final_amt = (
        monthly_investment_amount
        if monthly_investment_amount is not None
        else profile_data.get("monthly_investment_amount")
    )

    if not final_risk or final_horizon is None or not final_liq or final_amt is None:
        missing = []
        if not final_risk:
            missing.append("risk_tolerance")
        if final_horizon is None:
            missing.append("investment_horizon_years")
        if not final_liq:
            missing.append("liquidity_requirement")
        if final_amt is None:
            missing.append("monthly_investment_amount")
        return {
            "status": "error",
            "message": f"Missing required parameters for portfolio allocation: {', '.join(missing)}. "
            "Please provide them or run save_profile_fields first.",
        }

    return calculate_baseline_allocation(
        risk_tolerance=str(final_risk),
        investment_horizon_years=int(final_horizon),
        liquidity_requirement=str(final_liq),
        monthly_investment_amount=float(final_amt),
    )


def adjust_allocation_for_market_conditions(
    base_allocation: dict[str, float],
    market_overview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Applies bounded deterministic adjustments (max +-5%) to a base allocation based on synthetic market indicators.

    EDUCATIONAL SIMULATION ONLY: Modestly adjusts baseline allocations under explicit bounded rules.

    Args:
        base_allocation: Dict of asset class percentages summing to 100%.
        market_overview: Optional synthetic market overview dictionary. Fetched automatically if omitted.

    Returns:
        A dict containing original vs adjusted allocations, list of applied adjustments, and disclaimer.
    """
    if market_overview is None:
        market_overview = get_market_overview_data()

    return adjust_allocation_for_market(
        base_allocation=base_allocation,
        market_overview=market_overview,
    )


def analyze_illustrative_portfolio(
    allocation: dict[str, float],
    monthly_investment_amount: float | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Analyzes an illustrative portfolio allocation for growth vs defensive balance and diversification.

    EDUCATIONAL SIMULATION ONLY: Evaluates asset class balance and monthly currency breakdown.

    Args:
        allocation: Dict of asset class percentages summing to 100%.
        monthly_investment_amount: Optional monthly investment amount for currency allocation breakdown.
        tool_context: ADK ToolContext for automatic state fallback.

    Returns:
        A dict containing percentage breakdown, monthly currency breakdown, growth vs defensive split,
        diversification summary, assumptions, and educational disclaimer.
    """
    if (
        monthly_investment_amount is None
        and tool_context
        and hasattr(tool_context, "state")
    ):
        profile_data = tool_context.state.get("investor_profile_data", {})
        monthly_investment_amount = profile_data.get("monthly_investment_amount")

    return analyze_portfolio_data(
        allocation=allocation,
        monthly_investment_amount=monthly_investment_amount,
    )
