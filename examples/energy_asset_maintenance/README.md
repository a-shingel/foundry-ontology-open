# Energy Asset Maintenance Case Study

This example demonstrates the full ontology from the Palantir Foundry article:
- **Object Types**: Asset, MaintenanceEvent, Technician, SensorReading, WorkOrder
- **Link Types**: Asset→SensorReadings, Asset→MaintenanceEvents, WorkOrder→Technician, WorkOrder→Asset
- **Action Types**: CreateWorkOrder, EscalateAsset, CloseMaintenanceEvent
- **Functions**: get_high_risk_assets
- **Interfaces**: Inspectable (Asset, Pipeline)

Run the scenario:
```bash
cd examples/energy_asset_maintenance
python run_scenario.py
```
