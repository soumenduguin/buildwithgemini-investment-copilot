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

from app.market import load_synthetic_market_data
from app.market_tools import (
    analyze_asset_trend,
    compare_assets,
    get_market_overview,
    get_market_snapshot,
)


def test_load_synthetic_market_data():
    records = load_synthetic_market_data()
    assert isinstance(records, list)
    assert len(records) >= 8
    first = records[0]
    assert "asset_name" in first
    assert "asset_class" in first
    assert "price" in first
    assert "one_year_return_pct" in first
    assert "volatility_pct" in first


def test_get_market_snapshot_no_filter():
    res = get_market_snapshot()
    assert res["status"] == "success"
    assert res["total_records"] >= 8
    assert "disclaimer" in res


def test_get_market_snapshot_filters():
    res_name = get_market_snapshot(asset_name="GOLD_INDEX")
    assert res_name["status"] == "success"
    assert res_name["total_records"] == 1
    assert res_name["assets"][0]["asset_name"] == "GOLD_INDEX"

    res_class = get_market_snapshot(asset_class="Fixed Income")
    assert res_class["status"] == "success"
    assert res_class["total_records"] >= 1
    assert res_class["assets"][0]["asset_class"] == "Fixed Income"


def test_analyze_asset_trend_bullish():
    res = analyze_asset_trend("BROAD_EQUITY_INDEX")
    assert res["status"] == "success"
    assert res["asset_name"] == "BROAD_EQUITY_INDEX"
    assert res["trend_classification"] == "BULLISH_POSITIVE"
    assert res["volatility_classification"] == "MODERATE"
    assert "disclaimer" in res


def test_analyze_asset_trend_bearish():
    res = analyze_asset_trend("REAL_ESTATE_INDEX")
    assert res["status"] == "success"
    assert res["asset_name"] == "REAL_ESTATE_INDEX"
    assert res["trend_classification"] == "BEARISH_NEGATIVE"
    assert res["momentum_indicator"] == "NEGATIVE"


def test_analyze_asset_trend_invalid_name():
    res = analyze_asset_trend("NON_EXISTENT_ASSET")
    assert res["status"] == "error"
    assert "not found" in res["message"]
    assert "available_assets" in res


def test_analyze_asset_trend_empty_string():
    res = analyze_asset_trend("")
    assert res["status"] == "error"
    assert "required" in res["message"]


def test_compare_assets_valid():
    res = compare_assets(["BROAD_EQUITY_INDEX", "GOLD_INDEX", "BOND_INDEX"])
    assert res["status"] == "success"
    assert res["compared_count"] == 3
    assert len(res["comparisons"]) == 3
    names = [c["asset_name"] for c in res["comparisons"]]
    assert "BROAD_EQUITY_INDEX" in names
    assert "GOLD_INDEX" in names
    assert "BOND_INDEX" in names


def test_compare_assets_empty_list():
    res = compare_assets([])
    assert res["status"] == "error"
    assert "must contain at least one asset name" in res["message"]


def test_compare_assets_with_invalid_name():
    res = compare_assets(["BROAD_EQUITY_INDEX", "UNKNOWN_INDEX"])
    assert res["status"] == "success"
    assert res["compared_count"] == 1
    assert "UNKNOWN_INDEX" in res["missing_assets"]


def test_get_market_overview():
    res = get_market_overview()
    assert res["status"] == "success"
    assert res["total_assets"] >= 8
    assert len(res["asset_classes"]) >= 5
    assert "trend_counts" in res
    assert "highest_1y_return" in res
    assert "lowest_1y_return" in res
    assert "highest_volatility" in res
    assert "lowest_volatility" in res
    assert "EDUCATIONAL SIMULATION ONLY" in res["disclaimer"]
