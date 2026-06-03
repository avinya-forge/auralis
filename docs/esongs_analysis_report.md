# eSongs System Analysis Report: Auralis Integration

## 1. Executive Summary
This report details the current architectural state of Auralis and evaluates its readiness against the **eSongs** music identification system requirements. While Auralis possesses strong local audio processing and neural classification foundations, significant gaps exist in API connectivity, metadata schemas, and high-level agentic orchestration.

## 2. Component Mapping

### AUDIO: Processing & Feature Extraction
*   **Libraries:** `librosa`, `pydub`, `acoustid`, `mutagen`, `numpy`.
*   **Capabilities:**
    *   **Deterministic:** BPM, Key, ReplayGain, and Acoustic Fingerprinting.
    *   **Neural:** Zero-shot Raga identification via CLAP (`laion/clap-htsat-unfused`) and general genre/mood classification.
*   **Gap:** Lacks specialized models for instrument identification (e.g., Sitar vs. Sarod) and vocalist classification (e.g., Gender/Range/Style).

### DATA: Schemas & Persistence
*   **Metadata Storage:** `MetadataCache` (SQLite + JSON) for track tags.
*   **Neural Storage:** `EmbeddingDatabase` (SQLite + `float32` vectors) for semantic similarity.
*   **Mobile Storage:** `OfflineCache` (SQLite) for track caching with LRU eviction.
*   **Gap:** Current schemas lack structured fields for **Gharanas**, **Instruments**, and **Vocalist signatures**. Embeddings are stored but not yet linked to a multi-modal knowledge graph.

### SYSTEM: Orchestration & AI Logic
*   **Architecture:** Service-Oriented Architecture (SOA) with specialized singleton services (`AIService`, `AudioAnalysisService`).
*   **Orchestration:** `AIBatchProcessor` provides basic task queuing via `multiprocessing`.
*   **LLM Integration:** `ModelLoader` supports local Hugging Face transformers.
*   **Gap:** Missing a **Meta-Agent Orchestrator** for intelligent task routing and failover logic. No integration points for premium LLMs (GPT-4, Claude) for deep musicological analysis.

### API: External Connectivity
*   **Connections:** MusicBrainz, Last.fm, AcoustID.
*   **Gap:** Missing a REST/GraphQL gateway. The proposed FastAPI server (`API-002`) is currently [BLOCKED].

### UI: Mobile & Client Access
*   **Desktop:** Native PyQt6/wxPython implementation.
*   **Gap:** No mobile interface endpoints or P2P secure sync for mobile clients.

## 3. Contrast: Auralis vs. eSongs

| Category | eSongs Requirement | Auralis Status | Missing Module/Logic |
| :--- | :--- | :--- | :--- |
| **Identification** | Multi-modal Raga/Instrument | Raga/Mood only | `instrument_classifier.py` |
| **Data Schema** | Vocalist/Gharana/Instrument | Basic Tags + Embeddings | `schema_expansion_v2.sql` |
| **Orchestration** | Meta-Agent Task Router | Manual Batch Queue | `agent_orchestrator.py` |
| **Connectivity** | Mobile REST API | Local SQLite Only | `api_gateway (FastAPI)` |
| **LLM Hybrid** | Local/Premium LLM Support | Local Transformers only | `llm_bridge_service.py` |

## 4. Missing Modules List

1.  **`src/modules/api`**: FastAPI server for mobile client connectivity.
2.  **`src/modules/agent`**: Meta-Agent logic for confidence-based model routing.
3.  **`src/services/ai/instrument_classifier.py`**: Specialized CNN/Transformer for instrument detection.
4.  **`src/services/ai/vocalist_analyzer.py`**: Voice signature extraction and matching.
5.  **`src/services/llm_orchestrator.py`**: Integration layer for OpenAI/Anthropic API calls.
6.  **`src/modules/net/p2p_sync.py`**: Secure mesh networking for file chunks.

## 5. Conclusion & Strategic Recommendation
Auralis is 60% aligned with eSongs core identification goals but 20% aligned with its ecosystem requirements (Mobile/Agentic). Priority should be given to unblocking the **API Gateway** and expanding the **Metadata Schema** to support higher-order musicological data.
