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

from unittest.mock import MagicMock

from app.tools import (
    calculate_annual_investment_capacity,
    calculate_emergency_fund,
    calculate_monthly_surplus,
)


def test_calculate_monthly_surplus_positive():
    res = calculate_monthly_surplus(monthly_income=10000.0, monthly_expenses=6000.0)
    assert res["status"] == "success"
    assert res["monthly_income"] == 10000.0
    assert res["monthly_expenses"] == 6000.0
    assert res["monthly_surplus"] == 4000.0
    assert res["is_positive"] is True
    assert res["cash_flow_status"] == "POSITIVE"


def test_calculate_monthly_surplus_negative():
    res = calculate_monthly_surplus(monthly_income=5000.0, monthly_expenses=7000.0)
    assert res["status"] == "success"
    assert res["monthly_surplus"] == -2000.0
    assert res["is_positive"] is False
    assert res["cash_flow_status"] == "NEGATIVE"


def test_calculate_monthly_surplus_break_even():
    res = calculate_monthly_surplus(monthly_income=5000.0, monthly_expenses=5000.0)
    assert res["status"] == "success"
    assert res["monthly_surplus"] == 0.0
    assert res["is_positive"] is False
    assert res["cash_flow_status"] == "BREAK_EVEN"


def test_calculate_monthly_surplus_invalid_inputs():
    res_neg = calculate_monthly_surplus(monthly_income=-5000.0, monthly_expenses=4000.0)
    assert res_neg["status"] == "error"
    assert "cannot be negative" in res_neg["message"]

    res_invalid = calculate_monthly_surplus(
        monthly_income="abc", monthly_expenses=4000.0
    )
    assert res_invalid["status"] == "error"


def test_calculate_emergency_fund_default():
    res = calculate_emergency_fund(monthly_expenses=5000.0)
    assert res["status"] == "success"
    assert res["monthly_expenses"] == 5000.0
    assert res["number_of_months"] == 6
    assert res["emergency_fund_target"] == 30000.0


def test_calculate_emergency_fund_custom_months():
    res = calculate_emergency_fund(monthly_expenses=4000.0, number_of_months=3)
    assert res["status"] == "success"
    assert res["monthly_expenses"] == 4000.0
    assert res["number_of_months"] == 3
    assert (
        res["emergency_fund_target"] == 120000.0
        or res["emergency_fund_target"] == 12000.0
    )


def test_calculate_emergency_fund_invalid_inputs():
    res_zero = calculate_emergency_fund(monthly_expenses=5000.0, number_of_months=0)
    assert res_zero["status"] == "error"
    assert "greater than zero" in res_zero["message"]

    res_neg_exp = calculate_emergency_fund(monthly_expenses=-1000.0, number_of_months=6)
    assert res_neg_exp["status"] == "error"


def test_calculate_annual_investment_capacity_valid():
    res = calculate_annual_investment_capacity(monthly_investment=2500.0)
    assert res["status"] == "success"
    assert res["monthly_investment"] == 2500.0
    assert res["annual_investment_capacity"] == 30000.0


def test_calculate_annual_investment_capacity_zero():
    res = calculate_annual_investment_capacity(monthly_investment=0.0)
    assert res["status"] == "success"
    assert res["monthly_investment"] == 0.0
    assert res["annual_investment_capacity"] == 0.0


def test_calculate_annual_investment_capacity_invalid():
    res = calculate_annual_investment_capacity(monthly_investment=-500.0)
    assert res["status"] == "error"
    assert "cannot be a negative number" in res["message"]


def test_financial_tools_from_session_state():
    mock_context = MagicMock()
    mock_context.state = {
        "investor_profile_data": {
            "monthly_income": 12000.0,
            "monthly_expenses": 7000.0,
            "monthly_investment_amount": 3000.0,
        }
    }

    surplus_res = calculate_monthly_surplus(tool_context=mock_context)
    assert surplus_res["status"] == "success"
    assert surplus_res["monthly_surplus"] == 5000.0

    emergency_res = calculate_emergency_fund(tool_context=mock_context)
    assert emergency_res["status"] == "success"
    assert emergency_res["emergency_fund_target"] == 42000.0

    capacity_res = calculate_annual_investment_capacity(tool_context=mock_context)
    assert capacity_res["status"] == "success"
    assert capacity_res["annual_investment_capacity"] == 36000.0
