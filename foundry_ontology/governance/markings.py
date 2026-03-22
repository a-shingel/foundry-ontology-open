"""Data classification markings."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Marking:
    """Data classification marking (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)."""

    marking_id: str
    level: int  # higher = more restricted
    display_name: str = ""

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.marking_id


# Standard marking levels
PUBLIC = Marking("PUBLIC", 0, "Public")
INTERNAL = Marking("INTERNAL", 1, "Internal")
CONFIDENTIAL = Marking("CONFIDENTIAL", 2, "Confidential")
RESTRICTED = Marking("RESTRICTED", 3, "Restricted")


def get_marking_level(marking_id: str) -> int:
    """Get level for a standard marking."""
    levels = {"PUBLIC": 0, "INTERNAL": 1, "CONFIDENTIAL": 2, "RESTRICTED": 3}
    return levels.get(marking_id.upper(), 0)


def user_has_clearance(user_markings: list[str], required_marking: str) -> bool:
    """Check if user's clearance >= required marking level."""
    user_max = max((get_marking_level(m) for m in user_markings), default=0)
    required = get_marking_level(required_marking)
    return user_max >= required
