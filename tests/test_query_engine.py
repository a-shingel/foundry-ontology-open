"""Tests for query_engine module."""

import pytest
from foundry_ontology.core import ObjectType, Property, Ontology
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.link_type import Cardinality, LinkType
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.query_engine import objects


@pytest.fixture
def store_with_data():
    o = Ontology(ontology_id="test", display_name="Test", version="1.0")
    o.register_object_type(
        ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "ID", PropertyType.STRING, required=True),
                "name": Property("name", "Name", PropertyType.STRING),
                "status": Property("status", "Status", PropertyType.STRING),
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
                "reading_type": Property("reading_type", "Type", PropertyType.STRING),
            },
        )
    )
    o.register_link_type(
        LinkType("has_readings", "Has Readings", source_type="Asset", target_type="SensorReading", cardinality=Cardinality.ONE_TO_MANY)
    )
    store = ObjectStore(o)
    store.create("Asset", {"asset_id": "A1", "name": "P1", "status": "active"})
    store.create("Asset", {"asset_id": "A2", "name": "P2", "status": "inactive"})
    store.create("SensorReading", {"reading_id": "R1", "value": 10.0, "reading_type": "vibration"})
    store.create("SensorReading", {"reading_id": "R2", "value": 5.0, "reading_type": "temperature"})
    store.create_link("has_readings", "A1", "R1")
    store.create_link("has_readings", "A1", "R2")
    return store


class TestQueryEngine:
    def test_query_filter_by_property(self, store_with_data):
        results = objects(store_with_data, "Asset").filter(status="active").all()
        assert len(results) == 1
        assert results[0].instance_id == "A1"

    def test_query_navigate_link(self, store_with_data):
        results = objects(store_with_data, "Asset").filter(status="active").navigate("has_readings").all()
        assert len(results) == 2  # A1 has R1 and R2

    def test_query_chain_filter_and_navigate(self, store_with_data):
        results = (
            objects(store_with_data, "Asset")
            .filter(status="active")
            .navigate("has_readings")
            .filter(reading_type="vibration")
            .all()
        )
        assert len(results) == 1
        assert results[0].instance_id == "R1"

    def test_query_order_by(self, store_with_data):
        results = objects(store_with_data, "SensorReading").order_by("value", "desc").all()
        assert len(results) == 2
        assert results[0].properties["value"] == 10.0

    def test_query_take_limits_results(self, store_with_data):
        results = objects(store_with_data, "Asset").take(1)
        assert len(results) == 1

    def test_query_count(self, store_with_data):
        c = objects(store_with_data, "Asset").filter(status="active").count()
        assert c == 1

    def test_query_first_returns_single(self, store_with_data):
        inst = objects(store_with_data, "Asset").filter(asset_id="A1").first()
        assert inst is not None
        assert inst.instance_id == "A1"
