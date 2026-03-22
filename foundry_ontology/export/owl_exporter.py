"""Export operational ontology to W3C OWL/RDF (Turtle format).

THE BRIDGE THAT DOESN'T EXIST IN REAL FOUNDRY.
"""

from typing import Optional

from foundry_ontology.core import Ontology
from foundry_ontology.engine.object_store import ObjectStore

try:
    from rdflib import Graph, Literal, Namespace, BNode, URIRef
    from rdflib.namespace import OWL, RDF, RDFS, XSD
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False

NS = "http://foundry-ontology.org/ns#"
ENT = Namespace(NS) if RDFLIB_AVAILABLE else None


def _prop_type_to_xsd(pt) -> str:
    """Map PropertyType to XSD datatype."""
    m = {
        "string": str(XSD.string),
        "integer": str(XSD.integer),
        "float": str(XSD.float),
        "decimal": str(XSD.decimal),
        "boolean": str(XSD.boolean),
        "date": str(XSD.date),
        "datetime": str(XSD.dateTime),
        "timestamp": str(XSD.dateTime),
    }
    return m.get(pt.value if hasattr(pt, "value") else pt, str(XSD.string))


class OWLExporter:
    """Converts operational ontology to W3C OWL/RDF (Turtle format)."""

    def __init__(self):
        if not RDFLIB_AVAILABLE:
            raise ImportError("rdflib is required for OWL export. Install with: pip install rdflib")

    def export(self, ontology: Ontology) -> str:
        """Export ontology to Turtle string."""
        g = Graph()
        g.bind("ent", NS)
        g.bind("owl", "http://www.w3.org/2002/07/owl#")
        g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

        # ObjectTypes as owl:Class
        for ot in ontology.object_types.values():
            uri = URIRef(NS + ot.type_id)
            g.add((uri, RDF.type, OWL.Class))
            g.add((uri, RDFS.label, Literal(ot.display_name)))
            if ot.description:
                g.add((uri, RDFS.comment, Literal(ot.description)))

            # Properties as owl:DatatypeProperty
            for prop in ot.properties.values():
                prop_uri = URIRef(NS + ot.type_id + "_" + prop.name)
                g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
                g.add((prop_uri, RDFS.domain, uri))
                g.add((prop_uri, RDFS.range, URIRef(_prop_type_to_xsd(prop.property_type))))

            # Interfaces as superclasses
            for iface_id in ot.interfaces:
                if iface_id in ontology.interfaces:
                    g.add((uri, RDFS.subClassOf, URIRef(NS + iface_id)))

        # Interfaces as Classes
        for iface in ontology.interfaces.values():
            uri = URIRef(NS + iface.interface_id)
            g.add((uri, RDF.type, OWL.Class))
            g.add((uri, RDFS.label, Literal(iface.display_name)))

        # LinkTypes as owl:ObjectProperty
        for lt in ontology.link_types.values():
            uri = URIRef(NS + lt.link_id)
            g.add((uri, RDF.type, OWL.ObjectProperty))
            g.add((uri, RDFS.domain, URIRef(NS + lt.source_type)))
            g.add((uri, RDFS.range, URIRef(NS + lt.target_type)))
            g.add((uri, RDFS.label, Literal(lt.display_name)))

        return g.serialize(format="turtle")

    def export_to_file(self, ontology: Ontology, path: str) -> None:
        """Export to a Turtle file."""
        s = self.export(ontology)
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)

    def export_instances(self, store: ObjectStore, ontology: Ontology) -> str:
        """Export object instances as RDF."""
        g = Graph()
        g.bind("ent", NS)
        g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

        for inst in store.get_all_instances():
            uri = URIRef(NS + "instance/" + inst.instance_id)
            ot_uri = URIRef(NS + inst.object_type_id)
            g.add((uri, RDF.type, ot_uri))
            for k, v in inst.properties.items():
                if v is not None:
                    prop_uri = URIRef(NS + inst.object_type_id + "_" + k)
                    g.add((uri, prop_uri, Literal(v)))

        return g.serialize(format="turtle")
