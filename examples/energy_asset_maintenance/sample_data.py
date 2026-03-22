"""Seed data for energy asset example."""

from datetime import datetime, timedelta
from foundry_ontology.engine.object_store import ObjectStore


def seed_data(store: ObjectStore) -> None:
    """Seed the store with sample assets, readings, technicians, events, work orders."""
    base = datetime.now() - timedelta(days=60)

    # 10 assets
    for i in range(1, 11):
        store.create("Asset", {
            "asset_id": f"A{i:03d}",
            "name": f"Pump {i}" if i <= 5 else f"Well {i}",
            "asset_type": "pump" if i <= 5 else "well",
            "location": "North" if i % 2 else "South",
            "status": "decommissioned" if i == 10 else "active",
        }, created_by="system")

    # 20 sensor readings
    for i in range(1, 21):
        store.create("SensorReading", {
            "reading_id": f"R{i:03d}",
            "reading_type": "vibration" if i % 3 == 0 else "temperature",
            "value": 5.0 + (i % 10),
            "timestamp": base + timedelta(days=i),
        }, created_by="system")

    # Link readings to assets
    for i in range(1, 21):
        store.create_link("has_sensor_readings", f"A{(i % 10) + 1:03d}", f"R{i:03d}")

    # 5 technicians
    for i in range(1, 6):
        store.create("Technician", {
            "tech_id": f"T{i:03d}",
            "name": f"Tech {i}",
            "certification": "senior" if i == 1 else "advanced",
        }, created_by="system")

    # 10 maintenance events
    for i in range(1, 11):
        store.create("MaintenanceEvent", {
            "event_id": f"E{i:03d}",
            "event_type": "scheduled" if i % 2 else "inspection",
            "status": "completed" if i <= 3 else "scheduled",
            "scheduled_date": (base + timedelta(days=i * 5)).date(),
        }, created_by="system")
        store.create_link("has_maintenance_events", f"A{(i % 10) + 1:03d}", f"E{i:03d}")

    # 5 work orders
    for i in range(1, 6):
        store.create("WorkOrder", {
            "wo_id": f"WO{i:03d}",
            "priority": "CRITICAL" if i == 1 else "MEDIUM",
            "status": "open" if i <= 3 else "closed",
        }, created_by="system")
        store.create_link("work_order_asset", f"WO{i:03d}", f"A{i:03d}")
        store.create_link("work_order_technician", f"WO{i:03d}", f"T{i:03d}")
