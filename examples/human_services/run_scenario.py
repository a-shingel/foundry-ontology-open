"""Run eligibility determination scenario."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.console import Console
from examples.human_services.ontology_definition import build_human_services_ontology
from examples.human_services.sample_data import seed_data
from foundry_ontology.engine.object_store import ObjectStore
from foundry_ontology.engine.action_executor import ActionExecutor
from foundry_ontology.engine.audit_log import AuditLog

console = Console()

def main():
    ontology = build_human_services_ontology()
    store = ObjectStore(ontology)
    seed_data(store)
    audit = AuditLog()
    executor = ActionExecutor(ontology, store, audit)

    def resolver(aid, params):
        if aid == "SubmitApplication":
            c = store.get(params.get("client_id", ""))
            return {"client": c.properties if c else {}}
        return {}

    r = executor.execute("SubmitApplication", {"client_id": "C1", "benefit_type": "housing"}, "worker1", context_resolver=resolver)
    console.print("SubmitApplication:", "OK" if r.success else r.validation_errors)

if __name__ == "__main__":
    main()
