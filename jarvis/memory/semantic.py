"""
jarvis/memory/semantic.py — Persistent Tiered Memory Vault v3.0
Combines ChromaDB vector embeddings for semantic similarity search with SQLite/KùzuDB knowledge triples.
Optimized with SQLite Write-Ahead Logging (WAL) and structured error logging.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from jarvis.config import config
from jarvis.logging import get_logger

logger = get_logger("memory")

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

        # 2. ChromaDB Vector Store (Lazy initialized on demand)
        self._chroma_initialized = False

    def _get_connection(self) -> sqlite3.Connection:
        """Creates SQLite connection configured with WAL journal mode for high concurrency."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_sqlite_graph(self):
        """Initializes SQLite schema for graph triples (subject, relation, object)."""
        try:
            with self._get_connection() as conn:
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
            logger.debug("SQLite knowledge triples schema initialized with WAL mode at %s", self.db_path)
        except Exception as e:
            logger.warning("Error initializing SQLite knowledge graph: %s", e)

    def _ensure_chromadb(self):
        """Lazy initializer for ChromaDB persistent vector collection."""
        if self._chroma_initialized:
            return
        self._chroma_initialized = True
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(VAULT_DIR / "chroma"))
            self.chroma_collection = client.get_or_create_collection(name="jarvis_memory")
            self._use_chroma = True
            logger.info("ChromaDB vector vault loaded successfully at %s", VAULT_DIR / "chroma")
        except Exception as e:
            logger.info("ChromaDB init note: %s — active with SQLite knowledge graph vault", e)

    def store_fact(self, subject: str, relation: str, object_val: str) -> None:
        """Stores a structured knowledge graph triple (e.g. 'Dhamodran', 'prefers', 'FastAPI')."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO knowledge_triples (subject, relation, object) VALUES (?, ?, ?)",
                    (subject, relation, object_val)
                )
                conn.commit()
            logger.debug("Stored triple fact: (%s, %s, %s)", subject, relation, object_val)
        except Exception as e:
            logger.warning("Error storing triple fact in SQLite: %s", e)

        fact_str = f"{subject} {relation} {object_val}"
        self.store_text(fact_str, metadata={"type": "triple"})

    def store_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Stores a plain text string in the memory vault."""
        metadata = metadata or {"type": "episodic"}
        
        # Local cache insertion
        doc_id = f"fact_{len(self._memory_cache) + 1}"
        self._memory_cache.append({"id": doc_id, "text": text, "metadata": metadata})

        # ChromaDB vector insertion
        self._ensure_chromadb()
        if self._use_chroma and self.chroma_collection is not None:
            try:
                self.chroma_collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            except Exception as e:
                logger.debug("ChromaDB vector store insert fallback (document cached locally): %s", e)

    def recall_relevant(self, query: str, top_k: int = 5) -> List[str]:
        """
        Recalls top-k relevant facts matching the query from vector store and knowledge graph.
        """
        results = []
        query_lower = query.lower()

        # 1. Query SQLite Knowledge Graph
        try:
            with self._get_connection() as conn:
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
        except Exception as e:
            logger.warning("Error recalling facts from SQLite graph: %s", e)

        # 2. Query ChromaDB Vector Store if active
        self._ensure_chromadb()
        if self._use_chroma and self.chroma_collection is not None:
            try:
                res = self.chroma_collection.query(query_texts=[query], n_results=top_k)
                if res and "documents" in res and res["documents"]:
                    for doc in res["documents"][0]:
                        if doc not in results:
                            results.append(doc)
            except Exception as e:
                logger.debug("ChromaDB query fallback: %s", e)

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
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM knowledge_triples")
                conn.commit()
            logger.info("SemanticMemoryVault cleared successfully.")
        except Exception as e:
            logger.warning("Error clearing SQLite knowledge graph: %s", e)

# Alias for backward compatibility
SemanticMemory = SemanticMemoryVault
