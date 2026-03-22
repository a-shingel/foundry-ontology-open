"""Tests for governance module."""

import pytest
from foundry_ontology.core import ActionType, ObjectType, Property
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.action_type import ActionParameter
from foundry_ontology.governance.roles import User
from foundry_ontology.governance.permissions import PermissionCheck
from foundry_ontology.governance.markings import (
    get_marking_level,
    user_has_clearance,
    PUBLIC,
    CONFIDENTIAL,
)


class TestGovernance:
    def test_user_with_role_can_read(self):
        user = User("u1", "User 1", roles=["Engineer"])
        ot = ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        assert PermissionCheck.can_read(user, ot)

    def test_user_without_role_cannot_write(self):
        user = User("u1", "User 1", roles=["Viewer"])
        ot = ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        assert not PermissionCheck.can_write(user, ot)

    def test_marking_restricts_access(self):
        assert get_marking_level("PUBLIC") == 0
        assert get_marking_level("CONFIDENTIAL") == 2
        assert user_has_clearance(["PUBLIC"], "PUBLIC")
        assert not user_has_clearance(["PUBLIC"], "CONFIDENTIAL")
        assert user_has_clearance(["CONFIDENTIAL"], "PUBLIC")

    def test_admin_bypasses_marking(self):
        user = User("admin", "Admin", roles=["Admin"], markings=["PUBLIC"])
        ot = ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        assert PermissionCheck.can_read(user, ot)
        assert PermissionCheck.can_write(user, ot)

    def test_property_level_marking(self):
        user = User("u1", "User 1", roles=["Engineer"], markings=["INTERNAL"])
        ot = ObjectType(type_id="Asset", display_name="Asset", primary_key="id", properties={})
        assert PermissionCheck.can_read(user, ot, "name")

    def test_can_execute_requires_role(self):
        at = ActionType(
            action_id="Escalate",
            parameters=[],
            validation_rules=[],
            effects=[],
            required_roles=["SeniorEngineer"],
        )
        user_with = User("u1", "User", roles=["SeniorEngineer"])
        user_without = User("u2", "User", roles=["Engineer"])
        assert PermissionCheck.can_execute(user_with, at)
        assert not PermissionCheck.can_execute(user_without, at)
