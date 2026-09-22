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

from app.portfolio import normalize_allocation
from app.portfolio_tools import (
    adjust_allocation_for_market_conditions,
    analyze_illustrative_portfolio,
    calculate_illustrative_allocation,
)


def test_conservative_investor():
    res = calculate_illustrative_allocation(
        risk_tolerance="Conservative",
        investment_horizon_years=5,
        liquidity_requirement="Low",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "success"
    alloc = res["illustrative_allocation"]
    assert alloc["Debt"] > alloc["Equity"]
    assert sum(alloc.values()) == 100.0


def test_moderate_investor():
    res = calculate_illustrative_allocation(
        risk_tolerance="Moderate",
        investment_horizon_years=5,
        liquidity_requirement="Low",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "success"
    alloc = res["illustrative_allocation"]
    assert alloc["Equity"] == 45.0
    assert alloc["Debt"] == 30.0
    assert sum(alloc.values()) == 100.0


def test_aggressive_investor():
    res = calculate_illustrative_allocation(
        risk_tolerance="Aggressive",
        investment_horizon_years=5,
        liquidity_requirement="Low",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "success"
    alloc = res["illustrative_allocation"]
    assert alloc["Equity"] > alloc["Debt"]
    assert sum(alloc.values()) == 100.0


def test_short_horizon():
    res = calculate_illustrative_allocation(
        risk_tolerance="Moderate",
        investment_horizon_years=2,
        liquidity_requirement="Low",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "success"
    alloc = res["illustrative_allocation"]
    # Defensive shift for short horizon
    assert alloc["Debt"] + alloc["Cash/Liquid"] > 35.0
    assert sum(alloc.values()) == 100.0


def test_long_horizon():
    res = calculate_illustrative_allocation(
        risk_tolerance="Moderate",
        investment_horizon_years=10,
        liquidity_requirement="Low",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "success"
    alloc = res["illustrative_allocation"]
    assert alloc["Equity"] > 45.0
    assert sum(alloc.values()) == 100.0


def test_high_liquidity_requirement():
    res = calculate_illustrative_allocation(
        risk_tolerance="Moderate",
        investment_horizon_years=5,
        liquidity_requirement="High",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "success"
    alloc = res["illustrative_allocation"]
    assert alloc["Cash/Liquid"] >= 14.0
    assert sum(alloc.values()) == 100.0


def test_zero_or_invalid_amount():
    res = calculate_illustrative_allocation(
        risk_tolerance="Moderate",
        investment_horizon_years=5,
        liquidity_requirement="Low",
        monthly_investment_amount=0.0,
    )
    assert res["status"] == "error"
    assert "greater than 0" in res["message"]


def test_invalid_risk_tolerance():
    res = calculate_illustrative_allocation(
        risk_tolerance="SuperRisk",
        investment_horizon_years=5,
        liquidity_requirement="Low",
        monthly_investment_amount=10000.0,
    )
    assert res["status"] == "error"
    assert "Invalid risk_tolerance" in res["message"]


def test_sum_exactly_100_percent():
    for risk in ["Conservative", "Moderate", "Aggressive"]:
        for horizon in [2, 5, 10]:
            for liq in ["Low", "Medium", "High"]:
                res = calculate_illustrative_allocation(
                    risk_tolerance=risk,
                    investment_horizon_years=horizon,
                    liquidity_requirement=liq,
                    monthly_investment_amount=5000.0,
                )
                assert res["status"] == "success"
                alloc = res["illustrative_allocation"]
                assert round(sum(alloc.values()), 2) == 100.0


def test_no_negative_allocation():
    raw = {
        "Equity": -10.0,
        "Debt": 50.0,
        "Gold": 30.0,
        "International Equity": 20.0,
        "Cash/Liquid": 10.0,
    }
    norm = normalize_allocation(raw)
    assert all(val >= 0.0 for val in norm.values())
    assert sum(norm.values()) == 100.0


def test_market_adjustment_bounds():
    base = {
        "Equity": 45.0,
        "Debt": 30.0,
        "Gold": 10.0,
        "International Equity": 10.0,
        "Cash/Liquid": 5.0,
    }
    mock_market = {
        "status": "success",
        "highest_volatility": {
            "asset_name": "TECH_SECTOR_INDEX",
            "volatility_pct": 25.0,
        },
        "highest_1y_return": {"asset_name": "GOLD_INDEX", "one_year_return_pct": 20.0},
        "trend_counts": {"BULLISH_POSITIVE": 6},
    }
    res = adjust_allocation_for_market_conditions(
        base_allocation=base, market_overview=mock_market
    )
    assert res["status"] == "success"
    adj = res["adjusted_allocation"]
    assert sum(adj.values()) == 100.0
    # Equity should not change by more than 5%
    assert abs(adj["Equity"] - base["Equity"]) <= 5.0
    assert abs(adj["Gold"] - base["Gold"]) <= 5.0


def test_portfolio_analysis():
    alloc = {
        "Equity": 45.0,
        "Debt": 30.0,
        "Gold": 10.0,
        "International Equity": 10.0,
        "Cash/Liquid": 5.0,
    }
    res = analyze_illustrative_portfolio(
        allocation=alloc, monthly_investment_amount=40000.0
    )
    assert res["status"] == "success"
    assert res["growth_allocation_pct"] == 55.0
    assert res["defensive_allocation_pct"] == 45.0
    assert res["total_allocation_pct"] == 100.0
    assert res["monthly_currency_allocation"]["Equity"] == 18000.0
    assert res["monthly_currency_allocation"]["Debt"] == 12000.0
    assert "EDUCATIONAL SIMULATION ONLY" in res["disclaimer"]
