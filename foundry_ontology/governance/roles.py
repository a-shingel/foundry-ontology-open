"""Role-based access control."""

from dataclasses import dataclass


@dataclass
class Permission:
    """A permission (read, write, execute, etc.)."""

    permission_id: str
    display_name: str
    scope: str  # object_type_id or "*" for all


@dataclass
class Role:
    """A role with associated permissions."""

    role_id: str
    display_name: str
    description: str = ""
    permissions: list[Permission] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


@dataclass
class User:
    """A user with roles and markings clearance."""

    user_id: str
    display_name: str
    roles: list[str] = None  # role IDs
    markings: list[str] = None  # marking levels the user has clearance for

    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.markings is None:
            self.markings = []

    def has_role(self, role_id: str) -> bool:
        return role_id in self.roles
