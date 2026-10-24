"""
Tests for Auralis Autonomous Pipeline Engine
"""

import os
import pytest
from src.engine.autonomous_pipeline import AuralisAutonomousPipeline

def test_autonomous_pipeline_initialization():
    pipeline = AuralisAutonomousPipeline(
        parallel_workers=3,
        enable_airllm=False
    )
    assert pipeline.parallel_workers == 3
    assert pipeline.enable_airllm is False
    assert os.path.exists(pipeline.inventory_db)

def test_autonomous_pipeline_audit_depth():
    pipeline = AuralisAutonomousPipeline()
    audit = pipeline.audit_library_depth()
    assert "depth_violations_count" in audit
    assert audit["depth_violations_count"] == 0
    assert "language_breakdown" in audit
    assert "English" in audit["language_breakdown"]
    assert "Hindi" in audit["language_breakdown"]
