# 🖥️ Control Center HUD & 3D Holographic Canvas Skills — J.A.R.V.I.S. v3.0

> **Standard:** Stark Horizon v3.0 / v3.1  
> **Canvas Core:** `jarvis/control_center/widgets/voice_orb.py` (`VoiceOrbWidget`, `OrbDisplayMode`)  
> **Top Bar Spine:** `jarvis/control_center/widgets/top_bar.py` (`TopBarWidget`)  
> **Bottom Spine:** `jarvis/control_center/widgets/bottom_panel.py` (`BottomPanelWidget`)  
> **Theme Tokens:** `jarvis/control_center/theme.py`

---

## 1. 3D Holographic Canvas Architecture

The **VoiceOrbWidget** is an interactive, full-viewport 3D canvas featuring mathematical perspective projections, 48-band radial audio equalization, quantum orbital particle constellations, and sovereign AST code graph visualization.

```
                    ┌────────────────────────────────────────────────────────┐
                    │               3D Holographic Canvas                    │
                    │      (jarvis/control_center/widgets/voice_orb.py)      │
                    └──────────────────────────┬─────────────────────────────┘
                                               │
       ┌──────────────────────────┬────────────┴────────────┬──────────────────────────┐
       ▼                          ▼                         ▼                          ▼
  🎙️ Mode 1: Voice Orb       🕸️ Mode 2: Code Graph     ⚡ Mode 3: Hybrid         🔍 Navigation
  • 48 Radial Equalizer      • 3D AST Code Nodes       • Speech waves radiating   • Left-Drag Orbit
  • 32 Quantum Particles     • Clustered Filaments     • Through active code      • Right-Drag Pan
  • Outer Compass HUD Ring   • Dynamic Cluster Colors  • Graph branches           • Cursor-Centered Zoom
```

---

## 2. Interactive 2D & 3D Canvas Navigation

The canvas implements fluid camera kinematics inspired by 3D CAD, Google Earth, and image viewers:

| Gesture / Event | Action | Behavior & Coordinate Update |
|---|---|---|
| **Left-Click + Drag** | **3D Orbiting** | Rotates camera Euler angles: $\text{yaw} \leftarrow \text{yaw} + \Delta x \cdot 0.008$, $\text{pitch} \leftarrow \text{pitch} - \Delta y \cdot 0.008$. |
| **Right-Click + Drag** | **2D Canvas Pan** | Panning camera center: $\text{pan}_x \leftarrow \text{pan}_x + \Delta x$, $\text{pan}_y \leftarrow \text{pan}_y + \Delta y$. |
| **Shift + Left-Click Drag** | **2D Canvas Pan** | Alternative modifier for single-button or trackpad panning. |
| **Mouse Scroll Wheel** | **Cursor-Centered Zoom** | Zooms scale ($0.3\times$ to $5.0\times$) while offsetting pan relative to cursor so zoom focuses under mouse. |
| **Hover on Node** | **Freeze on Hover** | Temporarily halts sphere rotation ($\text{speed\_mult} = 0.0$) and renders floating metadata tooltip. |
| **Double-Click Node** | **AST Inspector** | Opens `CodeGraphDetailDialog` displaying complete AST classes, methods, docstrings, and blast radius. |
| **Double-Click Canvas** | **Reset View** | Resets camera zoom to $1.0\times$, pan to $(0,0)$, and default pitch. |

---

## 3. Top Header Bar Symmetrical 3-Column Layout

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ✦ J.A.R.V.I.S. CONTROL CENTER    │   MODE: [BALANCED] [SURVIVAL] [TURBO] [AUTO] [ℹ]  │  ● LOCAL SOVEREIGN │ 11:22:22  │
│    STARK HORIZON OS // 100% LOCAL  │                                                   │                    │ 2026-09-01│
└───────────────────────────────────┴───────────────────────────────────────────────────┴────────────────────────────┘
        [LEFT: Brand & OS]                      [CENTER: Centered Mode Selector]               [RIGHT: Status & Clock]
```

### A. Column Structure
1. **Left Column (Brand & OS Core):**
   - Glowing cyan beacon `✦` + Title `J.A.R.V.I.S. CONTROL CENTER` + Subtitle `STARK HORIZON OS // 100% LOCAL SOVEREIGN AI`.
2. **Center Column (Centered Cognitive Operating Mode Selector):**
   - Positioned in exact visual center between symmetrical spring stretches (`layout.addStretch(1)`).
   - Glassmorphic segmented pill: `[ BALANCED ] [ SURVIVAL ] [ TURBO ] [ AUTO ]` + `[ ℹ️ ]`.
   - Double-clicking or clicking `ℹ️` launches the **Model Information Dialog**.
3. **Right Column (Sovereign Telemetry & Cyber Clock):**
   - Status Pill: `● LOCAL SOVEREIGN` (emerald) / `● ONLINE CONNECTED` (cyan).
   - Cyber Vertical Divider: `QFrame(VLine)`.
   - Monospace cyber digital clock (`Consolas`) with calendar date.

---

## 4. Master Theme Tokens & Colors

```python
COLOR_CYAN = "#00f0ff"          # Primary Stark Horizon Accent
COLOR_CYAN_GLOW = "#38bdf8"     # Holographic Glow
COLOR_CYAN_DIM = "#0284c7"      # Subtle Wireframes
COLOR_EMERALD = "#00ffaa"       # Nominal / Voice Active / Sovereign
COLOR_AMBER = "#ffaa00"         # Muted / Warnings
COLOR_VERONICA_RED = "#ff0055"  # Protocol VERONICA / Security Alert
COLOR_BG_DARK = "#0b1528"       # Deep Cosmic Glass
```
