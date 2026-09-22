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

from app.schema import InvestorProfile, check_inconsistencies


def test_valid_profile_inconsistencies():
    data = {
        "investor_name": "Taylor",
        "age": 35,
        "monthly_income": 8000.0,
        "monthly_expenses": 4000.0,
        "current_savings": 20000.0,
        "monthly_investment_amount": 2000.0,
        "investment_goal": "Retirement",
        "horizon_years": 20,
        "risk_tolerance": "Moderate",
        "liquidity_requirement": "Low",
    }
    inconsistencies = check_inconsistencies(data)
    assert len(inconsistencies) == 0


def test_expenses_exceed_income():
    data = {
        "monthly_income": 5000.0,
        "monthly_expenses": 6000.0,
    }
    inconsistencies = check_inconsistencies(data)
    assert any(
        "Monthly expenses ($6,000.00) exceed monthly income ($5,000.00)" in inc
        for inc in inconsistencies
    )


def test_investment_exceeds_surplus():
    data = {
        "monthly_income": 10000.0,
        "monthly_expenses": 7000.0,
        "monthly_investment_amount": 4000.0,
    }
    inconsistencies = check_inconsistencies(data)
    assert any(
        "Monthly investment amount ($4,000.00) exceeds monthly net surplus ($3,000.00"
        in inc
        for inc in inconsistencies
    )


def test_invalid_age_and_horizon():
    data = {
        "age": 15,
        "horizon_years": 0,
    }
    inconsistencies = check_inconsistencies(data)
    assert len(inconsistencies) == 2


def test_investor_profile_creation():
    profile = InvestorProfile(
        investor_name="Jordan",
        age=30,
        monthly_income=10000.0,
        monthly_expenses=7000.0,
        current_savings=5000.0,
        monthly_investment_amount=1500.0,
        investment_goal="Retirement",
        horizon_years=25,
        risk_tolerance="Moderate",
        liquidity_requirement="Low",
    )
    assert profile.investor_name == "Jordan"
    assert "EDUCATIONAL SIMULATION ONLY" in profile.simulation_disclaimer
