"""Energy company ontology from the Foundry article."""

from foundry_ontology.core import (
    Ontology,
    ObjectType,
    Property,
    SharedProperty,
    LinkType,
    Cardinality,
    ActionType,
    ActionParameter,
    ValidationRule,
    ActionEffect,
    OntologyFunction,
    Interface,
)
from foundry_ontology.core.data_types import PropertyType


def build_energy_ontology() -> Ontology:
    """Build the energy asset maintenance ontology."""
    o = Ontology(
        ontology_id="energy_assets",
        display_name="Energy Asset Maintenance",
        version="1.0",
        description="Ontology for physical asset management in energy companies",
    )

    # Object Types
    asset = ObjectType(
        type_id="Asset",
        display_name="Physical Asset",
        description="A physical asset (well, pump, compressor)",
        primary_key="asset_id",
        properties={
            "asset_id": Property("asset_id", "Asset ID", PropertyType.STRING, required=True, is_primary_key=True),
            "name": Property("name", "Name", PropertyType.STRING, required=True),
            "asset_type": Property("asset_type", "Type", PropertyType.STRING, options=["well", "pump", "compressor", "pipeline"]),
            "location": Property("location", "Location", PropertyType.STRING),
            "status": Property("status", "Status", PropertyType.STRING, options=["active", "inactive", "decommissioned", "escalated"]),
        },
        interfaces=["Inspectable"],
    )
    o.register_object_type(asset)

    sensor = ObjectType(
        type_id="SensorReading",
        display_name="Sensor Reading",
        description="A sensor reading from an asset",
        primary_key="reading_id",
        properties={
            "reading_id": Property("reading_id", "Reading ID", PropertyType.STRING, required=True, is_primary_key=True),
            "reading_type": Property("reading_type", "Type", PropertyType.STRING, options=["vibration", "temperature", "pressure"]),
            "value": Property("value", "Value", PropertyType.FLOAT),
            "timestamp": Property("timestamp", "Timestamp", PropertyType.DATETIME),
        },
    )
    o.register_object_type(sensor)

    tech = ObjectType(
        type_id="Technician",
        display_name="Technician",
        description="Maintenance technician",
        primary_key="tech_id",
        properties={
            "tech_id": Property("tech_id", "Technician ID", PropertyType.STRING, required=True, is_primary_key=True),
            "name": Property("name", "Name", PropertyType.STRING),
            "certification": Property("certification", "Certification", PropertyType.STRING, options=["basic", "advanced", "senior"]),
        },
    )
    o.register_object_type(tech)

    event = ObjectType(
        type_id="MaintenanceEvent",
        display_name="Maintenance Event",
        description="A maintenance event for an asset",
        primary_key="event_id",
        properties={
            "event_id": Property("event_id", "Event ID", PropertyType.STRING, required=True, is_primary_key=True),
            "event_type": Property("event_type", "Type", PropertyType.STRING, options=["scheduled", "emergency", "inspection"]),
            "status": Property("status", "Status", PropertyType.STRING, options=["scheduled", "completed", "overdue"]),
            "scheduled_date": Property("scheduled_date", "Scheduled", PropertyType.DATE),
            "sign_off_by": Property("sign_off_by", "Sign-off", PropertyType.STRING),
        },
    )
    o.register_object_type(event)

    wo = ObjectType(
        type_id="WorkOrder",
        display_name="Work Order",
        description="A work order for maintenance",
        primary_key="wo_id",
        properties={
            "wo_id": Property("wo_id", "Work Order ID", PropertyType.STRING, required=True, is_primary_key=True),
            "priority": Property("priority", "Priority", PropertyType.STRING, options=["LOW", "MEDIUM", "CRITICAL"]),
            "status": Property("status", "Status", PropertyType.STRING, options=["open", "in_progress", "closed"]),
        },
    )
    o.register_object_type(wo)

    pipeline = ObjectType(
        type_id="Pipeline",
        display_name="Pipeline",
        description="A pipeline asset",
        primary_key="pipeline_id",
        properties={
            "pipeline_id": Property("pipeline_id", "Pipeline ID", PropertyType.STRING, required=True, is_primary_key=True),
            "name": Property("name", "Name", PropertyType.STRING),
            "inspection_date": Property("inspection_date", "Inspection Date", PropertyType.DATE),
        },
        interfaces=["Inspectable"],
    )
    o.register_object_type(pipeline)

    # Link Types
    o.register_link_type(LinkType("has_sensor_readings", "Has Sensor Readings", source_type="Asset", target_type="SensorReading", cardinality=Cardinality.ONE_TO_MANY))
    o.register_link_type(LinkType("has_maintenance_events", "Has Maintenance Events", source_type="Asset", target_type="MaintenanceEvent", cardinality=Cardinality.ONE_TO_MANY))
    o.register_link_type(LinkType("work_order_asset", "Work Order Asset", source_type="WorkOrder", target_type="Asset", cardinality=Cardinality.ONE_TO_ONE))
    o.register_link_type(LinkType("work_order_technician", "Work Order Technician", source_type="WorkOrder", target_type="Technician", cardinality=Cardinality.ONE_TO_ONE))

    # Interface
    iface = Interface("Inspectable", "Inspectable", required_properties=[Property("inspection_date", "Inspection Date", PropertyType.DATE)])
    o.register_interface(iface)
    asset.interfaces = ["Inspectable"]
    pipeline.interfaces = ["Inspectable"]
    asset.add_property(Property("inspection_date", "Inspection Date", PropertyType.DATE))

    # Action Types
    o.register_action_type(ActionType(
        action_id="EscalateAsset",
        display_name="Escalate Asset",
        description="Escalate an asset for maintenance",
        parameters=[
            ActionParameter("asset_id", PropertyType.STRING),
            ActionParameter("priority", PropertyType.STRING, options=["LOW", "MEDIUM", "CRITICAL"]),
        ],
        validation_rules=[
            ValidationRule("r1", "asset.get('status') != 'decommissioned'", "Cannot escalate decommissioned asset"),
        ],
        effects=[ActionEffect("edit_object", "Asset", {"status": "escalated"})],
        required_roles=["Engineer", "SeniorEngineer", "PlantManager"],
    ))

    o.register_action_type(ActionType(
        action_id="CreateWorkOrder",
        display_name="Create Work Order",
        parameters=[
            ActionParameter("asset_id", PropertyType.STRING),
            ActionParameter("tech_id", PropertyType.STRING),
            ActionParameter("priority", PropertyType.STRING, options=["LOW", "MEDIUM", "CRITICAL"]),
        ],
        validation_rules=[],
        effects=[],
        required_roles=["Engineer", "Admin"],
    ))

    o.register_action_type(ActionType(
        action_id="CloseMaintenanceEvent",
        display_name="Close Maintenance Event",
        parameters=[
            ActionParameter("event_id", PropertyType.STRING),
            ActionParameter("sign_off_by", PropertyType.STRING),
        ],
        validation_rules=[
            ValidationRule("r1", "'sign_off_by' in context and context.get('sign_off_by')", "Requires sign_off_by field"),
        ],
        effects=[ActionEffect("edit_object", "MaintenanceEvent", {"status": "completed"})],
        required_roles=["Technician", "Engineer"],
    ))

    # Function
    def get_high_risk_assets(vibration_threshold: float, days_since_maintenance: int):
        return ["asset_1", "asset_2"]  # Simplified

    o.register_function(OntologyFunction(
        function_id="get_high_risk_assets",
        display_name="Get High Risk Assets",
        description="Find assets with high vibration and no recent maintenance",
        input_types={"vibration_threshold": PropertyType.FLOAT, "days_since_maintenance": PropertyType.INTEGER},
        output_type="list",
        implementation=get_high_risk_assets,
    ))

    return o
