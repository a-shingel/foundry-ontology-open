# Architecture

## Three-Layer Model

foundry-ontology-open follows Palantir Foundry's three-layer Ontology architecture:

### Semantic Layer

- **ObjectType**: Schema for entities (Asset, Technician, etc.)
- **Property**: Fields with types (STRING, INTEGER, etc.) and optional ValueType constraints
- **LinkType**: Typed relationships between ObjectTypes with cardinality
- **Interface**: Polymorphic shapes implemented by multiple ObjectTypes

### Kinetic Layer

- **ActionType**: Executable actions with parameters, validation rules, and effects
- **OntologyFunction**: Server-side business logic (e.g., get_high_risk_assets)
- **ActionExecutor**: Runs actions with validation and audit
- **ValidationRule**: Python expressions evaluated at runtime

### Dynamic Layer

- **Roles & Permissions**: Role-based access control
- **Markings**: Data classification (PUBLIC, INTERNAL, CONFIDENTIAL)
- **AuditLog**: Immutable trail of all actions

## Export Bridge

Unique to this project:

- **OWLExporter**: Maps ObjectTypes → owl:Class, LinkTypes → owl:ObjectProperty
- **SHACLGenerator**: Converts validation rules to SHACL shapes
- **OntoGuardBridge**: Exports for OntoGuard-AI compatibility

## Data Flow

1. Define Ontology (schema)
2. Create instances in ObjectStore
3. Query via OntologyQuery (navigate links, filter)
4. Execute actions via ActionExecutor
5. Export to OWL/SHACL for interoperability
