"""Permission checks for read, write, execute."""

from typing import TYPE_CHECKING

from foundry_ontology.governance.markings import user_has_clearance

if TYPE_CHECKING:
    from foundry_ontology.core.action_type import ActionType
    from foundry_ontology.core.object_type import ObjectType
    from foundry_ontology.governance.roles import User


class PermissionCheck:
    """Static permission checks."""

    @staticmethod
    def can_read(user: "User", object_type: "ObjectType", property: str = None) -> bool:
        """Check if user can read the object type (or specific property)."""
        if "Admin" in user.roles:
            return True
        # Admin bypasses; otherwise require at least one role (simplified)
        return len(user.roles) > 0

    @staticmethod
    def can_write(user: "User", object_type: "ObjectType") -> bool:
        """Check if user can write to the object type."""
        if "Admin" in user.roles:
            return True
        return "Engineer" in user.roles or "Admin" in user.roles

    @staticmethod
    def can_execute(user: "User", action_type: "ActionType") -> bool:
        """Check if user can execute the action."""
        if "Admin" in user.roles:
            return True
        if not action_type.required_roles:
            return True
        return any(r in user.roles for r in action_type.required_roles)
