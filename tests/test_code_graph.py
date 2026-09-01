"""
tests/test_code_graph.py — Automated Unit Tests for AST Code Graph & Graphify Engine
"""

import pytest
from jarvis.analysis.code_graph import code_graph_engine, CodeGraphNode, CodeGraphEdge

def test_code_graph_engine_initialization():
    """Verify code graph engine parses files and creates nodes and edges."""
    engine = code_graph_engine
    assert len(engine.nodes) > 0, "Code graph should have parsed repository modules"
    assert len(engine.edges) > 0, "Code graph should have extracted import edges"
    
    summary = engine.get_topological_summary()
    assert summary["total_nodes"] == len(engine.nodes)
    assert summary["total_edges"] == len(engine.edges)
    assert "spine" in summary["clusters"]

def test_code_graph_3d_coordinates():
    """Verify all extracted nodes have valid 3D coordinates on the unit sphere."""
    engine = code_graph_engine
    for node in engine.nodes.values():
        dist = (node.x**2 + node.y**2 + node.z**2)**0.5
        assert 0.8 <= dist <= 1.2, f"Node {node.node_id} 3D coordinates should be normalized"

def test_code_graph_blast_radius():
    """Verify blast radius calculation returns downstream dependencies and callers."""
    engine = code_graph_engine
    # Pick a well-connected node like jarvis.config or jarvis.main
    target_node = None
    for n_id in engine.nodes:
        if "config" in n_id or "main" in n_id:
            target_node = n_id
            break
            
    assert target_node is not None, "Target node should exist in graph"
    blast = engine.get_blast_radius(target_node)
    assert "node_id" in blast
    assert "downstream_dependencies" in blast
    assert "callers_and_importers" in blast
    assert isinstance(blast["total_impact_count"], int)

def test_command_router_code_graph_intents():
    """Verify sub-millisecond command router handles code graph queries."""
    from jarvis.system.command_router import command_router
    
    # 1. Summary intent
    res = command_router.execute("Jarvis show code graph")
    assert res["matched"] is True
    assert res["intent"] == "code_graph_summary"
    assert "AST Code Graph comprises" in res["response"]
    
    # 2. Blast radius intent
    res_b = command_router.execute("what is the blast radius of jarvis.main")
    assert res_b["matched"] is True
    assert res_b["intent"] == "code_graph_blast"
    assert "AST Blast Radius" in res_b["response"]
    
    # 3. Dead code scan intent
    res_d = command_router.execute("scan dead code")
    assert res_d["matched"] is True
    assert res_d["intent"] == "code_graph_dead"
    assert "Scan complete" in res_d["response"] or "Zero isolated files" in res_d["response"]

def test_fastapi_spine_graph_endpoints():
    """Verify FastAPI spine endpoints return valid code graph schemas."""
    from fastapi.testclient import TestClient
    from jarvis.main import app
    
    client = TestClient(app)
    
    # 1. Topology
    r_topo = client.get("/api/v1/graph/topology")
    assert r_topo.status_code == 200
    assert "total_nodes" in r_topo.json()
    assert "total_edges" in r_topo.json()
    
    # 2. Nodes
    r_nodes = client.get("/api/v1/graph/nodes")
    assert r_nodes.status_code == 200
    assert len(r_nodes.json()) > 0
    
    # 3. Blast radius
    r_blast = client.get("/api/v1/graph/blast_radius?node_id=jarvis.main")
    assert r_blast.status_code == 200
    assert "downstream_dependencies" in r_blast.json()
    
    # 4. Rebuild
    r_rebuild = client.post("/api/v1/graph/rebuild")
    assert r_rebuild.status_code == 200
    assert r_rebuild.json()["status"] == "rebuilt"

def test_real_ast_metadata_extracted():
    """Verify 100% real AST metadata extraction: classes, functions, and sizes."""
    engine = code_graph_engine
    
    found_class = False
    found_function = False
    
    for node in engine.nodes.values():
        assert node.line_count > 0, f"Module {node.node_id} must have real line count"
        assert node.file_size_bytes > 0, f"Module {node.node_id} must have real file size"
        if node.classes:
            found_class = True
            cls = node.classes[0]
            assert "name" in cls
            assert "methods" in cls
        if node.functions:
            found_function = True
            fn = node.functions[0]
            assert "name" in fn
            assert "args" in fn

    assert found_class, "Code graph should extract real AST classes across repo"
    assert found_function, "Code graph should extract real AST functions across repo"

def test_voice_orb_zoom_and_hover_freeze(qapp):
    """Verify mouse scroll wheel zoom and freeze on hover in VoiceOrbWidget."""
    from jarvis.control_center.widgets.voice_orb import VoiceOrbWidget, OrbDisplayMode
    from PySide6.QtGui import QWheelEvent, QMouseEvent
    from PySide6.QtCore import QPointF, QPoint, Qt
    
    orb = VoiceOrbWidget()
    orb.set_display_mode(OrbDisplayMode.CODE_GRAPH)
    
    # 1. Initial zoom scale
    assert orb._zoom_scale == 1.0
    
    # 2. Simulate mouse scroll wheel zoom in
    event_zoom_in = QWheelEvent(
        QPointF(100, 100), QPointF(100, 100),
        QPoint(0, 0), QPoint(0, 120),
        Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase, False
    )
    orb.wheelEvent(event_zoom_in)
    assert orb._zoom_scale > 1.0
    
    # 3. Simulate mouse scroll wheel zoom out
    event_zoom_out = QWheelEvent(
        QPointF(100, 100), QPointF(100, 100),
        QPoint(0, 0), QPoint(0, -240),
        Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase, False
    )
    orb.wheelEvent(event_zoom_out)
    assert orb._zoom_scale < 1.12
    
    # 4. Freeze on hover logic
    orb._is_hovered = True
    orb._hovered_node_id = "jarvis.main"
    orb._on_tick()
    
    # 5. Test Zoom In / Zoom Out and Reset API
    orb.zoom_in()
    assert orb._zoom_scale > 1.0
    orb.zoom_out()
    orb.reset_view()
    assert orb._zoom_scale == 1.0
    assert orb._pan_x == 0.0
    assert orb._pan_y == 0.0

    # 6. Test Canvas Dragging Pan and Orbit
    orb._is_panning = True
    orb._drag_last_pos = QPointF(50, 50)
    event_move = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(80, 70),
        QPointF(80, 70),
        Qt.MouseButton.RightButton,
        Qt.MouseButton.RightButton,
        Qt.KeyboardModifier.NoModifier
    )
    orb.mouseMoveEvent(event_move)
    assert orb._pan_x == 30.0
    assert orb._pan_y == 20.0
    
    orb.close()

def test_code_graph_detail_dialog(qapp):
    """Verify CodeGraphDetailDialog renders real AST data for a node."""
    from jarvis.control_center.widgets.code_graph_detail_dialog import CodeGraphDetailDialog
    
    target_node = "jarvis.main"
    dlg = CodeGraphDetailDialog(target_node)
    
    assert dlg.node is not None
    assert dlg.node.node_id == target_node
    assert dlg.node.line_count > 0
    
    dlg.close()


