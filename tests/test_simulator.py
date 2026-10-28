"""Tests for deterministic fleet simulator."""

import pytest
from simulator.fleet_simulator import FleetSimulator


def test_fleet_simulator_determinism():
    sim1 = FleetSimulator(seed=42)
    batch1 = sim1.step(timestamp=1000.0, hour=9.0)

    sim2 = FleetSimulator(seed=42)
    batch2 = sim2.step(timestamp=1000.0, hour=9.0)

    # Identical seed must yield identical outputs
    for item1, item2 in zip(batch1, batch2):
        assert item1["payload"] == item2["payload"]
        assert item1["is_simulated"] is True


def test_fleet_simulator_valid_schema():
    sim = FleetSimulator(seed=123)
    batch = sim.step(timestamp=1000.0, hour=18.0)

    assert len(batch) == 5  # C2 through C6
    for item in batch:
        assert item["device_id"] == "simulator"
        p = item["payload"]
        assert p["coach_id"] in ["C2", "C3", "C4", "C5", "C6"]
        assert p["people_in"] >= 0
        assert p["people_out"] >= 0
