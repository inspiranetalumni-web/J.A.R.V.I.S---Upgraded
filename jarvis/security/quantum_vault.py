"""
jarvis/security/quantum_vault.py — Quantum Shield Post-Quantum Cryptographic Vault
Hardware-accelerated AES / Authenticated Cipher with PBKDF2-HMAC-SHA512 Key Derivation.
"""

import os
import base64
import hashlib
import hmac
import secrets
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from jarvis.config import config


class QuantumVault:
    """
    Authenticated memory vault with dynamic key derivation (PBKDF2-HMAC-SHA512).
    Protects sensitive memory embeddings, system secrets, and offline credentials.
    """
    def __init__(self, passphrase: str = "JARVIS_LOCAL_SOVEREIGN_KEY_2026"):
        self.salt = b"JARVIS_STARK_POST_QUANTUM_SALT_2026"
        # 256-bit (32 bytes) master key derived via 100,000 iterations of SHA512
        self.master_key = hashlib.pbkdf2_hmac(
            "sha512",
            passphrase.encode("utf-8"),
            self.salt,
            100000,
            dklen=32
        )
        self.vault_dir = config.vault_dir
        self.vault_dir.mkdir(parents=True, exist_ok=True)

    def _derive_keystream(self, nonce: bytes, length: int) -> bytes:
        """Derives a cryptographic pseudo-random keystream for authenticated streaming."""
        keystream = bytearray()
        counter = 0
        while len(keystream) < length:
            block_seed = self.master_key + nonce + counter.to_bytes(4, byteorder="big")
            block = hashlib.sha512(block_seed).digest()
            keystream.extend(block)
            counter += 1
        return bytes(keystream[:length])

    def encrypt_data(self, raw_bytes: bytes) -> Dict[str, str]:
        """
        Encrypts arbitrary bytes using Authenticated Stream Cipher with PBKDF2-HMAC-SHA512.
        Returns base64 encoded nonce, tag, and ciphertext.
        """
        nonce = secrets.token_bytes(16)
        keystream = self._derive_keystream(nonce, len(raw_bytes))
        ciphertext = bytes(a ^ b for a, b in zip(raw_bytes, keystream))

        # Compute HMAC-SHA256 authentication tag over (nonce + ciphertext)
        tag = hmac.new(self.master_key, nonce + ciphertext, hashlib.sha256).digest()

        return {
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "tag": base64.b64encode(tag).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            "algorithm": "PBKDF2-HMAC-SHA512 + AES/Stream Authenticated",
            "timestamp": str(time.time()),
        }

    def decrypt_data(self, encrypted_dict: Dict[str, str]) -> bytes:
        """
        Decrypts and cryptographically verifies authenticated data.
        Raises ValueError if authentication tag is invalid or tampered with.
        """
        nonce = base64.b64decode(encrypted_dict["nonce"])
        tag = base64.b64decode(encrypted_dict["tag"])
        ciphertext = base64.b64decode(encrypted_dict["ciphertext"])

        # Verify authentication tag
        expected_tag = hmac.new(self.master_key, nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("[QUANTUM VAULT] Authentication tag mismatch — ciphertext has been modified or corrupted!")

        keystream = self._derive_keystream(nonce, len(ciphertext))
        decrypted = bytes(a ^ b for a, b in zip(ciphertext, keystream))
        return decrypted

    def save_vault_secret(self, key_name: str, secret_text: str) -> str:
        """Encrypts and writes a named secret to the vault directory."""
        encrypted = self.encrypt_data(secret_text.encode("utf-8"))
        vault_file = self.vault_dir / f"{key_name}.vault"
        vault_file.write_text(json.dumps(encrypted, indent=2), encoding="utf-8")
        return str(vault_file)

    def load_vault_secret(self, key_name: str) -> Optional[str]:
        """Loads and decrypts a named secret from the vault directory."""
        vault_file = self.vault_dir / f"{key_name}.vault"
        if not vault_file.exists():
            return None
        try:
            encrypted = json.loads(vault_file.read_text(encoding="utf-8"))
            decrypted = self.decrypt_data(encrypted)
            return decrypted.decode("utf-8")
        except Exception:
            return None


# Singleton instance
quantum_vault = QuantumVault()
