"""Seed data for human services example."""

from foundry_ontology.engine.object_store import ObjectStore


def seed_data(store: ObjectStore) -> None:
    store.create("Client", {"client_id": "C1", "name": "Jane Doe", "age": 35, "income": 25000.0}, "system")
    store.create("Case", {"case_id": "CS1", "status": "pending"}, "system")
    store.create("Benefit", {"benefit_id": "B1", "benefit_type": "housing", "income_threshold": 30000.0}, "system")
    store.create_link("client_cases", "C1", "CS1")
    store.create_link("case_benefits", "CS1", "B1")
