"""MCP server exposing ontology as tools for AI agents."""

import json
from typing import Optional

from foundry_ontology.core import Ontology
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.query_engine import objects
from foundry_ontology.engine.action_executor import ActionExecutor
from foundry_ontology.engine.audit_log import AuditLog

try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def create_mcp_server(
    ontology: Ontology,
    store: Optional[ObjectStore] = None,
    audit: Optional[AuditLog] = None,
    name: str = "foundry-ontology",
) -> "FastMCP":
    """Create an MCP server with ontology tools and resources."""
    if not MCP_AVAILABLE:
        raise ImportError("mcp is required. Install with: pip install mcp")

    store = store or ObjectStore(ontology)
    audit = audit or AuditLog()
    executor = ActionExecutor(ontology, store, audit)

    mcp = FastMCP(name, instructions="Ontology tools for querying and acting on object types.")

    @mcp.tool()
    def list_object_types() -> str:
        """List all ObjectTypes with their descriptions."""
        result = []
        for ot in ontology.object_types.values():
            result.append({
                "type_id": ot.type_id,
                "display_name": ot.display_name,
                "description": ot.description,
                "properties": list(ot.properties.keys()),
            })
        return json.dumps(result, indent=2)

    @mcp.tool()
    def search_objects(type_id: str, filters: Optional[str] = None) -> str:
        """Search objects by type and optional JSON filters. Example: filters='{\"status\": \"active\"}'"""
        f = json.loads(filters) if filters else {}
        q = objects(store, type_id).filter(**f)
        instances = q.all()
        return json.dumps([inst.properties for inst in instances], indent=2)

    @mcp.tool()
    def get_object(instance_id: str) -> str:
        """Get a specific object by instance ID."""
        inst = store.get(instance_id)
        if not inst:
            return json.dumps({"error": "Not found"})
        return json.dumps(inst.properties, indent=2)

    @mcp.tool()
    def get_linked_objects(instance_id: str, link_type_id: str) -> str:
        """Get objects linked from this instance via the given link type."""
        linked = store.get_linked(instance_id, link_type_id)
        return json.dumps([o.properties for o in linked], indent=2)

    @mcp.tool()
    def execute_action(action_type_id: str, params: str) -> str:
        """Execute an action. params must be JSON object with parameter names."""
        p = json.loads(params)
        result = executor.execute(action_type_id, p, executed_by="mcp-client")
        return json.dumps({
            "success": result.success,
            "errors": result.validation_errors,
            "audit_entry_id": result.audit_entry_id,
        })

    @mcp.tool()
    def list_actions() -> str:
        """List available actions with their parameters."""
        return json.dumps([at.describe() for at in ontology.action_types.values()], indent=2)

    @mcp.tool()
    def describe_ontology() -> str:
        """Full ontology summary for agent context."""
        return json.dumps(ontology.to_dict(), indent=2)

    @mcp.resource("ontology://schema")
    def ontology_schema() -> str:
        """Full ontology definition."""
        return json.dumps(ontology.to_dict(), indent=2)

    return mcp


def run_mcp_server(ontology: Ontology, store: Optional[ObjectStore] = None):
    """Run the MCP server. Use: mcp run foundry_ontology.mcp.mcp_server:main with ontology loaded."""
    mcp = create_mcp_server(ontology, store)
    mcp.run()
