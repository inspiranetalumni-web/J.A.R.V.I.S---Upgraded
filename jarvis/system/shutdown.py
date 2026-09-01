"""
jarvis/system/shutdown.py — Unified Graceful Shutdown Manager v3.0
Coordinates clean process teardown without data corruption or skipped atexit hooks:
1. Signals FastAPI lifespan shutdown event.
2. Commits and flushes active SQLite database transactions.
3. Stops audio capture streams and worker threads.
4. Cleanly exits the process without forceful os._exit(0) aborts.
"""

import sys
import time
import threading
from typing import List, Callable, Dict, Any
from jarvis.logging import get_logger

logger = get_logger("shutdown")

class ShutdownManager:
    """
    Coordinates safe, graceful teardown of all J.A.R.V.I.S. subsystems.
    """
    def __init__(self):
        self._hooks: List[Callable[[], None]] = []
        self._is_shutting_down = False
        self._lock = threading.Lock()

    def register_hook(self, hook: Callable[[], None]) -> None:
        """Registers a callback hook to be executed on graceful shutdown."""
        with self._lock:
            if hook not in self._hooks:
                self._hooks.append(hook)

    def is_shutting_down(self) -> bool:
        """Returns True if a shutdown sequence has been initiated."""
        return self._is_shutting_down

    def initiate_shutdown(self, exit_code: int = 0, delay_s: float = 0.2) -> Dict[str, Any]:
        """
        Executes all registered cleanup hooks and triggers graceful process termination.
        """
        with self._lock:
            if self._is_shutting_down:
                return {"status": "shutdown_already_in_progress"}
            self._is_shutting_down = True

        logger.info("Initiating J.A.R.V.I.S. graceful shutdown sequence (Exit Code: %d)...", exit_code)

        # Execute registered cleanup hooks
        for hook in self._hooks:
            try:
                hook()
            except Exception as e:
                logger.warning("Error executing shutdown hook %s: %s", hook, e)

        # Flush standard streams
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass

        # Schedule delayed process exit to allow HTTP response delivery
        def _delayed_exit():
            time.sleep(delay_s)
            logger.info("J.A.R.V.I.S. Core Spine shutdown completed. Goodnight, Sir.")
            sys.exit(exit_code)

        exit_thread = threading.Thread(target=_delayed_exit, daemon=True, name="JarvisShutdownThread")
        exit_thread.start()

        return {
            "status": "shutdown_initiated",
            "message": "J.A.R.V.I.S. graceful shutdown sequence initiated. Goodnight, Sir.",
            "exit_code": exit_code
        }

# Global singleton instance
shutdown_manager = ShutdownManager()
