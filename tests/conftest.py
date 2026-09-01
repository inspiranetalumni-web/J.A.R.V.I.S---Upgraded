"""
tests/conftest.py — Shared Pytest fixtures for J.A.R.V.I.S. Test Suites
"""

import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Ensure a QApplication instance is active for headless / offscreen Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["pytest", "-platform", "offscreen"])
    yield app
