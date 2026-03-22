"""Tests for action_type module."""

import pytest
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.action_type import (
    ActionParameter,
    ActionType,
    ValidationRule,
)


class TestActionType:
    def test_action_validation_passes(self):
        at = ActionType(
            action_id="TestAction",
            parameters=[
                ActionParameter("x", PropertyType.STRING),
                ActionParameter("y", PropertyType.INTEGER),
            ],
            validation_rules=[],
            effects=[],
        )
        result = at.validate({"x": "hello", "y": 42})
        assert result.valid

    def test_action_validation_fails_missing_param(self):
        at = ActionType(
            action_id="TestAction",
            parameters=[ActionParameter("required_x", PropertyType.STRING, required=True)],
            validation_rules=[],
            effects=[],
        )
        result = at.validate({})
        assert not result.valid
        assert any("required_x" in e or "Missing" in e for e in result.errors)

    def test_action_validation_fails_rule(self):
        at = ActionType(
            action_id="EscalateAsset",
            parameters=[ActionParameter("asset_id", PropertyType.STRING)],
            validation_rules=[
                ValidationRule(
                    rule_id="r1",
                    expression="asset.get('status') != 'decommissioned'",
                    message="Cannot escalate decommissioned asset",
                ),
            ],
            effects=[],
        )
        # Pass asset in context (as would executor after resolving asset_id)
        result = at.validate({"asset_id": "A1", "asset": {"status": "decommissioned"}})
        assert not result.valid
        assert any("decommissioned" in e for e in result.errors)

    def test_action_requires_role(self):
        at = ActionType(
            action_id="CriticalAction",
            parameters=[],
            validation_rules=[],
            effects=[],
            required_roles=["SeniorEngineer", "PlantManager"],
        )
        assert "SeniorEngineer" in at.required_roles

    def test_action_effects_described_correctly(self):
        at = ActionType(
            action_id="CreateWO",
            display_name="Create Work Order",
            description="Creates a work order",
            parameters=[ActionParameter("asset_id", PropertyType.STRING)],
            validation_rules=[],
            effects=[],
            required_roles=["Engineer"],
        )
        desc = at.describe()
        assert desc["action_id"] == "CreateWO"
        assert desc["display_name"] == "Create Work Order"
        assert len(desc["parameters"]) == 1
        assert desc["parameters"][0]["name"] == "asset_id"
        assert "Engineer" in desc["required_roles"]

    def test_action_validation_options_enforced(self):
        at = ActionType(
            action_id="SetPriority",
            parameters=[
                ActionParameter("priority", PropertyType.STRING, options=["LOW", "MEDIUM", "CRITICAL"]),
            ],
            validation_rules=[],
            effects=[],
        )
        result = at.validate({"priority": "INVALID"})
        assert not result.valid
        result = at.validate({"priority": "CRITICAL"})
        assert result.valid
