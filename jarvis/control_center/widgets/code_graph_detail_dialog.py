"""
jarvis/control_center/widgets/code_graph_detail_dialog.py — Stark HUD AST Node Inspector Dialog
Displays 100% real backend AST metadata for any inspected code graph node:
- Real class definitions and methods
- Real top-level functions and parameter signatures
- Direct imports and downstream dependencies
- Inbound callers and blast radius impact analysis
"""

from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QListWidget, QListWidgetItem, QTextEdit, QFrame,
    QApplication, QHeaderView, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from jarvis.control_center.theme import (
    MASTER_STYLESHEET, COLOR_CYAN, COLOR_CYAN_DIM, COLOR_CYAN_GLOW,
    COLOR_EMERALD, COLOR_AMBER, COLOR_VERONICA_RED, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, FONT_FAMILY_MONO
)
from jarvis.analysis.code_graph import code_graph_engine, CodeGraphNode

class CodeGraphDetailDialog(QDialog):
    """
    Stark HUD pop-up dialog providing deep AST inspection of a codebase module.
    """
    def __init__(self, node_id: str, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.node = code_graph_engine.nodes.get(node_id)

        self.setWindowTitle(f"J.A.R.V.I.S. AST Node Inspector // {node_id}")
        self.resize(780, 560)
        self.setStyleSheet(MASTER_STYLESHEET + f"""
            QDialog {{
                background-color: #0b1528;
                border: 1px solid rgba(0, 240, 255, 0.35);
            }}
            QTabWidget::pane {{
                background-color: rgba(16, 36, 70, 0.58);
                border: 1px solid rgba(0, 240, 255, 0.22);
                border-radius: 6px;
                padding: 6px;
            }}
            QTabBar::tab {{
                background: rgba(15, 35, 71, 0.85);
                color: {COLOR_TEXT_SECONDARY};
                padding: 7px 16px;
                border: 1px solid rgba(0, 240, 255, 0.20);
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                font-size: 11px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: rgba(22, 52, 102, 0.95);
                color: {COLOR_CYAN};
                border: 1px solid {COLOR_CYAN};
                border-bottom: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 12)
        layout.setSpacing(10)

        if not self.node:
            lbl_err = QLabel(f"AST Node '{node_id}' not found in active graph.")
            lbl_err.setStyleSheet(f"color: {COLOR_VERONICA_RED}; font-size: 13px; font-weight: bold;")
            layout.addWidget(lbl_err)
            return

        blast = code_graph_engine.get_blast_radius(self.node_id)
        cluster_hex = code_graph_engine.CLUSTER_COLORS.get(self.node.cluster, COLOR_CYAN)

        # 1. Header Card with Module Title & Cluster Badge
        header_card = QFrame()
        header_card.setStyleSheet("background-color: rgba(18, 42, 82, 0.65); border: 1px solid rgba(0, 240, 255, 0.30); border-radius: 6px;")
        hdr_layout = QVBoxLayout(header_card)
        hdr_layout.setContentsMargins(12, 10, 12, 10)
        hdr_layout.setSpacing(4)

        title_row = QHBoxLayout()
        lbl_icon = QLabel("📦")
        lbl_icon.setStyleSheet("font-size: 16px;")
        title_row.addWidget(lbl_icon)

        lbl_title = QLabel(f"{self.node.label}.py")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #ffffff; letter-spacing: 0.5px;")
        title_row.addWidget(lbl_title)

        title_row.addStretch()

        lbl_cluster = QLabel(f"● {self.node.cluster.upper()}")
        lbl_cluster.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_cluster.setStyleSheet(f"color: {cluster_hex}; background: rgba(0,0,0,0.3); border: 1px solid {cluster_hex}; border-radius: 10px; padding: 3px 10px;")
        title_row.addWidget(lbl_cluster)

        hdr_layout.addLayout(title_row)

        lbl_path = QLabel(f"File Path: {self.node.file_path}")
        lbl_path.setFont(QFont("Consolas", 9))
        lbl_path.setStyleSheet(f"color: {COLOR_CYAN};")
        hdr_layout.addWidget(lbl_path)

        lbl_stats = QLabel(
            f"Metrics: {self.node.line_count} Lines  |  {self.node.file_size_bytes / 1024.0:.1f} KB on Disk  |  "
            f"{len(self.node.classes)} Classes  |  {len(self.node.functions)} Functions  |  "
            f"Blast Radius Impact: {blast['total_impact_count']} Links"
        )
        lbl_stats.setFont(QFont("Segoe UI", 8))
        lbl_stats.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        hdr_layout.addWidget(lbl_stats)

        lbl_doc = QLabel(f"Summary: {self.node.summary}")
        lbl_doc.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_doc.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_doc.setWordWrap(True)
        hdr_layout.addWidget(lbl_doc)

        layout.addWidget(header_card)

        # 2. Main Tabs
        tabs = QTabWidget()

        # Tab 1: Classes & Methods
        tab_classes = QWidget()
        l_c = QVBoxLayout(tab_classes)
        l_c.setContentsMargins(6, 6, 6, 6)
        tree_classes = QTreeWidget()
        tree_classes.setHeaderLabels(["Class / Method", "Type / Docstring"])
        tree_classes.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        tree_classes.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tree_classes.setColumnWidth(0, 240)
        tree_classes.setStyleSheet(f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_TEXT_PRIMARY}; font-size: 11px;")

        if self.node.classes:
            for cls in self.node.classes:
                p = QTreeWidgetItem(tree_classes)
                p.setText(0, f"🏛️ class {cls['name']}")
                p.setText(1, cls.get("doc", ""))
                p.setFont(0, QFont("Segoe UI", 9, QFont.Weight.Bold))
                p.setForeground(0, QColor(COLOR_CYAN))
                for m in cls.get("methods", []):
                    c = QTreeWidgetItem(p)
                    c.setText(0, f"  └ def {m}()")
                    c.setText(1, "Method")
                p.setExpanded(True)
        else:
            p = QTreeWidgetItem(tree_classes)
            p.setText(0, "(No classes defined in this module)")
            p.setText(1, "")

        l_c.addWidget(tree_classes)
        tabs.addTab(tab_classes, f"🏛️ Classes ({len(self.node.classes)})")

        # Tab 2: Top-Level Functions
        tab_fn = QWidget()
        l_f = QVBoxLayout(tab_fn)
        l_f.setContentsMargins(6, 6, 6, 6)
        list_fn = QListWidget()
        list_fn.setStyleSheet(f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_EMERALD}; font-family: {FONT_FAMILY_MONO}; font-size: 11px;")
        if self.node.functions:
            for fn in self.node.functions:
                args_str = ", ".join(fn.get("args", []))
                doc_str = f" — {fn.get('doc', '')}" if fn.get("doc") else ""
                list_fn.addItem(f"def {fn['name']}({args_str}){doc_str}")
        else:
            list_fn.addItem("(No top-level functions defined)")
        l_f.addWidget(list_fn)
        tabs.addTab(tab_fn, f"⚙️ Functions ({len(self.node.functions)})")

        # Tab 3: Direct Dependencies (Imports)
        tab_deps = QWidget()
        l_d = QVBoxLayout(tab_deps)
        l_d.setContentsMargins(6, 6, 6, 6)
        list_deps = QListWidget()
        list_deps.setStyleSheet(f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_CYAN}; font-family: {FONT_FAMILY_MONO}; font-size: 11px;")
        if blast["downstream_dependencies"]:
            for dep in sorted(blast["downstream_dependencies"]):
                list_deps.addItem(f"➜ {dep}")
        else:
            list_deps.addItem("(No internal jarvis dependencies)")
        l_d.addWidget(list_deps)
        tabs.addTab(tab_deps, f"🔗 Dependencies ({len(blast['downstream_dependencies'])})")

        # Tab 4: Incoming Callers & Blast Radius
        tab_callers = QWidget()
        l_call = QVBoxLayout(tab_callers)
        l_call.setContentsMargins(6, 6, 6, 6)
        list_callers = QListWidget()
        list_callers.setStyleSheet(f"background-color: rgba(18, 40, 78, 0.50); color: {COLOR_AMBER}; font-family: {FONT_FAMILY_MONO}; font-size: 11px;")
        if blast["callers_and_importers"]:
            for caller in sorted(blast["callers_and_importers"]):
                list_callers.addItem(f"⬅ {caller}")
        else:
            list_callers.addItem("(Leaf / Root module — zero incoming internal callers)")
        l_call.addWidget(list_callers)
        tabs.addTab(tab_callers, f"💥 Inbound Callers ({len(blast['callers_and_importers'])})")

        layout.addWidget(tabs, stretch=1)

        # 3. Bottom Action Bar
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self.btn_copy_path = QPushButton("📋 COPY FILE PATH")
        self.btn_copy_path.setObjectName("quickChip")
        self.btn_copy_path.clicked.connect(self._copy_path)
        action_bar.addWidget(self.btn_copy_path)

        action_bar.addStretch()

        self.btn_close = QPushButton("✕ CLOSE")
        self.btn_close.setObjectName("quickChip")
        self.btn_close.clicked.connect(self.accept)
        action_bar.addWidget(self.btn_close)

        layout.addLayout(action_bar)

    def _copy_path(self):
        if self.node:
            QApplication.clipboard().setText(self.node.file_path)
            self.btn_copy_path.setText("✅ PATH COPIED!")
            QTimer.singleShot(1500, lambda: self.btn_copy_path.setText("📋 COPY FILE PATH"))
