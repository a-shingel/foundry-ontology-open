# OWL Export Guide

## Overview

The OWLExporter converts your operational ontology to W3C OWL/RDF in Turtle format.

## Mapping Rules

- **ObjectType** → `owl:Class`
- **Property** → `owl:DatatypeProperty` with `rdfs:domain` and `rdfs:range`
- **LinkType** → `owl:ObjectProperty`
- **Interface** → `owl:Class` with implementors as `rdfs:subClassOf`

## Usage

```python
from foundry_ontology.export.owl_exporter import OWLExporter

exporter = OWLExporter()
ttl_string = exporter.export(ontology)
exporter.export_to_file(ontology, "output.ttl")

# Export instances as RDF
ttl_instances = exporter.export_instances(store, ontology)
```

## Namespace

Default namespace: `http://foundry-ontology.org/ns#`

## Dependencies

Requires `rdflib`: `pip install rdflib`
