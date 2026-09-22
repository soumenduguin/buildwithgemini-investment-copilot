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

from app.storage import STORAGE_FILE_PATH
from app.storage_tools import (
    delete_simulation,
    list_saved_scenarios,
    list_simulations,
    load_scenario,
    load_simulation,
    save_scenario,
    save_simulation,
)


def setup_function():
    """Reset persistent storage file before each test."""
    STORAGE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump({"simulations": {}, "scenarios": {}}, f)


def test_save_simulation():
    """1. Verify saving a complete fictional simulation record."""
    payload = {
        "fictional_investor_name": "Alex",
        "investor_profile": {
            "investor_name": "Alex",
            "age": 35,
            "monthly_income": 100000.0,
            "monthly_expenses": 60000.0,
            "monthly_investment_amount": 40000.0,
            "risk_tolerance": "Moderate",
            "horizon_years": 7,
        },
        "baseline_financial_metrics": {
            "monthly_surplus": 40000.0,
            "emergency_fund_target": 360000.0,
        },
        "baseline_portfolio": {
            "allocations": {
                "Equity": 55.0,
                "Debt": 30.0,
                "Gold": 10.0,
                "Cash": 5.0,
            }
        },
    }

    res = save_simulation(simulation_data=payload, simulation_id="SIM-ALEX-001")
    assert res["status"] == "success"
    assert res["simulation_id"] == "SIM-ALEX-001"
    assert res["fictional_investor_name"] == "Alex"
    assert "simulation_record" in res


def test_load_simulation():
    """2. Verify loading a persistent simulation by simulation_id and investor_name."""
    payload = {
        "fictional_investor_name": "Alex",
        "investor_profile": {"investor_name": "Alex", "risk_tolerance": "Moderate"},
    }
    save_simulation(simulation_data=payload, simulation_id="SIM-ALEX-001")

    # Load by exact simulation_id
    res_id = load_simulation(identifier="SIM-ALEX-001")
    assert res_id["status"] == "success"
    assert res_id["simulation_record"]["fictional_investor_name"] == "Alex"

    # Load by investor name
    res_name = load_simulation(identifier="Alex")
    assert res_name["status"] == "success"
    assert res_name["simulation_id"] == "SIM-ALEX-001"


def test_list_simulations():
    """3. Verify listing persistent simulations and filtering by investor name."""
    save_simulation(
        simulation_data={"fictional_investor_name": "Alex"}, simulation_id="SIM-001"
    )
    save_simulation(
        simulation_data={"fictional_investor_name": "Sam"}, simulation_id="SIM-002"
    )

    res_all = list_simulations()
    assert res_all["status"] == "success"
    assert res_all["count"] == 2

    res_filter = list_simulations(investor_name="Sam")
    assert res_filter["status"] == "success"
    assert res_filter["count"] == 1
    assert res_filter["simulations"][0]["simulation_id"] == "SIM-002"


def test_save_scenario():
    """4. Verify saving a What-If scenario associated with a simulation ID."""
    scen_payload = {
        "simulation_id": "SIM-ALEX-001",
        "scenario_name": "25% Equity Market Shock",
        "scenario_type": "market_shock",
        "changed_parameters": {"equity_shock": -0.25},
        "scenario_allocation": {"Equity": 40.0, "Debt": 45.0, "Gold": 15.0},
    }

    res = save_scenario(scenario_data=scen_payload, scenario_id="SCEN-SHOCK-001")
    assert res["status"] == "success"
    assert res["scenario_id"] == "SCEN-SHOCK-001"
    assert res["simulation_id"] == "SIM-ALEX-001"
    assert res["scenario_name"] == "25% Equity Market Shock"


def test_load_scenario():
    """5. Verify loading a persistent scenario by scenario_id."""
    scen_payload = {
        "simulation_id": "SIM-ALEX-001",
        "scenario_name": "Conservative Shift",
        "scenario_type": "parameter_modification",
        "changed_parameters": {"risk_tolerance": "Conservative"},
    }
    save_scenario(scenario_data=scen_payload, scenario_id="SCEN-CONS-001")

    res = load_scenario(scenario_id="SCEN-CONS-001")
    assert res["status"] == "success"
    assert res["scenario_record"]["scenario_name"] == "Conservative Shift"


def test_list_scenarios():
    """6. Verify listing scenarios associated with a simulation ID."""
    save_scenario(
        scenario_data={
            "simulation_id": "SIM-ALEX-001",
            "scenario_name": "Scenario A",
        },
        scenario_id="SCEN-A",
    )
    save_scenario(
        scenario_data={
            "simulation_id": "SIM-ALEX-001",
            "scenario_name": "Scenario B",
        },
        scenario_id="SCEN-B",
    )
    save_scenario(
        scenario_data={
            "simulation_id": "SIM-SAM-001",
            "scenario_name": "Scenario C",
        },
        scenario_id="SCEN-C",
    )

    res = list_saved_scenarios(simulation_id="SIM-ALEX-001")
    assert res["status"] == "success"
    assert res["count"] == 2
    scen_ids = [s["scenario_id"] for s in res["scenarios"]]
    assert "SCEN-A" in scen_ids
    assert "SCEN-B" in scen_ids
    assert "SCEN-C" not in scen_ids


def test_missing_simulation():
    """7. Verify handling of missing simulation returns clear 'not_found' status."""
    res = load_simulation(identifier="SIM-NONEXISTENT")
    assert res["status"] == "not_found"
    assert "No persistent simulation record found" in res["message"]


def test_missing_scenario():
    """8. Verify handling of missing scenario returns clear 'not_found' status."""
    res = load_scenario(scenario_id="SCEN-NONEXISTENT")
    assert res["status"] == "not_found"
    assert "No persistent scenario record found" in res["message"]


def test_invalid_record_payload():
    """9. Verify handling of invalid / malformed payload data without crashing."""
    res_sim = save_simulation(simulation_data=None)
    assert res_sim["status"] == "error"
    assert "Invalid simulation data" in res_sim["message"]

    res_scen = save_scenario(scenario_data="invalid_string")
    assert res_scen["status"] == "error"
    assert "Invalid scenario data" in res_scen["message"]

    res_del = delete_simulation(simulation_id="SIM-NONEXISTENT")
    assert res_del["status"] == "not_found"


def test_delete_simulation():
    """10. Verify deleting a simulation also cleans up associated scenarios."""
    save_simulation(
        simulation_data={"fictional_investor_name": "Alex"}, simulation_id="SIM-DEL-001"
    )
    save_scenario(
        scenario_data={
            "simulation_id": "SIM-DEL-001",
            "scenario_name": "Child Scenario",
        },
        scenario_id="SCEN-DEL-001",
    )

    res_del = delete_simulation(simulation_id="SIM-DEL-001")
    assert res_del["status"] == "success"

    assert load_simulation("SIM-DEL-001")["status"] == "not_found"
    assert load_scenario("SCEN-DEL-001")["status"] == "not_found"
