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

from google.adk.tools import ToolContext, load_memory, preload_memory

from app.memory import (
    MEMORY_DATASET_LABEL,
    get_investor_memory,
    save_investor_facts,
)


def save_investor_memory(
    investor_name: str,
    investment_goal: str | None = None,
    risk_tolerance: str | None = None,
    horizon_years: int | None = None,
    liquidity_preference: str | None = None,
    simulation_preferences: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Stores stable investor contextual facts (goal, risk tolerance, horizon years, liquidity preference, simulation preferences) into cross-session Memory.

    Args:
        investor_name: Name of fictional investor (e.g. 'Alex').
        investment_goal: Primary investment goal (e.g. 'Long-term wealth creation').
        risk_tolerance: Risk tolerance (e.g. 'Moderate', 'Conservative', 'Aggressive').
        horizon_years: Investment horizon in years (e.g. 7).
        liquidity_preference: Liquidity requirement/preference (e.g. 'Low', 'Medium', 'High').
        simulation_preferences: Stated preference regarding simulation behavior.

    Returns:
        Confirmation dictionary with saved memory status and stored stable facts.
    """
    facts = {
        "investor_name": investor_name,
        "investment_goal": investment_goal,
        "risk_tolerance": risk_tolerance,
        "horizon_years": horizon_years,
        "liquidity_preference": liquidity_preference,
        "simulation_preferences": simulation_preferences,
    }

    # If parameters missing, attempt to populate from current profile in tool_context session state
    if tool_context and "investor_profile_data" in tool_context.state:
        profile = tool_context.state["investor_profile_data"]
        if not investment_goal and "investment_goal" in profile:
            facts["investment_goal"] = profile["investment_goal"]
        if not risk_tolerance and "risk_tolerance" in profile:
            facts["risk_tolerance"] = profile["risk_tolerance"]
        if not horizon_years and "horizon_years" in profile:
            facts["horizon_years"] = profile["horizon_years"]
        if not liquidity_preference and "liquidity_requirement" in profile:
            facts["liquidity_preference"] = profile["liquidity_requirement"]

    res = save_investor_facts(investor_name, facts)
    return res


def recall_investor_memory(
    investor_name: str,
    query: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Searches and retrieves remembered stable contextual facts for a fictional investor across sessions.

    Args:
        investor_name: Name of fictional investor to query (e.g. 'Alex').
        query: Optional specific topic/question to query (e.g. 'risk tolerance', 'investment goal').

    Returns:
        Structured result containing remembered facts or status 'not_found' if no relevant memory exists.
    """
    res = get_investor_memory(investor_name, query)
    if res["status"] == "not_found":
        return {
            "status": "not_found",
            "investor_name": investor_name,
            "message": f"No relevant cross-session memory found for investor '{investor_name}'.",
            "dataset": MEMORY_DATASET_LABEL,
        }

    return {
        "status": "success",
        "investor_name": res["investor_name"],
        "remembered_facts": res["remembered_facts"],
        "formatted_summary": (
            f"Remembered facts for {res['investor_name']}:\n"
            + "\n".join([f"- {k}: {v}" for k, v in res["remembered_facts"].items()])
        ),
        "dataset": MEMORY_DATASET_LABEL,
    }


__all__ = [
    "load_memory",
    "preload_memory",
    "recall_investor_memory",
    "save_investor_memory",
]
