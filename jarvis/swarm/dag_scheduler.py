"""
jarvis/swarm/dag_scheduler.py — Directed Acyclic Graph (DAG) Swarm Scheduler
Orchestrates complex multi-agent workflows into parallel execution waves with dependency resolution.
"""

import time
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Callable, Optional
from .parallel_executor import HousePartySwarmExecutor, SwarmTaskResult

logger = logging.getLogger("jarvis.swarm.dag")


@dataclass
class TaskNode:
    task_id: str
    action: Callable[..., Any]
    dependencies: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class DAGExecutionReport:
    total_latency_ms: float
    sequential_latency_est_ms: float
    speedup_factor: float
    nodes_executed: int
    results: Dict[str, Any]
    status: str  # "COMPLETED" | "PARTIAL_FAILURE"


class SwarmDAGScheduler:
    """
    Schedules and executes task DAGs using wave-based parallel dispatching.
    """
    def __init__(self, max_workers: int = 6):
        self.executor = HousePartySwarmExecutor(max_workers=max_workers)
        self.nodes: Dict[str, TaskNode] = {}

    def add_task(
        self,
        task_id: str,
        action: Callable[..., Any],
        dependencies: Optional[List[str]] = None,
        description: str = ""
    ):
        """Registers a task node in the DAG."""
        self.nodes[task_id] = TaskNode(
            task_id=task_id,
            action=action,
            dependencies=dependencies or [],
            description=description
        )

    def build_execution_waves(self) -> List[List[str]]:
        """
        Performs topological sorting into dependency waves (tiers).
        Tasks in the same wave have all their dependencies met and can execute in parallel.
        """
        in_degree: Dict[str, int] = {tid: 0 for tid in self.nodes}
        dependents: Dict[str, List[str]] = {tid: [] for tid in self.nodes}

        for tid, node in self.nodes.items():
            for dep in node.dependencies:
                if dep in self.nodes:
                    in_degree[tid] += 1
                    dependents[dep].append(tid)

        waves: List[List[str]] = []
        completed: Set[str] = set()

        while len(completed) < len(self.nodes):
            current_wave = [
                tid for tid, deg in in_degree.items()
                if deg == 0 and tid not in completed
            ]

            if not current_wave:
                # Cycle detected or unreachable tasks
                remaining = [t for t in self.nodes if t not in completed]
                logger.warning(f"[SWARM DAG] Cyclic or unresolvable dependencies in tasks: {remaining}")
                current_wave = remaining

            waves.append(current_wave)
            for tid in current_wave:
                completed.add(tid)
                for dep_id in dependents.get(tid, []):
                    in_degree[dep_id] -= 1

        return waves

    async def execute_dag(self) -> DAGExecutionReport:
        """
        Executes all task nodes in wave order, feeding prior results as context.
        """
        t0 = time.perf_counter()
        waves = self.build_execution_waves()
        results: Dict[str, Any] = {}
        all_results_raw: List[SwarmTaskResult] = []
        has_failure = False

        for wave_idx, wave in enumerate(waves):
            logger.info(f"[SWARM DAG] Executing wave {wave_idx + 1}/{len(waves)}: {wave}")
            batch = [(tid, self.nodes[tid].action) for tid in wave]
            wave_results = await self.executor.execute_parallel_tasks(batch)

            for res in wave_results:
                all_results_raw.append(res)
                if res.status == "SUCCESS":
                    results[res.task_id] = res.result
                else:
                    results[res.task_id] = f"ERROR: {res.error}"
                    has_failure = True

        total_elapsed = (time.perf_counter() - t0) * 1000
        sequential_sum = sum(r.latency_ms for r in all_results_raw)
        speedup = (sequential_sum / total_elapsed) if total_elapsed > 0 else 1.0

        return DAGExecutionReport(
            total_latency_ms=round(total_elapsed, 2),
            sequential_latency_est_ms=round(sequential_sum, 2),
            speedup_factor=round(speedup, 2),
            nodes_executed=len(all_results_raw),
            results=results,
            status="COMPLETED" if not has_failure else "PARTIAL_FAILURE"
        )
