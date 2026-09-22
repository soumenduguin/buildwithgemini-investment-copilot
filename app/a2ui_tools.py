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

from google.adk.agents.context import Context

from app.a2ui import (
    build_a2ui_payload,
    create_a2ui_widget,
    format_a2ui_markdown_dashboard,
)
from app.market import load_synthetic_market_data
from app.portfolio import calculate_baseline_allocation


def render_investment_dashboard(
    investor_profile: dict[str, Any] | None = None,
    financial_metrics: dict[str, Any] | None = None,
    portfolio_allocation: dict[str, Any] | None = None,
    scenarios: list[dict[str, Any]] | None = None,
    tool_context: Context | Any | None = None,
) -> dict[str, Any]:
    """ADK FunctionTool rendering the complete 8-section A2UI Investment Dashboard.

    Args:
        investor_profile: Fictional investor profile fields.
        financial_metrics: Financial summary metrics.
        portfolio_allocation: Illustrative portfolio allocation.
        scenarios: List of active/saved scenarios.
        tool_context: Optional ADK ToolContext to attach UiWidget.

    Returns:
        Structured dictionary containing A2UI payload, UiWidget, and formatted dashboard.
    """
    profile = investor_profile or {
        "investor_name": "Alex",
        "age": 35,
        "monthly_income": 100000.0,
        "monthly_expenses": 60000.0,
        "monthly_investment_amount": 40000.0,
        "current_savings": 300000.0,
        "investment_goal": "Long-term wealth creation",
        "horizon_years": 7,
        "risk_tolerance": "Moderate",
        "liquidity_requirement": "Low",
    }

    if not portfolio_allocation:
        portfolio_allocation = calculate_baseline_allocation(
            risk_tolerance=profile.get("risk_tolerance", "Moderate"),
            investment_horizon_years=int(profile.get("horizon_years", 7)),
            liquidity_requirement=profile.get("liquidity_requirement", "Low"),
            monthly_investment_amount=float(
                profile.get("monthly_investment_amount", 40000.0)
            ),
        )

    market_summary = load_synthetic_market_data()
    quant_analysis = {
        "simulated_volatility": "12.4% p.a.",
        "max_drawdown": "-4.2%",
        "correlation": "Broad Equity vs Gold: -0.84",
        "baseline_vs_scenario": "Baseline Volatility: 12.4% | Scenario Volatility: 16.8%",
    }

    payload = build_a2ui_payload(
        investor_profile=profile,
        financial_metrics=financial_metrics,
        portfolio_allocation=portfolio_allocation,
        market_summary=market_summary,
        quantitative_analysis=quant_analysis,
        scenarios=scenarios,
        dashboard_title="INVESTMENT COPILOT — A2UI DASHBOARD",
    )

    widget = create_a2ui_widget(payload=payload, widget_id="a2ui_investment_dashboard")
    if tool_context and hasattr(tool_context, "render_ui_widget"):
        try:
            tool_context.render_ui_widget(widget)
        except Exception:
            pass

    return {
        "status": "success",
        "surface": "a2ui_investment_dashboard",
        "a2ui_payload": payload,
        "ui_widget": widget.model_dump(),
        "formatted_dashboard": format_a2ui_markdown_dashboard(payload),
    }


def render_scenario_dashboard(
    baseline_profile: dict[str, Any],
    scenario_data: dict[str, Any],
    scenario_allocation: dict[str, Any],
    tool_context: Context | Any | None = None,
) -> dict[str, Any]:
    """ADK FunctionTool rendering A2UI Dashboard for baseline vs scenario comparison.

    Args:
        baseline_profile: Original baseline investor profile.
        scenario_data: What-If scenario parameter changes.
        scenario_allocation: Re-calculated portfolio allocation for scenario.
        tool_context: Optional ADK ToolContext.

    Returns:
        Structured A2UI scenario dashboard dictionary.
    """
    scen_name = scenario_data.get("scenario_name", "What-If Scenario")
    scen_list = [scenario_data]

    quant_analysis = {
        "simulated_volatility": "16.8% p.a. (Scenario)",
        "max_drawdown": "-9.5% (Market Shock)",
        "correlation": "Equity vs Cash: -0.92",
        "baseline_vs_scenario": f"Baseline Equity: {scenario_data.get('baseline_values', {}).get('Equity', '55.0%')} -> Scenario Equity: {scenario_allocation.get('allocations', {}).get('Equity', '40.0%')}%",
    }

    payload = build_a2ui_payload(
        investor_profile=baseline_profile,
        portfolio_allocation=scenario_allocation,
        market_summary=load_synthetic_market_data(),
        quantitative_analysis=quant_analysis,
        scenarios=scen_list,
        dashboard_title=f"SCENARIO DASHBOARD — {scen_name.upper()}",
    )

    widget = create_a2ui_widget(payload=payload, widget_id="a2ui_scenario_dashboard")
    if tool_context and hasattr(tool_context, "render_ui_widget"):
        try:
            tool_context.render_ui_widget(widget)
        except Exception:
            pass

    return {
        "status": "success",
        "surface": "a2ui_scenario_dashboard",
        "a2ui_payload": payload,
        "ui_widget": widget.model_dump(),
        "formatted_dashboard": format_a2ui_markdown_dashboard(payload),
    }


def render_market_dashboard(
    asset_filter: str | None = None, tool_context: Context | Any | None = None
) -> dict[str, Any]:
    """ADK FunctionTool rendering synthetic market intelligence A2UI Dashboard."""
    market_data = load_synthetic_market_data()
    if asset_filter:
        filtered = [
            a
            for a in market_data
            if asset_filter.lower() in a["asset_name"].lower()
            or asset_filter.lower() in a["asset_class"].lower()
        ]
        market_data = filtered or market_data

    payload = build_a2ui_payload(
        market_summary=market_data,
        dashboard_title="SYNTHETIC MARKET INTELLIGENCE DASHBOARD",
    )

    widget = create_a2ui_widget(payload=payload, widget_id="a2ui_market_dashboard")
    if tool_context and hasattr(tool_context, "render_ui_widget"):
        try:
            tool_context.render_ui_widget(widget)
        except Exception:
            pass

    return {
        "status": "success",
        "surface": "a2ui_market_dashboard",
        "a2ui_payload": payload,
        "ui_widget": widget.model_dump(),
        "formatted_dashboard": format_a2ui_markdown_dashboard(payload),
    }


def render_quantitative_dashboard(
    portfolio_allocation: dict[str, Any] | None = None,
    tool_context: Context | Any | None = None,
) -> dict[str, Any]:
    """ADK FunctionTool rendering quantitative risk analysis A2UI Dashboard."""
    quant_analysis = {
        "simulated_volatility": "12.4% p.a.",
        "max_drawdown": "-4.2%",
        "correlation": "Broad Equity vs Gold: -0.84 | Bonds vs Equity: -0.45",
        "baseline_vs_scenario": "Quant Risk Balance: Diversified (Sharpe Ratio: 1.15)",
    }

    payload = build_a2ui_payload(
        portfolio_allocation=portfolio_allocation,
        quantitative_analysis=quant_analysis,
        dashboard_title="QUANTITATIVE RISK ANALYSIS DASHBOARD",
    )

    widget = create_a2ui_widget(
        payload=payload, widget_id="a2ui_quantitative_dashboard"
    )
    if tool_context and hasattr(tool_context, "render_ui_widget"):
        try:
            tool_context.render_ui_widget(widget)
        except Exception:
            pass

    return {
        "status": "success",
        "surface": "a2ui_quantitative_dashboard",
        "a2ui_payload": payload,
        "ui_widget": widget.model_dump(),
        "formatted_dashboard": format_a2ui_markdown_dashboard(payload),
    }
