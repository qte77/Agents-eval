"""
Tests for the time_taken metric.

This module verifies that the time_taken metric correctly computes the elapsed
time between two timestamps, ensuring accurate measurement of agent execution
duration for evaluation purposes.
"""

import asyncio
import time

import pytest

from app.evals.metrics import time_taken


@pytest.mark.asyncio
async def test_time_taken_metric():
    """Scenario: Calculate time taken for agent execution"""

    # Given: Start and end timestamps
    start_time = time.perf_counter()
    await asyncio.sleep(0.1)
    end_time = time.perf_counter()

    # When: Calculating time taken
    result = time_taken(start_time, end_time)

    # Then: Verify correct duration calculation
    assert result == pytest.approx(0.1, abs=0.05)
