"""Shared pytest fixtures for foundry-ontology-open tests."""

import pytest

from foundry_ontology.core import ObjectType, Property, Ontology
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.link_type import Cardinality, LinkType
from foundry_ontology.core.action_type import ActionParameter, ActionType, ValidationRule
from foundry_ontology.engine.object_store import ObjectStore


@pytest.fixture
def sample_ontology():
    """Pre-built ontology with 3 object types, 2 links, 2 actions."""
    o = Ontology(ontology_id="test_ontology", display_name="Test Ontology", version="1.0")
    o.register_object_type(
        ObjectType(
            type_id="Asset",
            display_name="Physical Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "Asset ID", PropertyType.STRING, required=True, is_primary_key=True),
                "name": Property("name", "Name", PropertyType.STRING, required=True),
                "status": Property("status", "Status", PropertyType.STRING, options=["active", "inactive", "decommissioned"]),
            },
        )
    )
    o.register_object_type(
        ObjectType(
            type_id="SensorReading",
            display_name="Sensor Reading",
            primary_key="reading_id",
            properties={
                "reading_id": Property("reading_id", "Reading ID", PropertyType.STRING, required=True, is_primary_key=True),
                "value": Property("value", "Value", PropertyType.FLOAT),
            },
        )
    )
    o.register_object_type(
        ObjectType(
            type_id="Technician",
            display_name="Technician",
            primary_key="tech_id",
            properties={
                "tech_id": Property("tech_id", "Technician ID", PropertyType.STRING, required=True, is_primary_key=True),
                "name": Property("name", "Name", PropertyType.STRING),
            },
        )
    )
    o.register_link_type(
        LinkType("has_sensor_readings", "Has Sensor Readings", source_type="Asset", target_type="SensorReading", cardinality=Cardinality.ONE_TO_MANY)
    )
    o.register_link_type(
        LinkType("assigned_technician", "Assigned Technician", source_type="Asset", target_type="Technician", cardinality=Cardinality.ONE_TO_ONE)
    )
    o.register_action_type(
        ActionType(
            action_id="EscalateAsset",
            display_name="Escalate Asset",
            parameters=[
                ActionParameter("asset_id", PropertyType.STRING),
                ActionParameter("priority", PropertyType.STRING, options=["LOW", "MEDIUM", "CRITICAL"]),
            ],
            validation_rules=[
                ValidationRule("r1", "asset.get('status') != 'decommissioned'", "Cannot escalate decommissioned asset"),
            ],
            effects=[],
            required_roles=["Engineer"],
        )
    )
    o.register_action_type(
        ActionType(
            action_id="CreateWorkOrder",
            display_name="Create Work Order",
            parameters=[
                ActionParameter("asset_id", PropertyType.STRING),
                ActionParameter("tech_id", PropertyType.STRING),
            ],
            validation_rules=[],
            effects=[],
            required_roles=["Engineer", "Admin"],
        )
    )
    return o


@pytest.fixture
def sample_store(sample_ontology):
    """ObjectStore with sample instances."""
    store = ObjectStore(sample_ontology)
    for i in range(1, 6):
        store.create("Asset", {"asset_id": f"A{i}", "name": f"Asset {i}", "status": "active"}, "system")
    for i in range(1, 4):
        store.create("Technician", {"tech_id": f"T{i}", "name": f"Tech {i}"}, "system")
    return store


@pytest.fixture
def sample_user_admin():
    """User with admin role."""
    from foundry_ontology.governance.roles import User
    return User(user_id="admin_1", display_name="Admin", roles=["Admin", "Engineer"], markings=["PUBLIC", "INTERNAL"])


@pytest.fixture
def sample_user_operator():
    """User with limited operator role."""
    from foundry_ontology.governance.roles import User
    return User(user_id="op_1", display_name="Operator", roles=["Engineer"], markings=["PUBLIC"])
