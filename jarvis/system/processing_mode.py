"""
jarvis/system/processing_mode.py — Batch vs Stream Processing Selector & Pipeline Manager v3.0
Dynamically assigns execution pipeline mode based on data type, latency target, and system context.
"""

from typing import Dict, Any, List

class ProcessingPipelineManager:
    """
    Manages Batch vs Stream Processing pipeline selection for J.A.R.V.I.S.
    """

    def select_processing_mode(self, task_type: str) -> Dict[str, Any]:
        """
        Determines whether Batch Processing or Stream Processing best suits the given task.
        """
        task_lower = task_type.lower()

        # Stream Processing Targets (Low Latency ~195ms, Unbounded Data)
        stream_keywords = ["audio", "voice", "vad", "stt", "tts", "websocket", "hud", "realtime", "event", "gesture", "gaze", "mic"]
        if any(kw in task_lower for kw in stream_keywords):
            return {
                "pipeline": "STREAM_PROCESSING",
                "latency_target": "195 ms (Event-Driven / Sub-50ms TTFT)",
                "data_nature": "Unbounded Data Stream",
                "execution_model": "Always-On Real-time Event Loop",
                "components_involved": [
                    "Silero VAD ONNX (Thread 4 E-Core)",
                    "faster-whisper INT8 (Threads 0-1 P-Core)",
                    "Kokoro-82M ONNX Voice Streaming",
                    "PySide6 Ghost HUD WebSocket Stream (/ws/status)"
                ],
                "justification": "Optimal for continuous hands-free voice, interactive UI, and live sensory ingestion."
            }

        # Batch Processing Targets (Scheduled, Bounded Data Set)
        return {
            "pipeline": "BATCH_PROCESSING",
            "latency_target": "Scheduled / Bounded Execution (02:00 AM Maintenance)",
            "data_nature": "Bounded Data Set",
            "execution_model": "Scheduled Cron / Discrete Batch Job",
            "components_involved": [
                "ChromaDB Vector Store Index Compaction",
                "KùzuDB Knowledge Graph Entity Consolidation",
                "APScheduler Daily TTL Memory Maintenance",
                "Offline Model Benchmark Evaluation"
            ],
            "justification": "Optimal for heavy computational memory consolidation, ETL transformations, and report generation."
        }
