"""
CLI entry point for running Control Center:
python -m jarvis.control_center
"""

import sys
from jarvis.control_center.app import launch_control_center

if __name__ == "__main__":
    sys.exit(launch_control_center())
