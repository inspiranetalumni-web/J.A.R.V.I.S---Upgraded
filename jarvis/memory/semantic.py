"""
jarvis/memory/semantic.py — Persistent Tiered Memory Vault v3.0
Combines ChromaDB vector embeddings for semantic similarity search with SQLite/KùzuDB knowledge triples.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from jarvis.config import config

VAULT_DIR = config.vault_dir
DB_PATH = VAULT_DIR / "knowledge_graph.db"

class SemanticMemoryVault:
    """
    Tiered Memory Vault for J.A.R.V.I.S.
    Stores episodic dialogues, user preferences, and knowledge graph triples.
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._use_chroma = False
        self.chroma_collection = None
        self._memory_cache: List[Dict[str, Any]] = []

        # 1. Initialize SQLite Knowledge Graph Triples Database
        self._init_sqlite_graph()

        # 2. Initialize ChromaDB Vector Store
        self._init_chromadb()

    def _init_sqlite_graph(self):
        """Initializes SQLite schema for graph triples (subject, relation, object)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_triples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    object TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _init_chromadb(self):
        """Initializes ChromaDB persistent vector collection."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(VAULT_DIR / "chroma"))
            self.chroma_collection = client.get_or_create_collection(name="jarvis_memory")
            self._use_chroma = True
            print("[MEMORY] ChromaDB vector vault loaded successfully")
        except Exception as e:
            print(f"[MEMORY] ChromaDB init note: {e} — active with SQLite knowledge graph vault")

    def store_fact(self, subject: str, relation: str, object_val: str) -> None:
        """Stores a structured knowledge graph triple (e.g. 'Dhamodran', 'prefers', 'FastAPI')."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO knowledge_triples (subject, relation, object) VALUES (?, ?, ?)",
                (subject, relation, object_val)
            )
            conn.commit()

        fact_str = f"{subject} {relation} {object_val}"
        self.store_text(fact_str, metadata={"type": "triple"})

    def store_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Stores a plain text string in the memory vault."""
        metadata = metadata or {"type": "episodic"}
        
        # Local cache insertion
        doc_id = f"fact_{len(self._memory_cache) + 1}"
        self._memory_cache.append({"id": doc_id, "text": text, "metadata": metadata})

        # ChromaDB vector insertion
        if self._use_chroma and self.chroma_collection is not None:
            try:
                self.chroma_collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            except Exception:
                pass

    def recall_relevant(self, query: str, top_k: int = 5) -> List[str]:
        """
        Recalls top-k relevant facts matching the query from vector store and knowledge graph.
        """
        results = []
        query_lower = query.lower()

        # 1. Query SQLite Knowledge Graph
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT subject, relation, object FROM knowledge_triples ORDER BY id DESC LIMIT ?",
                    (top_k,)
                )
                rows = cursor.fetchall()
                for sub, rel, obj in rows:
                    triple_str = f"Fact: {sub} {rel} {obj}"
                    if any(term in triple_str.lower() for term in query_lower.split()):
                        results.append(triple_str)
        except Exception:
            pass

        # 2. Query ChromaDB Vector Store if active
        if self._use_chroma and self.chroma_collection is not None:
            try:
                res = self.chroma_collection.query(query_texts=[query], n_results=top_k)
                if res and "documents" in res and res["documents"]:
                    for doc in res["documents"][0]:
                        if doc not in results:
                            results.append(doc)
            except Exception:
                pass

        # 3. Fallback: Search local memory cache
        if not results:
            for item in self._memory_cache:
                if any(term in item["text"].lower() for term in query_lower.split()):
                    results.append(item["text"])
                    if len(results) >= top_k:
                        break

        return results[:top_k]

    def clear(self) -> None:
        """Clears all stored memories from the vault."""
        self._memory_cache.clear()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM knowledge_triples")
            conn.commit()

# Alias for backward compatibility
SemanticMemory = SemanticMemoryVault

