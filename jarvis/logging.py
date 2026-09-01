"""
jarvis/logging.py — Structured Rotating Logging Infrastructure v3.0
Provides enterprise-grade rotating file logging to data/logs/jarvis.log (10MB max, 5 backups)
and color-formatted console stream output with microsecond timestamps and namespace tagging.
"""

import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from jarvis.config import config

LOG_FILE = config.logs_dir / "jarvis.log"
LOG_FORMAT = "[%(asctime)s.%(msecs)03d] [%(levelname)-7s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_is_configured = False

def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Initializes root 'jarvis' logger with rotating file and console handlers.
    Thread-safe and idempotent.
    """
    global _is_configured
    logger = logging.getLogger("jarvis")

    if _is_configured:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    # Ensure logs directory exists
    config.logs_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. Rotating File Handler (10MB per file, 5 backup generations)
    try:
        file_handler = RotatingFileHandler(
            filename=str(LOG_FILE),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"[LOGGING WARNING] Could not initialize file handler at {LOG_FILE}: {e}\n")

    # 2. Console Stream Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _is_configured = True
    logger.info("J.A.R.V.I.S. Structured Logging Subsystem initialized (Log File: %s)", LOG_FILE)
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Returns namespaced child logger under 'jarvis.<name>'.
    """
    if not _is_configured:
        setup_logging()
    return logging.getLogger(f"jarvis.{name}")

# Root module logger
logger = get_logger("core")
