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

from app.market import (
    analyze_asset_trend_data,
    compare_assets_data,
    get_market_overview_data,
    get_market_snapshot_data,
)


def get_market_snapshot(
    asset_name: str | None = None,
    asset_class: str | None = None,
) -> dict[str, Any]:
    """Retrieves synthetic market data records filtered by optional asset name or asset class.

    EDUCATIONAL SIMULATION ONLY: Returns fictitious market prices and performance metrics.

    Args:
        asset_name: Optional name filter (e.g., 'BROAD_EQUITY_INDEX', 'GOLD_INDEX').
        asset_class: Optional asset class filter (e.g., 'Broad Equity', 'Fixed Income').

    Returns:
        A dict containing matching synthetic asset records and an educational disclaimer.
    """
    return get_market_snapshot_data(asset_name=asset_name, asset_class=asset_class)


def analyze_asset_trend(asset_name: str) -> dict[str, Any]:
    """Performs deterministic trend, momentum, volatility, and price-range analysis for a synthetic asset.

    EDUCATIONAL SIMULATION ONLY: Analyzes fictitious market asset data using explicit deterministic rules.

    Args:
        asset_name: The target asset name to analyze (e.g., 'TECH_SECTOR_INDEX', 'BOND_INDEX').

    Returns:
        A dict containing deterministic trend classification, momentum indicator,
        volatility classification, 52-week price range position, and disclaimer.
    """
    return analyze_asset_trend_data(asset_name=asset_name)


def compare_assets(asset_names: list[str]) -> dict[str, Any]:
    """Side-by-side comparative analysis of multiple synthetic market assets.

    EDUCATIONAL SIMULATION ONLY: Compares fictitious metrics across multiple assets.

    Args:
        asset_names: A list of asset names to compare (e.g., ['BROAD_EQUITY_INDEX', 'GOLD_INDEX', 'BOND_INDEX']).

    Returns:
        A dict containing structured comparisons of returns, volatility, trend classifications,
        and an educational disclaimer.
    """
    return compare_assets_data(asset_names=asset_names)


def get_market_overview() -> dict[str, Any]:
    """Retrieves a high-level summary overview of the synthetic market dataset.

    EDUCATIONAL SIMULATION ONLY: Summarizes dataset statistics across all synthetic asset classes.

    Returns:
        A dict containing total asset count, represented asset classes, trend counts,
        highest/lowest 1-year returns, highest/lowest volatility assets, and disclaimer.
    """
    return get_market_overview_data()
