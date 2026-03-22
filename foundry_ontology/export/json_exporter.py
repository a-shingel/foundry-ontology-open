"""Export ontology to JSON for dashboards and visualization."""

from foundry_ontology.core import Ontology


class JSONExporter:
    """Export ontology to JSON format."""

    def export(self, ontology: Ontology) -> dict:
        """Export ontology as JSON-serializable dict."""
        return ontology.to_dict()
