"""Human services benefits eligibility ontology."""

from foundry_ontology.core import (
    Ontology, ObjectType, Property, LinkType, Cardinality,
    ActionType, ActionParameter, ValidationRule,
)
from foundry_ontology.core.data_types import PropertyType


def build_human_services_ontology() -> Ontology:
    o = Ontology("human_services", "Benefits Eligibility", "1.0")
    o.register_object_type(ObjectType(
        type_id="Client",
        display_name="Client",
        primary_key="client_id",
        properties={
            "client_id": Property("client_id", "ID", PropertyType.STRING, required=True, is_primary_key=True),
            "name": Property("name", "Name", PropertyType.STRING),
            "age": Property("age", "Age", PropertyType.INTEGER),
            "income": Property("income", "Income", PropertyType.FLOAT),
        },
    ))
    o.register_object_type(ObjectType(
        type_id="Case",
        display_name="Case",
        primary_key="case_id",
        properties={
            "case_id": Property("case_id", "ID", PropertyType.STRING, required=True, is_primary_key=True),
            "status": Property("status", "Status", PropertyType.STRING),
        },
    ))
    o.register_object_type(ObjectType(
        type_id="Benefit",
        display_name="Benefit",
        primary_key="benefit_id",
        properties={
            "benefit_id": Property("benefit_id", "ID", PropertyType.STRING, required=True, is_primary_key=True),
            "benefit_type": Property("benefit_type", "Type", PropertyType.STRING),
            "income_threshold": Property("income_threshold", "Income Threshold", PropertyType.FLOAT),
        },
    ))
    o.register_link_type(LinkType("client_cases", "Client Cases", source_type="Client", target_type="Case", cardinality=Cardinality.ONE_TO_MANY))
    o.register_link_type(LinkType("case_benefits", "Case Benefits", source_type="Case", target_type="Benefit", cardinality=Cardinality.ONE_TO_MANY))
    o.register_action_type(ActionType(
        action_id="SubmitApplication",
        parameters=[ActionParameter("client_id", PropertyType.STRING), ActionParameter("benefit_type", PropertyType.STRING)],
        validation_rules=[ValidationRule("r1", "client.get('age', 0) >= 18", "Client must be 18+")],
        effects=[],
        required_roles=["CaseWorker"],
    ))
    o.register_action_type(ActionType(
        action_id="ApproveBenefit",
        parameters=[ActionParameter("case_id", PropertyType.STRING)],
        validation_rules=[],
        effects=[],
        required_roles=["Approver"],
    ))
    return o
