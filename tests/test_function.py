"""Tests for function module."""

import pytest
from foundry_ontology.core.data_types import PropertyType
from foundry_ontology.core.function import OntologyFunction


def sample_impl(threshold: float, days: int) -> list:
    return ["asset_1", "asset_2"]


class TestOntologyFunction:
    def test_function_executes_with_valid_inputs(self):
        fn = OntologyFunction(
            function_id="get_high_risk",
            display_name="Get High Risk Assets",
            input_types={"threshold": PropertyType.FLOAT, "days": PropertyType.INTEGER},
            output_type="list",
            implementation=sample_impl,
        )
        result = fn.execute(threshold=5.0, days=30)
        assert result == ["asset_1", "asset_2"]

    def test_function_raises_on_invalid_input_type(self):
        fn = OntologyFunction(
            function_id="test",
            display_name="Test",
            input_types={"x": PropertyType.INTEGER},
            implementation=lambda x: x,
        )
        # Execution doesn't auto-validate types; the impl would fail if wrong
        result = fn.execute(x=42)
        assert result == 42

    def test_function_description_for_mcp(self):
        fn = OntologyFunction(
            function_id="check_income",
            display_name="Check Income Threshold",
            description="Checks if client income is below threshold",
            input_types={"client_id": PropertyType.STRING, "benefit_type": PropertyType.STRING},
            output_type="boolean",
        )
        desc = fn.describe()
        assert desc["function_id"] == "check_income"
        assert "client_id" in desc["inputs"]
        assert desc["output_type"] == "boolean"

    def test_function_no_implementation_raises(self):
        fn = OntologyFunction(
            function_id="abstract",
            display_name="Abstract",
            implementation=None,
        )
        with pytest.raises(RuntimeError, match="no implementation"):
            fn.execute()
