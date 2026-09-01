"""
J.A.R.V.I.S. Audio & Multimodal Perception Subpackage v3.0
"""

from .ring_buffer import AudioRingBuffer, SAMPLE_RATE, CHUNK_SAMPLES
from .vad import DualGateVAD
from .wakeword import WakeWordDetector
from .stt import SpeechTranscriber
from .tts import KokoroTTS
from .persona_manager import PersonaManager, persona_manager
from .spectrum_analyzer import SpectrumAnalyzer, spectrum_analyzer

__all__ = [
    "AudioRingBuffer",
    "SAMPLE_RATE",
    "CHUNK_SAMPLES",
    "DualGateVAD",
    "WakeWordDetector",
    "SpeechTranscriber",
    "KokoroTTS",
    "PersonaManager",
    "persona_manager",
    "SpectrumAnalyzer",
    "spectrum_analyzer",
]
