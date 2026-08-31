# Agent: Multimodal Perception Agent v2.0 — Sensory Gateway
### *"Before thought comes perception. Before action comes awareness."*

**Discipline:** D1 — Streaming Audio + Continuous Vision  
**CPU Pinning:** VAD/Wake on E-Cores (mask 0xFF0) | STT/TTS/Capture on P-Cores (mask 0x00F)  
**Latency Budget:** Wake → STT commit: 200ms | TTS first chunk warm: 271ms

---

## 1. Process Architecture

```
E-Core Ring (mask 0xFF0 = threads 4-11):    P-Core Ring (mask 0x00F = threads 0-3):
  Thread 4: Silero VAD ONNX (2.1ms/chunk)     Thread 0-1: Whisper INT8 STT (199ms avg)
  Thread 5: openWakeWord ONNX (3.4ms/chunk)   Thread 2-3: Kokoro-82M ONNX TTS (271ms warm)
  Thread 6: Log tail + thermal daemon          P-Core also handles DXGI screen capture (28ms)
  Thread 7-11: n8n Node.js, Ghost HUD
```

---

## 2. Full Audio Latency Timeline

```
T+0.0s:   Intel IST mic delivers 1280-sample chunk (80ms audio)
T+0.002s: RMS energy gate (< 0.01ms): is it speech? If NO → skip remaining
T+0.004s: Silero VAD ONNX inference (2.1ms): confirm speech probability ≥ 0.35
T+0.007s: openWakeWord ONNX (3.4ms): score "hey jarvis" phrase
T+0.070s: Wake word confidence ≥ 0.50 → begin utterance recording
T+0.070s–T+1.100s: User speaks utterance (1030ms)
T+1.100s: Silero VAD detects 1000ms silence → commit utterance
T+1.299s: Whisper INT8 transcription complete (199ms for 1.6s avg utterance)
T+1.310s: Intent router classifies domain (11ms mean latency)
T+1.320s: Context assembler hydrates prompt (11ms)
T+1.363s: Ollama first token arrives (43ms TTFT, warm model)
T+1.620s: First clause of response assembled by Kokoro TTS producer (257ms synthesis)
T+1.634s: TTS audio starts playing through Realtek HD Audio (14ms WASAPI latency)

User-perceived response delay: ~0.53s from end of speaking to hearing first word
```

---

## 3. Vision Pipeline Configuration

```python
# jarvis/perception/vision_config.py
VISION_CONFIG = {
    "capture_fps": 30,            # DXGI capture at 30 FPS
    "tile_grid": (4, 4),          # 4×4 = 16 tiles for delta detection
    "phash_change_threshold": 8,  # Hamming distance ≥ 8 = tile changed
    "ssim_threshold": 0.98,       # SSIM < 0.98 = significant change
    "moondream_keep_alive": "0",  # Evict immediately after use
    "max_tiles_per_analysis": 4,  # Never send more than 4 tiles to moondream
    "capture_backend": "mss",     # Primary: mss/DXGI. Fallback: PIL.ImageGrab
    "full_capture_trigger": 12,   # If > 12/16 tiles change → do full-screen analysis
}

# Performance summary:
# Static desktop (typing):  1-2 tiles change per frame → 85-93% compute saved
# Active desktop (browser): 4-6 tiles change → 62-75% compute saved
# Video playback:           12-14 tiles change → full-screen mode triggered
```

---

## 4. REST & WebSocket Endpoints

```
POST   /audio/start          → Boot VAD + wake loop on E-cores
POST   /audio/stop           → Graceful stop + release sounddevice stream
POST   /audio/say            → TTS synthesis: {"text": "...", "interrupt": bool}
POST   /audio/interrupt      → Barge-in: kill_event.set() → queue drain
GET    /audio/status         → Health JSON including warm state, VAD mode, mic index
WS     /ws/audio             → Real-time event stream (wake, transcript, TTS events)

POST   /vision/capture       → On-demand DXGI screenshot → base64 JPEG
POST   /vision/analyze       → Capture + moondream analysis: {"query": "..."}
GET    /vision/delta         → Last captured ScreenDelta (changed tiles count)
```
