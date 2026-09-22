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

from google.adk.tools import FunctionTool

from app.storage import storage_service


def save_simulation(
    simulation_data: dict[str, Any],
    simulation_id: str | None = None,
) -> dict[str, Any]:
    """Saves a completed fictional investment simulation record into persistent storage.

    Args:
        simulation_data: Dictionary containing fictional investor profile, baseline financial
          metrics, baseline portfolio allocation, and simulation assumptions.
        simulation_id: Optional custom simulation ID (e.g. 'SIM-001' or 'sim_alex_baseline').

    Returns:
        Structured confirmation dictionary with simulation_id and persistence_mode.
    """
    return storage_service.save_simulation(
        simulation_data=simulation_data, simulation_id=simulation_id
    )


def load_simulation(identifier: str) -> dict[str, Any]:
    """Retrieves a stored fictional simulation record by simulation_id or investor name.

    Args:
        identifier: simulation_id (e.g. 'SIM-001') or fictional investor name (e.g. 'Alex').

    Returns:
        Structured simulation record dictionary or status 'not_found'.
    """
    return storage_service.load_simulation(identifier=identifier)


def list_simulations(investor_name: str | None = None) -> dict[str, Any]:
    """Lists available persistent fictional simulation records.

    Args:
        investor_name: Optional investor name to filter by.

    Returns:
        Dictionary containing list of saved simulation summaries and total count.
    """
    return storage_service.list_simulations(investor_name=investor_name)


def delete_simulation(simulation_id: str) -> dict[str, Any]:
    """Safely deletes a persistent simulation record and its associated scenarios.

    Args:
        simulation_id: Unique simulation identifier.

    Returns:
        Deletion status dictionary.
    """
    return storage_service.delete_simulation(simulation_id=simulation_id)


def save_scenario(
    scenario_data: dict[str, Any],
    scenario_id: str | None = None,
) -> dict[str, Any]:
    """Persists a What-If scenario associated with a simulation.

    Args:
        scenario_data: Scenario dictionary containing simulation_id, scenario_name,
          scenario_type, changed_parameters, baseline_values, scenario_values, scenario_allocation.
        scenario_id: Optional custom scenario ID.

    Returns:
        Save confirmation dictionary.
    """
    return storage_service.save_scenario(
        scenario_data=scenario_data, scenario_id=scenario_id
    )


def load_scenario(scenario_id: str, simulation_id: str | None = None) -> dict[str, Any]:
    """Retrieves a stored What-If scenario record by scenario_id.

    Args:
        scenario_id: Unique scenario ID or scenario name.
        simulation_id: Optional parent simulation ID filter.

    Returns:
        Scenario record dictionary or status 'not_found'.
    """
    return storage_service.load_scenario(
        scenario_id=scenario_id, simulation_id=simulation_id
    )


def list_saved_scenarios(simulation_id: str | None = None) -> dict[str, Any]:
    """Lists stored What-If scenarios associated with a simulation in persistent storage.

    Args:
        simulation_id: Optional simulation ID filter.

    Returns:
        Dictionary containing list of scenario summaries and total count.
    """
    return storage_service.list_scenarios(simulation_id=simulation_id)


# ADK FunctionTool wrappers
save_simulation_tool = FunctionTool(save_simulation)
load_simulation_tool = FunctionTool(load_simulation)
list_simulations_tool = FunctionTool(list_simulations)
delete_simulation_tool = FunctionTool(delete_simulation)
save_scenario_tool = FunctionTool(save_scenario)
load_scenario_tool = FunctionTool(load_scenario)
list_saved_scenarios_tool = FunctionTool(list_saved_scenarios)

__all__ = [
    "delete_simulation",
    "delete_simulation_tool",
    "list_saved_scenarios",
    "list_saved_scenarios_tool",
    "list_simulations",
    "list_simulations_tool",
    "load_scenario",
    "load_scenario_tool",
    "load_simulation",
    "load_simulation_tool",
    "save_scenario",
    "save_scenario_tool",
    "save_simulation",
    "save_simulation_tool",
]
