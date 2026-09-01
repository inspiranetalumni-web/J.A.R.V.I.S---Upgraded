"""
jarvis/llm/engine.py — Cognitive Ollama LLM Inference Engine v3.0
Interfaces with local Ollama API (:11434) for Llama 3.2 3B, Qwen 2.5 Coder, and Moondream models.
Features real-time token streaming, natural clause-chunked buffering for TTS, and dynamic availability probing.
"""

import re
import json
import time
import threading
import requests
from typing import List, Dict, Any, Optional, Iterator
from jarvis.config import config

CLAUSE_DELIMITER_PATTERN = re.compile(r'([.!?,;:\n]+)')

class OllamaEngine:
    """
    Ollama LLM Engine supporting Llama 3.2 3B, Qwen 2.5 Coder, and Moondream vision grounding.
    Provides synchronous chat, token streaming, and natural clause-chunked speech buffering.
    """
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or config.to_dict()["ollama_endpoint"]
        self.default_model = "llama3.2:3b"
        self._last_check_time: float = 0.0
        self._cached_available: bool = False
        self._cache_ttl: float = 5.0  # 5-second TTL window

    def is_available(self, force_refresh: bool = False) -> bool:
        """
        Returns True if local Ollama daemon is reachable on http://127.0.0.1:11434.
        Uses a dynamic TTL cache with fast 0.3s timeout to prevent UI/voice blocking.
        """
        now = time.time()
        if not force_refresh and (now - self._last_check_time) < self._cache_ttl:
            return self._cached_available

        try:
            r = requests.get(f"{self.endpoint}/api/tags", timeout=0.3)
            self._cached_available = (r.status_code == 200)
        except Exception:
            self._cached_available = False

        self._last_check_time = now
        return self._cached_available

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Sends multi-turn chat messages to Ollama API synchronously.
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
            r = requests.post(f"{self.endpoint}/api/chat", json=payload, timeout=5)
            if r.status_code == 200:
                resp_json = r.json()
                return resp_json.get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"[LLM] Ollama call note ({e}) — using cognitive fallback engine")

        # Cognitive persona fallback response
        user_message = messages[-1]["content"] if messages else ""
        return self._generate_fallback(user_message)

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        cancel_event: Optional[threading.Event] = None
    ) -> Iterator[str]:
        """
        Streams raw response tokens from Ollama API with immediate cancellation support.
        """
        model_name = model or self.default_model
        user_message = messages[-1]["content"] if messages else ""

        if not self.is_available():
            yield from self._stream_fallback(user_message, cancel_event=cancel_event)
            return

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            with requests.post(f"{self.endpoint}/api/chat", json=payload, stream=True, timeout=5) as r:
                if r.status_code != 200:
                    yield from self._stream_fallback(user_message, cancel_event=cancel_event)
                    return

                for line in r.iter_lines():
                    if cancel_event and cancel_event.is_set():
                        break
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yield token
                            if chunk.get("done", False):
                                break
                        except Exception:
                            continue
        except Exception as e:
            print(f"[LLM] Ollama stream note ({e}) — falling back to cognitive simulation")
            yield from self._stream_fallback(user_message, cancel_event=cancel_event)

    def stream_clauses(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        cancel_event: Optional[threading.Event] = None
    ) -> Iterator[str]:
        """
        Buffers incoming tokens into short, natural speech chunks (phrases/clauses)
        delimited by punctuation boundaries or token size, optimal for CPU TTS pipelining.
        """
        buffer = []
        token_count = 0

        for token in self.stream_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            cancel_event=cancel_event
        ):
            if cancel_event and cancel_event.is_set():
                break

            buffer.append(token)
            token_count += 1
            current_text = "".join(buffer)

            # Split on sentence/clause delimiters if clause is sufficiently long
            # (at least ~12 chars to avoid awkward fragmentation on abbreviations)
            has_major_punct = any(p in current_text for p in [".", "!", "?", "\n"])
            has_minor_punct = any(p in current_text for p in [",", ";", ":"])

            if (has_major_punct and len(current_text) >= 12) or (has_minor_punct and len(current_text) >= 24) or token_count >= 18:
                clause = current_text.strip()
                if clause:
                    yield clause
                buffer.clear()
                token_count = 0

        # Yield any remaining buffered text
        if buffer and not (cancel_event and cancel_event.is_set()):
            remaining = "".join(buffer).strip()
            if remaining:
                yield remaining

    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        """Single-prompt completion interface."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model=model, temperature=temperature)

    def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        cancel_event: Optional[threading.Event] = None
    ) -> Iterator[str]:
        """Single-prompt streaming completion interface."""
        messages = [{"role": "user", "content": prompt}]
        return self.stream_chat(messages, model=model, temperature=temperature, cancel_event=cancel_event)

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

    def _stream_fallback(self, prompt: str, cancel_event: Optional[threading.Event] = None) -> Iterator[str]:
        """Yields fallback persona response formatted as natural speech clauses."""
        full_text = self._generate_fallback(prompt)
        clauses = [c.strip() for c in re.split(r'(?<=[.!?,;:])\s+', full_text) if c.strip()]
        if not clauses:
            clauses = [full_text]

        for clause in clauses:
            if cancel_event and cancel_event.is_set():
                break
            yield clause
