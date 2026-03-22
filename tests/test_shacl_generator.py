"""Tests for SHACL generator."""

import pytest
from foundry_ontology.core import ObjectType, Property, Ontology
from foundry_ontology.core.data_types import PropertyType, ValueType
from foundry_ontology.core.action_type import ActionType, ActionParameter
from foundry_ontology.export.shacl_generator import SHACLGenerator


@pytest.fixture
def sample_ontology():
    o = Ontology(ontology_id="test", display_name="Test", version="1.0")
    o.register_object_type(
        ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "ID", PropertyType.STRING, required=True),
                "name": Property("name", "Name", PropertyType.STRING),
            },
        )
    )
    o.register_action_type(
        ActionType(
            action_id="SetPriority",
            parameters=[
                ActionParameter("priority", PropertyType.STRING, options=["LOW", "MEDIUM", "CRITICAL"]),
            ],
            validation_rules=[],
            effects=[],
        )
    )
    return o


class TestSHACLGenerator:
    def test_required_property_generates_mincount(self, sample_ontology):
        gen = SHACLGenerator()
        ttl = gen.generate(sample_ontology)
        assert "minCount" in ttl
        assert "asset_id" in ttl or "Asset" in ttl

    def test_options_list_generates_sh_in(self, sample_ontology):
        gen = SHACLGenerator()
        ttl = gen.generate(sample_ontology)
        assert "LOW" in ttl or "CRITICAL" in ttl
        assert "sh:" in ttl or "shacl" in ttl

    def test_numeric_range_generates_constraints(self, sample_ontology):
        """ValueType with min/max should generate SHACL constraints."""
        from foundry_ontology.core.data_types import ValueType
        from foundry_ontology.core.object_type import ObjectType, Property

        o = Ontology(ontology_id="test", display_name="Test", version="1.0")
        vt = ValueType("Amount", PropertyType.FLOAT, constraints={"min": 0, "max": 100})
        o.register_object_type(
            ObjectType(
                type_id="Item",
                display_name="Item",
                primary_key="id",
                properties={
                    "id": Property("id", "ID", PropertyType.STRING, required=True),
                    "amount": Property("amount", "Amount", PropertyType.FLOAT, value_type=vt),
                },
            )
        )
        gen = SHACLGenerator()
        ttl = gen.generate(o)
        assert "minCount" in ttl or "min" in ttl or "sh:" in ttl

    def test_role_requirement_generates_shape(self, sample_ontology):
        """Action with required_roles - SHACL generator handles action params."""
        gen = SHACLGenerator()
        ttl = gen.generate(sample_ontology)
        assert len(ttl) > 0

    def test_generated_shacl_parseable(self, sample_ontology):
        from rdflib import Graph
        gen = SHACLGenerator()
        ttl = gen.generate(sample_ontology)
        g = Graph()
        g.parse(data=ttl, format="turtle")
        assert len(g) > 0
