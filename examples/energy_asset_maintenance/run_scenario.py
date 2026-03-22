"""Run the $340K payment scenario from the article."""

import sys
from pathlib import Path

# Ensure package root is on path
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Use local imports when run from this directory
try:
    from examples.energy_asset_maintenance.ontology_definition import build_energy_ontology
    from examples.energy_asset_maintenance.sample_data import seed_data
except ImportError:
    from ontology_definition import build_energy_ontology
    from sample_data import seed_data
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.query_engine import objects
from foundry_ontology.engine.audit_log import AuditLog
from foundry_ontology.engine.action_executor import ActionExecutor
from foundry_ontology.export.owl_exporter import OWLExporter
from foundry_ontology.export.shacl_generator import SHACLGenerator

console = Console()


def main():
    console.print(Panel.fit("[bold]Energy Asset Maintenance — Foundry Ontology Open[/bold]", border_style="green"))

    # 1. Load ontology and seed data
    ontology = build_energy_ontology()
    store = ObjectStore(ontology)
    seed_data(store)
    console.print("[green]OK[/green] Loaded ontology and seed data")

    # 2. Query: high-risk assets (active + has vibration readings)
    console.print("\n[bold]Query: Active assets with vibration readings[/bold]")
    results = (
        objects(store, "Asset")
        .filter(status="active")
        .navigate("has_sensor_readings")
        .filter(reading_type="vibration")
        .all()
    )
    table = Table()
    # Results after navigate are SensorReading objects
    cols = list(results[0].properties.keys())[:4] if results else ["reading_id", "value"]
    for c in cols:
        table.add_column(c)
    for r in results[:5]:
        table.add_row(*[str(r.properties.get(c, "")) for c in cols])
    console.print(table)
    console.print(f"[dim]Total: {len(results)}[/dim]")

    # 3. Execute EscalateAsset — success
    audit = AuditLog()
    executor = ActionExecutor(ontology, store, audit)

    def resolver(action_id, params):
        if action_id == "EscalateAsset":
            inst = store.get(params.get("asset_id", ""))
            return {"asset": inst.properties if inst else {}}
        return {}

    result = executor.execute("EscalateAsset", {"asset_id": "A001", "priority": "MEDIUM"}, "engineer1", context_resolver=resolver)
    if result.success:
        console.print("\n[green]OK EscalateAsset on A001: SUCCESS[/green]")
    else:
        console.print(f"\n[red]FAIL EscalateAsset: {result.validation_errors}[/red]")

    # 4. Execute EscalateAsset on decommissioned — FAIL
    result2 = executor.execute("EscalateAsset", {"asset_id": "A010", "priority": "LOW"}, "engineer1", context_resolver=resolver)
    if not result2.success:
        console.print(f"\n[yellow]OK EscalateAsset on decommissioned A010: Correctly REJECTED[/yellow]")
        console.print(f"  [dim]{result2.validation_errors}[/dim]")

    # 5. Export OWL and SHACL
    export_dir = Path(__file__).parent / "exported"
    export_dir.mkdir(exist_ok=True)
    OWLExporter().export_to_file(ontology, str(export_dir / "energy_ontology.ttl"))
    SHACLGenerator().generate_to_file(ontology, str(export_dir / "energy_shacl.ttl"))
    console.print(f"\n[green]OK Exported OWL -> {export_dir / 'energy_ontology.ttl'}[/green]")
    console.print(f"[green]OK Exported SHACL -> {export_dir / 'energy_shacl.ttl'}[/green]")

    # 6. Audit summary
    entries = audit.query()
    console.print(f"\n[bold]Audit log: {len(entries)} entries[/bold]")
    for e in entries[:3]:
        status = "[green]OK[/green]" if e.success else "[red]FAIL[/red]"
        console.print(f"  {status} {e.action_type_id} by {e.executed_by}")

    console.print("\n[dim]Scenario complete.[/dim]")


if __name__ == "__main__":
    main()
