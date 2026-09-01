"""
jarvis/audio/persona_manager.py — Dynamic Multi-Persona Voice & Prompt Synthesizer
Swaps Stark personas (J.A.R.V.I.S., F.R.I.D.A.Y., E.D.I.T.H.) on demand (< 2ms).
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

logger = logging.getLogger("jarvis.audio.persona")


@dataclass
class PersonaProfile:
    name: str
    display_title: str
    voice_embedding_id: str
    pitch_modifier: float
    speed: float
    system_prompt_prefix: str
    accent_description: str
    hud_accent_color: str


PERSONA_REGISTRY: Dict[str, PersonaProfile] = {
    "JARVIS": PersonaProfile(
        name="JARVIS",
        display_title="J.A.R.V.I.S.",
        voice_embedding_id="bm_george",
        pitch_modifier=1.0,
        speed=1.0,
        system_prompt_prefix="You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), Tony Stark's sovereign AI assistant. Speak calmly, politely, with British precision and dry wit.",
        accent_description="British Male (Calm, Polite, Precise)",
        hud_accent_color="#00D2FF"  # Stark Cyan
    ),
    "FRIDAY": PersonaProfile(
        name="FRIDAY",
        display_title="F.R.I.D.A.Y.",
        voice_embedding_id="af_bella",
        pitch_modifier=1.05,
        speed=1.1,
        system_prompt_prefix="You are F.R.I.D.A.Y., Tony Stark's tactical and alert AI assistant. Speak with Irish directness, protective urgency, and high efficiency.",
        accent_description="Irish Female (Tactical, Protective, Fast)",
        hud_accent_color="#00FF88"  # Tactical Emerald
    ),
    "EDITH": PersonaProfile(
        name="EDITH",
        display_title="E.D.I.T.H.",
        voice_embedding_id="am_adam",
        pitch_modifier=0.95,
        speed=1.15,
        system_prompt_prefix="You are E.D.I.T.H. (Even Dead, I'm The Hero), a direct, tactical technical AI assistant. Deliver ultra-concise, code-first answers with zero fluff.",
        accent_description="Direct Technical (Ultra-Brief, Fast)",
        hud_accent_color="#FFB300"  # Amber Tech
    ),
}


class PersonaManager:
    """
    Manages instant switching of active persona profiles, voice embeddings,
    and LLM system prompt directives.
    """
    def __init__(self, default_persona: str = "JARVIS"):
        self.active_persona: PersonaProfile = PERSONA_REGISTRY.get(default_persona.upper(), PERSONA_REGISTRY["JARVIS"])
        self._switch_count: int = 0
        self._last_switch_latency_ms: float = 0.0

    def switch_persona(self, persona_name: str) -> PersonaProfile:
        """Switches the active persona in < 2.0ms."""
        t0 = time.perf_counter()
        name_clean = persona_name.strip().upper().replace(".", "").replace("-", "")

        # Alias resolution
        if "FRIDAY" in name_clean:
            target_key = "FRIDAY"
        elif "EDITH" in name_clean:
            target_key = "EDITH"
        else:
            target_key = "JARVIS"

        self.active_persona = PERSONA_REGISTRY[target_key]
        self._switch_count += 1
        self._last_switch_latency_ms = (time.perf_counter() - t0) * 1000

        logger.info(f"[PERSONA] Switched to {self.active_persona.display_title} in {self._last_switch_latency_ms:.3f}ms")
        return self.active_persona

    def get_active_persona(self) -> PersonaProfile:
        """Returns active PersonaProfile."""
        return self.active_persona

    def get_tts_parameters(self) -> Dict[str, Any]:
        """Returns Kokoro TTS voice parameters for the active persona."""
        return {
            "voice": self.active_persona.voice_embedding_id,
            "speed": self.active_persona.speed,
            "pitch": self.active_persona.pitch_modifier,
            "persona_name": self.active_persona.name,
        }

    def get_system_prompt_prefix(self) -> str:
        """Returns system prompt prefix for active persona."""
        return self.active_persona.system_prompt_prefix

    def list_available_personas(self) -> List[Dict[str, Any]]:
        """Lists all registered personas."""
        return [
            {
                "key": p.name,
                "title": p.display_title,
                "voice": p.voice_embedding_id,
                "accent": p.accent_description,
                "speed": p.speed,
                "is_active": p.name == self.active_persona.name,
            }
            for p in PERSONA_REGISTRY.values()
        ]


# Singleton instance
persona_manager = PersonaManager()
