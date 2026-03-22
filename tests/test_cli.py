"""Tests for CLI."""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from foundry_ontology.cli import main


runner = CliRunner()


class TestCLI:
    def test_init_creates_project(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "my_ontology"
            result = runner.invoke(main, ["init", str(p)])
            assert result.exit_code == 0
            assert (p / "ontology.json").exists()

    def test_validate_valid_ontology(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({
                "ontology_id": "t",
                "display_name": "T",
                "version": "1.0",
                "object_types": {"Asset": {"properties": ["id"], "primary_key": "id"}},
                "link_types": {},
            }, f)
            path = f.name
        try:
            result = runner.invoke(main, ["validate", "--path", path])
            assert result.exit_code == 0
        finally:
            Path(path).unlink()

    def test_summary(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({
                "ontology_id": "t",
                "display_name": "T",
                "version": "1.0",
                "object_types": {"A": {"properties": ["id"], "primary_key": "id"}, "B": {"properties": ["id"], "primary_key": "id"}},
                "link_types": {"l1": {"source_type": "A", "target_type": "B", "cardinality": "one_to_many"}},
            }, f)
            path = f.name
        try:
            result = runner.invoke(main, ["summary", "--path", path])
            assert result.exit_code == 0
            assert "2" in result.output or "Object" in result.output
        finally:
            Path(path).unlink()
