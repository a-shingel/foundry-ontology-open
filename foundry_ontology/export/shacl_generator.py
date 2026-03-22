"""Generate SHACL shapes from Action validation rules.

THE OTHER BRIDGE THAT DOESN'T EXIST IN REAL FOUNDRY.
"""

from foundry_ontology.core import Ontology, ActionType

try:
    from rdflib import Graph, Literal, URIRef
    from rdflib.namespace import RDF
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False

NS = "http://foundry-ontology.org/ns#"
SHACL_NS = "https://www.w3.org/ns/shacl#"


class SHACLGenerator:
    """Converts ActionType validation rules into SHACL shapes."""

    def __init__(self):
        if not RDFLIB_AVAILABLE:
            raise ImportError("rdflib is required for SHACL. Install with: pip install rdflib")

    def generate(self, ontology: Ontology) -> str:
        """Generate SHACL Turtle for the ontology."""
        g = Graph()
        g.bind("ent", NS)
        g.bind("sh", SHACL_NS)
        g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")

        # Generate shapes from object types (required properties)
        for ot in ontology.object_types.values():
            shape_uri = URIRef(NS + "Shape_" + ot.type_id)
            g.add((shape_uri, RDF.type, URIRef(SHACL_NS + "NodeShape")))
            g.add((shape_uri, URIRef(SHACL_NS + "targetClass"), URIRef(NS + ot.type_id)))
            for prop in ot.properties.values():
                if prop.required:
                    prop_shape = URIRef(NS + "Shape_" + ot.type_id + "_" + prop.name)
                    g.add((shape_uri, URIRef(SHACL_NS + "property"), prop_shape))
                    g.add((prop_shape, RDF.type, URIRef(SHACL_NS + "PropertyShape")))
                    g.add((prop_shape, URIRef(SHACL_NS + "path"), URIRef(NS + ot.type_id + "_" + prop.name)))
                    g.add((prop_shape, URIRef(SHACL_NS + "minCount"), Literal(1)))

        # Generate shapes from action validation rules
        for at in ontology.action_types.values():
            self._add_action_shapes(g, at)

        return g.serialize(format="turtle")

    def _add_action_shapes(self, g: Graph, action: ActionType) -> None:
        """Add SHACL constraints derived from action validation rules."""
        for param in action.parameters:
            if param.options:
                # Options list -> sh:in
                shape_uri = URIRef(NS + "ActionParam_" + action.action_id + "_" + param.name)
                g.add((shape_uri, RDF.type, URIRef(SHACL_NS + "PropertyShape")))
                for opt in param.options:
                    g.add((shape_uri, URIRef(SHACL_NS + "in"), Literal(opt)))

    def generate_for_action(self, action: ActionType) -> str:
        """Generate SHACL for a single action."""
        g = Graph()
        g.bind("ent", NS)
        g.bind("sh", SHACL_NS)
        self._add_action_shapes(g, action)
        return g.serialize(format="turtle")

    def generate_to_file(self, ontology: Ontology, path: str) -> None:
        """Generate SHACL to file."""
        s = self.generate(ontology)
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
