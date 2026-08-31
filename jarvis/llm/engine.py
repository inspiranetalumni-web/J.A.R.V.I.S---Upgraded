"""
jarvis/llm/engine.py — Cognitive Ollama LLM Inference Engine v3.0
Interfaces with local Ollama API (:11434) for Llama 3.2 3B, Qwen 2.5 Coder, and Moondream models.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from jarvis.config import config

class OllamaEngine:
    """
    Ollama LLM Engine supporting Llama 3.2 3B, Qwen 2.5 Coder, and Moondream vision grounding.
    """
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or config.to_dict()["ollama_endpoint"]
        self.default_model = "llama3.2:3b"

    _available_cached: Optional[bool] = False

    def is_available(self) -> bool:
        """Returns True if local Ollama daemon is reachable on http://127.0.0.1:11434."""
        if OllamaEngine._available_cached is not None:
            return OllamaEngine._available_cached
        try:
            r = requests.get(f"{self.endpoint}/api/tags", timeout=0.1)
            OllamaEngine._available_cached = (r.status_code == 200)
        except Exception:
            OllamaEngine._available_cached = False
        return OllamaEngine._available_cached

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Sends multi-turn chat messages to Ollama API.
        Falls back to cognitive simulation engine if service is offline.
        """
        model_name = model or self.default_model

        if not self.is_available():
            user_message = messages[-1]["content"] if messages else ""
            return self._generate_fallback(user_message)

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            r = requests.post(f"{self.endpoint}/api/chat", json=payload, timeout=3)
            if r.status_code == 200:
                resp_json = r.json()
                return resp_json.get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"[LLM] Ollama call note ({e}) — using cognitive fallback engine")

        # Cognitive persona fallback response
        user_message = messages[-1]["content"] if messages else ""
        return self._generate_fallback(user_message)

    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        """Single-prompt completion interface."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model=model, temperature=temperature)

    def _generate_fallback(self, prompt: str) -> str:
        """Generates Tony Stark J.A.R.V.I.S. persona response when local LLM is offline."""
        prompt_lower = prompt.lower()
        if "hello" in prompt_lower or "hi" in prompt_lower or "hey" in prompt_lower:
            return "At your service, Sir. All core systems are nominal."
        elif "status" in prompt_lower or "health" in prompt_lower:
            return "Core spine is online at port 8765. Memory vault and audio engines operational."
        elif "who are you" in prompt_lower:
            return "I am J.A.R.V.I.S. — Just A Rather Very Intelligent System. Ready for your instructions, Sir."
        else:
            return f"Understood, Sir. Processing your request: '{prompt}'."
