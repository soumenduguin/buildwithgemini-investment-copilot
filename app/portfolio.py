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

EDUCATIONAL_PORTFOLIO_DISCLAIMER = (
    "EDUCATIONAL SIMULATION ONLY: This illustrative asset allocation is generated strictly "
    "for educational and fictitious portfolio simulation purposes using configured deterministic "
    "rules. It does NOT constitute personalized financial advice, wealth management recommendations, "
    "guaranteed returns, or real-world investment strategies."
)

ASSET_CLASSES = ["Equity", "Debt", "Gold", "International Equity", "Cash/Liquid"]

BASELINE_ALLOCATIONS: dict[str, dict[str, float]] = {
    "CONSERVATIVE": {
        "Equity": 20.0,
        "Debt": 55.0,
        "Gold": 10.0,
        "International Equity": 5.0,
        "Cash/Liquid": 10.0,
    },
    "MODERATE": {
        "Equity": 45.0,
        "Debt": 30.0,
        "Gold": 10.0,
        "International Equity": 10.0,
        "Cash/Liquid": 5.0,
    },
    "AGGRESSIVE": {
        "Equity": 60.0,
        "Debt": 15.0,
        "Gold": 5.0,
        "International Equity": 15.0,
        "Cash/Liquid": 5.0,
    },
}


def normalize_allocation(allocation: dict[str, float]) -> dict[str, float]:
    """Ensures no percentage is negative, normalizes total sum to exactly 100.0%, and rounds cleanly."""
    clamped = {k: max(0.0, float(v)) for k, v in allocation.items()}
    total = sum(clamped.values())

    if total <= 0:
        # Default equal split fallback
        default_val = 100.0 / len(ASSET_CLASSES)
        return dict.fromkeys(ASSET_CLASSES, default_val)

    scaled = {k: round((v / total) * 100.0, 2) for k, v in clamped.items()}
    scaled_total = round(sum(scaled.values()), 2)
    diff = round(100.0 - scaled_total, 2)

    if diff != 0:
        largest_key = max(scaled, key=lambda k: scaled[k])
        scaled[largest_key] = round(scaled[largest_key] + diff, 2)

    return scaled


def calculate_baseline_allocation(
    risk_tolerance: str,
    investment_horizon_years: int,
    liquidity_requirement: str,
    monthly_investment_amount: float,
) -> dict[str, Any]:
    """Calculates deterministic illustrative asset allocation based on investor parameters."""

    if monthly_investment_amount <= 0:
        return {
            "status": "error",
            "message": "monthly_investment_amount must be greater than 0.",
        }

    if investment_horizon_years <= 0:
        return {
            "status": "error",
            "message": "investment_horizon_years must be greater than 0.",
        }

    risk_clean = risk_tolerance.strip().upper() if risk_tolerance else ""
    if risk_clean not in BASELINE_ALLOCATIONS:
        valid_options = list(BASELINE_ALLOCATIONS.keys())
        return {
            "status": "error",
            "message": f"Invalid risk_tolerance '{risk_tolerance}'. Must be one of {valid_options}.",
        }

    base = dict(BASELINE_ALLOCATIONS[risk_clean])
    assumptions = [f"Baseline allocation selected for {risk_clean} risk tolerance."]

    # Horizon adjustments
    if investment_horizon_years <= 3:
        base["Debt"] += 5.0
        base["Cash/Liquid"] += 5.0
        base["Equity"] = max(0.0, base["Equity"] - 10.0)
        assumptions.append(
            f"Short horizon ({investment_horizon_years} yrs <= 3 yrs): Shifted 10% from Equity to Debt/Cash."
        )
    elif investment_horizon_years >= 7:
        base["Equity"] += 5.0
        base["Debt"] = max(0.0, base["Debt"] - 5.0)
        assumptions.append(
            f"Long horizon ({investment_horizon_years} yrs >= 7 yrs): Shifted 5% from Debt to Equity."
        )

    # Liquidity adjustments
    liq_clean = liquidity_requirement.strip().upper() if liquidity_requirement else ""
    if liq_clean == "HIGH":
        base["Cash/Liquid"] += 10.0
        base["Debt"] = max(0.0, base["Debt"] - 5.0)
        base["Equity"] = max(0.0, base["Equity"] - 5.0)
        assumptions.append(
            "High liquidity requirement: Shifted 10% to Cash/Liquid from Equity/Debt."
        )
    elif liq_clean in ("MEDIUM", "MODERATE"):
        base["Cash/Liquid"] += 5.0
        base["Debt"] = max(0.0, base["Debt"] - 5.0)
        assumptions.append(
            "Medium liquidity requirement: Shifted 5% to Cash/Liquid from Debt."
        )

    normalized = normalize_allocation(base)

    return {
        "status": "success",
        "risk_tolerance": risk_clean,
        "horizon_years": investment_horizon_years,
        "liquidity_requirement": liq_clean,
        "monthly_investment_amount": monthly_investment_amount,
        "illustrative_allocation": normalized,
        "assumptions": assumptions,
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }


def adjust_allocation_for_market(
    base_allocation: dict[str, float],
    market_overview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Applies bounded deterministic market adjustments (max +-5 percentage points) to a portfolio allocation."""
    if not base_allocation or not isinstance(base_allocation, dict):
        return {
            "status": "error",
            "message": "base_allocation dict is required.",
        }

    adjusted = dict(base_allocation)
    adjustments_made = []

    if market_overview and market_overview.get("status") == "success":
        highest_vol = market_overview.get("highest_volatility", {}).get(
            "volatility_pct", 0.0
        )
        highest_ret_asset = market_overview.get("highest_1y_return", {}).get(
            "asset_name", ""
        )

        # Rule 1: High market volatility -> Modest shift from Equity to Debt (bounded at 3.0%)
        if highest_vol > 20.0:
            shift = min(5.0, 3.0)
            if adjusted.get("Equity", 0.0) >= shift:
                adjusted["Equity"] -= shift
                adjusted["Debt"] = adjusted.get("Debt", 0.0) + shift
                adjustments_made.append(
                    f"Market volatility elevated ({highest_vol}% > 20%): Bounded shift of {shift}% from Equity to Debt."
                )

        # Rule 2: Strong commodity/Gold trend -> Modest shift to Gold (bounded at 3.0%)
        if (
            "GOLD" in highest_ret_asset.upper()
            or market_overview.get("trend_counts", {}).get("BULLISH_POSITIVE", 0) >= 5
        ):
            shift = min(5.0, 2.0)
            if adjusted.get("Cash/Liquid", 0.0) >= shift:
                adjusted["Cash/Liquid"] -= shift
                adjusted["Gold"] = adjusted.get("Gold", 0.0) + shift
                adjustments_made.append(
                    f"Strong market momentum: Bounded shift of {shift}% to Gold from Cash/Liquid."
                )

    normalized = normalize_allocation(adjusted)

    return {
        "status": "success",
        "original_allocation": base_allocation,
        "adjusted_allocation": normalized,
        "adjustments_applied": (
            adjustments_made
            if adjustments_made
            else ["No market adjustments triggered; baseline maintained."]
        ),
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }


def analyze_portfolio_data(
    allocation: dict[str, float],
    monthly_investment_amount: float | None = None,
) -> dict[str, Any]:
    """Generates a structured portfolio analysis, growth vs defensive balance, and diversification summary."""
    if not allocation or not isinstance(allocation, dict):
        return {
            "status": "error",
            "message": "allocation dictionary is required.",
        }

    normalized = normalize_allocation(allocation)

    growth_pct = round(
        normalized.get("Equity", 0.0) + normalized.get("International Equity", 0.0),
        2,
    )
    defensive_pct = round(
        normalized.get("Debt", 0.0)
        + normalized.get("Gold", 0.0)
        + normalized.get("Cash/Liquid", 0.0),
        2,
    )

    currency_breakdown = {}
    if monthly_investment_amount and monthly_investment_amount > 0:
        currency_breakdown = {
            k: round((v / 100.0) * monthly_investment_amount, 2)
            for k, v in normalized.items()
        }

    asset_count = sum(1 for v in normalized.values() if v > 0)
    diversification = (
        f"Multi-asset portfolio diversified across {asset_count} asset classes "
        f"({growth_pct}% Growth / {defensive_pct}% Defensive balance)."
    )

    assumptions = [
        "Illustrative asset class weightings sum to exactly 100.0%.",
        f"Growth assets (Equity + International Equity) comprise {growth_pct}% of total allocation.",
        f"Defensive & Liquid assets (Debt + Gold + Cash) comprise {defensive_pct}% of total allocation.",
        "Deterministic educational rules applied without individual security selection.",
    ]

    return {
        "status": "success",
        "asset_allocation_pct": normalized,
        "monthly_currency_allocation": currency_breakdown,
        "growth_allocation_pct": growth_pct,
        "defensive_allocation_pct": defensive_pct,
        "total_allocation_pct": round(sum(normalized.values()), 2),
        "diversification_summary": diversification,
        "assumptions": assumptions,
        "disclaimer": EDUCATIONAL_PORTFOLIO_DISCLAIMER,
    }
