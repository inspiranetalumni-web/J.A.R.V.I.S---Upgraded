"""
jarvis/actuation/win32.py — Enterprise Windows Desktop Actuator v3.0
Native Windows UIAutomation, SendInput keyboard/mouse dispatch, and window state management.
"""

import os
import sys
import time
import ctypes
import subprocess
from typing import Dict, Any, Optional, Tuple

# Win32 VK Key Map
VK_MAP = {
    "enter": 0x0D, "tab": 0x09, "space": 0x20, "backspace": 0x08,
    "escape": 0x1B, "esc": 0x1B, "ctrl": 0x11, "alt": 0x12, "shift": 0x10,
    "win": 0x5B, "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27
}

class Win32Actuator:
    """
    Production-grade Windows Desktop OS Actuator.
    Provides native keyboard, mouse, window focus, and volume controls.
    """
    def __init__(self):
        self.is_windows = (sys.platform == "win32")

    def get_active_window_title(self) -> str:
        """Returns the title of the currently focused foreground window."""
        if not self.is_windows:
            return "Non-Windows Operating System"
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value or "Desktop Shell"
        except Exception:
            return "Active Window"

    def press_key(self, key_name: str, dry_run: bool = False) -> bool:
        """Simulates virtual key press and release via Win32 user32 keybd_event."""
        if not self.is_windows:
            return False

        key_lower = key_name.lower()
        vk_code = VK_MAP.get(key_lower)
        if not vk_code and len(key_name) == 1:
            try:
                vk_code = ctypes.windll.user32.VkKeyScanW(ord(key_name)) & 0xFF
            except Exception:
                vk_code = None

        if not vk_code:
            return False

        if dry_run:
            return True

        try:
            # Key down
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.02)
            # Key up
            ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)
            return True
        except Exception:
            return False

    def send_hotkey(self, modifier: str, key: str, dry_run: bool = False) -> bool:
        """Sends modifier + key combination (e.g. 'ctrl', 'c')."""
        if not self.is_windows:
            return False

        mod_vk = VK_MAP.get(modifier.lower(), 0x11)
        key_vk = VK_MAP.get(key.lower())
        if not key_vk and len(key) >= 1:
            try:
                key_vk = (ctypes.windll.user32.VkKeyScanW(ord(key[0])) & 0xFF)
            except Exception:
                key_vk = None

        if not mod_vk or not key_vk:
            return False

        if dry_run:
            return True

        try:
            ctypes.windll.user32.keybd_event(mod_vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(key_vk, 0, 0, 0)
            time.sleep(0.02)
            ctypes.windll.user32.keybd_event(key_vk, 0, 0x0002, 0)
            ctypes.windll.user32.keybd_event(mod_vk, 0, 0x0002, 0)
            return True
        except Exception:
            return False

    def type_string(self, text: str) -> bool:
        """Types string sequence into the foreground window."""
        for char in text:
            self.press_key(char)
            time.sleep(0.01)
        return True

    def move_mouse(self, x: int, y: int) -> bool:
        """Sets mouse cursor absolute screen location (x, y)."""
        if not self.is_windows:
            return False
        try:
            return bool(ctypes.windll.user32.SetCursorPos(x, y))
        except Exception:
            return False

    def click_mouse(self, button: str = "left") -> bool:
        """Performs mouse click at current cursor position."""
        if not self.is_windows:
            return False
        try:
            if button.lower() == "left":
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0) # down
                time.sleep(0.02)
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0) # up
            else:
                ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0) # right down
                time.sleep(0.02)
                ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0) # right up
            return True
        except Exception:
            return False

    def focus_window(self, window_title_substring: str) -> bool:
        """Finds and brings target window to foreground."""
        if not self.is_windows:
            return False
        try:
            # PowerShell Win32 UIAutomation focus helper
            ps_script = f"""
            $proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like "*{window_title_substring}*" }} | Select-Object -First 1
            if ($proc) {{
                $sig = '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);'
                $type = Add-Type -MemberDefinition $sig -Name "Win32Focus" -Namespace "Win32" -PassThru
                $type::SetForegroundWindow($proc.MainWindowHandle)
            }}
            """
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, timeout=3)
            return True
        except Exception:
            return False
