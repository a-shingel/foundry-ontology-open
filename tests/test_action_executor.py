"""Tests for action_executor module."""

import pytest
from foundry_ontology.core import (
    ActionType,
    ActionParameter,
    ActionEffect,
    ValidationRule,
    ObjectType,
    Property,
    Ontology,
)
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.engine.audit_log import AuditLog
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.action_executor import ActionExecutor


@pytest.fixture
def ontology_with_action():
    o = Ontology(ontology_id="test", display_name="Test", version="1.0")
    o.register_object_type(
        ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "ID", PropertyType.STRING, required=True),
                "status": Property("status", "Status", PropertyType.STRING),
            },
        )
    )
    o.register_action_type(
        ActionType(
            action_id="EscalateAsset",
            parameters=[
                ActionParameter("asset_id", PropertyType.STRING),
                ActionParameter("priority", PropertyType.STRING, options=["LOW", "CRITICAL"]),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="r1",
                    expression="asset.get('status') != 'decommissioned'",
                    message="Cannot escalate decommissioned asset",
                ),
            ],
            effects=[
                ActionEffect("edit_object", "Asset", {"status": "escalated"}),
            ],
            required_roles=["Engineer"],
        )
    )
    return o


@pytest.fixture
def executor_setup(ontology_with_action):
    store = ObjectStore(ontology_with_action)
    store.create("Asset", {"asset_id": "A1", "status": "active"})
    store.create("Asset", {"asset_id": "A2", "status": "decommissioned"})
    audit = AuditLog()
    executor = ActionExecutor(ontology_with_action, store, audit)
    return executor, store, audit


class TestActionExecutor:
    def test_execute_action_success(self, executor_setup):
        executor, store, audit = executor_setup

        def resolver(action_id, params):
            if action_id == "EscalateAsset":
                inst = store.get(params["asset_id"])
                return {"asset": inst.properties if inst else {}}
            return {}

        result = executor.execute(
            "EscalateAsset",
            {"asset_id": "A1", "priority": "LOW"},
            executed_by="engineer1",
            context_resolver=resolver,
        )
        assert result.success
        assert result.audit_entry_id
        inst = store.get("A1")
        assert inst.properties["status"] == "escalated"

    def test_execute_action_validation_failure(self, executor_setup):
        executor, store, audit = executor_setup

        def resolver(action_id, params):
            inst = store.get(params["asset_id"])
            return {"asset": inst.properties if inst else {}}

        result = executor.execute(
            "EscalateAsset",
            {"asset_id": "A2", "priority": "LOW"},
            executed_by="engineer1",
            context_resolver=resolver,
        )
        assert not result.success
        assert any("decommissioned" in e for e in result.validation_errors)

    def test_execute_action_creates_audit_entry(self, executor_setup):
        executor, store, audit = executor_setup

        def resolver(action_id, params):
            inst = store.get(params["asset_id"])
            return {"asset": inst.properties if inst else {}}

        result = executor.execute(
            "EscalateAsset",
            {"asset_id": "A1", "priority": "LOW"},
            executed_by="u1",
            context_resolver=resolver,
        )
        assert result.success
        entry = audit.get(result.audit_entry_id)
        assert entry is not None
        assert entry.executed_by == "u1"
        assert entry.success is True

    def test_execute_action_role_denied(self, executor_setup):
        executor, store, audit = executor_setup

        def resolver(action_id, params):
            inst = store.get(params["asset_id"])
            return {"asset": inst.properties if inst else {}}

        result = executor.execute(
            "EscalateAsset",
            {"asset_id": "A1", "priority": "LOW"},
            executed_by="viewer1",
            context_resolver=resolver,
            executed_by_roles=["Viewer"],  # Action requires Engineer
        )
        assert not result.success
        assert "Insufficient role" in str(result.validation_errors) or "role" in str(result.validation_errors).lower()

    def test_execute_action_with_create_link_effect(self, ontology_with_action):
        """Test action with create_link effect."""
        from foundry_ontology.core import LinkType
        from foundry_ontology.core.link_type import Cardinality

        ontology_with_action.register_object_type(
            ObjectType("Technician", "Tech", primary_key="tech_id", properties={"tech_id": Property("tech_id", "ID", PropertyType.STRING)})
        )
        ontology_with_action.register_link_type(
            LinkType("assigned", "Assigned", source_type="Asset", target_type="Technician", cardinality=Cardinality.ONE_TO_ONE)
        )
        at = ontology_with_action.action_types["EscalateAsset"]
        at.effects = [
            ActionEffect("create_link", "assigned", {"source_id": "A1", "target_id": "T1"}),
        ]
        store = ObjectStore(ontology_with_action)
        store.create("Asset", {"asset_id": "A1", "status": "active"})
        store.create("Technician", {"tech_id": "T1"})
        audit = AuditLog()
        executor = ActionExecutor(ontology_with_action, store, audit)
        at.validation_rules = []  # skip validation for this test
        result = executor.execute("EscalateAsset", {"asset_id": "A1", "priority": "LOW"}, "eng1", executed_by_roles=["Engineer"])
        assert result.success
        linked = store.get_linked("A1", "assigned")
        assert len(linked) == 1
        assert linked[0].instance_id == "T1"

    def test_execute_action_with_notification_effect(self, ontology_with_action):
        ontology_with_action.action_types["EscalateAsset"].effects = [
            ActionEffect("notification", "system", {"message": "Asset A1 escalated"}),
        ]
        store = ObjectStore(ontology_with_action)
        store.create("Asset", {"asset_id": "A1", "status": "active"})
        audit = AuditLog()
        executor = ActionExecutor(ontology_with_action, store, audit)

        def resolver(aid, params):
            return {"asset": store.get(params["asset_id"]).properties if store.get(params["asset_id"]) else {}}

        result = executor.execute("EscalateAsset", {"asset_id": "A1", "priority": "LOW"}, "eng1", context_resolver=resolver, executed_by_roles=["Engineer"])
        assert result.success
        assert len(result.effects_applied) >= 1
