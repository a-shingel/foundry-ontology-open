# Foundry Comparison

This document maps Palantir Foundry Ontology concepts to foundry-ontology-open.

| Foundry | foundry-ontology-open |
|---------|------------------------|
| Object Type | `ObjectType` |
| Primary Key | `primary_key` on ObjectType |
| Property | `Property` |
| Value Type | `ValueType` (semantic wrapper with constraints) |
| Link Type | `LinkType` with `Cardinality` |
| Action Type | `ActionType` with `ValidationRule`, `ActionEffect` |
| Function | `OntologyFunction` |
| Interface | `Interface` |
| Object Storage V2 | `ObjectStore` |
| Objects.search() | `OntologyQuery` via `objects(store, type_id)` |
| Action execution | `ActionExecutor.execute()` |
| Audit | `AuditLog` |
| OWL export | Not in Foundry; `OWLExporter` here |
| SHACL from rules | Not in Foundry; `SHACLGenerator` here |
