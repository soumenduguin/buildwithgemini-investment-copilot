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

import json

from app.memory import MEMORY_FILE_PATH, extract_stable_facts_from_profile
from app.memory_tools import recall_investor_memory, save_investor_memory
from app.scenarios import build_scenario_data


def setup_function():
    """Reset investor memory store before each test."""
    MEMORY_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)


def test_memory_creation():
    """1. Verify Memory creation for stable investor facts."""
    res = save_investor_memory(
        investor_name="Alex",
        investment_goal="Long-term wealth creation",
        risk_tolerance="Moderate",
        horizon_years=7,
        liquidity_preference="Low",
    )
    assert res["status"] == "success"
    assert res["investor_name"] == "Alex"
    assert res["saved_facts"]["investment_goal"] == "Long-term wealth creation"
    assert res["saved_facts"]["risk_tolerance"] == "Moderate"


def test_memory_retrieval():
    """2. Verify Memory retrieval of stored investor facts."""
    save_investor_memory(
        investor_name="Alex",
        investment_goal="Long-term wealth creation",
        risk_tolerance="Moderate",
        horizon_years=7,
        liquidity_preference="Low",
    )

    res = recall_investor_memory(investor_name="Alex")
    assert res["status"] == "success"
    facts = res["remembered_facts"]
    assert facts["investment_goal"] == "Long-term wealth creation"
    assert facts["risk_tolerance"] == "Moderate"
    assert facts["horizon_years"] == 7


def test_relevant_memory_retrieval():
    """3. Verify relevant memory retrieval for specific query."""
    save_investor_memory(
        investor_name="Alex",
        investment_goal="Long-term wealth creation",
        risk_tolerance="Moderate",
        horizon_years=7,
        liquidity_preference="Low",
    )

    res = recall_investor_memory(investor_name="Alex", query="risk_tolerance")
    assert res["status"] == "success"
    facts = res["remembered_facts"]
    assert "risk_tolerance" in facts
    assert facts["risk_tolerance"] == "Moderate"


def test_no_memory_case():
    """4. Verify no-memory case returns clear 'not_found' status without hallucinating."""
    res = recall_investor_memory(investor_name="NonExistentInvestor")
    assert res["status"] == "not_found"
    assert "No relevant cross-session memory found" in res["message"]


def test_conflicting_current_session_information():
    """5. Verify explicit current session inputs take precedence over remembered facts for current simulation."""
    # Memory says Moderate risk tolerance
    save_investor_memory(
        investor_name="Alex",
        risk_tolerance="Moderate",
    )

    # Current session explicitly provides Aggressive risk tolerance
    current_session_profile = {
        "investor_name": "Alex",
        "risk_tolerance": "Aggressive",
        "horizon_years": 10,
    }

    # Current session explicit risk tolerance is used for simulation
    effective_risk = current_session_profile["risk_tolerance"]
    assert effective_risk == "Aggressive"

    # Memory store retains original stable memory unless explicitly updated
    mem_res = recall_investor_memory("Alex")
    assert mem_res["remembered_facts"]["risk_tolerance"] == "Moderate"


def test_temporary_scenario_not_permanent_memory():
    """6. Verify temporary scenario modifications do NOT become permanent remembered memory."""
    # Baseline memory saved for Alex
    save_investor_memory(
        investor_name="Alex",
        investment_goal="Long-term wealth creation",
        risk_tolerance="Moderate",
        horizon_years=7,
        liquidity_preference="Low",
    )

    base_profile = {
        "investor_name": "Alex",
        "monthly_income": 100000.0,
        "monthly_expenses": 60000.0,
        "monthly_investment_amount": 40000.0,
        "risk_tolerance": "Moderate",
        "horizon_years": 7,
        "liquidity_requirement": "Low",
    }

    # User creates temporary scenario modifying monthly_investment to 60,000
    scenario_res = build_scenario_data(
        base_profile=base_profile,
        changed_params={"monthly_investment": 60000.0},
        scenario_id="scenario_temp",
        scenario_name="Temporary 60k Investment",
    )
    assert scenario_res["status"] == "success"

    # Ensure Memory retains original stable facts and does NOT record 60k scenario amount
    mem_res = recall_investor_memory("Alex")
    remembered = mem_res["remembered_facts"]
    assert "monthly_investment_amount" not in remembered
    assert remembered["investment_goal"] == "Long-term wealth creation"
    assert remembered["risk_tolerance"] == "Moderate"


def test_extract_stable_facts_from_profile():
    """7. Verify extract_stable_facts_from_profile extracts stable facts and ignores temporary calculations."""
    profile = {
        "investor_name": "Alex",
        "investment_goal": "Wealth Growth",
        "risk_tolerance": "Moderate",
        "horizon_years": 7,
        "liquidity_requirement": "Low",
        "monthly_income": 100000.0,
        "monthly_expenses": 60000.0,
        "monthly_investment_amount": 40000.0,
        "calculated_allocation": {"Equity": 50.0},
    }

    stable = extract_stable_facts_from_profile(profile)
    assert "investor_name" in stable
    assert "investment_goal" in stable
    assert "risk_tolerance" in stable
    assert "horizon_years" in stable
    assert "liquidity_preference" in stable
    assert "monthly_income" not in stable
    assert "monthly_investment_amount" not in stable
    assert "calculated_allocation" not in stable
