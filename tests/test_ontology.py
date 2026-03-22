"""Tests for ontology module."""

import pytest
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.object_type import ObjectType, Property
from foundry_ontology.core.link_type import Cardinality, LinkType
from foundry_ontology.core.action_type import ActionType, ActionParameter
from foundry_ontology.core.interface import Interface
from foundry_ontology.core.ontology import Ontology
from foundry_ontology.core.function import OntologyFunction


class TestOntology:
    def test_register_and_retrieve_types(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        ot = ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        o.register_object_type(ot)
        assert "Asset" in o.object_types
        assert o.object_types["Asset"] == ot

    def test_register_link_type(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        lt = LinkType(
            link_id="has_sensors",
            display_name="Has Sensors",
            source_type="Asset",
            target_type="SensorReading",
            cardinality=Cardinality.ONE_TO_MANY,
        )
        o.register_link_type(lt)
        assert "has_sensors" in o.link_types

    def test_register_action_type(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        at = ActionType(
            action_id="Create",
            parameters=[ActionParameter("x", PropertyType.STRING)],
            validation_rules=[],
            effects=[],
        )
        o.register_action_type(at)
        assert "Create" in o.action_types

    def test_register_function(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        fn = OntologyFunction(
            function_id="get_assets",
            display_name="Get Assets",
            implementation=lambda: [],
        )
        o.register_function(fn)
        assert "get_assets" in o.functions

    def test_register_interface(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        iface = Interface(interface_id="I1", display_name="I1")
        o.register_interface(iface)
        assert "I1" in o.interfaces

    def test_get_linked_types(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        o.register_object_type(
            ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        )
        o.register_object_type(
            ObjectType(type_id="Sensor", display_name="Sensor", primary_key="id", properties={})
        )
        o.register_link_type(
            LinkType("l1", "L1", source_type="Asset", target_type="Sensor", cardinality=Cardinality.ONE_TO_MANY)
        )
        o.register_link_type(
            LinkType("l2", "L2", source_type="Sensor", target_type="Asset", cardinality=Cardinality.ONE_TO_MANY)
        )
        linked = o.get_linked_types("Asset")
        assert len(linked) == 2
        linked = o.get_linked_types("Sensor")
        assert len(linked) == 2

    def test_validate_ontology_invalid_link_refs(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        o.register_object_type(
            ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        )
        o.register_link_type(
            LinkType("l1", "L1", source_type="Asset", target_type="MissingType", cardinality=Cardinality.ONE_TO_ONE)
        )
        errors = o.validate_ontology()
        assert len(errors) >= 1
        assert any("MissingType" in e for e in errors)

    def test_validate_ontology_valid(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        o.register_object_type(
            ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        )
        o.register_object_type(
            ObjectType(type_id="Sensor", display_name="Sensor", primary_key="id", properties={})
        )
        o.register_link_type(
            LinkType("l1", "L1", source_type="Asset", target_type="Sensor", cardinality=Cardinality.ONE_TO_MANY)
        )
        errors = o.validate_ontology()
        assert len(errors) == 0

    def test_summary(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        o.register_object_type(
            ObjectType(type_id="A", display_name="A", primary_key="id", properties={})
        )
        o.register_link_type(LinkType("l1", "L1", source_type="A", target_type="A"))
        o.register_action_type(ActionType(action_id="Act1", parameters=[], validation_rules=[], effects=[]))
        s = o.summary()
        assert s["object_types"] == 1
        assert s["link_types"] == 1
        assert s["action_types"] == 1

    def test_to_dict(self):
        o = Ontology(ontology_id="o1", display_name="O1", version="1.0")
        o.register_object_type(
            ObjectType(
                type_id="Asset",
                display_name="Asset",
                primary_key="id",
                properties={"id": Property("id", "ID", PropertyType.STRING)},
            )
        )
        d = o.to_dict()
        assert d["ontology_id"] == "o1"
        assert "Asset" in d["object_types"]
        assert d["object_types"]["Asset"]["primary_key"] == "id"
