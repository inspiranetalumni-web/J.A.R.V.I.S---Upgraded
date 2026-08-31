"""
jarvis/learning/curriculum_engine.py — AI Mastery Curriculum & Practical Project Engine v3.0
Guides systematic learning and building in the exact order:
Prompting ➔ LLMs ➔ Embeddings ➔ RAG ➔ AI Agents ➔ Fine-Tuning ➔ AI Coding
"""

from typing import Dict, Any, List

CURRICULUM_STEPS: List[Dict[str, Any]] = [
    {
        "step": 1,
        "topic": "Prompting",
        "concept": "Structured System Prompts, Few-Shot In-Context Rules, Persona Directives & Schema Enforcement",
        "practical_project": "Persona Prompt Generator & Zero-Shot Intent Parser",
        "jarvis_module": "jarvis/agents/conversational.py",
        "status": "COMPLETED & BUILT"
    },
    {
        "step": 2,
        "topic": "LLMs",
        "concept": "Inference Engine Architecture, Sampling Options, Sub-50ms TTFT, Local Ollama / OpenVINO Execution",
        "practical_project": "Local Ollama Cognitive Core API & Persona Fallback Engine",
        "jarvis_module": "jarvis/llm/engine.py",
        "status": "COMPLETED & BUILT"
    },
    {
        "step": 3,
        "topic": "Embeddings",
        "concept": "Dense Vector Representations, Cosine Similarity Metrics, Vector Space Search",
        "practical_project": "ChromaDB Embedding Vector Indexer",
        "jarvis_module": "jarvis/memory/semantic.py",
        "status": "COMPLETED & BUILT"
    },
    {
        "step": 4,
        "topic": "RAG",
        "concept": "Retrieval-Augmented Generation, Context Compaction Budgeting, Hybrid ChromaDB + KùzuDB Graph Recall",
        "practical_project": "Sovereign Local Memory RAG Vault & Token Budgeter",
        "jarvis_module": "jarvis/context/budget.py",
        "status": "COMPLETED & BUILT"
    },
    {
        "step": 5,
        "topic": "AI Agents",
        "concept": "Multi-Agent Swarm Orchestration, Tool Calling, MCP Process Supervisors, 3-Stage Hybrid Intent Router",
        "practical_project": "Stark Horizon Multi-Agent Swarm Orchestrator & AAS MCP Integrator",
        "jarvis_module": "jarvis/mcp/router.py",
        "status": "COMPLETED & BUILT"
    },
    {
        "step": 6,
        "topic": "Fine-Tuning",
        "concept": "LoRA / QLoRA Adapters, Synthetic Data Generation, DPO Preference Alignment",
        "practical_project": "Local Llama-3.2-3B Persona LoRA Fine-Tuner",
        "jarvis_module": "jarvis/llm/finetune_adapter.py",
        "status": "READY FOR EXECUTION"
    },
    {
        "step": 7,
        "topic": "AI Coding",
        "concept": "Autonomous Code Generation, AST Parsing, Refactoring, Self-Testing & Verification Pipelines",
        "practical_project": "Stark Auto-Architect Autonomous Code Engine",
        "jarvis_module": "jarvis/agents/frontier_evaluator.py & dynamic_workflows.py",
        "status": "COMPLETED & BUILT"
    }
]

class AICurriculumEngine:
    """
    Tracks and executes the 7-stage AI Mastery Building Roadmap.
    """
    def get_full_curriculum(self) -> Dict[str, Any]:
        """Returns full curriculum roadmap and module mapping."""
        return {
            "title": "J.A.R.V.I.S. AI Mastery & Building Roadmap",
            "order": "Prompting ➔ LLMs ➔ Embeddings ➔ RAG ➔ AI Agents ➔ Fine-Tuning ➔ AI Coding",
            "total_stages": 7,
            "curriculum": CURRICULUM_STEPS
        }
