"""Tests for data_types module - PropertyType and ValueType."""

import pytest
from datetime import date, datetime

from foundry_ontology.core.data_types import PropertyType, ValueType


class TestPropertyType:
    """Tests for PropertyType enum."""

    def test_property_type_values(self):
        """All expected Foundry-mirroring types exist."""
        assert PropertyType.STRING.value == "string"
        assert PropertyType.INTEGER.value == "integer"
        assert PropertyType.FLOAT.value == "float"
        assert PropertyType.BOOLEAN.value == "boolean"
        assert PropertyType.DATE.value == "date"
        assert PropertyType.DATETIME.value == "datetime"
        assert PropertyType.OBJECT_REFERENCE.value == "object_reference"
        assert PropertyType.GEOHASH.value == "geohash"
        assert PropertyType.ATTACHMENT.value == "attachment"


class TestValueType:
    """Tests for ValueType semantic wrapper."""

    def test_value_type_basic_creation(self):
        """ValueType can be created with name and base type."""
        vt = ValueType(name="EmailAddress", base_type=PropertyType.STRING)
        assert vt.name == "EmailAddress"
        assert vt.base_type == PropertyType.STRING
        assert vt.constraints == {}
        assert vt.description == ""

    def test_value_type_with_constraints(self):
        """ValueType accepts constraints dict."""
        vt = ValueType(
            name="USD_Amount",
            base_type=PropertyType.DECIMAL,
            constraints={"min": 0, "max": 1_000_000},
        )
        assert vt.constraints["min"] == 0
        assert vt.constraints["max"] == 1_000_000

    def test_value_type_validate_none_passes(self):
        """None value passes validation (optional fields)."""
        vt = ValueType(name="OptionalField", base_type=PropertyType.STRING)
        valid, err = vt.validate(None)
        assert valid
        assert err is None

    def test_value_type_string_constraint_pattern(self):
        """Pattern constraint validates string format."""
        vt = ValueType(
            name="EmailAddress",
            base_type=PropertyType.STRING,
            constraints={"pattern": r"^[\w.+-]+@[\w.]+\.\w+$"},
        )
        valid, err = vt.validate("user@example.com")
        assert valid, err
        assert err is None

        valid, err = vt.validate("not-an-email")
        assert not valid
        assert "pattern" in err or "match" in err.lower()

    def test_value_type_min_max_constraint(self):
        """Numeric min/max constraints work."""
        vt = ValueType(
            name="AssetId",
            base_type=PropertyType.INTEGER,
            constraints={"min": 0, "max": 100},
        )
        valid, _ = vt.validate(50)
        assert valid
        valid, err = vt.validate(-1)
        assert not valid
        assert "min" in err.lower() or ">=" in err
        valid, err = vt.validate(150)
        assert not valid
        assert "max" in err.lower() or "<=" in err

    def test_value_type_in_enum_constraint(self):
        """'in' constraint validates against allowed values."""
        vt = ValueType(
            name="Status",
            base_type=PropertyType.STRING,
            constraints={"in": ["active", "inactive", "pending"]},
        )
        valid, _ = vt.validate("active")
        assert valid
        valid, err = vt.validate("unknown")
        assert not valid
        assert "one of" in err.lower()

    def test_value_type_min_length_constraint(self):
        """minLength constraint validates string length."""
        vt = ValueType(
            name="ShortCode",
            base_type=PropertyType.STRING,
            constraints={"minLength": 3},
        )
        valid, _ = vt.validate("abc")
        assert valid
        valid, err = vt.validate("ab")
        assert not valid

    def test_value_type_max_length_constraint(self):
        """maxLength constraint validates string length."""
        vt = ValueType(
            name="Code",
            base_type=PropertyType.STRING,
            constraints={"maxLength": 5},
        )
        valid, _ = vt.validate("abcde")
        assert valid
        valid, err = vt.validate("abcdef")
        assert not valid
