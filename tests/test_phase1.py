"""
tests/test_phase1.py — Pytest Verification Suite for Phase 1 Core Spine
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from jarvis.config import config, DynamicSystemConfig
from jarvis.system.spec_loader import HardwareAuditor, audit_hardware
from jarvis.main import app

def test_dynamic_config_paths():
    """Verify that all paths are dynamically resolved and directories exist."""
    assert isinstance(config.root_dir, Path)
    assert isinstance(config.data_dir, Path)
    assert isinstance(config.logs_dir, Path)
    assert isinstance(config.backups_dir, Path)
    assert isinstance(config.vault_dir, Path)
    assert isinstance(config.user_home, Path)

    assert config.data_dir.exists()
    assert config.logs_dir.exists()
    assert config.backups_dir.exists()
    assert config.vault_dir.exists()

def test_dynamic_config_to_dict():
    """Verify config dictionary serialization and default dynamic values."""
    config_dict = config.to_dict()
    required_keys = [
        "root_dir", "data_dir", "logs_dir", "backups_dir", "vault_dir",
        "user_home", "host_ip", "lan_ip", "fastapi_port", "fastapi_endpoint",
        "ollama_endpoint", "n8n_endpoint", "cpu_topology", "ram_total_gb",
        "ram_available_gb", "ram_ceiling_gb"
    ]
    for key in required_keys:
        assert key in config_dict, f"Missing key: {key}"

    assert config_dict["fastapi_port"] == 8765
    assert "http://" in config_dict["fastapi_endpoint"]

def test_hardware_auditor():
    """Verify hardware auditor probes CPU, GPU, Memory, and Accelerators correctly."""
    auditor = HardwareAuditor()
    audit_data = auditor.audit()

    assert "system_os" in audit_data
    assert "cpu" in audit_data
    assert "gpu" in audit_data
    assert "memory" in audit_data
    assert "accelerators" in audit_data

    assert audit_data["cpu"]["logical_cores"] >= 1
    assert audit_data["memory"]["total_ram_gb"] > 0
    assert audit_data["memory"]["ram_ceiling_gb"] >= 4.0
    assert isinstance(audit_data["gpu"], list)

def test_fastapi_spine_endpoints():
    """Test core FastAPI spine API endpoints via TestClient."""
    client = TestClient(app)

    # Test Root
    res_root = client.get("/")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert data_root["status"] == "online"
    assert "J.A.R.V.I.S." in data_root["system"]

    # Test Health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["status"] == "healthy"
    assert "uptime_seconds" in data_health
    assert "process_memory_mb" in data_health

    # Test Specs API
    res_specs = client.get("/api/v1/system/specs")
    assert res_specs.status_code == 200
    data_specs = res_specs.json()
    assert "cpu" in data_specs
    assert "memory" in data_specs

    # Test Config API
    res_config = client.get("/api/v1/system/config")
    assert res_config.status_code == 200
    data_cfg = res_config.json()
    assert data_cfg["fastapi_port"] == 8765
