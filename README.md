# Foundry Ontology Open

**Open-source implementation of Palantir Foundry's three-layer Ontology architecture — with the OWL/SHACL export bridge Foundry doesn't have.**

```
┌─────────────────────────────────────────────────────────────┐
│                    DYNAMIC LAYER                             │
│  Roles • Markings • Permissions • Audit Trail                │
├─────────────────────────────────────────────────────────────┤
│                    KINETIC LAYER                             │
│  Action Types • Functions • Validation Rules • Effects       │
├─────────────────────────────────────────────────────────────┤
│                    SEMANTIC LAYER                            │
│  Object Types • Properties • Link Types • Interfaces         │
├─────────────────────────────────────────────────────────────┤
│                    EXPORT BRIDGE (NEW)                       │
│  OWL Exporter • SHACL Generator • OntoGuard Bridge • MCP     │
└─────────────────────────────────────────────────────────────┘
```

## What This Is

- **Problem**: Palantir Foundry's Ontology is powerful but proprietary. You can't export to W3C standards.
- **Solution**: A lightweight Python library that mirrors Foundry's Object Types, Link Types, Action Types, and Functions — **plus** OWL/RDF and SHACL export, and an MCP server for AI agents.
- **Who it's for**: Data engineers, ontology developers, and anyone building semantic applications who wants vendor-neutral, standards-based output.

## Quick Start

```bash
git clone https://github.com/cloudbadal007/foundry-ontology-open.git
cd foundry-ontology-open
pip install -e .
python examples/energy_asset_maintenance/run_scenario.py
```

## Installation

```bash
pip install -e .
# or with dev deps: pip install -e ".[dev]"
```

## Usage Examples

### Define an Ontology

```python
from foundry_ontology.core import Ontology, ObjectType, Property, LinkType, Cardinality

o = Ontology("my_ontology", "My Ontology", "1.0")
o.register_object_type(ObjectType(
    type_id="Asset",
    display_name="Physical Asset",
    primary_key="asset_id",
    properties={
        "asset_id": Property("asset_id", "ID", PropertyType.STRING, required=True, is_primary_key=True),
        "name": Property("name", "Name", PropertyType.STRING),
    },
))
o.register_link_type(LinkType("has_sensors", "Has Sensors", source_type="Asset", target_type="SensorReading", cardinality=Cardinality.ONE_TO_MANY))
```

### Query via Links

```python
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.query_engine import objects

store = ObjectStore(o)
# ... create instances and links ...

results = (
    objects(store, "Asset")
    .filter(status="active")
    .navigate("has_sensor_readings")
    .filter(reading_type="vibration")
    .take(10)
)
```

### Execute Actions with Validation

```python
from foundry_ontology.engine.action_executor import ActionExecutor
from foundry_ontology.engine.audit_log import AuditLog

audit = AuditLog()
executor = ActionExecutor(o, store, audit)
result = executor.execute("EscalateAsset", {"asset_id": "A1", "priority": "CRITICAL"}, "user1")
```

### Export to OWL

```python
from foundry_ontology.export.owl_exporter import OWLExporter
OWLExporter().export_to_file(o, "ontology.ttl")
```

### Run MCP Server

```bash
foundry-ontology serve
# or: mcp run -m foundry_ontology.cli serve
```

## Case Studies

- **[Energy Asset Maintenance](examples/energy_asset_maintenance/)** — Assets, sensors, technicians, work orders, escalation actions
- **[Human Services](examples/human_services/)** — Benefits eligibility, clients, cases

## How This Compares to Palantir Foundry

| Foundry Concept      | foundry-ontology-open        |
|---------------------|------------------------------|
| Object Type         | ObjectType                   |
| Property / ValueType| Property + ValueType         |
| Link Type           | LinkType                     |
| Action Type         | ActionType                   |
| Function            | OntologyFunction             |
| Interface           | Interface                    |
| Object Storage      | ObjectStore (SQLite)         |
| Audit               | AuditLog                     |
| OWL Export          | **OWLExporter** (Foundry can't) |
| SHACL from rules    | **SHACLGenerator** (Foundry can't) |

## The Export Bridge

Foundry does not export to W3C OWL or SHACL. This library does:

- **OWLExporter**: ObjectTypes → owl:Class, Properties → owl:DatatypeProperty, LinkTypes → owl:ObjectProperty
- **SHACLGenerator**: Action validation rules → SHACL shapes
- **OntoGuard Bridge**: Export to [OntoGuard-AI](https://github.com/cloudbadal007/ontoguard-ai) format

## MCP Server

Expose your ontology to AI agents:

```bash
foundry-ontology serve
```

Tools: `list_object_types`, `search_objects`, `get_object`, `get_linked_objects`, `execute_action`, `list_actions`, `describe_ontology`

## Testing

```bash
pytest -v
pytest --cov=foundry_ontology
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Related Reading

- [Palantir Foundry Ontology: How It Works](https://medium.com/@cloudpankaj) (Medium)
- [MCP + A2A + OWL: The Agentic Mesh](https://medium.com/@cloudpankaj)
- [The Ontology Firewall](https://github.com/cloudbadal007/ontoguard-ai)

## Related Repos

- [ontoguard-ai](https://github.com/cloudbadal007/ontoguard-ai) — Ontology firewall + SHACL validation
- [ontology-mcp-self-healing](https://github.com/cloudbadal007/ontology-mcp-self-healing)
- [universal-agent-connector](https://github.com/cloudbadal007/universal-agent-connector)

## License

MIT

## Author

**Pankaj Kumar**
- GitHub: [cloudbadal007](https://github.com/cloudbadal007)
- Medium: @cloudpankaj
- Substack: badalaiworld.substack.com
- X: @CloudyPankaj
