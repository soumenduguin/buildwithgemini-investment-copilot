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

import csv
from pathlib import Path
from typing import Any

DATASET_PATH = Path(__file__).parent / "data" / "synthetic_market_data.csv"
EDUCATIONAL_MARKET_DISCLAIMER = (
    "SYNTHETIC DATASET FOR EDUCATIONAL SIMULATION ONLY: "
    "All prices, returns, volatility metrics, and asset performance data are fictitious "
    "and generated strictly for training and simulation purposes. They do NOT represent "
    "real current market prices or real financial instruments."
)


def load_synthetic_market_data() -> list[dict[str, Any]]:
    """Loads and parses the synthetic market dataset CSV file."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Synthetic market dataset not found at {DATASET_PATH}")

    records = []
    with open(DATASET_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "asset_name": row["asset_name"].strip(),
                    "asset_class": row["asset_class"].strip(),
                    "price": float(row["price"]),
                    "one_month_return_pct": float(row["one_month_return_pct"]),
                    "three_month_return_pct": float(row["three_month_return_pct"]),
                    "six_month_return_pct": float(row["six_month_return_pct"]),
                    "one_year_return_pct": float(row["one_year_return_pct"]),
                    "volatility_pct": float(row["volatility_pct"]),
                    "fifty_two_week_high": float(row["fifty_two_week_high"]),
                    "fifty_two_week_low": float(row["fifty_two_week_low"]),
                    "volume_trend": row["volume_trend"].strip(),
                }
            )
    return records


def get_market_snapshot_data(
    asset_name: str | None = None,
    asset_class: str | None = None,
) -> dict[str, Any]:
    """Retrieves synthetic market records matching optional asset_name or asset_class filters."""
    records = load_synthetic_market_data()

    filtered = records
    if asset_name:
        target_name = asset_name.strip().upper()
        filtered = [r for r in filtered if target_name in r["asset_name"].upper()]

    if asset_class:
        target_class = asset_class.strip().upper()
        filtered = [r for r in filtered if target_class in r["asset_class"].upper()]

    return {
        "status": "success",
        "total_records": len(filtered),
        "assets": filtered,
        "disclaimer": EDUCATIONAL_MARKET_DISCLAIMER,
    }


def analyze_asset_trend_data(asset_name: str) -> dict[str, Any]:
    """Deterministically analyzes trend, momentum, volatility, and price range position for an asset."""
    if not asset_name or not asset_name.strip():
        return {
            "status": "error",
            "message": "asset_name parameter is required for trend analysis.",
        }

    records = load_synthetic_market_data()
    target_name = asset_name.strip().upper()

    asset = None
    for r in records:
        if r["asset_name"].upper() == target_name:
            asset = r
            break

    if not asset:
        available_names = [r["asset_name"] for r in records]
        return {
            "status": "error",
            "message": f"Asset '{asset_name}' not found in synthetic dataset.",
            "available_assets": available_names,
        }

    p1m = asset["one_month_return_pct"]
    p3m = asset["three_month_return_pct"]
    p6m = asset["six_month_return_pct"]
    p1y = asset["one_year_return_pct"]
    vol = asset["volatility_pct"]
    price = asset["price"]
    high52 = asset["fifty_two_week_high"]
    low52 = asset["fifty_two_week_low"]

    # 1. Deterministic Trend Classification
    if p1y > 0 and p6m > 0 and p3m > 0:
        trend = "BULLISH_POSITIVE"
    elif p1y < 0 and p6m < 0 and p3m < 0:
        trend = "BEARISH_NEGATIVE"
    else:
        trend = "NEUTRAL_MIXED"

    # 2. Deterministic Momentum Indicators
    if p1m > 2.0 and p3m > 5.0:
        momentum = "STRONG_POSITIVE"
    elif p1m > 0:
        momentum = "WEAK_POSITIVE"
    elif p1m < 0:
        momentum = "NEGATIVE"
    else:
        momentum = "FLAT"

    # 3. Deterministic Volatility Classification
    if vol < 10.0:
        volatility_class = "LOW"
    elif vol <= 20.0:
        volatility_class = "MODERATE"
    else:
        volatility_class = "HIGH"

    # 4. Deterministic Price-Range Position
    if high52 > low52:
        range_pct = round(((price - low52) / (high52 - low52)) * 100, 2)
    else:
        range_pct = 50.0

    if range_pct >= 80.0:
        price_position = "NEAR_HIGH"
    elif range_pct >= 20.0:
        price_position = "MID_RANGE"
    else:
        price_position = "NEAR_LOW"

    return {
        "status": "success",
        "asset_name": asset["asset_name"],
        "asset_class": asset["asset_class"],
        "price": price,
        "returns": {
            "1m_pct": p1m,
            "3m_pct": p3m,
            "6m_pct": p6m,
            "1y_pct": p1y,
        },
        "trend_classification": trend,
        "momentum_indicator": momentum,
        "volatility_pct": vol,
        "volatility_classification": volatility_class,
        "fifty_two_week_high": high52,
        "fifty_two_week_low": low52,
        "range_position_pct": range_pct,
        "price_position_classification": price_position,
        "volume_trend": asset["volume_trend"],
        "disclaimer": EDUCATIONAL_MARKET_DISCLAIMER,
    }


def compare_assets_data(asset_names: list[str]) -> dict[str, Any]:
    """Compares multiple synthetic assets side-by-side using deterministic analysis."""
    if not asset_names or not isinstance(asset_names, list) or len(asset_names) == 0:
        return {
            "status": "error",
            "message": "asset_names list must contain at least one asset name.",
        }

    records = load_synthetic_market_data()
    all_by_name = {r["asset_name"].upper(): r for r in records}

    comparisons = []
    missing_assets = []

    for raw_name in asset_names:
        if not isinstance(raw_name, str):
            continue
        clean_name = raw_name.strip().upper()
        if clean_name in all_by_name:
            analysis = analyze_asset_trend_data(clean_name)
            comparisons.append(
                {
                    "asset_name": analysis["asset_name"],
                    "asset_class": analysis["asset_class"],
                    "price": analysis["price"],
                    "1y_return_pct": analysis["returns"]["1y_pct"],
                    "1m_return_pct": analysis["returns"]["1m_pct"],
                    "volatility_pct": analysis["volatility_pct"],
                    "volatility_classification": analysis["volatility_classification"],
                    "trend_classification": analysis["trend_classification"],
                    "price_position_classification": analysis[
                        "price_position_classification"
                    ],
                }
            )
        else:
            missing_assets.append(raw_name)

    return {
        "status": "success",
        "compared_count": len(comparisons),
        "comparisons": comparisons,
        "missing_assets": missing_assets,
        "disclaimer": EDUCATIONAL_MARKET_DISCLAIMER,
    }


def get_market_overview_data() -> dict[str, Any]:
    """Generates a high-level summary overview of the synthetic market dataset."""
    records = load_synthetic_market_data()

    if not records:
        return {
            "status": "error",
            "message": "No records found in synthetic dataset.",
        }

    asset_classes = sorted({r["asset_class"] for r in records})

    trends = {"BULLISH_POSITIVE": 0, "BEARISH_NEGATIVE": 0, "NEUTRAL_MIXED": 0}
    for r in records:
        analysis = analyze_asset_trend_data(r["asset_name"])
        t_cls = analysis.get("trend_classification", "NEUTRAL_MIXED")
        if t_cls in trends:
            trends[t_cls] += 1

    highest_1y = max(records, key=lambda r: r["one_year_return_pct"])
    lowest_1y = min(records, key=lambda r: r["one_year_return_pct"])

    highest_vol = max(records, key=lambda r: r["volatility_pct"])
    lowest_vol = min(records, key=lambda r: r["volatility_pct"])

    return {
        "status": "success",
        "total_assets": len(records),
        "asset_classes": asset_classes,
        "trend_counts": trends,
        "highest_1y_return": {
            "asset_name": highest_1y["asset_name"],
            "one_year_return_pct": highest_1y["one_year_return_pct"],
        },
        "lowest_1y_return": {
            "asset_name": lowest_1y["asset_name"],
            "one_year_return_pct": lowest_1y["one_year_return_pct"],
        },
        "highest_volatility": {
            "asset_name": highest_vol["asset_name"],
            "volatility_pct": highest_vol["volatility_pct"],
        },
        "lowest_volatility": {
            "asset_name": lowest_vol["asset_name"],
            "volatility_pct": lowest_vol["volatility_pct"],
        },
        "disclaimer": EDUCATIONAL_MARKET_DISCLAIMER,
    }
