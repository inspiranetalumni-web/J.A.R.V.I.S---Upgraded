"""
tests/conftest.py — Shared Pytest fixtures for J.A.R.V.I.S. Test Suites
Provides shared offscreen QApplication, isolated audio managers, and environment cleanup.
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

@pytest.fixture
def clean_audio_manager():
    """Provides an isolated AudioManager instance with clean thread teardown."""
    from jarvis.audio.manager import AudioManager
    manager = AudioManager()
    yield manager
    try:
        manager.stop_mic_listener()
    except Exception:
        pass
