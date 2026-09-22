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

from pydantic import BaseModel, Field


class InvestorProfile(BaseModel):
    """Structured model representing an educational investor profile."""

    investor_name: str = Field(description="Fictional investor name")
    age: int = Field(description="Investor age in years (18-120)")
    monthly_income: float = Field(description="Monthly income amount in USD")
    monthly_expenses: float = Field(description="Monthly living expenses in USD")
    current_savings: float = Field(
        description="Current liquid savings / emergency fund in USD"
    )
    monthly_investment_amount: float = Field(
        description="Monthly amount available for investment in USD"
    )
    investment_goal: str = Field(
        description="Primary financial or investment goal (e.g. Retirement, Home Purchase, Wealth Growth)"
    )
    horizon_years: int = Field(description="Investment time horizon in years")
    risk_tolerance: str = Field(
        description="Risk tolerance level (e.g. Low, Moderate, High)"
    )
    liquidity_requirement: str = Field(
        description="Liquidity requirement level (e.g. Low, Moderate, High)"
    )
    simulation_disclaimer: str = Field(
        default="EDUCATIONAL SIMULATION ONLY: This profile is generated strictly for educational and fictitious portfolio simulation purposes. It does NOT represent real financial advice, real-money investments, brokerage accounts, or real trading.",
        description="Mandatory simulation disclaimer",
    )


REQUIRED_FIELDS = [
    "investor_name",
    "age",
    "monthly_income",
    "monthly_expenses",
    "current_savings",
    "monthly_investment_amount",
    "investment_goal",
    "horizon_years",
    "risk_tolerance",
    "liquidity_requirement",
]


def check_inconsistencies(data: dict[str, Any]) -> list[str]:
    """Evaluates collected profile data for financial or logical inconsistencies."""
    inconsistencies = []

    age = data.get("age")
    if age is not None:
        try:
            age_val = int(age)
            if age_val < 18 or age_val > 120:
                inconsistencies.append(
                    f"Age ({age_val}) is outside the standard adult range (18-120)."
                )
        except (ValueError, TypeError):
            inconsistencies.append("Age must be a valid integer.")

    monthly_income = data.get("monthly_income")
    monthly_expenses = data.get("monthly_expenses")
    monthly_investment_amount = data.get("monthly_investment_amount")

    if monthly_income is not None and monthly_income < 0:
        inconsistencies.append("Monthly income cannot be negative.")

    if monthly_expenses is not None and monthly_expenses < 0:
        inconsistencies.append("Monthly expenses cannot be negative.")

    if monthly_income is not None and monthly_expenses is not None:
        if monthly_expenses > monthly_income:
            inconsistencies.append(
                f"Monthly expenses (${monthly_expenses:,.2f}) exceed monthly income (${monthly_income:,.2f}), resulting in a monthly deficit of ${monthly_expenses - monthly_income:,.2f}."
            )
        else:
            surplus = monthly_income - monthly_expenses
            if monthly_investment_amount is not None:
                if monthly_investment_amount < 0:
                    inconsistencies.append(
                        "Monthly investment amount cannot be negative."
                    )
                elif monthly_investment_amount > surplus:
                    inconsistencies.append(
                        f"Monthly investment amount (${monthly_investment_amount:,.2f}) exceeds monthly net surplus (${surplus:,.2f} = income ${monthly_income:,.2f} - expenses ${monthly_expenses:,.2f})."
                    )

    current_savings = data.get("current_savings")
    if current_savings is not None and current_savings < 0:
        inconsistencies.append("Current savings cannot be negative.")

    horizon_years = data.get("horizon_years")
    if horizon_years is not None:
        try:
            h_val = int(horizon_years)
            if h_val <= 0:
                inconsistencies.append(
                    f"Investment horizon ({h_val} years) must be a positive integer greater than 0."
                )
            elif h_val > 100:
                inconsistencies.append(
                    f"Investment horizon ({h_val} years) is unusually long (>100 years)."
                )
        except (ValueError, TypeError):
            inconsistencies.append(
                "Investment horizon must be a valid number of years."
            )

    return inconsistencies
