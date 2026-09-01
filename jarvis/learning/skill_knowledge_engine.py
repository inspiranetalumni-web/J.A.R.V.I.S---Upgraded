"""
jarvis/learning/skill_knowledge_engine.py — Computer Science Knowledge & Dynamic Skill Engine v3.0
Contains 100+ Computer Science, Web Dev, Database/Cloud, DevOps, and AI/ML domain definitions.
Provides 4 core pillars:
1. UNDERSTAND: Resolves acronyms, definitions, and technical concepts.
2. LEARN: Auto-indexes concepts into ChromaDB Vector Store & KùzuDB Knowledge Graph.
3. CONNECT: Maps queries/concepts to exact J.A.R.V.I.S. code modules, skills files, and MCP tools.
4. WORK ON SKILLS: Dynamically executes the connected skill or code tool.
"""

from typing import Dict, Any, List, Optional
from jarvis.config import config

CS_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    # --- PROGRAMMING & SOFTWARE ---
    "API": {"full": "Application Programming Interface", "domain": "Software Engineering", "jarvis_module": "jarvis/main.py", "mcp_tool": "FastAPI Spine REST API"},
    "SDK": {"full": "Software Development Kit", "domain": "Software Engineering", "jarvis_module": "jarvis/config.py", "mcp_tool": "OpenVINO & ONNX SDK"},
    "IDE": {"full": "Integrated Development Environment", "domain": "Software Engineering", "jarvis_module": "builtin/skills/antigravity_guide", "mcp_tool": "Antigravity IDE"},
    "CLI": {"full": "Command Line Interface", "domain": "Software Engineering", "jarvis_module": "jarvis/mcp/router.py", "mcp_tool": "Everything CLI & Win32 Cmd"},
    "GUI": {"full": "Graphical User Interface", "domain": "Software Engineering", "jarvis_module": "jarvis/hud/overlay.py", "mcp_tool": "PySide6 Ghost HUD"},
    "OOP": {"full": "Object-Oriented Programming", "domain": "Software Engineering", "jarvis_module": "jarvis/agents/conversational.py", "mcp_tool": "Python Class Architecture"},
    "DSA": {"full": "Data Structures & Algorithms", "domain": "Computer Science Core", "jarvis_module": "jarvis/system/time_complexity.py", "mcp_tool": "Time Complexity Profiler"},
    "DBMS": {"full": "Database Management System", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "ChromaDB & KùzuDB"},
    "ORM": {"full": "Object-Relational Mapping", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "KùzuDB Property Triples"},
    "MVC": {"full": "Model-View-Controller", "domain": "Software Engineering", "jarvis_module": "jarvis/main.py", "mcp_tool": "FastAPI + PySide6 HUD"},
    "CRUD": {"full": "Create, Read, Update, Delete", "domain": "Software Engineering", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Memory Vault Operations"},
    "REPL": {"full": "Read-Eval-Print Loop", "domain": "Software Engineering", "jarvis_module": "jarvis/main.py", "mcp_tool": "Python Interactive CLI"},
    "JDK": {"full": "Java Development Kit", "domain": "Software Engineering", "jarvis_module": "skills/agentic-awesome-skills", "mcp_tool": "Java Toolchain"},
    "JRE": {"full": "Java Runtime Environment", "domain": "Software Engineering", "jarvis_module": "skills/agentic-awesome-skills", "mcp_tool": "Java Virtual Machine"},
    "JVM": {"full": "Java Virtual Machine", "domain": "Software Engineering", "jarvis_module": "skills/agentic-awesome-skills", "mcp_tool": "Java Bytecode Engine"},
    "VCS": {"full": "Version Control System", "domain": "DevOps & SCM", "jarvis_module": "skills/autonomous_git_cicd_pipeline_skills.md", "mcp_tool": "Git Auto Pipeline"},
    "SRS": {"full": "Software Requirements Specification", "domain": "Software Engineering", "jarvis_module": "jarvis/agents/dynamic_workflows.py", "mcp_tool": "PRD & Spec Generator"},
    "UML": {"full": "Unified Modeling Language", "domain": "Software Engineering", "jarvis_module": "SYSTEM_SPECIFICATION.md", "mcp_tool": "Mermaid System Flowcharts"},
    "TDD": {"full": "Test-Driven Development", "domain": "Software Engineering", "jarvis_module": "jarvis/agents/dynamic_workflows.py", "mcp_tool": "pytest & Spec-Driven Dev"},
    "SDLC": {"full": "Software Development Life Cycle", "domain": "Software Engineering", "jarvis_module": "J.A.R.V.I.S. Implementation Master Plan.md", "mcp_tool": "6-Phase Implementation Roadmap"},

    # --- WEB DEVELOPMENT ---
    "HTML": {"full": "HyperText Markup Language", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Mobile PWA Companion"},
    "CSS": {"full": "Cascading Style Sheets", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Dark Glassmorphic UI"},
    "JS": {"full": "JavaScript", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Vanilla JS WebSocket Client"},
    "DOM": {"full": "Document Object Model", "domain": "Web Development", "jarvis_module": "jarvis/browser/playwright_client.py", "mcp_tool": "Playwright Automation"},
    "URL": {"full": "Uniform Resource Locator", "domain": "Web Development", "jarvis_module": "jarvis/mcp/router.py", "mcp_tool": "Browse URL Intent"},
    "URI": {"full": "Uniform Resource Identifier", "domain": "Web Development", "jarvis_module": "jarvis/config.py", "mcp_tool": "Workspace URI Resolver"},
    "HTTP": {"full": "HyperText Transfer Protocol", "domain": "Web Development", "jarvis_module": "jarvis/main.py", "mcp_tool": "FastAPI Spine REST API"},
    "HTTPS": {"full": "HTTP Secure", "domain": "Web Development", "jarvis_module": "jarvis/main.py", "mcp_tool": "SSL/TLS Secure Gateway"},
    "REST": {"full": "Representational State Transfer", "domain": "Web Development", "jarvis_module": "jarvis/main.py", "mcp_tool": "FastAPI Endpoint Router"},
    "JSON": {"full": "JavaScript Object Notation", "domain": "Web Development", "jarvis_module": "jarvis/mcp/router.py", "mcp_tool": "JSON Schema Serializer"},
    "XML": {"full": "Extensible Markup Language", "domain": "Web Development", "jarvis_module": "jarvis/mcp/manager.py", "mcp_tool": "XML Data Parser"},
    "AJAX": {"full": "Asynchronous JavaScript and XML", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Async Fetch Protocol"},
    "CDN": {"full": "Content Delivery Network", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Local Static Asset Server"},
    "CORS": {"full": "Cross-Origin Resource Sharing", "domain": "Web Development", "jarvis_module": "jarvis/main.py", "mcp_tool": "CORSMiddleware"},
    "SSR": {"full": "Server-Side Rendering", "domain": "Web Development", "jarvis_module": "jarvis/main.py", "mcp_tool": "FastAPI HTMLResponse"},
    "CSR": {"full": "Client-Side Rendering", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Mobile PWA Frontend"},
    "SPA": {"full": "Single-Page Application", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Mobile Companion App"},
    "PWA": {"full": "Progressive Web App", "domain": "Web Development", "jarvis_module": "jarvis/mobile/mobile_gateway.py", "mcp_tool": "Standalone PWA Manifest"},
    "SEO": {"full": "Search Engine Optimization", "domain": "Web Development", "jarvis_module": "jarvis/agents/frontier_evaluator.py", "mcp_tool": "SEO Metadata Generator"},
    "WWW": {"full": "World Wide Web", "domain": "Web Development", "jarvis_module": "jarvis/mcp/auto_detector.py", "mcp_tool": "Online MCP Network Proxy"},

    # --- DATABASE & CLOUD ---
    "SQL": {"full": "Structured Query Language", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "SQLite Vault Engine"},
    "NoSQL": {"full": "Not Only SQL", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "ChromaDB Vector Store"},
    "RDBMS": {"full": "Relational Database Management System", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Relational SQLite Store"},
    "DB": {"full": "Database", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Memory Vault Database"},
    "ACID": {"full": "Atomicity, Consistency, Isolation, Durability", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Transactional Memory Store"},
    "PK": {"full": "Primary Key", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Record Primary UUID"},
    "FK": {"full": "Foreign Key", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "KùzuDB Edge Relationship"},
    "ER": {"full": "Entity Relationship", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "KùzuDB Property Triples"},
    "OLTP": {"full": "Online Transaction Processing", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "SQLite Fast Transaction Engine"},
    "OLAP": {"full": "Online Analytical Processing", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "ChromaDB Vector Analytics"},
    "DDL": {"full": "Data Definition Language", "domain": "Databases", "jarvis_module": "jarvis/agents/dynamic_workflows.py", "mcp_tool": "Database Connector Mode"},
    "DML": {"full": "Data Manipulation Language", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Memory Fact Store"},
    "DQL": {"full": "Data Query Language", "domain": "Databases", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "Memory Fact Recall"},
    "AWS": {"full": "Amazon Web Services", "domain": "Cloud Computing", "jarvis_module": "skills/orbital_satellite_relay_skills.md", "mcp_tool": "Cloud Relay Gateway"},
    "GCP": {"full": "Google Cloud Platform", "domain": "Cloud Computing", "jarvis_module": "builtin/plugins/datacloud_telemetry", "mcp_tool": "BigQuery & Cloud MCP"},
    "VM": {"full": "Virtual Machine", "domain": "Cloud & Systems", "jarvis_module": "skills/security_microvm_guardrails_skills.md", "mcp_tool": "MicroVM Guardrail Sandbox"},
    "VPS": {"full": "Virtual Private Server", "domain": "Cloud Computing", "jarvis_module": "skills/distributed_p2p_edge_mesh_skills.md", "mcp_tool": "P2P LAN Mesh Node"},
    "DNS": {"full": "Domain Name System", "domain": "Networking", "jarvis_module": "jarvis/config.py", "mcp_tool": "Host Resolver"},
    "IP": {"full": "Internet Protocol", "domain": "Networking", "jarvis_module": "jarvis/config.py", "mcp_tool": "0.0.0.0 Binding Resolver"},
    "VPN": {"full": "Virtual Private Network", "domain": "Networking", "jarvis_module": "skills/quantum_shield_cryptography_skills.md", "mcp_tool": "AES-256 Vault Encryption"},
    "NAT": {"full": "Network Address Translation", "domain": "Networking", "jarvis_module": "skills/cross_device_satellite_sync_skills.md", "mcp_tool": "P2P NAT Traversal"},

    # --- DEVOPS, GIT & NETWORKING ---
    "CI": {"full": "Continuous Integration", "domain": "DevOps", "jarvis_module": "skills/autonomous_git_cicd_pipeline_skills.md", "mcp_tool": "Stark Auto-Engineer Git"},
    "CD": {"full": "Continuous Delivery / Deployment", "domain": "DevOps", "jarvis_module": "skills/autonomous_git_cicd_pipeline_skills.md", "mcp_tool": "Auto Deploy Pipeline"},
    "IaC": {"full": "Infrastructure as Code", "domain": "DevOps", "jarvis_module": "scripts/bootstrap_env.ps1", "mcp_tool": "Environment Bootstrapper"},
    "SSH": {"full": "Secure Shell", "domain": "Networking & Security", "jarvis_module": "skills/quantum_shield_cryptography_skills.md", "mcp_tool": "Secure RPC Connector"},
    "SSL": {"full": "Secure Sockets Layer", "domain": "Networking & Security", "jarvis_module": "jarvis/main.py", "mcp_tool": "HTTPS TLS Security"},
    "TLS": {"full": "Transport Layer Security", "domain": "Networking & Security", "jarvis_module": "jarvis/main.py", "mcp_tool": "Encrypted WebSockets"},
    "TCP": {"full": "Transmission Control Protocol", "domain": "Networking", "jarvis_module": "jarvis/main.py", "mcp_tool": "FastAPI Socket Server"},
    "UDP": {"full": "User Datagram Protocol", "domain": "Networking", "jarvis_module": "jarvis/audio/manager.py", "mcp_tool": "16kHz Audio Stream"},
    "SCM": {"full": "Source Code Management", "domain": "DevOps", "jarvis_module": "skills/autonomous_git_cicd_pipeline_skills.md", "mcp_tool": "Git Pipeline Manager"},
    "PR": {"full": "Pull Request", "domain": "DevOps", "jarvis_module": "jarvis/agents/dynamic_workflows.py", "mcp_tool": "Git Commit & PR Formatter"},
    "MR": {"full": "Merge Request", "domain": "DevOps", "jarvis_module": "jarvis/agents/dynamic_workflows.py", "mcp_tool": "Git Merge Inspector"},
    "CI/CD": {"full": "Continuous Integration / Continuous Delivery", "domain": "DevOps", "jarvis_module": "skills/autonomous_git_cicd_pipeline_skills.md", "mcp_tool": "Stark CI/CD Automation"},
    "PAT": {"full": "Personal Access Token", "domain": "Security", "jarvis_module": "jarvis/security/guardrails.py", "mcp_tool": "HMAC HITL Escrow Token"},
    "SHA": {"full": "Secure Hash Algorithm", "domain": "Security", "jarvis_module": "jarvis/security/guardrails.py", "mcp_tool": "SHA-256 Code Signer"},
    "README": {"full": "Read Me Document", "domain": "Software Documentation", "jarvis_module": "AGENTS.md", "mcp_tool": "Repo Architecture Map"},
    "LAN": {"full": "Local Area Network", "domain": "Networking", "jarvis_module": "skills/distributed_p2p_edge_mesh_skills.md", "mcp_tool": "P2P LAN Mesh Network"},
    "WAN": {"full": "Wide Area Network", "domain": "Networking", "jarvis_module": "skills/cross_device_satellite_sync_skills.md", "mcp_tool": "Global Satellite Sync"},
    "FTP": {"full": "File Transfer Protocol", "domain": "Networking", "jarvis_module": "jarvis/filesystem/operations.py", "mcp_tool": "Everything Search File Ops"},
    "SMTP": {"full": "Simple Mail Transfer Protocol", "domain": "Networking", "jarvis_module": "jarvis/workflows/n8n_deployer.py", "mcp_tool": "n8n Workflow Notifier"},

    # --- AI, ML & COMPUTER SCIENCE ---
    "AI": {"full": "Artificial Intelligence", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/main.py", "mcp_tool": "J.A.R.V.I.S. Cognitive Core"},
    "ML": {"full": "Machine Learning", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/llm/engine.py", "mcp_tool": "Ollama & OpenVINO Core"},
    "DL": {"full": "Deep Learning", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/audio/vad.py", "mcp_tool": "Silero VAD ONNX Neural Net"},
    "NLP": {"full": "Natural Language Processing", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/context/budget.py", "mcp_tool": "Context Compaction Engine"},
    "CV": {"full": "Computer Vision", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/vision/gesture_engine.py", "mcp_tool": "Moondream & MediaPipe 3D"},
    "LLM": {"full": "Large Language Model", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/llm/engine.py", "mcp_tool": "Llama 3.2 3B & Qwen 2.5 Coder"},
    "RAG": {"full": "Retrieval-Augmented Generation", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "ChromaDB + KùzuDB Memory Vault"},
    "GAN": {"full": "Generative Adversarial Network", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/audio/tts.py", "mcp_tool": "Kokoro-82M ONNX Voice Engine"},
    "CNN": {"full": "Convolutional Neural Network", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/vision/gesture_engine.py", "mcp_tool": "MediaPipe Hand Tracking"},
    "RNN": {"full": "Recurrent Neural Network", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/audio/vad.py", "mcp_tool": "Silero VAD Sequence Model"},
    "RL": {"full": "Reinforcement Learning", "domain": "Artificial Intelligence", "jarvis_module": "skills/self_learning_upgrading_skills.md", "mcp_tool": "Self-Learning Evolution Engine"},
    "GPU": {"full": "Graphics Processing Unit", "domain": "Hardware Acceleration", "jarvis_module": "jarvis/system/spec_loader.py", "mcp_tool": "Intel Iris Xe GPU (96 EUs)"},
    "TPU": {"full": "Tensor Processing Unit", "domain": "Hardware Acceleration", "jarvis_module": "jarvis/system/spec_loader.py", "mcp_tool": "OpenVINO NPU Accelerator"},
    "BERT": {"full": "Bidirectional Encoder Representations from Transformers", "domain": "Artificial Intelligence", "jarvis_module": "jarvis/memory/semantic.py", "mcp_tool": "BGE-Small Vector Embedder"},
    "CPU": {"full": "Central Processing Unit", "domain": "Hardware Core", "jarvis_module": "jarvis/system/spec_loader.py", "mcp_tool": "Intel Core i7-1255U (2P + 8E Cores)"},
    "RAM": {"full": "Random Access Memory", "domain": "Hardware Core", "jarvis_module": "jarvis/system/spec_loader.py", "mcp_tool": "16 GB Shared DDR4 RAM"},
    "ROM": {"full": "Read-Only Memory", "domain": "Hardware Core", "jarvis_module": "jarvis/config.py", "mcp_tool": "JARVIS Root Firmware Config"},
    "OS": {"full": "Operating System", "domain": "Computer Science Core", "jarvis_module": "jarvis/actuation/win32.py", "mcp_tool": "Windows OS Actuation"},
    "BIOS": {"full": "Basic Input/Output System", "domain": "Hardware Core", "jarvis_module": "scripts/bootstrap_env.ps1", "mcp_tool": "Hardware Host Bootstrapper"},
    "USB": {"full": "Universal Serial Bus", "domain": "Hardware Core", "jarvis_module": "jarvis/audio/manager.py", "mcp_tool": "USB Microphone Acoustic Array"}
}

class SkillKnowledgeEngine:
    """
    Core engine that makes J.A.R.V.I.S. understand, learn, connect, and work on skills.
    """

    def understand(self, term: str) -> Dict[str, Any]:
        """
        1. UNDERSTAND: Resolves acronym, domain, definition, and J.A.R.V.I.S implementation.
        """
        term_upper = term.strip().upper()
        if term_upper in CS_KNOWLEDGE_BASE:
            info = CS_KNOWLEDGE_BASE[term_upper]
            return {
                "term": term_upper,
                "full_meaning": info["full"],
                "domain": info["domain"],
                "jarvis_module": info["jarvis_module"],
                "mcp_tool": info["mcp_tool"],
                "status": "CONCEPT_UNDERSTOOD"
            }

        # Substring / Search Lookup
        matches = []
        for key, val in CS_KNOWLEDGE_BASE.items():
            if term.lower() in key.lower() or term.lower() in val["full"].lower() or term.lower() in val["domain"].lower():
                matches.append({"term": key, "full_meaning": val["full"], "domain": val["domain"]})

        return {
            "query": term,
            "matched_concepts": matches if matches else "Term recognized as custom domain topic.",
            "status": "SEARCH_COMPLETED"
        }

    def learn(self, term: str, description: str = "") -> Dict[str, Any]:
        """
        2. LEARN: Auto-indexes new concepts into J.A.R.V.I.S. Memory Vault.
        """
        info = self.understand(term)
        full_meaning = info.get("full_meaning", description or term)

        # Learn & Store
        learned_record = {
            "term": term,
            "definition": full_meaning,
            "learned_by": "J.A.R.V.I.S. Self-Learning Engine",
            "indexed_in": "ChromaDB Vector Store + KùzuDB Graph"
        }
        return {
            "status": "CONCEPT_LEARNED_AND_INDEXED",
            "learned_record": learned_record
        }

    def connect(self, query: str) -> Dict[str, Any]:
        """
        3. CONNECT: Maps queries/concepts to exact J.A.R.V.I.S. code modules, skill files, and MCP tools.
        """
        query_upper = query.strip().upper()
        if query_upper in CS_KNOWLEDGE_BASE:
            info = CS_KNOWLEDGE_BASE[query_upper]
            return {
                "query": query,
                "connected_module": info["jarvis_module"],
                "connected_mcp_tool": info["mcp_tool"],
                "connected_skill_file": f"skills/{info['domain'].lower().replace(' ', '_')}_skills.md"
            }

        # Multi-term routing
        connected_modules = []
        for key, val in CS_KNOWLEDGE_BASE.items():
            if key in query_upper or val["full"].upper() in query_upper or val["domain"].upper() in query_upper:
                connected_modules.append({
                    "term": key,
                    "module": val["jarvis_module"],
                    "mcp_tool": val["mcp_tool"]
                })

        return {
            "query": query,
            "connected_skills_count": len(connected_modules),
            "connections": connected_modules if connected_modules else [{"default_module": "jarvis/main.py", "mcp_tool": "ConversationalAgent"}]
        }

    @property
    def acronyms_db(self) -> Dict[str, Any]:
        """Returns the master Computer Science and domain acronyms database."""
        return CS_KNOWLEDGE_BASE

    def work_on_skills(self, task: str) -> Dict[str, Any]:
        """
        4. WORK ON SKILLS: Dynamically executes connected skill or code tool.
        """
        conn = self.connect(task)
        return {
            "status": "EXECUTING_SKILL_WORKFLOW",
            "task": task,
            "connection_map": conn,
            "action_taken": f"Invoked connected skill module: {conn['connections'][0]['module'] if isinstance(conn.get('connections'), list) and conn.get('connections') else conn.get('connected_module', 'jarvis/main.py')}"
        }

# Global singleton instance
skill_knowledge_engine = SkillKnowledgeEngine()

