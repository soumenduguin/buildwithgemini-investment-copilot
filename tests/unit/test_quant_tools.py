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

from app.quant import (
    _std_dev,
    calculate_returns_data,
    run_sandboxed_python,
)
from app.quant_tools import (
    analyze_correlations,
    analyze_drawdowns,
    analyze_historical_returns,
    analyze_portfolio_quantitatively,
    analyze_volatility,
    compare_scenarios_quantitatively,
    execute_quantitative_analysis,
)


def test_return_calculation():
    """1. Verify return calculation (average return, cumulative return, period-by-period returns)."""
    res = analyze_historical_returns(["Domestic Broad Equity Index"])
    assert res["status"] == "success"
    assert "Domestic Broad Equity Index" in res["results"]
    metrics = res["results"]["Domestic Broad Equity Index"]
    assert "average_monthly_return_pct" in metrics
    assert "annualized_cumulative_return_pct" in metrics
    assert len(metrics["period_returns_pct"]) == 12


def test_volatility_calculation():
    """2. Verify volatility calculation (annualized standard deviation, portfolio weighted volatility)."""
    alloc = {"Equity": 60.0, "Debt": 30.0, "Gold": 10.0}
    res = analyze_volatility(
        asset_names=["Domestic Broad Equity Index"], portfolio_allocation=alloc
    )
    assert res["status"] == "success"
    assert "portfolio_weighted_volatility_pct" in res
    assert res["portfolio_weighted_volatility_pct"] > 0.0


def test_drawdown_calculation():
    """3. Verify drawdown calculation (peak price, end price, max drawdown)."""
    res = analyze_drawdowns(["Domestic Broad Equity Index"])
    assert res["status"] == "success"
    assert "Domestic Broad Equity Index" in res["results"]
    dd = res["results"]["Domestic Broad Equity Index"]
    assert dd["peak_simulated_price"] >= 100.0
    assert dd["max_drawdown_pct"] <= 0.0


def test_correlation_calculation():
    """4. Verify correlation calculation (pairwise correlation matrix)."""
    res = analyze_correlations(
        ["Domestic Broad Equity Index", "Commodity Gold Reserve"]
    )
    assert res["status"] == "success"
    matrix = res["correlation_matrix"]
    assert "Domestic Broad Equity Index" in matrix
    assert matrix["Domestic Broad Equity Index"]["Domestic Broad Equity Index"] == 1.0


def test_portfolio_calculation():
    """5. Verify portfolio quantitative analysis (weighted return, weighted volatility, contributions)."""
    alloc = {"Equity": 45.0, "Debt": 30.0, "Gold": 10.0, "Cash": 15.0}
    res = analyze_portfolio_quantitatively(
        portfolio_allocation=alloc, monthly_investment=50000.0
    )
    assert res["status"] == "success"
    assert res["weighted_annual_return_pct"] > 0.0
    assert res["weighted_annual_volatility_pct"] > 0.0
    assert "asset_class_contributions" in res


def test_baseline_vs_scenario_comparison():
    """6. Verify quantitative scenario comparison (baseline vs scenario volatility and return deltas)."""
    res = compare_scenarios_quantitatively(scenario_id="hypothetical_shock")
    assert res["status"] == "success"
    assert "deltas" in res
    assert "volatility_delta_pct" in res["deltas"]


def test_empty_dataset_handling(monkeypatch):
    """7. Verify empty dataset handling returns error cleanly."""
    monkeypatch.setattr("app.quant.load_synthetic_market_data", lambda: [])
    res = calculate_returns_data()
    assert res["status"] == "error"
    assert "empty" in res["message"].lower()


def test_invalid_data_handling():
    """8. Verify invalid asset data or invalid allocations are handled cleanly."""
    res = analyze_portfolio_quantitatively(
        portfolio_allocation={"InvalidAsset": -100.0}
    )
    assert res["status"] == "error"


def test_missing_values_handling():
    """9. Verify missing asset return series fall back safely without crashing."""
    res = analyze_historical_returns(["Unknown Asset Class 123"])
    assert res["status"] == "success"
    assert "Unknown Asset Class 123" in res["results"]


def test_division_by_zero_handling():
    """10. Verify zero-volatility / constant return series does not raise ZeroDivisionError."""
    const_returns = [2.0] * 12
    std = _std_dev(const_returns)
    assert std == 0.0

    # Sandboxed python with zero variance series
    code = "res = sum([2, 2, 2]) / 3"
    exec_res = run_sandboxed_python(code)
    assert exec_res["status"] == "success"
    assert exec_res["variables"]["res"] == 2.0


def test_code_execution_failure_handling():
    """11. Verify syntax error or execution failure in sandboxed Python is caught safely."""
    invalid_code = "x = 1 / 0"
    res = execute_quantitative_analysis(python_code=invalid_code)
    assert res["status"] == "error"
    assert "ZeroDivisionError" in res["message"] or "failed" in res["message"]
