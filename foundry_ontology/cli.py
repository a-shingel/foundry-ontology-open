"""CLI for foundry-ontology-open."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from foundry_ontology.core import Ontology, ObjectType, Property
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.link_type import LinkType, Cardinality
from foundry_ontology.core.action_type import ActionType, ActionParameter
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.query_engine import objects
from foundry_ontology.engine.audit_log import AuditLog
from foundry_ontology.engine.action_executor import ActionExecutor
from foundry_ontology.export.owl_exporter import OWLExporter
from foundry_ontology.export.shacl_generator import SHACLGenerator
from foundry_ontology.export.json_exporter import JSONExporter

console = Console()


def _load_ontology_from_file(path: Path) -> Ontology:
    """Load ontology from a JSON file (schema export)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Reconstruct ontology from dict - simplified
    o = Ontology(
        ontology_id=data.get("ontology_id", "default"),
        display_name=data.get("display_name", "Ontology"),
        version=data.get("version", "1.0"),
        description=data.get("description", ""),
    )
    for tid, ot_data in data.get("object_types", {}).items():
        props = {}
        for pname in ot_data.get("properties", []):
            props[pname] = Property(pname, pname, PropertyType.STRING)
        ot = ObjectType(
            type_id=tid,
            display_name=ot_data.get("display_name", tid),
            description=ot_data.get("description", ""),
            primary_key=ot_data.get("primary_key", ""),
            properties=props,
        )
        o.register_object_type(ot)
    for lid, lt_data in data.get("link_types", {}).items():
        lt = LinkType(
            link_id=lid,
            display_name=lt_data.get("display_name", lid),
            source_type=lt_data.get("source_type", ""),
            target_type=lt_data.get("target_type", ""),
            cardinality=Cardinality(lt_data.get("cardinality", "one_to_many")),
        )
        o.register_link_type(lt)
    return o


@click.group()
def main():
    """Foundry Ontology Open - Open-source Palantir Foundry Ontology implementation."""
    pass


@main.command()
@click.argument("name")
def init(name: str):
    """Scaffold a new ontology project."""
    base = Path(name)
    base.mkdir(parents=True, exist_ok=True)
    (base / "ontology.json").write_text(json.dumps({
        "ontology_id": name,
        "display_name": name,
        "version": "1.0.0",
        "description": f"Ontology: {name}",
        "object_types": {},
        "link_types": {},
        "action_types": {},
    }, indent=2))
    console.print(f"[green]Created ontology project: {base}[/green]")


@main.command()
@click.option("--path", "-p", default="ontology.json", help="Path to ontology JSON")
def validate(path: str):
    """Check ontology integrity."""
    p = Path(path)
    if not p.exists():
        console.print(f"[red]File not found: {p}[/red]")
        raise SystemExit(1)
    o = _load_ontology_from_file(p)
    errors = o.validate_ontology()
    if errors:
        for e in errors:
            console.print(f"[red]{e}[/red]")
        raise SystemExit(1)
    console.print("[green]Ontology is valid.[/green]")


@main.command()
@click.argument("type_id")
@click.option("--filter", "filters", multiple=True, help="Filter as key=value")
@click.option("--path", "-p", default="ontology.json")
@click.option("--data", "-d", default="data.db", help="SQLite database path")
def query(type_id: str, filters: tuple, path: str, data: str):
    """Query objects by type and optional filters."""
    o = _load_ontology_from_file(Path(path))
    store = ObjectStore(o, data)
    f = dict(x.split("=", 1) for x in filters) if filters else {}
    q = objects(store, type_id).filter(**f)
    results = q.all()
    table = Table(title=f"Query: {type_id}")
    if results:
        for k in results[0].properties:
            table.add_column(k)
        for r in results:
            table.add_row(*[str(r.properties.get(k, "")) for k in results[0].properties])
    console.print(table)
    console.print(f"[dim]Total: {len(results)}[/dim]")


@main.command()
@click.argument("format_type", type=click.Choice(["owl", "shacl", "json"]))
@click.argument("output", type=click.Path())
@click.option("--path", "-p", default="ontology.json")
def export(format_type: str, output: str, path: str):
    """Export ontology to OWL, SHACL, or JSON."""
    o = _load_ontology_from_file(Path(path))
    out_path = Path(output)
    if format_type == "owl":
        OWLExporter().export_to_file(o, str(out_path))
        console.print(f"[green]Exported OWL to {out_path}[/green]")
    elif format_type == "shacl":
        SHACLGenerator().generate_to_file(o, str(out_path))
        console.print(f"[green]Exported SHACL to {out_path}[/green]")
    elif format_type == "json":
        out_path.write_text(json.dumps(JSONExporter().export(o), indent=2), encoding="utf-8")
        console.print(f"[green]Exported JSON to {out_path}[/green]")


@main.command()
@click.option("--path", "-f", default="ontology.json")
def serve(path: str):
    """Start MCP server (stdio transport for Claude Desktop)."""
    try:
        from foundry_ontology.mcp.mcp_server import create_mcp_server
    except ImportError:
        console.print("[red]MCP requires: pip install mcp[/red]")
        raise SystemExit(1)
    o = _load_ontology_from_file(Path(path)) if Path(path).exists() else Ontology("default", "Default", "1.0")
    store = ObjectStore(o)
    mcp = create_mcp_server(o, store)
    console.print("[green]Starting MCP server (stdio)...[/green]")
    mcp.run()


@main.command()
@click.option("--path", "-p", default="ontology.json")
def summary(path: str):
    """Print ontology stats."""
    p = Path(path)
    if not p.exists():
        console.print(f"[red]File not found: {p}[/red]")
        raise SystemExit(1)
    o = _load_ontology_from_file(p)
    s = o.summary()
    table = Table(title="Ontology Summary")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    for k, v in s.items():
        table.add_row(k.replace("_", " ").title(), str(v))
    console.print(table)


if __name__ == "__main__":
    main()
