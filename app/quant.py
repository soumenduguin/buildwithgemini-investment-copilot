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

import math
import sys
import traceback
from typing import Any

from app.market import load_synthetic_market_data

QUANT_DATASET_LABEL = "Synthetic Market Dataset (app/data/synthetic_market_data.csv)"
QUANT_LIMITATION_DISCLAIMER = (
    "LIMITATION: This is an educational calculation based on synthetic simulation data "
    "and is not a prediction or guarantee of future real-world market performance."
)

# Simulated historical monthly return series for synthetic asset classes (in %)
SIMULATED_MONTHLY_RETURNS: dict[str, list[float]] = {
    "BROAD_EQUITY_INDEX": [
        2.5,
        -1.8,
        3.2,
        1.1,
        -4.2,
        2.8,
        1.5,
        -0.8,
        3.9,
        -2.1,
        1.7,
        2.4,
    ],
    "LARGE_CAP_INDEX": [1.8, -1.2, 2.5, 0.9, -3.1, 2.1, 1.2, -0.5, 2.8, -1.5, 1.3, 1.9],
    "MID_CAP_INDEX": [3.2, -2.9, 4.1, 1.8, -5.8, 3.6, 2.1, -1.4, 4.8, -3.2, 2.4, 3.1],
    "BOND_INDEX": [0.5, 0.6, 0.4, 0.5, 0.8, 0.4, 0.5, 0.6, 0.3, 0.5, 0.6, 0.4],
    "GOLD_INDEX": [-0.5, 1.2, -1.8, 2.1, 3.5, -0.4, 1.1, 2.2, -1.1, 1.5, -0.2, 0.9],
    "GLOBAL_EQUITY_INDEX": [
        1.9,
        -1.5,
        2.8,
        1.2,
        -3.8,
        2.3,
        1.4,
        -0.7,
        3.1,
        -1.9,
        1.5,
        2.1,
    ],
    "LIQUID_CASH_INDEX": [
        0.35,
        0.36,
        0.35,
        0.36,
        0.35,
        0.36,
        0.35,
        0.36,
        0.35,
        0.36,
        0.35,
        0.36,
    ],
    "TECH_SECTOR_INDEX": [
        4.2,
        -3.5,
        5.1,
        2.2,
        -6.5,
        4.8,
        3.1,
        -2.1,
        5.8,
        -4.2,
        3.5,
        4.2,
    ],
    "REAL_ESTATE_INDEX": [
        -1.2,
        -2.1,
        -0.8,
        -1.5,
        0.5,
        -1.8,
        -0.5,
        -2.2,
        1.1,
        -1.9,
        -0.8,
        -1.1,
    ],
}

# Alias mapping for portfolio asset classes to asset return keys
ASSET_ALIAS_MAP: dict[str, str] = {
    "equity": "BROAD_EQUITY_INDEX",
    "domestic broad equity index": "BROAD_EQUITY_INDEX",
    "broad equity": "BROAD_EQUITY_INDEX",
    "large-cap equity": "LARGE_CAP_INDEX",
    "mid-cap equity": "MID_CAP_INDEX",
    "debt": "BOND_INDEX",
    "fixed income": "BOND_INDEX",
    "fixed income bond index": "BOND_INDEX",
    "bond": "BOND_INDEX",
    "gold": "GOLD_INDEX",
    "commodity gold reserve": "GOLD_INDEX",
    "commodities": "GOLD_INDEX",
    "international equity": "GLOBAL_EQUITY_INDEX",
    "global developed equity index": "GLOBAL_EQUITY_INDEX",
    "cash / liquid": "LIQUID_CASH_INDEX",
    "cash": "LIQUID_CASH_INDEX",
    "cash equivalents": "LIQUID_CASH_INDEX",
    "liquid": "LIQUID_CASH_INDEX",
}


def run_sandboxed_python(
    python_code: str, custom_locals: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Executes a sandboxed Python code string for quantitative financial analysis.

    Args:
        python_code: Python snippet to execute.
        custom_locals: Additional local variables to inject.

    Returns:
        Execution results or error trace.
    """
    clean_code = python_code.strip()
    if not clean_code:
        return {
            "status": "error",
            "message": "Python code snippet cannot be empty.",
            "dataset": QUANT_DATASET_LABEL,
        }

    # Prepare safe execution environment
    market_assets = load_synthetic_market_data()
    safe_globals: dict[str, Any] = {
        "__builtins__": {
            "abs": abs,
            "all": all,
            "any": any,
            "dict": dict,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "print": print,
            "range": range,
            "round": round,
            "set": set,
            "str": str,
            "sum": sum,
            "zip": zip,
        },
        "math": math,
        "market_assets": market_assets,
        "monthly_returns": SIMULATED_MONTHLY_RETURNS,
    }

    local_vars: dict[str, Any] = {}
    if custom_locals:
        local_vars.update(custom_locals)

    try:
        # Execute python snippet
        exec(clean_code, safe_globals, local_vars)
        # Filter out builtins from returned local variables
        filtered_locals = {
            k: v
            for k, v in local_vars.items()
            if not k.startswith("__") and not callable(v)
        }
        return {
            "status": "success",
            "executed_code": clean_code,
            "variables": filtered_locals,
            "dataset": QUANT_DATASET_LABEL,
            "disclaimer": QUANT_LIMITATION_DISCLAIMER,
        }
    except Exception as e:
        exc_type, exc_val, exc_tb = sys.exc_info()
        tb_str = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
            "traceback": tb_str,
            "executed_code": clean_code,
            "dataset": QUANT_DATASET_LABEL,
        }


def _get_returns_for_asset(asset_name: str) -> list[float]:
    """Helper to find return series for an asset by exact name, alias, or keyword."""
    clean = asset_name.strip().lower()
    if clean in ASSET_ALIAS_MAP:
        target_key = ASSET_ALIAS_MAP[clean]
        if target_key in SIMULATED_MONTHLY_RETURNS:
            return SIMULATED_MONTHLY_RETURNS[target_key]

    for key, returns in SIMULATED_MONTHLY_RETURNS.items():
        if clean in key.lower() or key.lower() in clean:
            return returns

    # Fallback default return series
    return [1.0, 1.2, -0.8, 1.5, -1.1, 1.8, 0.9, -0.5, 1.4, -0.7, 1.1, 1.2]


def _std_dev(values: list[float]) -> float:
    """Calculates population standard deviation safely."""
    if not values or len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def calculate_returns_data(asset_names: list[str] | None = None) -> dict[str, Any]:
    """1. Historical Return Analysis over synthetic asset data."""
    all_market = load_synthetic_market_data()
    if not all_market:
        return {
            "status": "error",
            "message": "Synthetic market data file is empty or missing.",
            "dataset": QUANT_DATASET_LABEL,
        }

    targets = asset_names if asset_names else [a["asset_name"] for a in all_market]
    results = {}

    for name in targets:
        returns = _get_returns_for_asset(name)
        if not returns:
            continue
        avg_ret = sum(returns) / len(returns)
        # Cumulative compounding return
        cum_factor = 1.0
        for r in returns:
            cum_factor *= 1.0 + (r / 100.0)
        cum_ret = (cum_factor - 1.0) * 100.0

        results[name] = {
            "average_monthly_return_pct": round(avg_ret, 2),
            "annualized_cumulative_return_pct": round(cum_ret, 2),
            "period_returns_pct": returns,
        }

    return {
        "status": "success",
        "analysis": "Historical Return Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "results": results,
        "method": "Arithmetic average and geometric compounding over 12 monthly periods",
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def calculate_volatility_data(
    asset_names: list[str] | None = None,
    portfolio_allocation: dict[str, float] | None = None,
) -> dict[str, Any]:
    """2. Volatility Analysis over synthetic asset data."""
    all_market = load_synthetic_market_data()
    if not all_market:
        return {
            "status": "error",
            "message": "Synthetic market data file is empty or missing.",
            "dataset": QUANT_DATASET_LABEL,
        }

    targets = asset_names if asset_names else [a["asset_name"] for a in all_market]
    asset_volatilities = {}

    for name in targets:
        returns = _get_returns_for_asset(name)
        monthly_std = _std_dev(returns)
        # Annualized volatility = monthly_std * sqrt(12)
        ann_vol = monthly_std * math.sqrt(12)
        asset_volatilities[name] = {
            "monthly_std_dev_pct": round(monthly_std, 2),
            "annualized_volatility_pct": round(ann_vol, 2),
        }

    # Calculate portfolio volatility if allocation provided
    portfolio_vol = None
    if portfolio_allocation:
        # Normalize weights
        total_w = sum(portfolio_allocation.values())
        if total_w > 0:
            weighted_vol = 0.0
            for class_name, weight in portfolio_allocation.items():
                w = weight / total_w
                rets = _get_returns_for_asset(class_name)
                ann_v = _std_dev(rets) * math.sqrt(12)
                weighted_vol += w * ann_v
            portfolio_vol = round(weighted_vol, 2)

    return {
        "status": "success",
        "analysis": "Volatility Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "asset_volatilities": asset_volatilities,
        "portfolio_weighted_volatility_pct": portfolio_vol,
        "method": "Standard deviation of monthly return series multiplied by sqrt(12)",
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def calculate_drawdown_data(asset_names: list[str] | None = None) -> dict[str, Any]:
    """3. Drawdown Analysis over synthetic asset data."""
    all_market = load_synthetic_market_data()
    if not all_market:
        return {
            "status": "error",
            "message": "Synthetic market data file is empty or missing.",
            "dataset": QUANT_DATASET_LABEL,
        }

    targets = asset_names if asset_names else [a["asset_name"] for a in all_market]
    results = {}

    for name in targets:
        returns = _get_returns_for_asset(name)
        if not returns:
            continue

        price = 100.0
        peak = 100.0
        drawdowns = []
        max_dd = 0.0

        for r in returns:
            price *= 1.0 + (r / 100.0)
            if price > peak:
                peak = price
            dd = ((price - peak) / peak) * 100.0
            drawdowns.append(round(dd, 2))
            if dd < max_dd:
                max_dd = dd

        results[name] = {
            "peak_simulated_price": round(peak, 2),
            "end_simulated_price": round(price, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "period_drawdowns_pct": drawdowns,
        }

    return {
        "status": "success",
        "analysis": "Drawdown Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "results": results,
        "method": "Running peak-to-trough price series calculation",
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def calculate_correlation_data(
    asset_names: list[str] | None = None,
) -> dict[str, Any]:
    """4. Correlation Analysis between synthetic assets."""
    all_market = load_synthetic_market_data()
    if not all_market:
        return {
            "status": "error",
            "message": "Synthetic market data file is empty or missing.",
            "dataset": QUANT_DATASET_LABEL,
        }

    valid_targets = (
        asset_names if asset_names else [a["asset_name"] for a in all_market]
    )

    matrix: dict[str, dict[str, float]] = {}

    for name1 in valid_targets:
        matrix[name1] = {}
        rets1 = _get_returns_for_asset(name1)
        mean1 = sum(rets1) / len(rets1)
        std1 = _std_dev(rets1)

        for name2 in valid_targets:
            rets2 = _get_returns_for_asset(name2)
            mean2 = sum(rets2) / len(rets2)
            std2 = _std_dev(rets2)

            if std1 == 0 or std2 == 0:
                corr = 1.0 if name1 == name2 else 0.0
            else:
                cov = sum(
                    (rets1[i] - mean1) * (rets2[i] - mean2)
                    for i in range(min(len(rets1), len(rets2)))
                ) / len(rets1)
                corr = cov / (std1 * std2)

            matrix[name1][name2] = round(max(-1.0, min(1.0, corr)), 2)

    return {
        "status": "success",
        "analysis": "Correlation Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "correlation_matrix": matrix,
        "method": "Pearson pairwise correlation over monthly return series",
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def calculate_portfolio_quant_data(
    portfolio_allocation: dict[str, float] | None = None,
    monthly_investment: float | None = None,
) -> dict[str, Any]:
    """5. Portfolio Quantitative Analysis given illustrative allocation."""
    alloc = portfolio_allocation or {
        "Equity": 45.0,
        "Debt": 30.0,
        "Gold": 10.0,
        "International Equity": 10.0,
        "Cash / Liquid": 5.0,
    }
    total_w = sum(alloc.values())
    if total_w <= 0:
        return {
            "status": "error",
            "message": "Portfolio allocation weights must sum to > 0.",
            "dataset": QUANT_DATASET_LABEL,
        }

    norm_alloc = {k: round((v / total_w) * 100.0, 2) for k, v in alloc.items()}

    weighted_ret = 0.0
    weighted_vol = 0.0
    asset_contributions = {}

    for asset_class, weight in norm_alloc.items():
        rets = _get_returns_for_asset(asset_class)
        avg_ret = (sum(rets) / len(rets)) * 12  # Annualized simple
        ann_vol = _std_dev(rets) * math.sqrt(12)

        ret_contrib = (weight / 100.0) * avg_ret
        vol_contrib = (weight / 100.0) * ann_vol

        weighted_ret += ret_contrib
        weighted_vol += vol_contrib

        asset_contributions[asset_class] = {
            "weight_pct": weight,
            "annual_return_pct": round(avg_ret, 2),
            "annual_volatility_pct": round(ann_vol, 2),
            "return_contribution_pct": round(ret_contrib, 2),
            "volatility_contribution_pct": round(vol_contrib, 2),
        }

    # Diversification ratio estimate
    sum_individual_vols = sum(
        v["weight_pct"] / 100.0 * v["annual_volatility_pct"]
        for v in asset_contributions.values()
    )
    div_ratio = round(sum_individual_vols / max(0.01, weighted_vol), 2)

    monthly_amt = monthly_investment or 50000.0
    annual_capacity = monthly_amt * 12

    return {
        "status": "success",
        "analysis": "Portfolio Quantitative Analysis",
        "dataset": QUANT_DATASET_LABEL,
        "portfolio_allocation_pct": norm_alloc,
        "weighted_annual_return_pct": round(weighted_ret, 2),
        "weighted_annual_volatility_pct": round(weighted_vol, 2),
        "diversification_ratio": div_ratio,
        "monthly_investment": monthly_amt,
        "annual_investment_capacity": annual_capacity,
        "asset_class_contributions": asset_contributions,
        "method": "Weighted sum of asset returns, volatilities, and diversification ratio",
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }


def compare_scenarios_quant_data(
    baseline_alloc: dict[str, float] | None = None,
    scenario_alloc: dict[str, float] | None = None,
    scenario_name: str = "Hypothetical Scenario",
) -> dict[str, Any]:
    """6. Baseline vs Scenario Quantitative Comparison."""
    b_quant = calculate_portfolio_quant_data(baseline_alloc)
    s_quant = calculate_portfolio_quant_data(scenario_alloc)

    b_ret = b_quant["weighted_annual_return_pct"]
    s_ret = s_quant["weighted_annual_return_pct"]
    b_vol = b_quant["weighted_annual_volatility_pct"]
    s_vol = s_quant["weighted_annual_volatility_pct"]

    ret_delta = round(s_ret - b_ret, 2)
    vol_delta = round(s_vol - b_vol, 2)

    risk_shift = (
        "Higher Volatility / Growth Focus"
        if vol_delta > 0.5
        else (
            "Lower Volatility / Defensive Focus"
            if vol_delta < -0.5
            else "Neutral Risk Shift"
        )
    )

    return {
        "status": "success",
        "analysis": f"Quantitative Comparison: Baseline vs {scenario_name}",
        "dataset": QUANT_DATASET_LABEL,
        "baseline_metrics": {
            "weighted_annual_return_pct": b_ret,
            "weighted_annual_volatility_pct": b_vol,
            "allocation": b_quant["portfolio_allocation_pct"],
        },
        "scenario_metrics": {
            "scenario_name": scenario_name,
            "weighted_annual_return_pct": s_ret,
            "weighted_annual_volatility_pct": s_vol,
            "allocation": s_quant["portfolio_allocation_pct"],
        },
        "deltas": {
            "return_delta_pct": ret_delta,
            "volatility_delta_pct": vol_delta,
            "risk_profile_shift": risk_shift,
        },
        "method": "Side-by-side asset-class weighted return and volatility delta analysis",
        "disclaimer": QUANT_LIMITATION_DISCLAIMER,
    }
