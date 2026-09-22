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

import re
from pathlib import Path
from typing import Any

KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"

EDUCATIONAL_KNOWLEDGE_LABEL = "Synthetic Educational Investment Simulation Knowledge"
NON_ADVISORY_DISCLAIMER = (
    "EDUCATIONAL SIMULATION KNOWLEDGE ONLY: The retrieved information describes rules, "
    "assumptions, and definitions for an educational portfolio simulator. It does NOT "
    "constitute real-world financial advice, asset recommendations, or investment advice."
)


def load_knowledge_sections() -> list[dict[str, Any]]:
    """Loads all markdown files in app/knowledge_base and splits them into sections."""
    sections = []
    if not KNOWLEDGE_BASE_DIR.exists():
        return sections

    for md_file in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        doc_name = md_file.name

        # Split file content into sections by markdown headers (## or ###)
        raw_chunks = re.split(r"\n(?=#{1,3}\s)", text)
        for chunk in raw_chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            # Extract title from first header line if present
            lines = chunk.split("\n")
            title = lines[0].lstrip("#").strip() if lines else doc_name

            sections.append(
                {
                    "source_document": doc_name,
                    "section_title": title,
                    "content": chunk,
                    "tokens": set(re.findall(r"\w+", chunk.lower())),
                }
            )

    return sections


def _score_section(query_tokens: set[str], section: dict[str, Any]) -> float:
    """Calculates keyword/heading relevance score for a section."""
    if not query_tokens:
        return 0.0

    content_tokens = section["tokens"]
    title_tokens = set(re.findall(r"\w+", section["section_title"].lower()))
    doc_tokens = set(
        re.findall(r"\w+", section["source_document"].lower().replace(".md", ""))
    )

    # Calculate token overlaps
    body_matches = query_tokens.intersection(content_tokens)
    title_matches = query_tokens.intersection(title_tokens)
    doc_matches = query_tokens.intersection(doc_tokens)

    score = len(body_matches) * 1.0 + len(title_matches) * 2.5 + len(doc_matches) * 3.0

    # Normalize by query size
    normalized = score / max(1.0, float(len(query_tokens)))
    return round(normalized, 3)


def search_knowledge_base(
    query: str, top_k: int = 3, min_score: float = 0.25
) -> dict[str, Any]:
    """Retrieves relevant passages from the synthetic educational knowledge base.

    Args:
        query: User question or search query string.
        top_k: Maximum number of matching passages to return.
        min_score: Minimum relevance threshold to filter noise.

    Returns:
        Structured result containing matched passages, source documents, and non-advisory labels.
    """
    clean_query = query.strip()
    if not clean_query:
        return {
            "status": "error",
            "message": "Query string cannot be empty.",
            "educational_label": EDUCATIONAL_KNOWLEDGE_LABEL,
        }

    query_tokens = set(re.findall(r"\w+", clean_query.lower()))

    # Ignore generic stop words for better precision
    stop_words = {
        "a",
        "an",
        "the",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "what",
        "why",
        "how",
        "this",
        "that",
        "my",
        "your",
        "tell",
        "me",
        "give",
        "rule",
        "does",
    }
    filtered_query_tokens = query_tokens - stop_words
    search_tokens = filtered_query_tokens if filtered_query_tokens else query_tokens

    all_sections = load_knowledge_sections()
    scored = []
    for sec in all_sections:
        score = _score_section(search_tokens, sec)
        if score >= min_score:
            scored.append((score, sec))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return {
            "status": "success",
            "query": clean_query,
            "matches_found": 0,
            "matches": [],
            "message": (
                f"No relevant rules or definitions found in the current synthetic simulation "
                f"knowledge base for query: '{clean_query}'."
            ),
            "educational_label": EDUCATIONAL_KNOWLEDGE_LABEL,
            "disclaimer": NON_ADVISORY_DISCLAIMER,
        }

    top_matches = []
    for score, sec in scored[:top_k]:
        top_matches.append(
            {
                "source_document": sec["source_document"],
                "section_title": sec["section_title"],
                "relevant_content": sec["content"],
                "relevance_score": score,
            }
        )

    return {
        "status": "success",
        "query": clean_query,
        "matches_found": len(top_matches),
        "matches": top_matches,
        "educational_label": EDUCATIONAL_KNOWLEDGE_LABEL,
        "disclaimer": NON_ADVISORY_DISCLAIMER,
    }
