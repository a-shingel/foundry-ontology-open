"""Bridge to OntoGuard-AI format for runtime agent validation.

Links to github.com/cloudbadal007/ontoguard-ai
"""

from foundry_ontology.core import Ontology


class OntoGuardBridge:
    """Export to OntoGuard-AI format."""

    def export(self, ontology: Ontology) -> dict:
        """Export ontology as OntoGuard JSON format."""
        shapes = []
        for ot in ontology.object_types.values():
            shape = {
                "type": "ObjectType",
                "id": ot.type_id,
                "display_name": ot.display_name,
                "properties": [
                    {
                        "name": p.name,
                        "required": p.required,
                        "type": p.property_type.value if hasattr(p.property_type, "value") else str(p.property_type),
                    }
                    for p in ot.properties.values()
                ],
            }
            shapes.append(shape)

        for at in ontology.action_types.values():
            shape = {
                "type": "ActionType",
                "id": at.action_id,
                "parameters": [p.name for p in at.parameters],
                "validation_rules": [r.rule_id for r in at.validation_rules],
            }
            shapes.append(shape)

        return {"ontology_id": ontology.ontology_id, "version": ontology.version, "shapes": shapes}
