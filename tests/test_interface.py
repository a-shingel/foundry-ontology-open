"""Tests for interface module."""

import pytest
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.interface import Interface
from foundry_ontology.core.object_type import ObjectType, Property
from foundry_ontology.core.ontology import Ontology


class TestInterface:
    def test_interface_compliance_check_passes(self):
        iface = Interface(
            interface_id="Inspectable",
            display_name="Inspectable",
            required_properties=[
                Property("inspection_date", "Inspection Date", PropertyType.DATE),
                Property("inspector_id", "Inspector ID", PropertyType.STRING),
            ],
        )
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="id",
            properties={
                "id": Property("id", "ID", PropertyType.STRING, required=True),
                "inspection_date": Property("inspection_date", "Inspection Date", PropertyType.DATE),
                "inspector_id": Property("inspector_id", "Inspector ID", PropertyType.STRING),
            },
            interfaces=["Inspectable"],
        )
        assert iface.check_compliance(ot)

    def test_interface_compliance_check_fails_missing_property(self):
        iface = Interface(
            interface_id="Inspectable",
            display_name="Inspectable",
            required_properties=[
                Property("inspection_date", "Inspection Date", PropertyType.DATE),
                Property("inspector_id", "Inspector ID", PropertyType.STRING),
            ],
        )
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="id",
            properties={
                "id": Property("id", "ID", PropertyType.STRING),
                "inspection_date": Property("inspection_date", "Inspection Date", PropertyType.DATE),
                # missing inspector_id
            },
        )
        assert not iface.check_compliance(ot)

    def test_get_implementors_returns_correct_types(self):
        ontology = Ontology(
            ontology_id="test",
            display_name="Test",
            version="1.0",
        )
        iface = Interface(
            interface_id="Inspectable",
            display_name="Inspectable",
            required_properties=[
                Property("inspection_date", "Inspection Date", PropertyType.DATE),
            ],
        )
        ontology.register_interface(iface)

        asset = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="id",
            properties={
                "id": Property("id", "ID", PropertyType.STRING),
                "inspection_date": Property("inspection_date", "Inspection Date", PropertyType.DATE),
            },
            interfaces=["Inspectable"],
        )
        pipeline = ObjectType(
            type_id="Pipeline",
            display_name="Pipeline",
            primary_key="id",
            properties={
                "id": Property("id", "ID", PropertyType.STRING),
                "inspection_date": Property("inspection_date", "Inspection Date", PropertyType.DATE),
            },
            interfaces=["Inspectable"],
        )
        other = ObjectType(
            type_id="Other",
            display_name="Other",
            primary_key="id",
            properties={"id": Property("id", "ID", PropertyType.STRING)},
            interfaces=[],
        )
        ontology.register_object_type(asset)
        ontology.register_object_type(pipeline)
        ontology.register_object_type(other)

        implementors = iface.get_implementors(ontology)
        assert len(implementors) == 2
        type_ids = {ot.type_id for ot in implementors}
        assert type_ids == {"Asset", "Pipeline"}
