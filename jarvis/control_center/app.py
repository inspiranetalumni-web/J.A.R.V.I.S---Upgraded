"""
jarvis/control_center/app.py — Control Center Application Launcher
Instantiates QApplication with Stark Horizon theme and displays JarvisControlCenterWindow.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from jarvis.config import config
from jarvis.control_center.main_window import JarvisControlCenterWindow

def launch_control_center(endpoint: str = None) -> int:
    """
    Launches the J.A.R.V.I.S Control Center desktop shell.
    Respects config.enable_control_center feature flag.
    """
    if not config.enable_control_center:
        print("[CONTROL CENTER] Feature flag 'enable_control_center' is disabled. Skipping launch.")
        return 0

    endpoint = endpoint or config.to_dict()["fastapi_endpoint"]

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication.instance()
    is_external_app = app is not None
    if not is_external_app:
        app = QApplication(sys.argv)

    app.setApplicationName("J.A.R.V.I.S Control Center")
    app.setOrganizationName("Stark Industries Sovereign OS")

    window = JarvisControlCenterWindow(endpoint=endpoint)
    window.show()

    if not is_external_app:
        return app.exec()
    return 0

if __name__ == "__main__":
    sys.exit(launch_control_center())
