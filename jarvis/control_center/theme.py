"""
jarvis/control_center/theme.py — Futuristic Stark Cosmic Glass Theme & Design Tokens
Provides luminous cosmic sapphire glassmorphism color palettes, glowing neon accents,
font definitions, and master QSS stylesheets for Qt PySide6 with zero solid black rectangles.
"""

# Core Color Palette (Stark Cosmic Sapphire Standard)
COLOR_BG_DARK = "#0a192f"
COLOR_BG_SURFACE = "#0f2347"
COLOR_BG_CARD = "rgba(16, 36, 70, 0.58)"
COLOR_BG_CARD_HOVER = "rgba(24, 52, 100, 0.80)"
COLOR_BG_INSET = "rgba(20, 48, 92, 0.48)"
COLOR_BG_INPUT = "rgba(18, 40, 78, 0.55)"
COLOR_BG_TRANSLUCENT = "rgba(15, 35, 71, 0.85)"

COLOR_CYAN = "#00f0ff"
COLOR_CYAN_DIM = "#00a2b8"
COLOR_CYAN_GLOW = "#33f3ff"
COLOR_BLUE = "#00a8ff"
COLOR_EMERALD = "#00ffaa"
COLOR_AMBER = "#ffaa00"
COLOR_VERONICA_RED = "#ff0055"
COLOR_RED_DIM = "#990033"

COLOR_TEXT_PRIMARY = "#f1f5f9"
COLOR_TEXT_SECONDARY = "#94a3b8"
COLOR_TEXT_MUTED = "#64748b"
COLOR_TEXT_CYAN = "#00f0ff"

COLOR_BORDER_NORMAL = "rgba(0, 240, 255, 0.16)"
COLOR_BORDER_GLOW = "#00f0ff"
COLOR_BORDER_CARD = "rgba(0, 240, 255, 0.22)"
COLOR_BORDER_SUBTLE = "rgba(0, 240, 255, 0.12)"

FONT_FAMILY_UI = "Segoe UI, Inter, -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif"
FONT_FAMILY_MONO = "Consolas, 'Cascadia Code', 'JetBrains Mono', 'Courier New', monospace"

MASTER_STYLESHEET = f"""
/* Master Stark Cosmic Sapphire Glass QSS Stylesheet */

QWidget {{
    background-color: transparent;
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY_UI};
    font-size: 13px;
    selection-background-color: {COLOR_CYAN_DIM};
    selection-color: #ffffff;
}}

QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a192f, stop:0.4 #0c1e3c, stop:1 #0e2448);
}}

QFrame#cardFrame {{
    background-color: rgba(16, 36, 70, 0.58);
    border: 1px solid rgba(0, 240, 255, 0.22);
    border-radius: 8px;
}}

QFrame#cardFrame:hover {{
    border: 1px solid rgba(0, 240, 255, 0.40);
    background-color: rgba(22, 48, 92, 0.70);
}}

QFrame#headerFrame {{
    background-color: rgba(15, 35, 71, 0.88);
    border-bottom: 1px solid rgba(0, 240, 255, 0.25);
}}

QFrame#bottomFrame {{
    background-color: rgba(15, 35, 71, 0.88);
    border-top: 1px solid rgba(0, 240, 255, 0.25);
}}

/* Push Buttons */
QPushButton {{
    background-color: rgba(18, 40, 78, 0.65);
    color: {COLOR_CYAN};
    border: 1px solid rgba(0, 240, 255, 0.35);
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}}

QPushButton:hover {{
    background-color: rgba(0, 240, 255, 0.22);
    border: 1px solid {COLOR_CYAN};
    color: #ffffff;
}}

QPushButton:pressed {{
    background-color: rgba(0, 240, 255, 0.38);
    border: 1px solid {COLOR_CYAN_GLOW};
}}

QPushButton:disabled {{
    background-color: rgba(16, 32, 60, 0.40);
    color: {COLOR_TEXT_MUTED};
    border: 1px solid rgba(255, 255, 255, 0.08);
}}

QPushButton#dangerBtn {{
    background-color: rgba(255, 0, 85, 0.15);
    color: {COLOR_VERONICA_RED};
    border: 1px solid {COLOR_VERONICA_RED};
}}

QPushButton#dangerBtn:hover {{
    background-color: rgba(255, 0, 85, 0.32);
    color: #ffffff;
}}

QPushButton#successBtn {{
    background-color: rgba(0, 255, 170, 0.15);
    color: {COLOR_EMERALD};
    border: 1px solid {COLOR_EMERALD};
}}

QPushButton#successBtn:hover {{
    background-color: rgba(0, 255, 170, 0.32);
    color: #ffffff;
}}

/* Mode Switcher Buttons */
QPushButton#modeBtn {{
    background-color: rgba(16, 36, 70, 0.65);
    color: {COLOR_TEXT_SECONDARY};
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: bold;
}}

QPushButton#modeBtn:hover {{
    color: {COLOR_CYAN};
    background-color: rgba(0, 240, 255, 0.14);
}}

QPushButton#modeBtn[active="true"], QPushButton#modeBtn:checked {{
    background-color: rgba(0, 240, 255, 0.22);
    color: {COLOR_CYAN};
    border: 1px solid {COLOR_CYAN};
}}

/* Scrollbars: Minimalist Auto-Hide / Sleek Floating Style */
QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(0, 240, 255, 0.25);
    min-height: 24px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLOR_CYAN};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    background: transparent;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    height: 0px;
}}

/* Scroll Areas */
QScrollArea {{
    background: transparent;
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
    background-color: transparent;
}}

/* Subsystem Status Cards */
QFrame#statusCard {{
    background-color: rgba(18, 38, 72, 0.55);
    border: 1px solid rgba(0, 240, 255, 0.20);
    border-radius: 6px;
}}

QFrame#statusCard:hover {{
    background-color: rgba(26, 54, 102, 0.75);
    border: 1px solid rgba(0, 240, 255, 0.45);
}}

QFrame#statusCard QLabel {{
    background: transparent;
    background-color: transparent;
}}

/* Labels (Default transparent background to prevent dark artifacts) */
QLabel {{
    background: transparent;
    background-color: transparent;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel#brandTitle {{
    color: {COLOR_CYAN};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 1.5px;
}}

QLabel#brandSub {{
    color: {COLOR_TEXT_MUTED};
    font-size: 10px;
    letter-spacing: 1px;
}}

QLabel#sectionTitle {{
    color: {COLOR_CYAN};
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

QLabel#monoValue {{
    font-family: {FONT_FAMILY_MONO};
    font-size: 13px;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel#monoValueCyan {{
    font-family: {FONT_FAMILY_MONO};
    font-size: 13px;
    color: {COLOR_CYAN};
    font-weight: bold;
}}

/* Quick Action Chips */
QPushButton#quickChip {{
    background-color: rgba(20, 44, 84, 0.70);
    color: {COLOR_TEXT_SECONDARY};
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 11px;
    padding: 3px 10px;
    font-size: 10.5px;
    font-weight: 600;
}}

QPushButton#quickChip:hover {{
    background-color: rgba(0, 240, 255, 0.20);
    color: {COLOR_CYAN};
    border: 1px solid {COLOR_CYAN};
}}

QPushButton#quickChip:pressed {{
    background-color: rgba(0, 240, 255, 0.35);
    color: #ffffff;
}}

/* Micro Progress Bars */
QProgressBar {{
    background-color: rgba(16, 36, 70, 0.65);
    border: 1px solid rgba(0, 240, 255, 0.20);
    border-radius: 3px;
    text-align: center;
    color: transparent;
    max-height: 6px;
    min-height: 6px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLOR_CYAN_DIM}, stop:1 {COLOR_CYAN});
    border-radius: 2px;
}}

/* Text / Scroll Areas */
QTextEdit, QPlainTextEdit {{
    background-color: rgba(18, 40, 78, 0.50);
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid rgba(0, 240, 255, 0.22);
    border-radius: 6px;
    font-family: {FONT_FAMILY_MONO};
    font-size: 12px;
    padding: 8px;
}}

QToolTip {{
    background-color: rgba(15, 35, 71, 0.95);
    color: {COLOR_CYAN};
    border: 1px solid {COLOR_CYAN_DIM};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}}
"""

