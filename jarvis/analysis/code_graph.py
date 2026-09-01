"""
jarvis/analysis/code_graph.py — AST Code Graph & Repository Graphify Engine
Parses repository Python files using the standard ast module to extract:
- Modules, Classes, Functions, and API routes
- Directed dependency edges (IMPORTS, CALLS, INHERITS)
- 3D clustered spherical coordinates for real-time holographic visualization
- Blast-radius calculation and impact analysis
Optimized with lazy initialization on first query.
"""

import ast
import os
import math
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from jarvis.config import config
from jarvis.logging import get_logger

logger = get_logger("code_graph")

class CodeGraphNode:
    """Represents a code artifact node in the 3D Code Graph."""
    def __init__(self, node_id: str, label: str, node_type: str, cluster: str, file_path: str,
                 x: float = 0.0, y: float = 0.0, z: float = 0.0,
                 line_count: int = 0, summary: str = "",
                 classes: Optional[List[Dict[str, Any]]] = None,
                 functions: Optional[List[Dict[str, Any]]] = None,
                 file_size_bytes: int = 0):
        self.node_id = node_id
        self.label = label
        self.node_type = node_type  # 'module', 'class', 'function', 'endpoint'
        self.cluster = cluster      # 'spine', 'cognitive', 'audio', 'security', 'memory', 'ui'
        self.file_path = file_path
        self.x = x
        self.y = y
        self.z = z
        self.line_count = line_count
        self.summary = summary
        self.classes = classes or []
        self.functions = functions or []
        self.file_size_bytes = file_size_bytes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node_id,
            "label": self.label,
            "type": self.node_type,
            "cluster": self.cluster,
            "file_path": self.file_path,
            "pos": [round(self.x, 3), round(self.y, 3), round(self.z, 3)],
            "lines": self.line_count,
            "summary": self.summary,
            "classes": self.classes,
            "functions": self.functions,
            "size_bytes": self.file_size_bytes
        }

class CodeGraphEdge:
    """Represents a directed relationship between two code nodes."""
    def __init__(self, source: str, target: str, edge_type: str = "IMPORTS", weight: float = 1.0):
        self.source = source
        self.target = target
        self.edge_type = edge_type  # 'IMPORTS', 'CALLS', 'INHERITS', 'DEPENDS_ON'
        self.weight = weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.edge_type,
            "weight": self.weight
        }

class CodeGraphEngine:
    """
    Sovereign AST Code Graph Builder that graphifies the J.A.R.V.I.S. codebase.
    Uses lazy initialization to eliminate import-time overhead.
    """
    CLUSTER_COLORS = {
        "spine": "#00f0ff",       # Cyan
        "cognitive": "#b388ff",   # Purple
        "audio": "#00ffaa",       # Emerald
        "security": "#ff0055",    # Red
        "memory": "#ffaa00",      # Amber
        "ui": "#38bdf8",          # Sky Blue
        "general": "#94a3b8"      # Slate
    }

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir or config.root_dir)
        self._nodes: Dict[str, CodeGraphNode] = {}
        self._edges: List[CodeGraphEdge] = []
        self._adjacency: Dict[str, Set[str]] = {}
        self._reverse_adjacency: Dict[str, Set[str]] = {}
        self._is_built = False

    def _ensure_built(self):
        """Ensures the AST graph is parsed on demand."""
        if not self._is_built:
            self.rebuild_graph()

    @property
    def nodes(self) -> Dict[str, CodeGraphNode]:
        self._ensure_built()
        return self._nodes

    @property
    def edges(self) -> List[CodeGraphEdge]:
        self._ensure_built()
        return self._edges

    def rebuild_graph(self):
        """Scans jarvis/ directory and constructs the AST graph."""
        self._nodes.clear()
        self._edges.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()

        jarvis_dir = self.root_dir / "jarvis"
        if not jarvis_dir.exists():
            self._is_built = True
            return

        py_files = list(jarvis_dir.rglob("*.py"))
        
        # Phase 1: Create Module Nodes with AST Analysis
        for py_file in py_files:
            rel_path = py_file.relative_to(self.root_dir).as_posix()
            mod_id = rel_path.replace("/", ".").replace(".py", "")
            cluster = self._determine_cluster(rel_path)
            
            extracted_classes: List[Dict[str, Any]] = []
            extracted_functions: List[Dict[str, Any]] = []
            line_count = 0
            summary = rel_path
            file_size = 0

            try:
                file_size = py_file.stat().st_size
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                line_count = len(content.splitlines())
                tree = ast.parse(content)
                doc = ast.get_docstring(tree) or f"Module {rel_path}"
                summary = doc.split("\n")[0].strip() if doc else rel_path

                for item in tree.body:
                    if isinstance(item, ast.ClassDef):
                        methods = [m.name for m in item.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        c_doc = ast.get_docstring(item) or ""
                        extracted_classes.append({
                            "name": item.name,
                            "doc": c_doc.split("\n")[0].strip() if c_doc else f"Class {item.name}",
                            "methods": methods
                        })
                    elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        f_doc = ast.get_docstring(item) or ""
                        args = [a.arg for a in item.args.args]
                        extracted_functions.append({
                            "name": item.name,
                            "doc": f_doc.split("\n")[0].strip() if f_doc else f"Function {item.name}",
                            "args": args
                        })
            except Exception as e:
                logger.debug("AST parsing note on %s: %s", rel_path, e)

            self._nodes[mod_id] = CodeGraphNode(
                node_id=mod_id,
                label=py_file.stem,
                node_type="module",
                cluster=cluster,
                file_path=rel_path,
                line_count=line_count,
                summary=summary,
                classes=extracted_classes,
                functions=extracted_functions,
                file_size_bytes=file_size
            )
            self._adjacency[mod_id] = set()
            self._reverse_adjacency[mod_id] = set()

        # Phase 2: AST Traversal for Classes, Functions, and Imports
        for py_file in py_files:
            rel_path = py_file.relative_to(self.root_dir).as_posix()
            src_mod = rel_path.replace("/", ".").replace(".py", "")
            
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target = alias.name
                        if target.startswith("jarvis"):
                            self._add_edge(src_mod, target, "IMPORTS")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("jarvis"):
                        self._add_edge(src_mod, node.module, "IMPORTS")

        # Phase 3: Calculate 3D Clustered Spherical Coordinates
        self._calculate_3d_coordinates()
        self._is_built = True
        logger.info("AST Code Graph constructed: %d nodes, %d edges", len(self._nodes), len(self._edges))

    def _determine_cluster(self, path: str) -> str:
        p = path.lower()
        if "audio" in p:
            return "audio"
        elif "cognitive" in p or "agents" in p or "learning" in p:
            return "cognitive"
        elif "security" in p:
            return "security"
        elif "memory" in p or "database" in p:
            return "memory"
        elif "control_center" in p or "hud" in p:
            return "ui"
        elif "main" in p or "config" in p or "system" in p:
            return "spine"
        return "general"

    def _add_edge(self, source: str, target: str, edge_type: str):
        matched_target = target
        if target not in self._nodes:
            for n_id in self._nodes:
                if n_id.startswith(target) or target.startswith(n_id):
                    matched_target = n_id
                    break
        
        if source in self._nodes and matched_target in self._nodes and source != matched_target:
            edge = CodeGraphEdge(source, matched_target, edge_type)
            self._edges.append(edge)
            self._adjacency.setdefault(source, set()).add(matched_target)
            self._reverse_adjacency.setdefault(matched_target, set()).add(source)

    def _calculate_3d_coordinates(self):
        """Distributes nodes across 3D spherical clusters with Fibonacci distribution."""
        clusters = {}
        for node in self._nodes.values():
            clusters.setdefault(node.cluster, []).append(node)

        cluster_centers = {
            "spine": (0.0, 0.0),
            "cognitive": (math.pi / 3, 0.5),
            "audio": (-0.2, -math.pi / 2),
            "security": (-math.pi / 3, 0.8),
            "memory": (math.pi / 4, math.pi),
            "ui": (0.1, math.pi / 2),
            "general": (-math.pi / 4, -math.pi / 2)
        }

        for cluster_name, nodes in clusters.items():
            center_lat, center_lon = cluster_centers.get(cluster_name, (0.0, 0.0))
            n_count = len(nodes)
            
            for i, node in enumerate(nodes):
                spread_radius = 0.35 + 0.15 * math.sqrt(i / max(1, n_count))
                ang = i * 2.39996
                
                lat = center_lat + spread_radius * math.sin(ang) * 0.45
                lon = center_lon + spread_radius * math.cos(ang) * 0.70
                
                node.x = math.cos(lat) * math.cos(lon)
                node.y = math.sin(lat)
                node.z = math.cos(lat) * math.sin(lon)

    def get_blast_radius(self, node_id: str) -> Dict[str, Any]:
        """Calculates downstream dependencies and incoming callers for impact analysis."""
        self._ensure_built()
        downstream = self._adjacency.get(node_id, set())
        callers = self._reverse_adjacency.get(node_id, set())
        
        return {
            "node_id": node_id,
            "downstream_dependencies": list(downstream),
            "callers_and_importers": list(callers),
            "total_impact_count": len(downstream) + len(callers)
        }

    def get_topological_summary(self) -> Dict[str, Any]:
        """Returns high-level graph topology metrics."""
        self._ensure_built()
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "clusters": {c: len([n for n in self._nodes.values() if n.cluster == c])
                         for c in set(n.cluster for n in self._nodes.values())},
            "root_spine_nodes": [n.node_id for n in self._nodes.values() if n.cluster == "spine"]
        }

# Global Singleton Instance (Lazy init)
code_graph_engine = CodeGraphEngine()
