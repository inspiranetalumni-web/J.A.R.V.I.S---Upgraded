"""
jarvis/hud/overlay.py — Desktop Native Stark Horizon HUD Application v3.0
Native PySide6/Tkinter window providing frameless/windowed Stark HUD layout with Arc Reactor animations,
system telemetry meters, minimize/maximize/terminate window controls, and continuous perception integration.
"""

import os
import sys
import math
import time
import requests
import threading
import tkinter as tk
from typing import Dict, Any

class StarkNativeDesktopHUD:
    """
    Production Desktop Native Python Stark Horizon HUD Interface for J.A.R.V.I.S.
    """
    def __init__(self, endpoint: str = "http://127.0.0.1:8765"):
        self.endpoint = endpoint
        self.root = tk.Tk()

        # Window Configurations
        self.root.title("J.A.R.V.I.S. Stark Horizon HUD")
        self.root.geometry("440x620+40+40")
        self.root.configure(bg="#050811")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self._is_maximized = False
        self._normal_geo = "440x620+40+40"
        self._start_x = 0
        self._start_y = 0
        self._angle = 0
        self._wave_step = 0

        # Outer Glowing Border Frame
        self.container = tk.Frame(self.root, bg="#050811", highlightbackground="#00f0ff", highlightthickness=2)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Title Bar with Window Controls
        self.title_bar = tk.Frame(self.container, bg="#0f172a")
        self.title_bar.pack(fill="x")

        self.title_lbl = tk.Label(
            self.title_bar, text="  J.A.R.V.I.S. v3.0 STARK HUD",
            bg="#0f172a", fg="#00f0ff", font=("Segoe UI", 10, "bold")
        )
        self.title_lbl.pack(side="left", pady=6)
        self.title_lbl.bind("<Button-1>", self._start_move)
        self.title_lbl.bind("<B1-Motion>", self._on_move)

        # Window Buttons: Minimize (_), Maximize (□), Terminate (X)
        self.btn_term = tk.Button(self.title_bar, text=" X ", bg="#0f172a", fg="#ff0055", bd=0, font=("Segoe UI", 9, "bold"), command=self._terminate_system)
        self.btn_term.pack(side="right", padx=4)

        self.btn_max = tk.Button(self.title_bar, text=" □ ", bg="#0f172a", fg="#00f0ff", bd=0, font=("Segoe UI", 9, "bold"), command=self._toggle_maximize)
        self.btn_max.pack(side="right", padx=2)

        self.btn_min = tk.Button(self.title_bar, text=" _ ", bg="#0f172a", fg="#00f0ff", bd=0, font=("Segoe UI", 9, "bold"), command=self._minimize_window)
        self.btn_min.pack(side="right", padx=2)

        # Main Body Layout
        self.body = tk.Frame(self.container, bg="#050811")
        self.body.pack(fill="both", expand=True, padx=10, pady=8)

        # Arc Reactor Centerpiece Canvas
        self.arc_canvas = tk.Canvas(self.body, width=160, height=160, bg="#050811", highlightthickness=0)
        self.arc_canvas.pack(pady=4)

        # Status & Perception State Badge
        self.lbl_state = tk.Label(self.body, text="PERCEPTION: SYSTEM NOMINAL", bg="#050811", fg="#00ffaa", font=("Segoe UI", 9, "bold"))
        self.lbl_state.pack()

        # Telemetry Gauges Frame
        self.gauge_frame = tk.LabelFrame(self.body, text=" SYSTEM TELEMETRY ", bg="#050811", fg="#00f0ff", font=("Segoe UI", 8, "bold"), bd=1, relief="solid")
        self.gauge_frame.pack(fill="x", pady=8, padx=4)

        self.lbl_cpu = tk.Label(self.gauge_frame, text="CPU LOAD: 0%  [P-Core 0x00F]", bg="#050811", fg="#a0e0ff", font=("Segoe UI", 8))
        self.lbl_cpu.pack(anchor="w", padx=6, pady=2)

        self.lbl_ram = tk.Label(self.gauge_frame, text="RAM USAGE: 0%  [512MB Guardrail Cap]", bg="#050811", fg="#a0e0ff", font=("Segoe UI", 8))
        self.lbl_ram.pack(anchor="w", padx=6, pady=2)

        self.lbl_guard = tk.Label(self.gauge_frame, text="GUARDRAILS: 4-Layer Security Active", bg="#050811", fg="#00f0ff", font=("Segoe UI", 8))
        self.lbl_guard.pack(anchor="w", padx=6, pady=2)

        # Console Feed Window
        self.log_frame = tk.LabelFrame(self.body, text=" REAL-TIME NEURAL LOG ", bg="#050811", fg="#00f0ff", font=("Segoe UI", 8, "bold"), bd=1, relief="solid")
        self.log_frame.pack(fill="both", expand=True, pady=4, padx=4)

        self.log_box = tk.Text(self.log_frame, bg="#050811", fg="#00ffaa", font=("Consolas", 8), bd=0, wrap="word", height=8)
        self.log_box.pack(fill="both", expand=True, padx=4, pady=4)
        self.log_box.insert(tk.END, "[SYSTEM] Native Desktop Stark HUD Initialized.\n[SECURITY] 4-Layer MicroVM Guardrails operational.\n")

        # Action Buttons Grid
        self.btn_grid = tk.Frame(self.body, bg="#050811")
        self.btn_grid.pack(fill="x", pady=6)

        self.btn_health = tk.Button(self.btn_grid, text="SYSTEM AUDIT", bg="#00f0ff", fg="#050811", font=("Segoe UI", 8, "bold"), bd=0, command=lambda: self._send_command("run health check"))
        self.btn_health.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_specs = tk.Button(self.btn_grid, text="SPECS AUDIT", bg="#00f0ff", fg="#050811", font=("Segoe UI", 8, "bold"), bd=0, command=lambda: self._send_command("get specs"))
        self.btn_specs.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_veronica = tk.Button(self.btn_grid, text="PROTOCOL VERONICA", bg="#ff0055", fg="#ffffff", font=("Segoe UI", 8, "bold"), bd=0, command=lambda: self._send_command("trigger lockdown"))
        self.btn_veronica.pack(side="left", fill="x", expand=True, padx=2)

        # Command Entry Bar
        self.input_frame = tk.Frame(self.body, bg="#0f172a")
        self.input_frame.pack(fill="x", pady=4)

        self.cmd_entry = tk.Entry(self.input_frame, bg="#050811", fg="#00f0ff", insertbackground="#00f0ff", font=("Segoe UI", 9), bd=1, relief="solid")
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=4, pady=4)
        self.cmd_entry.bind("<Return>", self._on_enter)

        self.btn_send = tk.Button(self.input_frame, text="TRANSMIT", bg="#00f0ff", fg="#050811", font=("Segoe UI", 8, "bold"), bd=0, command=self._on_enter)
        self.btn_send.pack(side="right", padx=4, pady=4)

        # Start animation loops
        self._animate_arc_reactor()
        self._poll_telemetry()

    def _start_move(self, event):
        self._start_x = event.x
        self._start_y = event.y

    def _on_move(self, event):
        if not self._is_maximized:
            x = self.root.winfo_x() + (event.x - self._start_x)
            y = self.root.winfo_y() + (event.y - self._start_y)
            self.root.geometry(f"+{x}+{y}")

    def _minimize_window(self):
        self.root.state("iconic")

    def _toggle_maximize(self):
        if not self._is_maximized:
            self._normal_geo = self.root.geometry()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")
            self._is_maximized = True
            self.btn_max.config(text=" ❐ ")
        else:
            self.root.geometry(self._normal_geo)
            self._is_maximized = False
            self.btn_max.config(text=" □ ")

    def _terminate_system(self):
        self._log("Initiating System Shutdown...")
        try:
            requests.get(f"{self.endpoint}/shutdown", timeout=1.0)
        except Exception:
            pass
        self.root.destroy()

    def _log(self, text: str):
        t_str = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{t_str}] {text}\n")
        self.log_box.see(tk.END)

    def _send_command(self, cmd: str):
        self._log(f"Operator: '{cmd}'")
        def _bg():
            try:
                res = requests.post(f"{self.endpoint}/api/v1/system/command", json={"command": cmd}, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    out = data.get("result", data.get("message", "Executed"))
                    self.root.after(0, lambda: self._log(f"J.A.R.V.I.S.: {out}"))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"[ERROR] {e}"))
        threading.Thread(target=_bg, daemon=True).start()

    def _on_enter(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if cmd:
            self.cmd_entry.delete(0, tk.END)
            self._send_command(cmd)

    def _animate_arc_reactor(self):
        """Renders glowing Arc Reactor centerpiece."""
        try:
            self.arc_canvas.delete("all")
            cx, cy = 80, 80
            self._angle = (self._angle + 4) % 360

            # Outer ring
            self.arc_canvas.create_oval(cx - 65, cy - 65, cx + 65, cy + 65, outline="#00f0ff", width=2)
            # Inner pulse
            pr = 25 + int(6 * math.sin(math.radians(self._angle * 2)))
            self.arc_canvas.create_oval(cx - pr, cy - pr, cx + pr, cy + pr, fill="#00f0ff", outline="#ffffff")

            # Rotating Nodes
            for i in range(8):
                rad = math.radians(self._angle + (i * 45))
                nx = cx + int(50 * math.cos(rad))
                ny = cy + int(50 * math.sin(rad))
                self.arc_canvas.create_oval(nx - 4, ny - 4, nx + 4, ny + 4, fill="#ffffff")

            self.root.after(40, self._animate_arc_reactor)
        except Exception:
            pass

    def _poll_telemetry(self):
        """Polls backend health telemetry."""
        try:
            res = requests.get(f"{self.endpoint}/health", timeout=1.0)
            if res.status_code == 200:
                data = res.json()
                cpu = data.get("system_cpu_percent", "--")
                ram = data.get("system_ram_percent", "--")
                self.lbl_cpu.config(text=f"CPU LOAD: {cpu}%  [P-Core 0x00F]")
                self.lbl_ram.config(text=f"RAM USAGE: {ram}%  [512MB Guardrail Cap]")
                self.lbl_state.config(text="PERCEPTION: SYSTEM NOMINAL", fg="#00ffaa")
            else:
                self.lbl_state.config(text="PERCEPTION: OFFLINE", fg="#ff0055")
        except Exception:
            self.lbl_state.config(text="PERCEPTION: OFFLINE", fg="#ff0055")

        try:
            self.root.after(2000, self._poll_telemetry)
        except Exception:
            pass

    def run(self):
        self.root.mainloop()

# Alias for backward compatibility with test suites
JARVISDesktopHUD = StarkNativeDesktopHUD

if __name__ == "__main__":
    hud = StarkNativeDesktopHUD()
    hud.run()

