"""Tests for audit_log module."""

import tempfile
from datetime import datetime, timedelta

import pytest
from foundry_ontology.engine.audit_log import AuditEntry, AuditLog


class TestAuditLog:
    def test_append_and_retrieve(self):
        log = AuditLog()
        entry = AuditEntry(
            entry_id="",
            timestamp=datetime.now(),
            action_type_id="CreateWorkOrder",
            executed_by="user1",
            parameters={"asset_id": "A1"},
            effects=[],
            success=True,
        )
        eid = log.append(entry)
        assert eid
        retrieved = log.get(eid)
        assert retrieved is not None
        assert retrieved.action_type_id == "CreateWorkOrder"
        assert retrieved.executed_by == "user1"

    def test_query_by_action_type(self):
        log = AuditLog()
        log.append(
            AuditEntry(
                entry_id="", timestamp=datetime.now(), action_type_id="Create", executed_by="u1",
                parameters={}, effects=[], success=True,
            )
        )
        log.append(
            AuditEntry(
                entry_id="", timestamp=datetime.now(), action_type_id="Delete", executed_by="u1",
                parameters={}, effects=[], success=True,
            )
        )
        results = log.query(action_type_id="Create")
        assert len(results) == 1
        assert results[0].action_type_id == "Create"

    def test_query_by_user(self):
        log = AuditLog()
        log.append(
            AuditEntry(
                entry_id="", timestamp=datetime.now(), action_type_id="A1", executed_by="alice",
                parameters={}, effects=[], success=True,
            )
        )
        log.append(
            AuditEntry(
                entry_id="", timestamp=datetime.now(), action_type_id="A2", executed_by="bob",
                parameters={}, effects=[], success=True,
            )
        )
        results = log.query(user="alice")
        assert len(results) == 1
        assert results[0].executed_by == "alice"

    def test_query_by_date_range(self):
        log = AuditLog()
        now = datetime.now()
        log.append(
            AuditEntry(
                entry_id="", timestamp=now - timedelta(hours=2), action_type_id="A1",
                executed_by="u1", parameters={}, effects=[], success=True,
            )
        )
        log.append(
            AuditEntry(
                entry_id="", timestamp=now, action_type_id="A2",
                executed_by="u1", parameters={}, effects=[], success=True,
            )
        )
        results = log.query(after=now - timedelta(hours=1))
        assert len(results) == 1

    def test_export_csv(self):
        log = AuditLog()
        log.append(
            AuditEntry(
                entry_id="", timestamp=datetime.now(), action_type_id="Test",
                executed_by="u1", parameters={}, effects=[], success=True,
            )
        )
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            log.export_csv(path)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert "action_type_id" in content or "Test" in content
        finally:
            import os
            os.unlink(path)
