"""Tests for object_store module."""

import tempfile
from pathlib import Path

import pytest
from foundry_ontology.core import ObjectType, Property, Ontology
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.link_type import Cardinality, LinkType
from foundry_ontology.engine.object_store import ObjectStore, ObjectInstance


@pytest.fixture
def sample_ontology():
    o = Ontology(ontology_id="test", display_name="Test", version="1.0")
    o.register_object_type(
        ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "ID", PropertyType.STRING, required=True, is_primary_key=True),
                "name": Property("name", "Name", PropertyType.STRING),
                "status": Property("status", "Status", PropertyType.STRING, options=["active", "inactive"]),
            },
        )
    )
    o.register_object_type(
        ObjectType(
            type_id="SensorReading",
            display_name="Sensor",
            primary_key="reading_id",
            properties={
                "reading_id": Property("reading_id", "ID", PropertyType.STRING, required=True),
                "value": Property("value", "Value", PropertyType.FLOAT),
            },
        )
    )
    o.register_link_type(
        LinkType("has_readings", "Has Readings", source_type="Asset", target_type="SensorReading", cardinality=Cardinality.ONE_TO_MANY)
    )
    return o


class TestObjectStore:
    def test_create_object_instance(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        inst = store.create("Asset", {"asset_id": "A1", "name": "Pump 1"}, created_by="user1")
        assert inst.instance_id == "A1"
        assert inst.object_type_id == "Asset"
        assert inst.properties["name"] == "Pump 1"

    def test_get_instance_by_id(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "Pump 1"})
        inst = store.get("A1")
        assert inst is not None
        assert inst.instance_id == "A1"

    def test_update_instance_increments_version(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "Pump 1"})
        updated = store.update("A1", {"name": "Pump 1 Updated"}, updated_by="user2")
        assert updated is not None
        assert updated.version == 2
        assert updated.properties["name"] == "Pump 1 Updated"

    def test_delete_instance(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "Pump 1"})
        assert store.get("A1") is not None
        store.delete("A1")
        assert store.get("A1") is None

    def test_search_with_filter(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "P1", "status": "active"})
        store.create("Asset", {"asset_id": "A2", "name": "P2", "status": "inactive"})
        results = store.search("Asset", {"status": "active"})
        assert len(results) == 1
        assert results[0].instance_id == "A1"

    def test_create_link_between_instances(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "P1"})
        store.create("SensorReading", {"reading_id": "R1", "value": 5.0})
        ok = store.create_link("has_readings", "A1", "R1")
        assert ok
        linked = store.get_linked("A1", "has_readings")
        assert len(linked) == 1
        assert linked[0].instance_id == "R1"

    def test_get_linked_objects(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "P1"})
        store.create("SensorReading", {"reading_id": "R1", "value": 1.0})
        store.create("SensorReading", {"reading_id": "R2", "value": 2.0})
        store.create_link("has_readings", "A1", "R1")
        store.create_link("has_readings", "A1", "R2")
        linked = store.get_linked("A1", "has_readings")
        assert len(linked) == 2

    def test_count_with_filter(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "P1", "status": "active"})
        store.create("Asset", {"asset_id": "A2", "name": "P2", "status": "active"})
        store.create("Asset", {"asset_id": "A3", "name": "P3", "status": "inactive"})
        assert store.count("Asset") == 3
        assert store.count("Asset", {"status": "active"}) == 2

    def test_create_instance_validates_against_type(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        with pytest.raises(ValueError, match="Validation"):
            store.create("Asset", {"name": "P1"})  # missing asset_id
        with pytest.raises(ValueError, match="Unknown"):
            store.create("UnknownType", {"id": "x"})
