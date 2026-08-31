# Agent: OS Actuation Agent v2.0 — Desktop & IoT Commander
### *"The mind directs. The hands execute. Both must be reliable."*

**Capabilities:** Win32 SendInput, UIAutomation, Home Assistant WebSocket, Zigbee2MQTT  
**Input Latency:** Win32 < 1ms | UIA find: 8ms | IoT HTTP: 8-15ms  
**Safety:** All mutating desktop/IoT actions require HITL approval

---

## 1. Action Classification

| Action Type | Classification | Mechanism | Latency |
| :--- | :--- | :--- | :--- |
| `open_app("VS Code")` | HITL | ShellExecute | ~50ms |
| `click_element(desc)` | HITL | UIA / Win32 | ~9ms |
| `type_text(str)` | HITL | Win32 SendInput | ~1ms |
| `get_clipboard()` | Autonomous | `pyperclip` | ~1ms |
| `read_screen()` | Autonomous | DXGI + moondream | ~180ms |
| `smart_home_get(entity)` | Autonomous | HA REST GET | ~8ms |
| `smart_home_set(entity)` | HITL | HA REST POST | ~15ms |
| `toggle_lights(area)` | HITL | HA service call | ~15ms |

---

## 2. Core Implementation

```python
# jarvis/actuation/os_agent.py — OS Actuation Agent core
import subprocess, ctypes, requests, asyncio

class OSActuationAgent:
    """Routes OS actions to Win32, UIAutomation, or Home Assistant."""
    
    def open_application(self, app_name: str) -> bool:
        """Open a Windows application by name (requires HITL)."""
        app_map = {
            "vs code": r"code.exe",
            "vscode": r"code.exe",
            "notepad": r"notepad.exe",
            "terminal": r"wt.exe",           # Windows Terminal
            "powershell": r"pwsh.exe",
            "n8n": r"http://127.0.0.1:5678", # Open in browser
        }
        target = app_map.get(app_name.lower())
        if not target:
            return False
        
        if target.startswith("http"):
            # Open URL in default browser
            subprocess.Popen(["cmd.exe", "/c", "start", target])
        else:
            subprocess.Popen([target])
        return True
    
    async def execute_iot_action(self, entity_id: str, service: str, **kwargs) -> dict:
        """
        Execute Home Assistant service call.
        Example: execute_iot_action("light.bedroom", "light.turn_on", brightness=200)
        """
        from jarvis.actuation.iot_mesh import HomeAssistantClient
        client = HomeAssistantClient()
        
        domain = entity_id.split(".")[0]  # "light" from "light.bedroom"
        return await client.call_service(domain, service, entity_id, **kwargs)
    
    def get_focused_window(self) -> str:
        """Return the title of the currently focused window."""
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
```

---

## 3. Common Voice Command → Actuation Mapping

```
"Open VS Code"
  → open_application("VS Code")
  → subprocess.Popen(["code.exe"])
  → Time: ~50ms

"Turn on the bedroom lights"  
  → execute_iot_action("light.bedroom", "light.turn_on")
  → HA REST: POST /api/services/light/turn_on
  → Time: ~15ms + Zigbee propagation ~5ms

"What's on my screen?"
  → read_screen() → DXGI capture (28ms) → moondream analyze (88ms)
  → TTS: "You have VS Code open with a Python file..."
  → Time: ~116ms + TTS (271ms) = ~387ms total

"Type 'Hello World' in the active window"
  → verify_keyboard_focus() → type_text_unicode("Hello World")
  → Time: ~2ms (11 chars × 2 key events per char)

"Click the Submit button"
  → UIALocator.find_by_name("Submit") (12ms) → click_element() (1ms)
  → Fallback: vision_grounding("Submit button") (180ms) if UIA fails
  → Time: 13ms nominal, 180ms vision fallback
```

---

## 4. Endpoints

```
POST   /actuation/click       → {"target": "CSS or description", "button": "left"}
POST   /actuation/type        → {"text": "...", "target_window": "VS Code"}
POST   /actuation/open        → {"app": "VS Code"}
POST   /actuation/smart-home  → {"entity_id": "light.bedroom", "service": "turn_on"}
GET    /actuation/screen       → Captures and returns DXGI screenshot as base64 JPEG
GET    /actuation/focus        → Returns title of currently focused window
```
