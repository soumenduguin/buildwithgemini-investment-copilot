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
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STORAGE_FILE_PATH = Path(__file__).parent / "data" / "simulations_store.json"
STORAGE_LABEL = (
    "Persistent Simulation Store (Firestore / app/data/simulations_store.json)"
)


def _ensure_storage_dir() -> None:
    STORAGE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORAGE_FILE_PATH.exists():
        with open(STORAGE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({"simulations": {}, "scenarios": {}}, f, indent=2)


class SimulationStorageService:
    """Persistent storage engine for fictional investment simulations and scenarios.

    Supports dual-mode persistence:
    1. Cloud Firestore primary storage if available and provisioned.
    2. Local file-backed JSON store fallback (`app/data/simulations_store.json`).
    """

    def __init__(self, file_path: Path = STORAGE_FILE_PATH):
        self._file_path = file_path
        self._lock = threading.Lock()
        _ensure_storage_dir()
        self._firestore_client = None
        self._init_firestore()

    def _init_firestore(self) -> None:
        """Attempts to initialize Cloud Firestore client."""
        try:
            from google.cloud import firestore

            project = (
                os.environ.get("GOOGLE_CLOUD_PROJECT")
                or os.environ.get("ANTIGRAVITY_PROJECT_ID")
                or "qwiklabs-gcp-02-55287fa59349"
            )
            client = firestore.Client(project=project)
            # Test ping collection access
            _ = client.collection("_ping_check").limit(1).get()
            self._firestore_client = client
        except Exception:
            # Fall back seamlessly to file store if Firestore is unprovisioned/offline
            self._firestore_client = None

    def _load_local_data(self) -> dict[str, Any]:
        with self._lock:
            try:
                with open(self._file_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"simulations": {}, "scenarios": {}}

    def _save_local_data(self, data: dict[str, Any]) -> None:
        with self._lock:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def save_simulation(
        self,
        simulation_data: dict[str, Any],
        simulation_id: str | None = None,
    ) -> dict[str, Any]:
        """Saves a complete fictional investor simulation record.

        Args:
            simulation_data: Structured simulation payload containing investor profile,
              baseline financial metrics, baseline portfolio, and assumptions.
            simulation_id: Optional unique identifier. If not provided, one is generated.

        Returns:
            Dictionary containing save status, simulation_id, and persistence_mode.
        """
        if not simulation_data or not isinstance(simulation_data, dict):
            return {
                "status": "error",
                "message": "Invalid simulation data provided.",
            }

        investor_name = (
            simulation_data.get("fictional_investor_name")
            or simulation_data.get("investor_name")
            or (simulation_data.get("investor_profile") or {}).get("investor_name")
            or "Fictional Investor"
        )

        sid = (
            simulation_id
            or simulation_data.get("simulation_id")
            or f"sim_{investor_name.lower().replace(' ', '_')}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )

        record = {
            "simulation_id": sid,
            "fictional_investor_name": investor_name,
            "created_at": simulation_data.get("created_at")
            or datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "investor_profile": simulation_data.get("investor_profile")
            or simulation_data.get("profile")
            or {},
            "baseline_financial_metrics": simulation_data.get(
                "baseline_financial_metrics"
            )
            or simulation_data.get("financial_metrics")
            or {},
            "baseline_portfolio": simulation_data.get("baseline_portfolio")
            or simulation_data.get("portfolio")
            or {},
            "assumptions": simulation_data.get("assumptions")
            or {
                "disclaimer": "EDUCATIONAL SIMULATION ONLY: Fictional portfolio simulation record."
            },
        }

        mode = "firestore" if self._firestore_client else "local_file_backed"

        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("simulations").document(sid)
                doc_ref.set(record)
            except Exception:
                mode = "local_file_backed"
                self._save_local_simulation(sid, record)
        else:
            self._save_local_simulation(sid, record)

        return {
            "status": "success",
            "simulation_id": sid,
            "fictional_investor_name": investor_name,
            "persistence_mode": mode,
            "simulation_record": record,
        }

    def _save_local_simulation(self, sid: str, record: dict[str, Any]) -> None:
        local_data = self._load_local_data()
        if "simulations" not in local_data:
            local_data["simulations"] = {}
        local_data["simulations"][sid] = record
        self._save_local_data(local_data)

    def load_simulation(self, identifier: str) -> dict[str, Any]:
        """Retrieves a simulation by simulation_id or fictional_investor_name.

        Args:
            identifier: simulation_id (e.g. 'SIM-001') or investor name (e.g. 'Alex').

        Returns:
            Structured simulation record or status 'not_found'.
        """
        clean_id = identifier.strip()
        if not clean_id:
            return {
                "status": "error",
                "message": "Simulation ID or investor name is required.",
            }

        # Check Firestore primary
        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("simulations").document(
                    clean_id
                )
                doc = doc_ref.get()
                if doc.exists:
                    return {
                        "status": "success",
                        "simulation_id": clean_id,
                        "simulation_record": doc.to_dict(),
                        "persistence_mode": "firestore",
                    }
            except Exception:
                pass

        # Check Local File Store fallback
        local_data = self._load_local_data()
        simulations = local_data.get("simulations", {})

        # Direct match by simulation_id
        if clean_id in simulations:
            return {
                "status": "success",
                "simulation_id": clean_id,
                "simulation_record": simulations[clean_id],
                "persistence_mode": "local_file_backed",
            }

        # Case-insensitive match by simulation_id or investor_name
        search_term = clean_id.lower()
        for sid, rec in simulations.items():
            if sid.lower() == search_term or (
                rec.get("fictional_investor_name", "").lower() == search_term
            ):
                return {
                    "status": "success",
                    "simulation_id": sid,
                    "simulation_record": rec,
                    "persistence_mode": "local_file_backed",
                }

        return {
            "status": "not_found",
            "simulation_id": clean_id,
            "message": f"No persistent simulation record found matching '{clean_id}'.",
        }

    def list_simulations(self, investor_name: str | None = None) -> dict[str, Any]:
        """Lists available stored simulations.

        Args:
            investor_name: Optional filter by investor name.

        Returns:
            List of simulation summaries and total count.
        """
        summaries = []

        if self._firestore_client:
            try:
                query = self._firestore_client.collection("simulations")
                if investor_name:
                    query = query.where(
                        "fictional_investor_name", "==", investor_name.strip()
                    )
                docs = query.stream()
                for doc in docs:
                    d = doc.to_dict()
                    summaries.append(
                        {
                            "simulation_id": d.get("simulation_id"),
                            "fictional_investor_name": d.get("fictional_investor_name"),
                            "created_at": d.get("created_at"),
                            "updated_at": d.get("updated_at"),
                        }
                    )
                return {
                    "status": "success",
                    "simulations": summaries,
                    "count": len(summaries),
                    "persistence_mode": "firestore",
                }
            except Exception:
                pass

        # Local File Store fallback
        local_data = self._load_local_data()
        simulations = local_data.get("simulations", {})
        filter_name = investor_name.strip().lower() if investor_name else None

        for sid, rec in simulations.items():
            inv_name = rec.get("fictional_investor_name", "")
            if filter_name and inv_name.lower() != filter_name:
                continue
            summaries.append(
                {
                    "simulation_id": sid,
                    "fictional_investor_name": inv_name,
                    "created_at": rec.get("created_at"),
                    "updated_at": rec.get("updated_at"),
                }
            )

        return {
            "status": "success",
            "simulations": summaries,
            "count": len(summaries),
            "persistence_mode": "local_file_backed",
        }

    def delete_simulation(self, simulation_id: str) -> dict[str, Any]:
        """Deletes a simulation and associated scenarios safely.

        Args:
            simulation_id: Unique simulation ID.

        Returns:
            Deletion confirmation dictionary.
        """
        clean_id = simulation_id.strip()
        if not clean_id:
            return {
                "status": "error",
                "message": "Simulation ID is required for deletion.",
            }

        existed = False
        mode = "local_file_backed"

        if self._firestore_client:
            try:
                doc_ref = self._firestore_client.collection("simulations").document(
                    clean_id
                )
                if doc_ref.get().exists:
                    doc_ref.delete()
                    existed = True
                    mode = "firestore"
            except Exception:
                pass

        local_data = self._load_local_data()
        sims = local_data.get("simulations", {})
        scens = local_data.get("scenarios", {})

        if clean_id in sims:
            existed = True
            del sims[clean_id]
            # Remove associated scenarios
            scen_ids_to_del = [
                scid
                for scid, sc in scens.items()
                if sc.get("simulation_id") == clean_id
            ]
            for scid in scen_ids_to_del:
                del scens[scid]
            self._save_local_data(local_data)

        if not existed:
            return {
                "status": "not_found",
                "simulation_id": clean_id,
                "message": f"Simulation ID '{clean_id}' does not exist.",
            }

        return {
            "status": "success",
            "simulation_id": clean_id,
            "message": f"Simulation '{clean_id}' and its scenarios were successfully deleted.",
            "persistence_mode": mode,
        }

    def save_scenario(
        self,
        scenario_data: dict[str, Any],
        scenario_id: str | None = None,
    ) -> dict[str, Any]:
        """Persists a What-If scenario associated with a simulation.

        Args:
            scenario_data: Scenario dictionary containing simulation_id, scenario_name,
              scenario_type, changed_parameters, baseline_values, scenario_values, scenario_allocation.
            scenario_id: Optional scenario identifier.

        Returns:
            Save confirmation dictionary.
        """
        if not scenario_data or not isinstance(scenario_data, dict):
            return {
                "status": "error",
                "message": "Invalid scenario data provided.",
            }

        simulation_id = scenario_data.get("simulation_id") or "SIM-DEFAULT"
        scenario_name = (
            scenario_data.get("scenario_name")
            or scenario_data.get("name")
            or "What-If Scenario"
        )
        scid = (
            scenario_id
            or scenario_data.get("scenario_id")
            or f"scen_{scenario_name.lower().replace(' ', '_')}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )

        record = {
            "scenario_id": scid,
            "simulation_id": simulation_id,
            "scenario_name": scenario_name,
            "scenario_type": scenario_data.get("scenario_type")
            or "parameter_modification",
            "changed_parameters": scenario_data.get("changed_parameters")
            or scenario_data.get("modifications")
            or {},
            "baseline_values": scenario_data.get("baseline_values") or {},
            "scenario_values": scenario_data.get("scenario_values") or {},
            "scenario_allocation": scenario_data.get("scenario_allocation") or {},
            "allocation_differences": scenario_data.get("allocation_differences")
            or scenario_data.get("changes")
            or {},
            "quantitative_analysis": scenario_data.get("quantitative_analysis") or {},
            "created_at": datetime.now(UTC).isoformat(),
        }

        mode = "firestore" if self._firestore_client else "local_file_backed"

        if self._firestore_client:
            try:
                doc_ref = (
                    self._firestore_client.collection("simulations")
                    .document(simulation_id)
                    .collection("scenarios")
                    .document(scid)
                )
                doc_ref.set(record)
            except Exception:
                mode = "local_file_backed"
                self._save_local_scenario(scid, record)
        else:
            self._save_local_scenario(scid, record)

        return {
            "status": "success",
            "scenario_id": scid,
            "simulation_id": simulation_id,
            "scenario_name": scenario_name,
            "persistence_mode": mode,
            "scenario_record": record,
        }

    def _save_local_scenario(self, scid: str, record: dict[str, Any]) -> None:
        local_data = self._load_local_data()
        if "scenarios" not in local_data:
            local_data["scenarios"] = {}
        local_data["scenarios"][scid] = record
        self._save_local_data(local_data)

    def load_scenario(
        self, scenario_id: str, simulation_id: str | None = None
    ) -> dict[str, Any]:
        """Retrieves a stored scenario by scenario_id.

        Args:
            scenario_id: Unique scenario ID.
            simulation_id: Optional parent simulation ID.

        Returns:
            Scenario record dictionary or status 'not_found'.
        """
        clean_scid = scenario_id.strip()
        if not clean_scid:
            return {
                "status": "error",
                "message": "Scenario ID is required.",
            }

        # Check Firestore primary
        if self._firestore_client and simulation_id:
            try:
                doc_ref = (
                    self._firestore_client.collection("simulations")
                    .document(simulation_id)
                    .collection("scenarios")
                    .document(clean_scid)
                )
                doc = doc_ref.get()
                if doc.exists:
                    return {
                        "status": "success",
                        "scenario_id": clean_scid,
                        "scenario_record": doc.to_dict(),
                        "persistence_mode": "firestore",
                    }
            except Exception:
                pass

        # Check Local File Store fallback
        local_data = self._load_local_data()
        scenarios = local_data.get("scenarios", {})

        if clean_scid in scenarios:
            return {
                "status": "success",
                "scenario_id": clean_scid,
                "scenario_record": scenarios[clean_scid],
                "persistence_mode": "local_file_backed",
            }

        # Search by case-insensitive name or ID
        search_term = clean_scid.lower()
        for scid, rec in scenarios.items():
            if (
                scid.lower() == search_term
                or rec.get("scenario_name", "").lower() == search_term
            ):
                return {
                    "status": "success",
                    "scenario_id": scid,
                    "scenario_record": rec,
                    "persistence_mode": "local_file_backed",
                }

        return {
            "status": "not_found",
            "scenario_id": clean_scid,
            "message": f"No persistent scenario record found matching '{clean_scid}'.",
        }

    def list_scenarios(self, simulation_id: str | None = None) -> dict[str, Any]:
        """Lists scenarios associated with a simulation ID or all saved scenarios.

        Args:
            simulation_id: Optional simulation ID filter.

        Returns:
            List of scenario summaries and total count.
        """
        summaries = []

        if self._firestore_client and simulation_id:
            try:
                docs = (
                    self._firestore_client.collection("simulations")
                    .document(simulation_id)
                    .collection("scenarios")
                    .stream()
                )
                for doc in docs:
                    d = doc.to_dict()
                    summaries.append(
                        {
                            "scenario_id": d.get("scenario_id"),
                            "simulation_id": d.get("simulation_id"),
                            "scenario_name": d.get("scenario_name"),
                            "scenario_type": d.get("scenario_type"),
                            "created_at": d.get("created_at"),
                        }
                    )
                return {
                    "status": "success",
                    "simulation_id": simulation_id,
                    "scenarios": summaries,
                    "count": len(summaries),
                    "persistence_mode": "firestore",
                }
            except Exception:
                pass

        # Local File Store fallback
        local_data = self._load_local_data()
        scenarios = local_data.get("scenarios", {})
        filter_sim_id = simulation_id.strip() if simulation_id else None

        for scid, rec in scenarios.items():
            parent_sim = rec.get("simulation_id")
            if filter_sim_id and parent_sim != filter_sim_id:
                # Also allow matching by investor name or substring
                if not (parent_sim and filter_sim_id.lower() in parent_sim.lower()):
                    continue
            summaries.append(
                {
                    "scenario_id": scid,
                    "simulation_id": parent_sim,
                    "scenario_name": rec.get("scenario_name"),
                    "scenario_type": rec.get("scenario_type"),
                    "created_at": rec.get("created_at"),
                }
            )

        return {
            "status": "success",
            "simulation_id": simulation_id,
            "scenarios": summaries,
            "count": len(summaries),
            "persistence_mode": "local_file_backed",
        }


# Global storage service instance
storage_service = SimulationStorageService()
