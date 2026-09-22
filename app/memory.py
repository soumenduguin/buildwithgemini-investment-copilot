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
import threading
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from google.adk.events import Event
from google.adk.memory.base_memory_service import (
    BaseMemoryService,
    SearchMemoryResponse,
)
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.sessions import Session

MEMORY_FILE_PATH = Path(__file__).parent / "data" / "investor_memory.json"
MEMORY_DATASET_LABEL = "Investor Memory Store (app/data/investor_memory.json)"

STABLE_FACT_KEYS = {
    "investor_name",
    "investment_goal",
    "risk_tolerance",
    "horizon_years",
    "liquidity_requirement",
    "liquidity_preference",
    "simulation_preferences",
}


def _ensure_memory_file() -> None:
    """Ensures parent directory and investor_memory.json file exist."""
    MEMORY_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE_PATH.exists():
        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)


class FileBackedMemoryService(BaseMemoryService):
    """File-backed Google ADK Memory Service implementation.

    Persists stable investor contextual facts as JSON to enable cross-session
    memory retrieval across local server and process restarts.
    """

    def __init__(self, file_path: Path = MEMORY_FILE_PATH):
        self._file_path = file_path
        self._lock = threading.Lock()
        _ensure_memory_file()

    def _load_data(self) -> dict[str, Any]:
        with self._lock:
            try:
                with open(self._file_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

    def _save_data(self, data: dict[str, Any]) -> None:
        with self._lock:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    async def add_session_to_memory(self, session: Session) -> None:
        """Ingests full session events into memory."""
        data = self._load_data()
        user_key = f"{session.app_name}/{session.user_id}"
        if user_key not in data:
            data[user_key] = {}

        event_list = []
        for event in session.events:
            if event.content and event.content.parts:
                text = " ".join([p.text for p in event.content.parts if p.text])
                if text:
                    ts = getattr(event.timestamp, "isoformat", None)
                    ts_str = ts() if callable(ts) else str(event.timestamp)
                    event_list.append(
                        {
                            "author": event.author,
                            "timestamp": ts_str,
                            "text": text,
                        }
                    )
        data[user_key][session.id] = event_list
        self._save_data(data)

    async def add_events_to_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        events: Sequence[Event],
        session_id: str | None = None,
        custom_metadata: Mapping[str, object] | None = None,
    ) -> None:
        """Adds explicit event deltas to memory."""
        data = self._load_data()
        user_key = f"{app_name}/{user_id}"
        sid = session_id or "default_session"
        if user_key not in data:
            data[user_key] = {}
        if sid not in data[user_key]:
            data[user_key][sid] = []

        for event in events:
            if event.content and event.content.parts:
                text = " ".join([p.text for p in event.content.parts if p.text])
                if text:
                    data[user_key][sid].append(
                        {
                            "author": event.author,
                            "timestamp": str(event.timestamp),
                            "text": text,
                        }
                    )
        self._save_data(data)

    async def add_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        memories: Sequence[MemoryEntry],
        custom_metadata: Mapping[str, object] | None = None,
    ) -> None:
        """Adds explicit memory entries directly to file store."""
        data = self._load_data()
        user_key = f"{app_name}/{user_id}"
        if user_key not in data:
            data[user_key] = {}
        if "explicit_memories" not in data[user_key]:
            data[user_key]["explicit_memories"] = []

        for mem in memories:
            text = ""
            if mem.content and mem.content.parts:
                text = " ".join([p.text for p in mem.content.parts if p.text])
            data[user_key]["explicit_memories"].append(
                {
                    "author": mem.author,
                    "timestamp": mem.timestamp or datetime.now(UTC).isoformat(),
                    "text": text,
                }
            )
        self._save_data(data)

    async def search_memory(
        self, *, app_name: str, user_id: str, query: str
    ) -> SearchMemoryResponse:
        """Searches remembered investor entries matching query keywords."""
        data = self._load_data()
        user_key = f"{app_name}/{user_id}"
        user_data = data.get(user_key, {})

        words = [w.lower() for w in query.split() if len(w) > 2]
        response = SearchMemoryResponse()

        # Search across session lists and explicit memories
        for _section, items in user_data.items():
            if isinstance(items, list):
                for item in items:
                    text = item.get("text", "")
                    if any(w in text.lower() for w in words) or not words:
                        from google.genai import types as genai_types

                        content = genai_types.Content(
                            parts=[genai_types.Part.from_text(text=text)],
                            role=item.get("author", "user"),
                        )
                        response.memories.append(
                            MemoryEntry(
                                content=content,
                                author=item.get("author", "user"),
                                timestamp=item.get("timestamp"),
                            )
                        )
            elif isinstance(items, dict):
                for event in items.values():
                    if isinstance(event, list):
                        for ev in event:
                            text = ev.get("text", "")
                            if any(w in text.lower() for w in words) or not words:
                                from google.genai import types as genai_types

                                content = genai_types.Content(
                                    parts=[genai_types.Part.from_text(text=text)],
                                    role=ev.get("author", "user"),
                                )
                                response.memories.append(
                                    MemoryEntry(
                                        content=content,
                                        author=ev.get("author", "user"),
                                        timestamp=ev.get("timestamp"),
                                    )
                                )

        return response


# Global memory service instance
memory_service = FileBackedMemoryService()


def save_investor_facts(investor_name: str, facts: dict[str, Any]) -> dict[str, Any]:
    """Stores stable investor contextual facts into persistent memory store.

    Args:
        investor_name: Name of fictional investor.
        facts: Dictionary containing stable facts (goal, risk, horizon, liquidity, preferences).

    Returns:
        Confirmation dictionary with saved memory status.
    """
    _ensure_memory_file()
    clean_name = investor_name.strip()
    if not clean_name:
        return {"status": "error", "message": "Investor name is required."}

    # Filter facts to retain strictly stable contextual parameters
    stable_facts = {}
    for k, v in facts.items():
        if k in STABLE_FACT_KEYS and v is not None:
            stable_facts[k] = v

    if not stable_facts:
        return {
            "status": "error",
            "message": "No stable contextual facts provided to remember.",
        }

    with open(MEMORY_FILE_PATH, encoding="utf-8") as f:
        try:
            store = json.load(f)
        except Exception:
            store = {}

    key = clean_name.lower()
    if key not in store:
        store[key] = {
            "investor_name": clean_name,
            "created_at": datetime.now(UTC).isoformat(),
            "facts": {},
        }

    store[key]["updated_at"] = datetime.now(UTC).isoformat()
    store[key]["facts"].update(stable_facts)

    with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)

    return {
        "status": "success",
        "investor_name": clean_name,
        "saved_facts": store[key]["facts"],
        "dataset": MEMORY_DATASET_LABEL,
    }


def get_investor_memory(investor_name: str, query: str | None = None) -> dict[str, Any]:
    """Retrieves remembered stable facts for a given investor.

    Args:
        investor_name: Name of fictional investor.
        query: Optional specific property/topic to query.

    Returns:
        Structured result containing remembered facts or status "not_found".
    """
    _ensure_memory_file()
    clean_name = investor_name.strip().lower()

    with open(MEMORY_FILE_PATH, encoding="utf-8") as f:
        try:
            store = json.load(f)
        except Exception:
            store = {}

    entry = store.get(clean_name)
    if not entry:
        return {
            "status": "not_found",
            "investor_name": investor_name,
            "message": f"No relevant cross-session memory found for investor '{investor_name}'.",
            "dataset": MEMORY_DATASET_LABEL,
        }

    facts = entry.get("facts", {})
    if query:
        clean_q = query.strip().lower()
        matched_facts = {
            k: v
            for k, v in facts.items()
            if clean_q in k.lower() or clean_q in str(v).lower()
        }
        if matched_facts:
            return {
                "status": "success",
                "investor_name": entry["investor_name"],
                "remembered_facts": matched_facts,
                "dataset": MEMORY_DATASET_LABEL,
            }

    return {
        "status": "success",
        "investor_name": entry["investor_name"],
        "remembered_facts": facts,
        "dataset": MEMORY_DATASET_LABEL,
    }


def extract_stable_facts_from_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Extracts strictly stable contextual facts from an investor profile dictionary.

    Ignores financial amounts, portfolio weights, scenarios, and calculations.
    """
    extracted = {}
    if "investor_name" in profile:
        extracted["investor_name"] = profile["investor_name"]
    if "investment_goal" in profile:
        extracted["investment_goal"] = profile["investment_goal"]
    if "risk_tolerance" in profile:
        extracted["risk_tolerance"] = profile["risk_tolerance"]
    if "horizon_years" in profile:
        extracted["horizon_years"] = profile["horizon_years"]
    if "liquidity_requirement" in profile:
        extracted["liquidity_preference"] = profile["liquidity_requirement"]
    return extracted
