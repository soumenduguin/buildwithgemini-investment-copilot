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
from typing import Any

from google.adk.tools import ToolContext

from app.schema import REQUIRED_FIELDS, InvestorProfile, check_inconsistencies


def save_profile_fields(fields_json: str, tool_context: ToolContext) -> dict[str, Any]:
    """Saves or updates one or more fields in the investor profile session state.

    Args:
        fields_json: A JSON string containing key-value pairs for fields to update.
            Supported keys are: investor_name (str), age (int), monthly_income (float),
            monthly_expenses (float), current_savings (float), monthly_investment_amount (float),
            investment_goal (str), horizon_years (int), risk_tolerance (str),
            liquidity_requirement (str).

    Returns:
        A dict containing updated profile fields, remaining missing fields,
        detected financial/logical inconsistencies, and completeness status.
    """
    try:
        new_data = json.loads(fields_json)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Invalid JSON format in fields_json: {e!s}",
        }

    profile_data = tool_context.state.get("investor_profile_data", {})
    if not isinstance(profile_data, dict):
        profile_data = {}

    for key, val in new_data.items():
        if key in REQUIRED_FIELDS:
            # Type conversions for numeric fields
            if key in ["age", "horizon_years"]:
                try:
                    val = int(val)
                except (ValueError, TypeError):
                    pass
            elif key in [
                "monthly_income",
                "monthly_expenses",
                "current_savings",
                "monthly_investment_amount",
            ]:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    pass
            profile_data[key] = val

    tool_context.state["investor_profile_data"] = profile_data

    collected = {
        k: profile_data[k]
        for k in REQUIRED_FIELDS
        if k in profile_data and profile_data[k] is not None
    }
    missing = [k for k in REQUIRED_FIELDS if k not in collected]
    inconsistencies = check_inconsistencies(profile_data)
    is_complete = len(missing) == 0 and len(inconsistencies) == 0

    return {
        "status": "success",
        "collected_fields": collected,
        "missing_fields": missing,
        "inconsistencies": inconsistencies,
        "is_complete": is_complete,
    }


def get_profile_status(tool_context: ToolContext) -> dict[str, Any]:
    """Retrieves the current investor profile collection status from session state.

    Returns:
        A dict containing collected fields, missing fields, detected inconsistencies,
        and whether all required profile information has been gathered.
    """
    profile_data = tool_context.state.get("investor_profile_data", {})
    if not isinstance(profile_data, dict):
        profile_data = {}

    collected = {
        k: profile_data[k]
        for k in REQUIRED_FIELDS
        if k in profile_data and profile_data[k] is not None
    }
    missing = [k for k in REQUIRED_FIELDS if k not in collected]
    inconsistencies = check_inconsistencies(profile_data)
    is_complete = len(missing) == 0 and len(inconsistencies) == 0

    return {
        "collected_fields": collected,
        "missing_fields": missing,
        "inconsistencies": inconsistencies,
        "is_complete": is_complete,
    }


def finalize_investor_profile(tool_context: ToolContext) -> dict[str, Any]:
    """Finalizes and outputs the structured Investor Profile once all fields are collected and verified.

    Returns:
        A dict containing the complete Investor Profile object and simulation disclaimer,
        or an error if required fields are missing or inconsistencies exist.
    """
    status = get_profile_status(tool_context)
    if not status["is_complete"]:
        return {
            "status": "error",
            "message": "Cannot finalize profile. Information is missing or inconsistencies exist.",
            "missing_fields": status["missing_fields"],
            "inconsistencies": status["inconsistencies"],
        }

    profile_data = status["collected_fields"]
    profile = InvestorProfile(**profile_data)

    # Save finalized profile to state
    tool_context.state["finalized_investor_profile"] = profile.model_dump()
    tool_context.state["profile_status"] = "COMPLETE"

    return {
        "status": "success",
        "profile": profile.model_dump(),
        "disclaimer": profile.simulation_disclaimer,
    }


def calculate_monthly_surplus(
    monthly_income: float | None = None,
    monthly_expenses: float | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates monthly cash flow surplus or deficit for a fictional investor.

    Formula: monthly_surplus = monthly_income - monthly_expenses

    Args:
        monthly_income: Monthly gross income in USD/currency. If None, pulled from session profile.
        monthly_expenses: Monthly living expenses in USD/currency. If None, pulled from session profile.
        tool_context: Optional ADK ToolContext injected automatically.

    Returns:
        A dict containing monthly_income, monthly_expenses, monthly_surplus,
        is_positive flag, cash_flow_status, and an educational summary.
    """
    profile = {}
    if tool_context and hasattr(tool_context, "state"):
        profile = tool_context.state.get("investor_profile_data", {})

    if monthly_income is None:
        monthly_income = profile.get("monthly_income")
    if monthly_expenses is None:
        monthly_expenses = profile.get("monthly_expenses")

    if monthly_income is None or monthly_expenses is None:
        return {
            "status": "error",
            "message": "Both monthly_income and monthly_expenses are required to calculate monthly surplus.",
        }

    try:
        monthly_income = float(monthly_income)
        monthly_expenses = float(monthly_expenses)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": "monthly_income and monthly_expenses must be valid numeric values.",
        }

    if monthly_income < 0 or monthly_expenses < 0:
        return {
            "status": "error",
            "message": "Monthly income and monthly expenses cannot be negative numbers.",
        }

    monthly_surplus = monthly_income - monthly_expenses
    is_positive = monthly_surplus > 0
    if monthly_surplus > 0:
        cash_flow_status = "POSITIVE"
    elif monthly_surplus == 0:
        cash_flow_status = "BREAK_EVEN"
    else:
        cash_flow_status = "NEGATIVE"

    return {
        "status": "success",
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_surplus": monthly_surplus,
        "is_positive": is_positive,
        "cash_flow_status": cash_flow_status,
        "educational_note": (
            f"Monthly cash flow is {cash_flow_status.lower().replace('_', ' ')} with a net "
            f"surplus/deficit of ${monthly_surplus:,.2f}."
        ),
    }


def calculate_emergency_fund(
    monthly_expenses: float | None = None,
    number_of_months: int = 6,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates target emergency fund size based on monthly living expenses and target duration.

    Formula: emergency_fund_target = monthly_expenses * number_of_months

    Args:
        monthly_expenses: Monthly living expenses in USD. If None, pulled from session profile.
        number_of_months: Target duration in months (default: 6). Must be a positive integer.
        tool_context: Optional ADK ToolContext injected automatically.

    Returns:
        A dict containing monthly_expenses, number_of_months, emergency_fund_target,
        and educational guidance.
    """
    profile = {}
    if tool_context and hasattr(tool_context, "state"):
        profile = tool_context.state.get("investor_profile_data", {})

    if monthly_expenses is None:
        monthly_expenses = profile.get("monthly_expenses")

    if monthly_expenses is None:
        return {
            "status": "error",
            "message": "monthly_expenses is required to calculate emergency fund target.",
        }

    try:
        monthly_expenses = float(monthly_expenses)
        number_of_months = int(number_of_months)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": "monthly_expenses must be numeric and number_of_months must be an integer.",
        }

    if monthly_expenses < 0:
        return {
            "status": "error",
            "message": "Monthly expenses cannot be a negative number.",
        }

    if number_of_months <= 0:
        return {
            "status": "error",
            "message": "Number of months for emergency fund target must be greater than zero.",
        }

    emergency_fund_target = monthly_expenses * float(number_of_months)

    return {
        "status": "success",
        "monthly_expenses": monthly_expenses,
        "number_of_months": number_of_months,
        "emergency_fund_target": emergency_fund_target,
        "educational_note": (
            f"An emergency fund target covering {number_of_months} months of living expenses "
            f"(${monthly_expenses:,.2f}/mo) equals ${emergency_fund_target:,.2f}."
        ),
    }


def calculate_annual_investment_capacity(
    monthly_investment: float | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Calculates total annual investment capacity based on monthly investment contributions.

    Formula: annual_investment_capacity = monthly_investment * 12

    Args:
        monthly_investment: Planned monthly investment amount in USD. If None, pulled from session profile.
        tool_context: Optional ADK ToolContext injected automatically.

    Returns:
        A dict containing monthly_investment, annual_investment_capacity, and educational note.
    """
    profile = {}
    if tool_context and hasattr(tool_context, "state"):
        profile = tool_context.state.get("investor_profile_data", {})

    if monthly_investment is None:
        monthly_investment = profile.get("monthly_investment_amount")

    if monthly_investment is None:
        return {
            "status": "error",
            "message": "monthly_investment is required to calculate annual investment capacity.",
        }

    try:
        monthly_investment = float(monthly_investment)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": "monthly_investment must be a valid numeric value.",
        }

    if monthly_investment < 0:
        return {
            "status": "error",
            "message": "Monthly investment amount cannot be a negative number.",
        }

    annual_capacity = monthly_investment * 12.0

    return {
        "status": "success",
        "monthly_investment": monthly_investment,
        "annual_investment_capacity": annual_capacity,
        "educational_note": (
            f"Contributing ${monthly_investment:,.2f} per month yields an annual investment capacity "
            f"of ${annual_capacity:,.2f}."
        ),
    }
