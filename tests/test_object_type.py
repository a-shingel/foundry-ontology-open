"""Tests for object_type module."""

import pytest
from foundry_ontology.core.data_types import PropertyType, ValueType
from foundry_ontology.core.object_type import (
    ObjectType,
    Property,
    SharedProperty,
    ValidationResult,
)


class TestObjectType:
    def test_create_object_type_with_properties(self):
        ot = ObjectType(
            type_id="Asset",
            display_name="Physical Asset",
            description="A physical asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property(
                    name="asset_id",
                    display_name="Asset ID",
                    property_type=PropertyType.STRING,
                    required=True,
                    is_primary_key=True,
                ),
                "name": Property(
                    name="name",
                    display_name="Name",
                    property_type=PropertyType.STRING,
                    required=True,
                ),
            },
        )
        assert ot.type_id == "Asset"
        assert ot.primary_key == "asset_id"
        assert ot.get_property("asset_id") is not None
        assert ot.get_property("name") is not None

    def test_primary_key_required(self):
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property(
                    name="asset_id",
                    display_name="Asset ID",
                    property_type=PropertyType.STRING,
                    required=True,
                    is_primary_key=True,
                ),
            },
        )
        result = ot.validate_instance({})
        assert not result.valid
        assert any("asset_id" in e or "required" in e.lower() for e in result.errors)

    def test_validate_instance_valid_data(self):
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "Asset ID", PropertyType.STRING, required=True, is_primary_key=True),
                "name": Property("name", "Name", PropertyType.STRING, required=True),
            },
        )
        result = ot.validate_instance({"asset_id": "A1", "name": "Pump 1"})
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_instance_missing_required(self):
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "Asset ID", PropertyType.STRING, required=True),
                "name": Property("name", "Name", PropertyType.STRING, required=True),
            },
        )
        result = ot.validate_instance({"asset_id": "A1"})
        assert not result.valid
        assert any("name" in e for e in result.errors)

    def test_validate_instance_wrong_type(self):
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="asset_id",
            properties={
                "asset_id": Property("asset_id", "Asset ID", PropertyType.STRING, required=True),
                "count": Property("count", "Count", PropertyType.INTEGER),
            },
        )
        result = ot.validate_instance({"asset_id": "A1", "count": "not-a-number"})
        assert not result.valid

    def test_shared_property_across_types(self):
        sp = SharedProperty(
            name="created_at",
            display_name="Created At",
            property_type=PropertyType.DATETIME,
            used_by=["Asset", "Technician"],
        )
        assert sp.used_by == ["Asset", "Technician"]

    def test_value_type_constraint_enforcement(self):
        vt = ValueType(
            name="Email",
            base_type=PropertyType.STRING,
            constraints={"pattern": r"^[\w.+-]+@[\w.]+\.\w+$"},
        )
        prop = Property("email", "Email", PropertyType.STRING, value_type=vt)
        valid, _ = prop.validate_value("a@b.com")
        assert valid
        valid, _ = prop.validate_value("invalid")
        assert not valid

    def test_add_property(self):
        ot = ObjectType(type_id="T", display_name="T", primary_key="id", properties={})
        ot.add_property(
            Property("id", "ID", PropertyType.STRING, required=True, is_primary_key=True)
        )
        ot.add_property(Property("x", "X", PropertyType.INTEGER))
        assert "id" in ot.properties
        assert "x" in ot.properties
        assert ot.primary_key == "id"

    def test_implements(self):
        ot = ObjectType(
            type_id="Asset",
            display_name="Asset",
            primary_key="id",
            properties={},
            interfaces=["Inspectable"],
        )
        assert ot.implements("Inspectable")
        assert not ot.implements("Unknown")
