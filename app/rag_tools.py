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

from app.knowledge import search_knowledge_base


def search_investment_knowledge(query: str) -> dict[str, Any]:
    """Retrieves synthetic educational investment simulation rules, assumptions, asset roles, risk profile definitions, liquidity guidelines, and scenario mechanics from the reference knowledge base.

    SYNTHETIC EDUCATIONAL INVESTMENT SIMULATION KNOWLEDGE ONLY: Use when explaining simulator rules, asset class roles, risk profiles, liquidity shifts, portfolio assumptions, or scenario behavior.

    Args:
        query: Search question or topic (e.g. 'What role does gold play in this simulation?', 'Why did portfolio become defensive?', 'What rules govern high liquidity?', 'What assumptions were used to create portfolio?').

    Returns:
        Structured search results with source document names, section titles, matching passages, and non-advisory labels.
    """
    return search_knowledge_base(query)
