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

from app.knowledge import KNOWLEDGE_BASE_DIR
from app.portfolio import calculate_baseline_allocation
from app.rag_tools import search_investment_knowledge


def test_knowledge_documents_exist():
    """Requirement 1: Verify all 5 reference documents exist in app/knowledge_base."""
    expected_files = [
        "risk_profiles.md",
        "asset_classes.md",
        "liquidity_guidelines.md",
        "portfolio_assumptions.md",
        "scenario_assumptions.md",
    ]
    assert KNOWLEDGE_BASE_DIR.exists()
    for filename in expected_files:
        filepath = KNOWLEDGE_BASE_DIR / filename
        assert filepath.exists(), f"Missing required document: {filename}"
        assert filepath.stat().st_size > 100, f"Document is empty: {filename}"


def test_retrieval_functionality():
    """Requirement 2: Verify search_investment_knowledge returns structured matches and educational labels."""
    res = search_investment_knowledge(query="simulation rules")
    assert res["status"] == "success"
    assert "educational_label" in res
    assert "matches" in res
    assert res["matches_found"] > 0


def test_risk_profile_query():
    """Requirement 3: Verify risk profile questions retrieve risk_profiles.md."""
    res = search_investment_knowledge(
        query="Why did the simulation classify this investor as moderate risk profile?"
    )
    assert res["status"] == "success"
    docs = [m["source_document"] for m in res["matches"]]
    assert "risk_profiles.md" in docs


def test_asset_class_query():
    """Requirement 4: Verify asset class questions retrieve asset_classes.md."""
    res = search_investment_knowledge(
        query="What role does gold and domestic equity play in this simulation?"
    )
    assert res["status"] == "success"
    docs = [m["source_document"] for m in res["matches"]]
    assert "asset_classes.md" in docs


def test_liquidity_query():
    """Requirement 5: Verify liquidity questions retrieve liquidity_guidelines.md."""
    res = search_investment_knowledge(
        query="Why did high liquidity requirements change liquid cash allocation?"
    )
    assert res["status"] == "success"
    docs = [m["source_document"] for m in res["matches"]]
    assert "liquidity_guidelines.md" in docs


def test_portfolio_rule_query():
    """Requirement 6: Verify portfolio rule questions retrieve portfolio_assumptions.md."""
    res = search_investment_knowledge(
        query="What assumptions baseline horizon liquidity market adjustment limits were used for portfolio?"
    )
    assert res["status"] == "success"
    docs = [m["source_document"] for m in res["matches"]]
    assert "portfolio_assumptions.md" in docs


def test_scenario_query():
    """Requirement 7: Verify scenario questions retrieve scenario_assumptions.md."""
    res = search_investment_knowledge(
        query="What rules govern market shock baseline preservation hypothetical scenario isolation?"
    )
    assert res["status"] == "success"
    docs = [m["source_document"] for m in res["matches"]]
    assert "scenario_assumptions.md" in docs


def test_unknown_question_handled():
    """Requirement 8: Verify unknown/unsupported questions return explicit notice without hallucination."""
    res = search_investment_knowledge(
        query="what exact rule determines cryptocurrency dogecoin leverage options trading margin?"
    )
    assert res["status"] == "success"
    assert res["matches_found"] == 0
    assert "No relevant rules" in res["message"]


def test_rag_does_not_modify_portfolio_calculations():
    """Requirement 9: Verify retrieval does not alter deterministic portfolio calculations."""
    base_res_before = calculate_baseline_allocation("MODERATE", 7, "LOW", 40000.0)

    # Perform multiple retrieval queries
    search_investment_knowledge("risk profiles")
    search_investment_knowledge("portfolio assumptions")

    base_res_after = calculate_baseline_allocation("MODERATE", 7, "LOW", 40000.0)

    assert (
        base_res_before["illustrative_allocation"]
        == base_res_after["illustrative_allocation"]
    )
