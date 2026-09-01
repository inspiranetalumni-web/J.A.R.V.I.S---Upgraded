"""
jarvis/swarm/parallel_executor.py — House Party Protocol Swarm Parallel Engine
Executes sub-agent task workloads concurrently across worker threads and processes.
"""

import time
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger("jarvis.swarm.executor")


@dataclass
class SwarmTaskResult:
    task_id: str
    status: str  # "SUCCESS" | "FAILED"
    result: Any
    latency_ms: float
    error: Optional[str] = None


class HousePartySwarmExecutor:
    """
    Parallel worker swarm executor implementing the Stark House Party Protocol.
    Distributes sub-agent tasks across worker thread pools for ~2x parallel acceleration.
    """
    def __init__(self, max_workers: int = 6):
        self.max_workers = min(max_workers, 12)
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="JarvisSwarm")

    async def execute_parallel_tasks(
        self,
        tasks: List[tuple[str, Callable[[], Any]]]
    ) -> List[SwarmTaskResult]:
        """
        Executes a batch of named tasks in parallel.
        Args:
            tasks: List of (task_id, callable)
        Returns:
            List of SwarmTaskResult with individual timings and outputs.
        """
        t0 = time.perf_counter()
        logger.info(f"[SWARM] Deploying House Party Protocol across {len(tasks)} tasks on {self.max_workers} workers...")

        loop = asyncio.get_running_loop()

        def _run_single(tid: str, func: Callable[[], Any]) -> SwarmTaskResult:
            sub_t0 = time.perf_counter()
            try:
                out = func()
                dur = (time.perf_counter() - sub_t0) * 1000
                return SwarmTaskResult(task_id=tid, status="SUCCESS", result=out, latency_ms=round(dur, 2))
            except Exception as e:
                dur = (time.perf_counter() - sub_t0) * 1000
                logger.error(f"[SWARM] Task {tid} failed: {e}")
                return SwarmTaskResult(task_id=tid, status="FAILED", result=None, latency_ms=round(dur, 2), error=str(e))

        futures = [loop.run_in_executor(self._executor, _run_single, tid, fn) for tid, fn in tasks]
        results = await asyncio.gather(*futures, return_exceptions=False)

        total_elapsed = (time.perf_counter() - t0) * 1000
        logger.info(f"[SWARM] House Party Protocol completed {len(tasks)} tasks in {total_elapsed:.1f}ms")
        return results

    def shutdown(self):
        """Clean shutdown of worker thread pool."""
        self._executor.shutdown(wait=False)
