"""Tests for link_type module."""

import pytest
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.link_type import Cardinality, LinkType
from foundry_ontology.core.object_type import ObjectType, Property
from foundry_ontology.core.ontology import Ontology


class TestLinkType:
    def test_create_link_one_to_many(self):
        lt = LinkType(
            link_id="has_readings",
            display_name="Has Readings",
            source_type="Asset",
            target_type="SensorReading",
            cardinality=Cardinality.ONE_TO_MANY,
        )
        assert lt.cardinality == Cardinality.ONE_TO_MANY
        assert lt.source_type == "Asset"
        assert lt.target_type == "SensorReading"

    def test_create_link_many_to_many(self):
        lt = LinkType(
            link_id="shared_assets",
            display_name="Shared Assets",
            source_type="Project",
            target_type="Asset",
            cardinality=Cardinality.MANY_TO_MANY,
        )
        assert lt.cardinality == Cardinality.MANY_TO_MANY

    def test_link_references_valid_types(self):
        lt = LinkType(
            link_id="link1",
            display_name="Link",
            source_type="A",
            target_type="B",
        )
        assert lt.source_type == "A"
        assert lt.target_type == "B"

    def test_link_with_properties(self):
        lt = LinkType(
            link_id="assignment",
            display_name="Assignment",
            source_type="WorkOrder",
            target_type="Technician",
            properties={
                "assigned_date": Property("assigned_date", "Assigned Date", PropertyType.DATETIME),
            },
        )
        assert "assigned_date" in lt.properties

    def test_link_references_invalid_type_raises(self):
        """LinkType with invalid source/target should be caught by ontology.validate_ontology()."""
        o = Ontology("test", "Test", "1.0")
        o.register_object_type(
            ObjectType("Asset", "Asset", primary_key="id", properties={"id": Property("id", "ID", PropertyType.STRING)})
        )
        o.register_link_type(
            LinkType("bad_link", "Bad", source_type="Asset", target_type="NonExistent", cardinality=Cardinality.ONE_TO_ONE)
        )
        errors = o.validate_ontology()
        assert any("NonExistent" in e for e in errors)

    def test_reverse_navigation_name(self):
        lt = LinkType(
            link_id="parent_of",
            display_name="Parent Of",
            source_type="Asset",
            target_type="Asset",
            reverse_name="parent",
        )
        assert lt.reverse_name == "parent"
