# 🕸️ Code Graph & Graphify System Skill Map — J.A.R.V.I.S. v3.0

> **Standard:** Stark Horizon v3.0 / v3.1 Sovereign AI  
> **Engine Core:** `jarvis/analysis/code_graph.py` (`CodeGraphEngine`, `CodeGraphNode`, `CodeGraphEdge`)  
> **Holographic 3D Visualizer:** `jarvis/control_center/widgets/voice_orb.py`  
> **Stark HUD AST Inspector Dialog:** `jarvis/control_center/widgets/code_graph_detail_dialog.py`  
> **Diagnostic Tab 5:** `jarvis/control_center/developer_window.py` (`_build_code_graph_tab`)

---

## 1. Overview & Graphify Philosophy

The **Code Graph** (Code Knowledge Graph) represents the entire repository as a **multi-dimensional directed property graph** rather than flat text files. **Graphify** is the sovereign AST (Abstract Syntax Tree) pipeline that transforms source code text into queryable nodes, edges, line metrics, classes, functions, and 3D spatial coordinates without external cloud dependencies.

```
                    ┌──────────────────────────────────────────────────┐
                    │            AST Code Graph Engine                 │
                    │       (jarvis/analysis/code_graph.py)            │
                    └────────────────────────┬─────────────────────────┘
                                             │
       ┌────────────────────────┬────────────┴───────────┬────────────────────────┐
       ▼                        ▼                        ▼                        ▼
  📦 100% Real AST Nodes   🔗 Directed Edges        🌐 3D Coordinates        💥 Blast Radius
  • Modules (line count)   • IMPORTS (Internal)     • Fibonacci Sphere       • Callers & Importers
  • Classes & Methods      • CALLS                  • 6 Subsystem Clusters   • Direct Dependencies
  • Top-Level Functions    • INHERITS               • 2D/3D Pan & Zoom       • Impact Link Counts
  • Byte sizes & Docs      • DEPENDS_ON             • Freeze on Hover        • Orphan / Dead Scan
```

---

## 2. 6 Functional 3D Subsystem Clusters

| Cluster | Spatial Anchor | Representative Modules | Color Token | Hex Code |
|---|---|---|---|---|
| **Spine** | Equator Front ($z \approx 0$) | `jarvis.main`, `jarvis.config`, `jarvis.system.spec_loader` | Cyan | `#00f0ff` |
| **Cognitive** | North Front-Right ($y > 0$) | `conversational`, `ollama_client`, `dynamic_workflows` | Purple | `#b388ff` |
| **Audio** | West Equatorial ($x < 0$) | `audio.manager`, `dual_gate_vad`, `wake_word` | Emerald | `#00ffaa` |
| **Security** | South Front-Right ($y < 0$) | `guardrails`, `veronica`, `stark_hacking` | Veronica Red | `#ff0055` |
| **Memory** | North Back ($z < 0$) | `semantic_vault`, `skill_knowledge_engine` | Amber | `#ffaa00` |
| **UI / HUD** | East Equatorial ($x > 0$) | `control_center`, `voice_orb`, `developer_window` | Sky Blue | `#38bdf8` |

---

## 3. Mathematical 3D Spherical Distribution

Nodes are mapped onto the 3D unit sphere ($x^2 + y^2 + z^2 \approx 1.0$) using a **Clustered Fibonacci Spherical Spiral**:

$$\phi = \arccos\left(1 - \frac{2(i + 0.5)}{N}\right), \quad \theta = \pi (1 + \sqrt{5}) i$$
$$x_0 = \sin\phi \cos\theta, \quad y_0 = \sin\phi \sin\theta, \quad z_0 = \cos\phi$$

Coordinates are then anchored toward their respective cluster center $(c_x, c_y, c_z)$ and normalized to unit radius $R = 1.0 \pm 0.1$.

---

## 4. Full REST API Reference (FastAPI Spine `:8765`)

| HTTP Method | Endpoint | Description | Query / Body Params |
|---|---|---|---|
| `GET` | `/api/v1/graph/topology` | High-level summary of total modules, edges, and cluster distribution | None |
| `GET` | `/api/v1/graph/nodes` | List of all extracted AST code nodes with line counts & 3D coordinates | None |
| `GET` | `/api/v1/graph/blast_radius` | Impact analysis & downstream callers for a specific module | `?node_id=jarvis.main` |
| `POST` | `/api/v1/graph/rebuild` | Triggers real-time AST re-scanning and graphification | None |

---

## 5. Sub-Millisecond Voice Command Triggers

- *"Jarvis, show code graph"* ➔ Instant voice report of active AST modules, edges, and cluster topology.
- *"Jarvis, what is the blast radius of voice orb?"* ➔ Queries AST call hierarchy and reports connected callers and dependencies.
- *"Jarvis, scan dead code"* ➔ Traverses the AST graph to find any orphaned/isolated files with zero links.

---

## 6. Stark HUD AST Node Inspector Dialog

When any code node is double-clicked in the 3D Holographic Canvas or Developer Window, the **`CodeGraphDetailDialog`** displays:
- **Header:** Real module name, Cluster badge, Local filesystem path, Line count, File size in KB, and Docstring summary.
- **Tab 1: 🏛️ Classes & Methods:** Tree listing all classes defined in the file with their respective methods.
- **Tab 2: ⚙️ Functions:** List of all top-level functions with complete argument parameter lists.
- **Tab 3: 🔗 Direct Dependencies:** Internal `jarvis.*` imported modules.
- **Tab 4: 💥 Inbound Callers:** Other modules that depend on or import this file.
- **Actions:** `📋 COPY FILE PATH`, `✕ CLOSE`.
