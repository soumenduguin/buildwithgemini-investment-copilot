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

from datetime import UTC, datetime
from typing import Any

from app.market import get_market_overview_data
from app.portfolio import (
    ASSET_CLASSES,
    EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    adjust_allocation_for_market,
    analyze_portfolio_data,
    calculate_baseline_allocation,
)
from app.tools import (
    calculate_annual_investment_capacity,
    calculate_emergency_fund,
    calculate_monthly_surplus,
)

SUPPORTED_SCENARIO_PARAMS = {
    "monthly_income": float,
    "monthly_expenses": float,
    "monthly_investment": float,
    "investment_horizon_years": int,
    "risk_tolerance": str,
    "liquidity_requirement": str,
}


def build_scenario_data(
    base_profile: dict[str, Any],
    changed_params: dict[str, Any],
    scenario_id: str,
    scenario_name: str | None = None,
) -> dict[str, Any]:
    """Generates a non-destructive What-If scenario comparing baseline vs modified scenario parameters."""
    if not base_profile or not isinstance(base_profile, dict):
        return {
            "status": "error",
            "message": "Valid base investor profile is required.",
        }

    valid_changes = {}
    baseline_values = {}
    scenario_values = {}
    invalid_messages = []

    # Map possible key aliases
    param_map = {
        "monthly_income": "monthly_income",
        "income": "monthly_income",
        "monthly_expenses": "monthly_expenses",
        "expenses": "monthly_expenses",
        "monthly_investment": "monthly_investment_amount",
        "monthly_investment_amount": "monthly_investment_amount",
        "investment_horizon_years": "horizon_years",
        "horizon_years": "horizon_years",
        "horizon": "horizon_years",
        "risk_tolerance": "risk_tolerance",
        "risk": "risk_tolerance",
        "liquidity_requirement": "liquidity_requirement",
        "liquidity": "liquidity_requirement",
    }

    for raw_k, raw_v in changed_params.items():
        if raw_v is None:
            continue
        canon_k = param_map.get(raw_k.strip().lower())
        if not canon_k:
            invalid_messages.append(f"Unsupported parameter '{raw_k}'.")
            continue

        base_val = base_profile.get(canon_k)

        # Validation rules
        if canon_k in (
            "monthly_income",
            "monthly_expenses",
            "monthly_investment_amount",
        ):
            try:
                num_v = float(raw_v)
                if num_v < 0:
                    invalid_messages.append(f"Parameter '{raw_k}' cannot be negative.")
                    continue
                valid_changes[canon_k] = num_v
                baseline_values[canon_k] = (
                    float(base_val) if base_val is not None else 0.0
                )
                scenario_values[canon_k] = num_v
            except (ValueError, TypeError):
                invalid_messages.append(f"Parameter '{raw_k}' must be a valid number.")
                continue
        elif canon_k == "horizon_years":
            try:
                int_v = int(raw_v)
                if int_v <= 0:
                    invalid_messages.append(
                        "investment_horizon_years must be greater than 0."
                    )
                    continue
                valid_changes[canon_k] = int_v
                baseline_values[canon_k] = int(base_val) if base_val is not None else 5
                scenario_values[canon_k] = int_v
            except (ValueError, TypeError):
                invalid_messages.append("investment_horizon_years must be an integer.")
                continue
        elif canon_k == "risk_tolerance":
            str_v = str(raw_v).strip().title()
            if str_v.upper() not in ("CONSERVATIVE", "MODERATE", "AGGRESSIVE"):
                invalid_messages.append(
                    f"Invalid risk_tolerance '{raw_v}'. Must be Conservative, Moderate, or Aggressive."
                )
                continue
            valid_changes[canon_k] = str_v
            baseline_values[canon_k] = str(base_val) if base_val else "Moderate"
            scenario_values[canon_k] = str_v
        elif canon_k == "liquidity_requirement":
            str_v = str(raw_v).strip().title()
            if str_v.upper() not in ("LOW", "MEDIUM", "MODERATE", "HIGH"):
                invalid_messages.append(
                    f"Invalid liquidity_requirement '{raw_v}'. Must be Low, Medium, or High."
                )
                continue
            valid_changes[canon_k] = str_v
            baseline_values[canon_k] = str(base_val) if base_val else "Low"
            scenario_values[canon_k] = str_v

    if invalid_messages and not valid_changes:
        return {
            "status": "error",
            "message": f"Scenario validation failed: {'; '.join(invalid_messages)}",
        }

    if not valid_changes:
        return {
            "status": "error",
            "message": "No valid parameter changes provided for scenario.",
        }

    # Construct scenario profile copy (baseline profile is NEVER mutated)
    scen_profile = dict(base_profile)
    scen_profile.update(valid_changes)

    # 1. Baseline Calculations
    base_income = float(base_profile.get("monthly_income", 100000.0))
    base_expenses = float(base_profile.get("monthly_expenses", 60000.0))
    base_investment = float(base_profile.get("monthly_investment_amount", 30000.0))
    base_risk = str(base_profile.get("risk_tolerance", "Moderate"))
    base_horizon = int(base_profile.get("horizon_years", 5))
    base_liq = str(base_profile.get("liquidity_requirement", "Low"))

    base_surplus = calculate_monthly_surplus(base_income, base_expenses)
    base_ef = calculate_emergency_fund(base_expenses, 6)
    base_capacity = calculate_annual_investment_capacity(base_investment)

    base_alloc_res = calculate_baseline_allocation(
        base_risk, base_horizon, base_liq, base_investment
    )
    base_market_adj = adjust_allocation_for_market(
        base_alloc_res["illustrative_allocation"]
    )
    base_analysis = analyze_portfolio_data(
        base_market_adj["adjusted_allocation"], base_investment
    )

    # 2. Scenario Calculations
    scen_income = float(scen_profile.get("monthly_income", base_income))
    scen_expenses = float(scen_profile.get("monthly_expenses", base_expenses))
    scen_investment = float(
        scen_profile.get("monthly_investment_amount", base_investment)
    )
    scen_risk = str(scen_profile.get("risk_tolerance", base_risk))
    scen_horizon = int(scen_profile.get("horizon_years", base_horizon))
    scen_liq = str(scen_profile.get("liquidity_requirement", base_liq))

    scen_surplus = calculate_monthly_surplus(scen_income, scen_expenses)
    scen_ef = calculate_emergency_fund(scen_expenses, 6)
    scen_capacity = calculate_annual_investment_capacity(scen_investment)

    scen_alloc_res = calculate_baseline_allocation(
        scen_risk, scen_horizon, scen_liq, scen_investment
    )
    scen_market_adj = adjust_allocation_for_market(
        scen_alloc_res["illustrative_allocation"]
    )
    scen_analysis = analyze_portfolio_data(
        scen_market_adj["adjusted_allocation"], scen_investment
    )

    # 3. Differences
    base_alloc = base_market_adj["adjusted_allocation"]
    scen_alloc = scen_market_adj["adjusted_allocation"]

    alloc_diffs = {
        ac: round(scen_alloc.get(ac, 0.0) - base_alloc.get(ac, 0.0), 2)
        for ac in ASSET_CLASSES
    }

    financial_diffs = {
        "monthly_surplus": round(
            scen_surplus["monthly_surplus"] - base_surplus["monthly_surplus"], 2
        ),
        "emergency_fund_target": round(
            scen_ef["emergency_fund_target"] - base_ef["emergency_fund_target"],
            2,
        ),
        "annual_investment_capacity": round(
            scen_capacity["annual_investment_capacity"]
            - base_capacity["annual_investment_capacity"],
            2,
        ),
    }

    # Bulleted Explanations
    explanations = []
    for k, v in scenario_values.items():
        b_val = baseline_values[k]
        explanations.append(f"{k}: Changed from {b_val} to {v}.")

    for ac, diff in alloc_diffs.items():
        if diff != 0:
            direction = "increased" if diff > 0 else "decreased"
            explanations.append(
                f"{ac} allocation {direction} by {abs(diff)}% (from {base_alloc.get(ac)}% to {scen_alloc.get(ac)}%)."
            )

    display_name = (
        scenario_name
        if scenario_name
        else f"What-If: {', '.join([f'{k}={v}' for k, v in scenario_values.items()])}"
    )

    return {
        "status": "success",
        "scenario_id": scenario_id,
        "scenario_name": display_name,
        "created_at": datetime.now(UTC).isoformat(),
        "base_profile_reference": base_profile,
        "changed_parameters": scenario_values,
        "baseline_values": baseline_values,
        "scenario_values": scenario_values,
        "baseline_metrics": {
            "surplus": base_surplus,
            "emergency_fund": base_ef,
            "annual_capacity": base_capacity,
        },
        "scenario_metrics": {
            "surplus": scen_surplus,
            "emergency_fund": scen_ef,
            "annual_capacity": scen_capacity,
        },
        "baseline_allocation": base_alloc,
        "scenario_allocation": scen_alloc,
        "allocation_differences": alloc_diffs,
        "financial_metric_changes": financial_diffs,
        "baseline_portfolio_analysis": base_analysis,
        "scenario_portfolio_analysis": scen_analysis,
        "explanation": explanations,
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }


def build_market_shock_data(
    base_profile: dict[str, Any],
    asset_class: str,
    percentage_change: float,
    scenario_id: str,
    scenario_name: str | None = None,
) -> dict[str, Any]:
    """Simulates a hypothetical synthetic market shock on asset class return/volatility without modifying baseline data."""
    if not base_profile or not isinstance(base_profile, dict):
        return {
            "status": "error",
            "message": "Valid base investor profile is required.",
        }

    asset_clean = asset_class.strip()
    base_market = get_market_overview_data()

    # Create shocked market overview copy
    shocked_market = dict(base_market)

    # Apply hypothetical shock indicator changes
    market_notes = []
    if (
        "EQUITY" in asset_clean.upper()
        or "STOCK" in asset_clean.upper()
        or "BROAD" in asset_clean.upper()
    ):
        if percentage_change < 0:
            # Drop in equity spikes market volatility indicator
            shocked_market["highest_volatility"] = {
                "asset_name": "TECH_SECTOR_INDEX",
                "volatility_pct": 28.5,
            }
            market_notes.append(
                f"Equity Market Shock ({percentage_change}%): Synthetic volatility spiked to 28.5% (>20% threshold)."
            )
        else:
            shocked_market["highest_1y_return"] = {
                "asset_name": "BROAD_EQUITY_INDEX",
                "one_year_return_pct": 25.0,
            }
            market_notes.append(
                f"Equity Market Shock (+{percentage_change}%): 1-Yr synthetic equity return surged to 25.0%."
            )
    elif "GOLD" in asset_clean.upper() or "COMMODITY" in asset_clean.upper():
        if percentage_change > 0:
            shocked_market["highest_1y_return"] = {
                "asset_name": "GOLD_INDEX",
                "one_year_return_pct": 22.0,
            }
            market_notes.append(
                f"Gold Market Shock (+{percentage_change}%): Synthetic Gold 1-Yr return reached 22.0%."
            )
        else:
            market_notes.append(
                f"Gold Market Shock ({percentage_change}%): Synthetic Gold return softened."
            )
    else:
        market_notes.append(
            f"Market Shock on {asset_clean} ({percentage_change}%): Applied hypothetical shock indicators."
        )

    # 1. Baseline Calculations
    base_investment = float(base_profile.get("monthly_investment_amount", 30000.0))
    base_risk = str(base_profile.get("risk_tolerance", "Moderate"))
    base_horizon = int(base_profile.get("horizon_years", 5))
    base_liq = str(base_profile.get("liquidity_requirement", "Low"))

    base_alloc_res = calculate_baseline_allocation(
        base_risk, base_horizon, base_liq, base_investment
    )
    base_market_adj = adjust_allocation_for_market(
        base_alloc_res["illustrative_allocation"], base_market
    )

    # 2. Shocked Scenario Calculations
    shocked_market_adj = adjust_allocation_for_market(
        base_alloc_res["illustrative_allocation"], shocked_market
    )
    shocked_analysis = analyze_portfolio_data(
        shocked_market_adj["adjusted_allocation"], base_investment
    )

    base_alloc = base_market_adj["adjusted_allocation"]
    shocked_alloc = shocked_market_adj["adjusted_allocation"]

    alloc_diffs = {
        ac: round(shocked_alloc.get(ac, 0.0) - base_alloc.get(ac, 0.0), 2)
        for ac in ASSET_CLASSES
    }

    display_name = (
        scenario_name
        if scenario_name
        else f"Market Shock: {asset_clean} ({percentage_change:+}%)"
    )

    explanations = list(market_notes)
    explanations.extend(shocked_market_adj.get("adjustments_applied", []))

    return {
        "status": "success",
        "scenario_id": scenario_id,
        "scenario_name": display_name,
        "created_at": datetime.now(UTC).isoformat(),
        "base_profile_reference": base_profile,
        "shock_details": {
            "asset_class": asset_clean,
            "percentage_change": percentage_change,
        },
        "baseline_allocation": base_alloc,
        "scenario_allocation": shocked_alloc,
        "allocation_differences": alloc_diffs,
        "scenario_portfolio_analysis": shocked_analysis,
        "explanation": explanations,
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }
