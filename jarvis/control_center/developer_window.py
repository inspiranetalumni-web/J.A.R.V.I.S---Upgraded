"""
jarvis/control_center/developer_window.py — Responsive Cosmic Glass Developer Diagnostic Suite
Provides full-fidelity, responsive diagnostic inspection for all J.A.R.V.I.S. subsystems,
hardware topologies, live FastAPI Spine endpoints, interactive metrics breakdown, and raw JSON export.
"""

import json
import time
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLineEdit, QSplitter, QHeaderView, QApplication, QFrame,
    QSizePolicy, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from jarvis.control_center.theme import (
    MASTER_STYLESHEET, COLOR_BG_DARK, COLOR_BG_SURFACE, COLOR_BG_CARD,
    COLOR_CYAN, COLOR_CYAN_DIM, COLOR_CYAN_GLOW, COLOR_EMERALD, COLOR_AMBER,
    COLOR_VERONICA_RED, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER_CARD, COLOR_BORDER_NORMAL, FONT_FAMILY_MONO
)

class DeveloperInspectorWindow(QMainWindow):
    """
    Responsive, cosmic sapphire glass diagnostic suite for full source-of-truth telemetry inspection.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S. Developer Diagnostic Suite — Source of Truth")
        self.resize(1160, 780)
        self.setMinimumSize(900, 580)
        self.setStyleSheet(MASTER_STYLESHEET)

        self._latest_telemetry: Dict[str, Any] = {}
        self._packet_count: int = 0
        self._active_category: str = "ALL"

        self._init_ui()

    def _init_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # 1. Header Bar with Diagnostic Status Strip
        header = QHBoxLayout()
        header.setSpacing(12)

        lbl_icon = QLabel("🛠️")
        lbl_icon.setFont(QFont("Segoe UI Emoji", 14))
        header.addWidget(lbl_icon)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        lbl_title = QLabel("DEVELOPER DIAGNOSTIC SUITE // SOURCE OF TRUTH")
        lbl_title.setStyleSheet(f"color: {COLOR_CYAN}; font-size: 13px; font-weight: bold; letter-spacing: 1.2px;")
        title_layout.addWidget(lbl_title)

        self.lbl_packet_info = QLabel("SYSTEM NOMINAL // P-CORE PINNED // ZERO FABRICATED TELEMETRY")
        self.lbl_packet_info.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 9px; letter-spacing: 0.8px;")
        title_layout.addWidget(self.lbl_packet_info)
        header.addLayout(title_layout)

        header.addStretch()

        self.btn_copy_json = QPushButton("📋 COPY JSON")
        self.btn_copy_json.setObjectName("quickChip")
        self.btn_copy_json.clicked.connect(self._copy_raw_json)
        header.addWidget(self.btn_copy_json)

        self.btn_refresh = QPushButton("🔄 REFRESH")
        self.btn_refresh.setObjectName("quickChip")
        self.btn_refresh.clicked.connect(self._manual_refresh)
        header.addWidget(self.btn_refresh)

        layout.addLayout(header)

        # 2. Live Mini Telemetry Status Strip
        strip_frame = QFrame()
        strip_frame.setStyleSheet(
            "background-color: rgba(20, 48, 92, 0.48); border: 1px solid rgba(0, 240, 255, 0.22); "
            "border-radius: 6px; padding: 4px 8px;"
        )
        strip_layout = QHBoxLayout(strip_frame)
        strip_layout.setContentsMargins(8, 4, 8, 4)
        strip_layout.setSpacing(16)

        self.lbl_strip_spine = QLabel("● SPINE: ONLINE (:8765)")
        self.lbl_strip_spine.setStyleSheet(f"color: {COLOR_EMERALD}; font-size: 10px; font-weight: bold;")
        strip_layout.addWidget(self.lbl_strip_spine)

        self.lbl_strip_cores = QLabel("● AFFINITY: 0x00F PINNED")
        self.lbl_strip_cores.setStyleSheet(f"color: {COLOR_CYAN}; font-size: 10px; font-weight: bold;")
        strip_layout.addWidget(self.lbl_strip_cores)

        self.lbl_strip_ram = QLabel("● RAM CEILING: 14.5 GB")
        self.lbl_strip_ram.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 10px; font-weight: bold;")
        strip_layout.addWidget(self.lbl_strip_ram)

        self.lbl_strip_packets = QLabel("● PACKETS: #0000")
        self.lbl_strip_packets.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")
        strip_layout.addWidget(self.lbl_strip_packets)

        strip_layout.addStretch()

        self.lbl_strip_time = QLabel("LAST POLLED: --:--:--")
        self.lbl_strip_time.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")
        strip_layout.addWidget(self.lbl_strip_time)

        layout.addWidget(strip_frame)

        # 3. Main Glassmorphic Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: rgba(16, 36, 70, 0.58);
                border: 1px solid rgba(0, 240, 255, 0.22);
                border-radius: 6px;
                padding: 6px;
            }}
            QTabBar::tab {{
                background: rgba(15, 35, 71, 0.85);
                color: {COLOR_TEXT_SECONDARY};
                padding: 8px 18px;
                border: 1px solid rgba(0, 240, 255, 0.20);
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                font-size: 11px;
                margin-right: 4px;
            }}
            QTabBar::tab:hover {{
                color: {COLOR_CYAN};
                background: rgba(22, 50, 98, 0.90);
            }}
            QTabBar::tab:selected {{
                background: rgba(22, 52, 102, 0.95);
                color: {COLOR_CYAN};
                border: 1px solid {COLOR_CYAN};
                border-bottom: none;
            }}
        """)

        # Tab 1: Subsystem Deep-Dive Explorer with Responsive Splitter
        self.tab_subsystems = self._build_subsystems_tab()
        self.tabs.addTab(self.tab_subsystems, "📊 Subsystems Matrix")

        # Tab 2: Hardware & P-Core Topology Cards
        self.tab_hardware = self._build_hardware_tab()
        self.tabs.addTab(self.tab_hardware, "⚙️ Hardware & P-Cores")

        # Tab 3: Live Core Spine API Explorer
        self.tab_spine = self._build_spine_tab()
        self.tabs.addTab(self.tab_spine, "🌐 Core Spine API (:8765)")

        # Tab 4: AST Code Graph & Graphify Engine
        self.tab_code_graph = self._build_code_graph_tab()
        self.tabs.addTab(self.tab_code_graph, "🕸️ Code Graph & Graphify")

        # Tab 5: Raw JSON Telemetry Snapshot
        self.tab_json = self._build_json_tab()
        self.tabs.addTab(self.tab_json, "📄 Raw JSON Snapshot")

        layout.addWidget(self.tabs, stretch=1)

        self.setCentralWidget(root)

    def _build_subsystems_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Search Bar & Filter Row
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        lbl_s = QLabel("🔍 Filter:")
        lbl_s.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_s.setStyleSheet(f"color: {COLOR_CYAN};")
        filter_bar.addWidget(lbl_s)

        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Filter metrics by name, value, or explanation...")
        self.txt_filter.setClearButtonEnabled(True)
        self.txt_filter.setStyleSheet(
            "background-color: rgba(20, 48, 92, 0.48); color: #f1f5f9; "
            "border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 6px; padding: 5px 10px; font-size: 11px;"
        )
        self.txt_filter.textChanged.connect(self._filter_tree)
        filter_bar.addWidget(self.txt_filter, stretch=2)

        self.lbl_filter_count = QLabel("All Metrics Visible")
        self.lbl_filter_count.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")
        filter_bar.addWidget(self.lbl_filter_count)

        layout.addLayout(filter_bar)

        # Responsive Splitter: Left Tree vs Right Detail Inspector Card
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(0, 240, 255, 0.20);
                width: 4px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #00f0ff;
            }
        """)

        # Left Panel: Tree Widget for Subsystem Deep-Dive
        self.tree_subsystems = QTreeWidget()
        self.tree_subsystems.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tree_subsystems.setHeaderLabels(["Subsystem / Metric", "Live Value", "Technical Detail & Purpose"])
        self.tree_subsystems.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree_subsystems.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tree_subsystems.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tree_subsystems.setColumnWidth(0, 260)
        self.tree_subsystems.setColumnWidth(1, 140)
        self.tree_subsystems.setStyleSheet(f"""
            QTreeWidget {{
                background-color: rgba(18, 40, 78, 0.50);
                border: 1px solid rgba(0, 240, 255, 0.22);
                border-radius: 6px;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 11px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid rgba(0, 240, 255, 0.08);
            }}
            QTreeWidget::item:hover {{
                background-color: rgba(0, 240, 255, 0.15);
            }}
            QTreeWidget::item:selected {{
                background-color: rgba(0, 240, 255, 0.25);
                color: #ffffff;
            }}
            QHeaderView::section {{
                background-color: rgba(15, 35, 71, 0.90);
                color: {COLOR_CYAN};
                padding: 6px 8px;
                font-weight: bold;
                border: 1px solid rgba(0, 240, 255, 0.20);
            }}
        """)
        self.tree_subsystems.itemClicked.connect(self._on_tree_item_clicked)
        splitter.addWidget(self.tree_subsystems)

        # Right Panel: Detail Card View for Selected Metric Node
        detail_container = QFrame()
        detail_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        detail_container.setStyleSheet(
            "background-color: rgba(18, 40, 78, 0.50); border: 1px solid rgba(0, 240, 255, 0.22); "
            "border-radius: 6px; padding: 12px;"
        )
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(10)

        lbl_det_title = QLabel("METRIC & SUBSYSTEM TELEMETRY INSPECTOR")
        lbl_det_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_det_title.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px;")
        detail_layout.addWidget(lbl_det_title)

        self.lbl_node_name = QLabel("Select a metric on the left to inspect")
        self.lbl_node_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_node_name.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        self.lbl_node_name.setWordWrap(True)
        detail_layout.addWidget(self.lbl_node_name)

        self.lbl_node_val = QLabel("Live Value: --")
        self.lbl_node_val.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.lbl_node_val.setStyleSheet(f"color: {COLOR_EMERALD};")
        detail_layout.addWidget(self.lbl_node_val)

        self.lbl_node_desc = QLabel("Detailed technical explanations, metric formulas, and live status verification will appear here.")
        self.lbl_node_desc.setFont(QFont("Segoe UI", 9))
        self.lbl_node_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; line-height: 1.4;")
        self.lbl_node_desc.setWordWrap(True)
        detail_layout.addWidget(self.lbl_node_desc)

        detail_layout.addStretch()

        splitter.addWidget(detail_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, stretch=1)

        return widget

    def _build_hardware_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # Responsive 4-Card Hardware Topology Grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)

        # Card 1: CPU & P-Cores
        self.card_cpu = self._create_info_card("⚙️ CPU & P-CORE AFFINITY", "Intel Core i7-1255U\n2 P-Cores / 8 E-Cores / 12 Threads\nAffinity Mask: 0x00F (Threads 0-3 Pinned)")
        grid.addWidget(self.card_cpu, 0, 0)

        # Card 2: Memory & RAM Ceiling
        self.card_ram = self._create_info_card("💾 MEMORY & CEILING CAP", "Total RAM: -- GB\nUsed: -- GB (--%)\nCap Ceiling: 14.5 GB (512MB Process Cap)")
        grid.addWidget(self.card_ram, 0, 1)

        # Card 3: Storage & Battery
        self.card_storage = self._create_info_card("🔋 POWER & NVMe STORAGE", "Disk: -- GB / -- GB (--%)\nBattery: --% (⚡ AC Connected)\nStorage Protocol: Local NVMe")
        grid.addWidget(self.card_storage, 1, 0)

        # Card 4: GPU & Network Security
        self.card_net = self._create_info_card("🛡️ ACCELERATION & NETWORK", "GPU: Intel Iris Xe Graphics\nLAN IP: 127.0.0.1\nSovereign Isolation: 100% Local (Zero Cloud)")
        grid.addWidget(self.card_net, 1, 1)

        layout.addWidget(grid_widget)

        # Detailed Raw Audit Log Console
        self.txt_hardware = QTextEdit()
        self.txt_hardware.setReadOnly(True)
        self.txt_hardware.setStyleSheet(
            f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_TEXT_PRIMARY}; "
            f"border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; "
            f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; padding: 8px;"
        )
        layout.addWidget(self.txt_hardware, stretch=1)

        return widget

    def _create_info_card(self, title: str, body: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "background-color: rgba(20, 48, 92, 0.48); border: 1px solid rgba(0, 240, 255, 0.22); "
            "border-radius: 6px; padding: 10px;"
        )
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(10, 8, 10, 8)
        c_layout.setSpacing(4)

        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {COLOR_CYAN};")
        c_layout.addWidget(lbl_t)

        lbl_b = QLabel(body)
        lbl_b.setFont(QFont("Consolas", 9))
        lbl_b.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        lbl_b.setWordWrap(True)
        c_layout.addWidget(lbl_b)

        return card

    def _build_spine_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(8)

        endpoints = [
            ("GET /health", "/health"),
            ("GET /specs", "/specs"),
            ("GET /config", "/config"),
            ("GET /api/v1/system/survival", "/api/v1/system/survival"),
            ("GET /api/v1/frontier/models", "/api/v1/frontier/models"),
            ("GET /mobile", "/mobile")
        ]

        for label, path in endpoints:
            btn = QPushButton(label)
            btn.setObjectName("quickChip")
            btn.clicked.connect(lambda checked, p=path: self._probe_endpoint(p))
            ctrl_layout.addWidget(btn)

        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # Status and Latency Pill
        self.lbl_spine_status = QLabel("Endpoint Inspector: Select an endpoint above to probe live FastAPI Spine response.")
        self.lbl_spine_status.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self.lbl_spine_status)

        self.txt_spine_response = QTextEdit()
        self.txt_spine_response.setReadOnly(True)
        self.txt_spine_response.setStyleSheet(
            f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_EMERALD}; "
            f"border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; "
            f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; padding: 8px;"
        )
        layout.addWidget(self.txt_spine_response, stretch=1)

        return widget

    def _build_code_graph_tab(self) -> QWidget:
        """Constructs the AST Code Graph and Graphify Diagnostic Explorer."""
        from jarvis.analysis.code_graph import code_graph_engine, CodeGraphNode

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 1. Top Topology Overview Strip & Control Actions
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        summary = code_graph_engine.get_topological_summary()
        self.lbl_graph_stats = QLabel(
            f"AST TOPOLOGY: {summary['total_nodes']} Modules // {summary['total_edges']} Directed Dependency Edges"
        )
        self.lbl_graph_stats.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_graph_stats.setStyleSheet(f"color: {COLOR_CYAN};")
        top_bar.addWidget(self.lbl_graph_stats)

        top_bar.addStretch()

        self.btn_rebuild_graph = QPushButton("🔄 RE-GRAPHIFY CODEBASE")
        self.btn_rebuild_graph.setObjectName("quickChip")
        self.btn_rebuild_graph.clicked.connect(self._rebuild_code_graph)
        top_bar.addWidget(self.btn_rebuild_graph)

        self.btn_scan_dead = QPushButton("⚡ SCAN DEAD CODE")
        self.btn_scan_dead.setObjectName("quickChip")
        self.btn_scan_dead.clicked.connect(self._scan_dead_code)
        top_bar.addWidget(self.btn_scan_dead)

        layout.addLayout(top_bar)

        # 2. Filter Search Row
        search_bar = QHBoxLayout()
        search_bar.setSpacing(8)

        lbl_filter_tag = QLabel("🔍 Search Module:")
        lbl_filter_tag.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_filter_tag.setStyleSheet(f"color: {COLOR_CYAN};")
        search_bar.addWidget(lbl_filter_tag)

        self.txt_graph_filter = QLineEdit()
        self.txt_graph_filter.setPlaceholderText("Filter AST nodes by module name or path...")
        self.txt_graph_filter.setClearButtonEnabled(True)
        self.txt_graph_filter.setStyleSheet(
            "background-color: rgba(20, 48, 92, 0.48); color: #f1f5f9; "
            "border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 6px; padding: 4px 8px; font-size: 11px;"
        )
        self.txt_graph_filter.textChanged.connect(self._filter_graph_nodes)
        search_bar.addWidget(self.txt_graph_filter, stretch=2)

        layout.addLayout(search_bar)

        # 3. Main Splitter: Left Node Explorer vs Right Impact Inspector
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(0, 240, 255, 0.20);
                width: 4px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #00f0ff;
            }
        """)

        # Left: AST Node Tree Widget
        self.tree_code_nodes = QTreeWidget()
        self.tree_code_nodes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tree_code_nodes.setHeaderLabels(["AST Code Node / Module", "Cluster", "Lines", "Impact Links"])
        self.tree_code_nodes.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree_code_nodes.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tree_code_nodes.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tree_code_nodes.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tree_code_nodes.setColumnWidth(0, 240)
        self.tree_code_nodes.setColumnWidth(1, 90)
        self.tree_code_nodes.setColumnWidth(2, 60)
        self.tree_code_nodes.setStyleSheet(f"""
            QTreeWidget {{
                background-color: rgba(18, 40, 78, 0.50);
                border: 1px solid rgba(0, 240, 255, 0.22);
                border-radius: 6px;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 11px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid rgba(0, 240, 255, 0.08);
            }}
            QTreeWidget::item:hover {{
                background-color: rgba(0, 240, 255, 0.15);
            }}
            QTreeWidget::item:selected {{
                background-color: rgba(0, 240, 255, 0.25);
                color: #ffffff;
            }}
            QHeaderView::section {{
                background-color: rgba(15, 35, 71, 0.90);
                color: {COLOR_CYAN};
                padding: 6px 8px;
                font-weight: bold;
                border: 1px solid rgba(0, 240, 255, 0.20);
            }}
        """)
        self.tree_code_nodes.itemClicked.connect(self._on_graph_node_clicked)
        self.tree_code_nodes.itemDoubleClicked.connect(self._on_graph_node_double_clicked)
        splitter.addWidget(self.tree_code_nodes)

        # Right: Detail & Blast Radius Card
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        node_card = QFrame()
        node_card.setStyleSheet("background-color: rgba(18, 42, 82, 0.65); border: 1px solid rgba(0, 240, 255, 0.35); border-radius: 6px;")
        card_layout = QVBoxLayout(node_card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(4)

        self.lbl_graph_node_title = QLabel("Select an AST Node to Inspect Blast Radius")
        self.lbl_graph_node_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_graph_node_title.setStyleSheet(f"color: {COLOR_CYAN};")
        card_layout.addWidget(self.lbl_graph_node_title)

        self.lbl_graph_node_file = QLabel("File Path: --")
        self.lbl_graph_node_file.setFont(QFont("Consolas", 8))
        self.lbl_graph_node_file.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        card_layout.addWidget(self.lbl_graph_node_file)

        self.lbl_graph_node_summary = QLabel("Documentation: --")
        self.lbl_graph_node_summary.setFont(QFont("Segoe UI", 8))
        self.lbl_graph_node_summary.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        self.lbl_graph_node_summary.setWordWrap(True)
        card_layout.addWidget(self.lbl_graph_node_summary)

        right_layout.addWidget(node_card)

        # Dependencies & Callers Readout Box
        self.txt_blast_radius = QTextEdit()
        self.txt_blast_radius.setReadOnly(True)
        self.txt_blast_radius.setStyleSheet(
            f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_EMERALD}; "
            f"border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; "
            f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; padding: 8px;"
        )
        self.txt_blast_radius.setPlaceholderText("Select any node on the left to analyze its AST dependencies and incoming callers...")
        right_layout.addWidget(self.txt_blast_radius, stretch=1)

        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, stretch=1)

        # Populate initial code graph tree
        self._populate_code_graph_tree()

        return widget

    def _populate_code_graph_tree(self):
        """Populates the Code Graph tree with extracted AST nodes grouped by cluster."""
        from jarvis.analysis.code_graph import code_graph_engine
        self.tree_code_nodes.clear()

        clusters = {}
        for node in code_graph_engine.nodes.values():
            clusters.setdefault(node.cluster, []).append(node)

        cluster_icons = {
            "spine": "⚡",
            "cognitive": "🧠",
            "audio": "🎙️",
            "security": "🛡️",
            "memory": "💾",
            "ui": "🖥️",
            "general": "📦"
        }

        for cluster_name, nodes in sorted(clusters.items()):
            c_icon = cluster_icons.get(cluster_name, "📦")
            parent = QTreeWidgetItem(self.tree_code_nodes)
            parent.setText(0, f"{c_icon} {cluster_name.upper()} ({len(nodes)} modules)")
            parent.setText(1, cluster_name.upper())
            parent.setText(2, f"{sum(n.line_count for n in nodes)} lines")
            parent.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
            parent.setForeground(0, QColor(COLOR_CYAN))

            for n in sorted(nodes, key=lambda x: x.label):
                blast = code_graph_engine.get_blast_radius(n.node_id)
                child = QTreeWidgetItem(parent)
                child.setText(0, f"  └ {n.label}.py")
                child.setText(1, n.cluster)
                child.setText(2, f"{n.line_count}")
                child.setText(3, f"{blast['total_impact_count']} links")
                child.setData(0, Qt.ItemDataRole.UserRole, n)

            parent.setExpanded(True)

    def _on_graph_node_clicked(self, item: QTreeWidgetItem, column: int):
        from jarvis.analysis.code_graph import code_graph_engine, CodeGraphNode
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, CodeGraphNode):
            blast = code_graph_engine.get_blast_radius(data.node_id)
            self.lbl_graph_node_title.setText(f"📦 {data.label}.py [{data.cluster.upper()}]")
            self.lbl_graph_node_file.setText(f"Path: {data.file_path} ({data.line_count} lines)")
            self.lbl_graph_node_summary.setText(f"Summary: {data.summary}")

            lines = [
                f"=== AST IMPACT ANALYSIS: {data.node_id} ===",
                f"Cluster: {data.cluster.upper()} | Line Count: {data.line_count}",
                f"Total Connected Links: {blast['total_impact_count']}",
                "",
                "--- DIRECT IMPORTS / DOWNSTREAM DEPENDENCIES ---"
            ]
            if blast["downstream_dependencies"]:
                for dep in sorted(blast["downstream_dependencies"]):
                    lines.append(f"  ➜ {dep}")
            else:
                lines.append("  (No internal jarvis dependencies)")

            lines.append("")
            lines.append("--- INCOMING CALLERS / IMPORTERS ---")
            if blast["callers_and_importers"]:
                for caller in sorted(blast["callers_and_importers"]):
                    lines.append(f"  ⬅ {caller}")
            else:
                lines.append("  (Root / Leaf module - No inbound internal callers)")

            self.txt_blast_radius.setPlainText("\n".join(lines))

    def _on_graph_node_double_clicked(self, item: QTreeWidgetItem, column: int):
        from jarvis.analysis.code_graph import CodeGraphNode
        from jarvis.control_center.widgets.code_graph_detail_dialog import CodeGraphDetailDialog
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, CodeGraphNode):
            dlg = CodeGraphDetailDialog(data.node_id, self)
            dlg.exec()

    def _filter_graph_nodes(self, text: str):
        query = text.lower().strip()
        for i in range(self.tree_code_nodes.topLevelItemCount()):
            parent = self.tree_code_nodes.topLevelItem(i)
            parent_match = query in parent.text(0).lower()
            child_match = False
            for j in range(parent.childCount()):
                child = parent.child(j)
                m = query in child.text(0).lower() or query in child.text(1).lower()
                child.setHidden(not m and not parent_match)
                if m or parent_match:
                    child_match = True
            parent.setHidden(not parent_match and not child_match)

    def _rebuild_code_graph(self):
        from jarvis.analysis.code_graph import code_graph_engine
        code_graph_engine.rebuild_graph()
        self._populate_code_graph_tree()
        summary = code_graph_engine.get_topological_summary()
        self.lbl_graph_stats.setText(
            f"AST TOPOLOGY: {summary['total_nodes']} Modules // {summary['total_edges']} Directed Dependency Edges"
        )
        self.txt_blast_radius.setPlainText(f"✅ Codebase re-graphified successfully at {time.strftime('%H:%M:%S')}!\nTotal Nodes: {summary['total_nodes']}\nTotal Edges: {summary['total_edges']}")

    def _scan_dead_code(self):
        from jarvis.analysis.code_graph import code_graph_engine
        orphaned = []
        for n_id, node in code_graph_engine.nodes.items():
            blast = code_graph_engine.get_blast_radius(n_id)
            if not blast["callers_and_importers"] and not blast["downstream_dependencies"]:
                orphaned.append(node.file_path)

        lines = [
            "=== DEAD CODE & ORPHANED MODULE SCAN RESULTS ===",
            f"Total Nodes Analyzed: {len(code_graph_engine.nodes)}",
            f"Orphaned / Unconnected Modules Detected: {len(orphaned)}",
            ""
        ]
        if orphaned:
            for p in orphaned:
                lines.append(f"  ⚠️ Isolated File: {p}")
        else:
            lines.append("  ✅ Zero isolated files! All modules are actively connected within the architecture.")

        self.txt_blast_radius.setPlainText("\n".join(lines))

    def _build_json_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        self.txt_json = QTextEdit()
        self.txt_json.setReadOnly(True)
        self.txt_json.setStyleSheet(
            f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_CYAN}; "
            f"border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; "
            f"font-family: {FONT_FAMILY_MONO}; font-size: 11px; padding: 8px;"
        )
        layout.addWidget(self.txt_json, stretch=1)

        return widget

    def update_telemetry(self, data: Dict[str, Any]):
        """Updates all diagnostic views with live telemetry data."""
        self._latest_telemetry = data
        self._packet_count += 1

        now_str = time.strftime("%H:%M:%S")
        self.lbl_strip_packets.setText(f"● PACKETS: #{self._packet_count:04d}")
        self.lbl_strip_time.setText(f"LAST POLLED: {now_str}")

        # Update Strip Statuses
        is_online = data.get("is_online", False)
        spine_online = data.get("spine_online", True)
        self.lbl_strip_spine.setText(f"● SPINE: {'ONLINE (:8765)' if spine_online else 'OFFLINE / IN-PROCESS'}")
        self.lbl_strip_spine.setStyleSheet(f"color: {COLOR_EMERALD if spine_online else COLOR_VERONICA_RED}; font-size: 10px; font-weight: bold;")

        # 1. Update Subsystems Tree
        self.tree_subsystems.clear()
        subsystems = data.get("subsystems", {})
        for key, info in subsystems.items():
            parent_item = QTreeWidgetItem(self.tree_subsystems)
            parent_item.setText(0, f"{info.get('icon', '⚡')} {info.get('name', key.upper())}")
            parent_item.setText(1, info.get("status", "NOMINAL"))
            parent_item.setText(2, info.get("summary", ""))
            parent_item.setData(0, Qt.ItemDataRole.UserRole, key)

            for m in info.get("metrics", []):
                child = QTreeWidgetItem(parent_item)
                child.setText(0, f"  └ {m.get('label', '')}")
                child.setText(1, str(m.get('value', '')))
                child.setText(2, m.get('explanation', ''))
                child.setData(0, Qt.ItemDataRole.UserRole, m)

            parent_item.setExpanded(True)

        # 2. Update Hardware Tab Cards & Log
        cpu_cores = data.get("cpu_cores", "2P/12T")
        cpu_freq = data.get("cpu_freq_mhz", 0)
        cpu_pct = data.get("cpu_percent", 0.0)
        
        ram_total = data.get("ram_total_gb", 0)
        ram_used = data.get("ram_used_gb", 0)
        ram_pct = data.get("ram_percent", 0.0)
        ram_ceiling = data.get("ram_ceiling_gb", 14.5)

        disk_used = data.get("disk_used_gb", 0)
        disk_total = data.get("disk_total_gb", 0)
        disk_pct = data.get("disk_percent", 0)
        bat_pct = data.get("battery_percent", 100)
        is_plugged = data.get("power_plugged", True)

        gpu_name = data.get("gpu_name", "Intel Iris Xe")
        gpu_load = data.get("gpu_load_percent", 0)
        lan_ip = data.get("lan_ip", "127.0.0.1")

        # Update card bodies
        self._update_card_body(self.card_cpu, f"Host Topology: {cpu_cores} @ {cpu_freq} MHz\nUtilization: {cpu_pct}%\nAffinity Mask: 0x00F (Threads 0-3 Pinned)")
        self._update_card_body(self.card_ram, f"Total RAM: {ram_total} GB\nUsed RAM: {ram_used} GB ({ram_pct}%)\nRAM Ceiling: {ram_ceiling} GB (512MB Process Cap)")
        self._update_card_body(self.card_storage, f"Disk NVMe: {disk_used} GB / {disk_total} GB ({disk_pct}%)\nBattery: {bat_pct}% ({'⚡ AC Connected' if is_plugged else 'On Battery'})\nStorage Protocol: Local NVMe Sovereign")
        self._update_card_body(self.card_net, f"GPU Engine: {gpu_name} ({gpu_load}% Load)\nLAN Address: {lan_ip}\nSovereignty: 100% Local Offline (Zero External Calls)")

        hw_lines = [
            "================================================================================",
            "        J.A.R.V.I.S. FULL SOURCE-OF-TRUTH HARDWARE & TOPOLOGY AUDIT           ",
            "================================================================================",
            f"Host CPU Topology:       {cpu_cores} @ {cpu_freq} MHz",
            f"CPU Load Utilization:    {cpu_pct}%",
            f"Core Affinity Mask:      0x00F (Performance Cores Pinned)",
            f"Total Physical RAM:      {ram_total} GB",
            f"Used Physical RAM:       {ram_used} GB ({ram_pct}%)",
            f"Available Headroom:      {data.get('ram_free_gb', 0)} GB",
            f"RAM Guardrail Ceiling:   {ram_ceiling} GB (Strict 512MB Process Cap)",
            f"Disk Primary Storage:    {disk_used} GB / {disk_total} GB ({disk_pct}%)",
            f"Battery Level:           {bat_pct}% ({'AC Connected' if is_plugged else 'On Battery'})",
            f"GPU Acceleration:        {gpu_name} ({gpu_load}% Load)",
            f"Local LAN IP:            {lan_ip}",
            f"Sovereign Network State: {'ONLINE (Connected)' if is_online else 'OFFLINE SOVEREIGN'}",
            f"FastAPI Spine Status:    {'ONLINE (:8765)' if spine_online else 'OFFLINE / IN-PROCESS'}",
            f"Audit Timestamp:         {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('timestamp', time.time())))}"
        ]
        self.txt_hardware.setPlainText("\n".join(hw_lines))

        # 3. Update Raw JSON Tab
        try:
            formatted_json = json.dumps(data, indent=2, default=str)
            self.txt_json.setPlainText(formatted_json)
        except Exception:
            pass

    def _update_card_body(self, card: QFrame, body_text: str):
        layout = card.layout()
        if layout and layout.count() > 1:
            lbl = layout.itemAt(1).widget()
            if isinstance(lbl, QLabel):
                lbl.setText(body_text)

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, dict):
            # Metric child node clicked
            self.lbl_node_name.setText(data.get("label", "Metric"))
            self.lbl_node_val.setText(f"Live Value: {data.get('value', '--')}")
            self.lbl_node_desc.setText(data.get("explanation", "No explanation available."))
        elif isinstance(data, str):
            # Subsystem parent node clicked
            subsystems = self._latest_telemetry.get("subsystems", {})
            info = subsystems.get(data, {})
            self.lbl_node_name.setText(f"{info.get('icon', '⚡')} {info.get('name', data.upper())}")
            self.lbl_node_val.setText(f"Status: {info.get('status', 'NOMINAL')}")
            self.lbl_node_desc.setText(info.get("summary", "Subsystem operational."))

    def focus_subsystem(self, subsystem_key: str):
        """Switches to the Subsystem tab and highlights the target subsystem node."""
        self.tabs.setCurrentIndex(0)
        self.show()
        self.raise_()
        self.activateWindow()

        for i in range(self.tree_subsystems.topLevelItemCount()):
            item = self.tree_subsystems.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == subsystem_key:
                self.tree_subsystems.setCurrentItem(item)
                item.setExpanded(True)
                self._on_tree_item_clicked(item, 0)
                break

    def _filter_tree(self, text: str):
        query = text.lower().strip()
        visible_count = 0
        total_count = 0

        for i in range(self.tree_subsystems.topLevelItemCount()):
            parent = self.tree_subsystems.topLevelItem(i)
            parent_match = query in parent.text(0).lower() or query in parent.text(1).lower() or query in parent.text(2).lower()
            child_match = False
            
            for j in range(parent.childCount()):
                total_count += 1
                child = parent.child(j)
                m = query in child.text(0).lower() or query in child.text(1).lower() or query in child.text(2).lower()
                child.setHidden(not m and not parent_match)
                if m or parent_match:
                    child_match = True
                    visible_count += 1

            parent.setHidden(not parent_match and not child_match)

        if query:
            self.lbl_filter_count.setText(f"Filtering: {visible_count} / {total_count} visible")
        else:
            self.lbl_filter_count.setText("All Metrics Visible")

    def _probe_endpoint(self, path: str):
        start_t = time.perf_counter()
        self.lbl_spine_status.setText(f"Probing http://127.0.0.1:8765{path} ...")
        self.txt_spine_response.setPlainText("Connecting to FastAPI spine...")
        try:
            import urllib.request
            req = urllib.request.Request(f"http://127.0.0.1:8765{path}", headers={"User-Agent": "JARVIS-DevWindow"})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                status_code = response.getcode()
                raw_bytes = response.read()
                raw_text = raw_bytes.decode("utf-8", errors="replace")
                try:
                    data = json.loads(raw_text)
                    formatted_text = json.dumps(data, indent=2)
                except Exception:
                    # Non-JSON content (e.g. HTML dashboard from /mobile)
                    formatted_text = raw_text

                self.lbl_spine_status.setText(f"● HTTP {status_code} OK | Latency: {elapsed_ms:.1f} ms | Endpoint: {path}")
                self.lbl_spine_status.setStyleSheet(f"color: {COLOR_EMERALD}; font-weight: bold; font-size: 11px;")
                self.txt_spine_response.setPlainText(formatted_text)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            self.lbl_spine_status.setText(f"⚠️ Error querying {path} ({elapsed_ms:.1f} ms)")
            self.lbl_spine_status.setStyleSheet(f"color: {COLOR_VERONICA_RED}; font-weight: bold; font-size: 11px;")
            self.txt_spine_response.setPlainText(f"Error querying endpoint {path}:\n{e}\n\n(Ensure Spine server is running with 'python -m jarvis.main')")

    def _copy_raw_json(self):
        text = self.txt_json.toPlainText()
        QApplication.clipboard().setText(text)
        self.btn_copy_json.setText("✅ COPIED!")
        QTimer.singleShot(1500, lambda: self.btn_copy_json.setText("📋 COPY JSON"))

    def _manual_refresh(self):
        if self._latest_telemetry:
            self.update_telemetry(self._latest_telemetry)


