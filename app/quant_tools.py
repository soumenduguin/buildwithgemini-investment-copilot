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

from app.quant import (
    QUANT_DATASET_LABEL,
    QUANT_LIMITATION_DISCLAIMER,
    calculate_correlation_data,
    calculate_drawdown_data,
    calculate_portfolio_quant_data,
    calculate_returns_data,
    calculate_volatility_data,
    compare_scenarios_quant_data,
    run_sandboxed_python,
)


def execute_quantitative_analysis(
    python_code: str, tool_context: ToolContext | None = None
) -> dict[str, Any]:
    """Executes sandboxed Python code over synthetic market datasets, baseline investor profiles, and illustrative portfolio allocations for custom quantitative financial analysis.

    Args:
        python_code: Valid Python code snippet evaluating quantitative metrics (e.g. returns, volatility, drawdowns, ratios, correlations).

    Returns:
        Structured result containing executed code, computed variables, interpretation, and educational disclaimers.
    """
    res = run_sandboxed_python(python_code)
    if res["status"] == "error":
        return {
            "status": "error",
            "message": f"Code execution failed: {res.get('message')}",
            "traceback": res.get("traceback"),
            "dataset": QUANT_DATASET_LABEL,
            "disclaimer": QUANT_LIMITATION_DISCLAIMER,
        }

    return {
        "status": "success",
        "analysis_type": "Custom Sandboxed Python Execution",
        "dataset": QUANT_DATASET_LABEL,
        "executed_code": python_code,
        "results": res["variables"],
        "method": "Sandboxed Python execution over synthetic market returns",
        "interpretation": (
            "Custom quantitative analysis computed safely using sandboxed Python code "
            "over synthetic investment simulation data."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def analyze_historical_returns(
    asset_names: list[str] | None = None,
) -> dict[str, Any]:
    """Calculates historical return metrics (average monthly return, annualized cumulative return, period-by-period returns) over synthetic assets.

    Args:
        asset_names: Optional list of synthetic asset names to analyze. If None, analyzes all synthetic market assets.

    Returns:
        Structured return analysis with period returns, cumulative growth, calculation method, and educational disclaimer.
    """
    data = calculate_returns_data(asset_names)
    if data["status"] == "error":
        return data

    res_summary = []
    for asset, metrics in data["results"].items():
        res_summary.append(
            f"- {asset}: Avg Monthly Return = {metrics['average_monthly_return_pct']}%, "
            f"Annual Cumulative Return = {metrics['annualized_cumulative_return_pct']}%"
        )

    return {
        "status": "success",
        "analysis": "Historical Return Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "results": data["results"],
        "formatted_summary": "\n".join(res_summary),
        "method": data["method"],
        "interpretation": (
            "Higher average monthly returns reflect synthetic historical growth assets, "
            "while lower stable returns reflect defensive fixed income or cash assets."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def analyze_volatility(
    asset_names: list[str] | None = None,
    portfolio_allocation: dict[str, float] | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates volatility metrics (standard deviation of returns, relative asset volatility, portfolio weighted volatility) over synthetic assets or portfolio allocations.

    Args:
        asset_names: Optional list of asset names to analyze.
        portfolio_allocation: Optional dictionary mapping asset classes to percentage weights. If omitted and session state exists, evaluates active baseline portfolio.

    Returns:
        Structured volatility analysis with asset standard deviations, portfolio weighted volatility, and educational disclaimers.
    """
    alloc = portfolio_allocation
    if not alloc and tool_context and "baseline_allocation" in tool_context.state:
        alloc = tool_context.state["baseline_allocation"].get("illustrative_allocation")

    data = calculate_volatility_data(asset_names, alloc)
    if data["status"] == "error":
        return data

    asset_summary = []
    for name, v in data["asset_volatilities"].items():
        asset_summary.append(
            f"- {name}: Monthly Std Dev = {v['monthly_std_dev_pct']}%, "
            f"Annualized Volatility = {v['annualized_volatility_pct']}%"
        )

    port_vol = data.get("portfolio_weighted_volatility_pct")
    port_text = (
        f"Weighted Portfolio Annual Volatility = {port_vol}%"
        if port_vol is not None
        else "No portfolio allocation specified."
    )

    return {
        "status": "success",
        "analysis": "Volatility Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "asset_volatilities": data["asset_volatilities"],
        "portfolio_weighted_volatility_pct": port_vol,
        "formatted_summary": "\n".join(asset_summary) + f"\n\n{port_text}",
        "method": data["method"],
        "interpretation": (
            "Annualized volatility measures simulated price fluctuation. Lower weighted "
            "portfolio volatility indicates higher defensive asset cushion."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def analyze_drawdowns(
    asset_names: list[str] | None = None,
) -> dict[str, Any]:
    """Calculates drawdown metrics (running peak, drawdown series, maximum drawdown) over synthetic market assets.

    Args:
        asset_names: Optional list of asset names to analyze.

    Returns:
        Structured drawdown analysis with peak price, ending price, max drawdown %, and educational disclaimer.
    """
    data = calculate_drawdown_data(asset_names)
    if data["status"] == "error":
        return data

    dd_summary = []
    for name, dd in data["results"].items():
        dd_summary.append(
            f"- {name}: Peak Price = ${dd['peak_simulated_price']}, "
            f"End Price = ${dd['end_simulated_price']}, "
            f"Max Drawdown = {dd['max_drawdown_pct']}%"
        )

    return {
        "status": "success",
        "analysis": "Drawdown Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "results": data["results"],
        "formatted_summary": "\n".join(dd_summary),
        "method": data["method"],
        "interpretation": (
            "Maximum drawdown indicates peak-to-trough price decline in synthetic historical series, "
            "reflecting downside downside risk under stress."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def analyze_correlations(
    asset_names: list[str] | None = None,
) -> dict[str, Any]:
    """Calculates correlation matrix and pairwise correlations between synthetic market assets.

    Args:
        asset_names: Optional list of asset names to analyze.

    Returns:
        Structured correlation matrix dictionary, method description, and educational disclaimer.
    """
    data = calculate_correlation_data(asset_names)
    if data["status"] == "error":
        return data

    return {
        "status": "success",
        "analysis": "Correlation Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "correlation_matrix": data["correlation_matrix"],
        "method": data["method"],
        "interpretation": (
            "Positive correlations mean assets move together in the simulation; low or "
            "negative correlations (e.g. Gold vs Equity) enhance multi-asset diversification."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def analyze_portfolio_quantitatively(
    portfolio_allocation: dict[str, float] | None = None,
    monthly_investment: float | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates comprehensive quantitative portfolio statistics (weighted return, weighted volatility, asset class contribution %, diversification ratio).

    Args:
        portfolio_allocation: Optional dictionary mapping asset classes to percentage weights.
        monthly_investment: Monthly contribution amount (in USD/INR).

    Returns:
        Structured portfolio quantitative analysis with weighted return, weighted volatility, asset contributions, and diversification stats.
    """
    alloc = portfolio_allocation
    if not alloc and tool_context and "baseline_allocation" in tool_context.state:
        alloc = tool_context.state["baseline_allocation"].get("illustrative_allocation")

    amt = monthly_investment
    if amt is None and tool_context and "investor_profile_data" in tool_context.state:
        amt = tool_context.state["investor_profile_data"].get("monthly_investment")

    data = calculate_portfolio_quant_data(alloc, amt)
    if data["status"] == "error":
        return data

    contrib_lines = []
    for ac, info in data["asset_class_contributions"].items():
        contrib_lines.append(
            f"- {ac} ({info['weight_pct']}% weight): Ann Return = {info['annual_return_pct']}%, "
            f"Ann Volatility = {info['annual_volatility_pct']}%, "
            f"Return Contribution = +{info['return_contribution_pct']}%"
        )

    return {
        "status": "success",
        "analysis": "Portfolio Quantitative Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "portfolio_allocation_pct": data["portfolio_allocation_pct"],
        "weighted_annual_return_pct": data["weighted_annual_return_pct"],
        "weighted_annual_volatility_pct": data["weighted_annual_volatility_pct"],
        "diversification_ratio": data["diversification_ratio"],
        "asset_class_contributions": data["asset_class_contributions"],
        "formatted_summary": (
            f"Weighted Simulated Annual Return: {data['weighted_annual_return_pct']}%\n"
            f"Weighted Simulated Annual Volatility: {data['weighted_annual_volatility_pct']}%\n"
            f"Diversification Ratio: {data['diversification_ratio']}\n\n"
            "Asset Contributions:\n" + "\n".join(contrib_lines)
        ),
        "method": data["method"],
        "interpretation": (
            "Illustrative portfolio combines growth and defensive assets to achieve balanced "
            "simulated return and volatility characteristics under synthetic model assumptions."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def compare_scenarios_quantitatively(
    scenario_id: str,
    scenario_id_2: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates quantitative comparison (simulated return, volatility, max drawdown, risk shift) between Baseline portfolio and a Scenario, or between two Scenarios.

    Args:
        scenario_id: Target scenario identifier (e.g. 'scenario_1', 'equity_shock_scenario').
        scenario_id_2: Optional second scenario identifier. If omitted, compares target scenario against stored Baseline.

    Returns:
        Structured quantitative comparison with baseline vs scenario metrics, explicit deltas (+/-), and risk shift interpretation.
    """
    scenarios = tool_context.state.get("scenarios", {}) if tool_context else {}

    target = scenarios.get(scenario_id)
    if not target:
        # Fallback hypothetical target if not found in session state
        target_alloc = {
            "Equity": 35.0,
            "Debt": 40.0,
            "Gold": 12.0,
            "International Equity": 8.0,
            "Cash / Liquid": 5.0,
        }
        name1 = scenario_id
    else:
        target_alloc = target.get("scenario_allocation", {}).get(
            "illustrative_allocation", {}
        )
        name1 = target.get("scenario_name", scenario_id)

    if scenario_id_2:
        target2 = scenarios.get(scenario_id_2)
        alloc2 = (
            target2.get("scenario_allocation", {}).get("illustrative_allocation", {})
            if target2
            else {}
        )
        name2 = (
            target2.get("scenario_name", scenario_id_2) if target2 else scenario_id_2
        )
        data = compare_scenarios_quant_data(
            target_alloc, alloc2, scenario_name=f"{name1} vs {name2}"
        )
    else:
        baseline_alloc = None
        if tool_context and "baseline_allocation" in tool_context.state:
            baseline_alloc = tool_context.state["baseline_allocation"].get(
                "illustrative_allocation"
            )

        data = compare_scenarios_quant_data(
            baseline_alloc, target_alloc, scenario_name=name1
        )

    return {
        "status": "success",
        "analysis": data["analysis"],
        "dataset": QUANT_DATASET_LABEL,
        "baseline_metrics": data["baseline_metrics"],
        "scenario_metrics": data["scenario_metrics"],
        "deltas": data["deltas"],
        "formatted_summary": (
            f"Analysis: {data['analysis']}\n"
            f"Baseline Volatility: {data['baseline_metrics']['weighted_annual_volatility_pct']}%\n"
            f"Scenario Volatility: {data['scenario_metrics']['weighted_annual_volatility_pct']}%\n"
            f"Volatility Delta: {data['deltas']['volatility_delta_pct']}%\n"
            f"Risk Shift: {data['deltas']['risk_profile_shift']}"
        ),
        "method": data["method"],
        "interpretation": (
            f"Hypothetical scenario results in a volatility change of {data['deltas']['volatility_delta_pct']}% "
            f"relative to baseline, indicating a '{data['deltas']['risk_profile_shift']}'."
        ),
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }
