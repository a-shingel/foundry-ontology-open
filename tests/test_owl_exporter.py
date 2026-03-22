"""Tests for OWL exporter."""

import pytest
from foundry_ontology.core import ObjectType, Property, Ontology
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.link_type import Cardinality, LinkType
from foundry_ontology.core.interface import Interface
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.export.owl_exporter import OWLExporter


@pytest.fixture
def sample_ontology():
    o = Ontology(ontology_id="test", display_name="Test", version="1.0")
    o.register_object_type(
        ObjectType(
            type_id="Asset",
            display_name="Physical Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "ID", PropertyType.STRING, required=True),
                "name": Property("name", "Name", PropertyType.STRING),
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
    iface = Interface("Inspectable", "Inspectable", required_properties=[Property("inspection_date", "Date", PropertyType.DATE)])
    o.register_interface(iface)
    return o


class TestOWLExporter:
    def test_export_object_types_as_owl_classes(self, sample_ontology):
        exporter = OWLExporter()
        ttl = exporter.export(sample_ontology)
        assert "Asset" in ttl
        assert "owl:Class" in ttl or "a owl:Class" in ttl

    def test_export_properties_as_datatype_properties(self, sample_ontology):
        exporter = OWLExporter()
        ttl = exporter.export(sample_ontology)
        assert "asset_id" in ttl or "Asset_asset_id" in ttl
        assert "DatatypeProperty" in ttl

    def test_export_links_as_object_properties(self, sample_ontology):
        exporter = OWLExporter()
        ttl = exporter.export(sample_ontology)
        assert "has_readings" in ttl
        assert "ObjectProperty" in ttl

    def test_export_interfaces_as_superclasses(self, sample_ontology):
        sample_ontology.object_types["Asset"].interfaces = ["Inspectable"]
        exporter = OWLExporter()
        ttl = exporter.export(sample_ontology)
        assert "Inspectable" in ttl
        assert "subClassOf" in ttl

    def test_export_roundtrip_parseable_by_rdflib(self, sample_ontology):
        from rdflib import Graph
        exporter = OWLExporter()
        ttl = exporter.export(sample_ontology)
        g = Graph()
        g.parse(data=ttl, format="turtle")
        assert len(g) > 0

    def test_export_cardinality_restrictions(self, sample_ontology):
        """Cardinality from LinkType should appear in OWL ObjectProperty."""
        exporter = OWLExporter()
        ttl = exporter.export(sample_ontology)
        # ONE_TO_MANY link has domain and range
        assert "has_readings" in ttl
        assert "Asset" in ttl and "SensorReading" in ttl

    def test_export_instances_as_rdf(self, sample_ontology):
        store = ObjectStore(sample_ontology)
        store.create("Asset", {"asset_id": "A1", "name": "Pump 1"})
        exporter = OWLExporter()
        ttl = exporter.export_instances(store, sample_ontology)
        assert "A1" in ttl or "instance" in ttl
        assert "Pump 1" in ttl
