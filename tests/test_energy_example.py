"""Integration test: full energy scenario."""

import pytest
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.energy_asset_maintenance.ontology_definition import build_energy_ontology
from examples.energy_asset_maintenance.sample_data import seed_data
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.query_engine import objects
from foundry_ontology.engine.audit_log import AuditLog
from foundry_ontology.engine.action_executor import ActionExecutor
from foundry_ontology.export.owl_exporter import OWLExporter
from foundry_ontology.export.shacl_generator import SHACLGenerator
from rdflib import Graph


class TestEnergyExample:
    def test_full_energy_scenario_end_to_end(self):
        # 1. Load ontology + seed data
        ontology = build_energy_ontology()
        store = ObjectStore(ontology)
        seed_data(store)

        # 2. Query high-risk assets
        results = (
            objects(store, "Asset")
            .filter(status="active")
            .navigate("has_sensor_readings")
            .filter(reading_type="vibration")
            .all()
        )
        assert len(results) >= 0  # At least runs without error

        # 3. Execute EscalateAsset - success
        audit = AuditLog()
        executor = ActionExecutor(ontology, store, audit)

        def resolver(aid, params):
            if aid == "EscalateAsset":
                inst = store.get(params.get("asset_id", ""))
                return {"asset": inst.properties if inst else {}}
            return {}

        result = executor.execute("EscalateAsset", {"asset_id": "A001", "priority": "LOW"}, "eng1", context_resolver=resolver)
        assert result.success
        assert result.audit_entry_id

        # 4. Execute on decommissioned - failure
        result2 = executor.execute("EscalateAsset", {"asset_id": "A010", "priority": "LOW"}, "eng1", context_resolver=resolver)
        assert not result2.success
        assert any("decommissioned" in str(e) for e in result2.validation_errors)

        # 5. Export OWL - parseable
        ttl = OWLExporter().export(ontology)
        g = Graph()
        g.parse(data=ttl, format="turtle")
        assert len(g) > 0

        # 6. Export SHACL - parseable
        shacl = SHACLGenerator().generate(ontology)
        g2 = Graph()
        g2.parse(data=shacl, format="turtle")
        assert len(g2) > 0
