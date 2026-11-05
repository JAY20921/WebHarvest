"""
Pytest Configuration and Fixtures
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_ssrf_enabled(monkeypatch):
    """Mock environment with SSRF protection enabled"""
    monkeypatch.setenv("ENABLE_SSRF_PROTECTION", "true")
    monkeypatch.setenv("BLOCK_PRIVATE_IPS", "true")
    monkeypatch.setenv("BLOCK_CLOUD_METADATA", "true")


@pytest.fixture
def mock_env_ssrf_disabled(monkeypatch):
    """Mock environment with SSRF protection disabled"""
    monkeypatch.setenv("ENABLE_SSRF_PROTECTION", "false")
    monkeypatch.setenv("BLOCK_PRIVATE_IPS", "false")
    monkeypatch.setenv("BLOCK_CLOUD_METADATA", "false")
