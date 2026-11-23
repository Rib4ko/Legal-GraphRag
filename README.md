# Moroccan Legal GraphRAG ⚖️🧠

[![CI Verification](https://github.com/Rib4ko/Legal-GraphRag/actions/workflows/ci.yml/badge.svg)](https://github.com/Rib4ko/Legal-GraphRag/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Neo4j](https://img.shields.io/badge/Knowledge_Graph-Neo4j-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-DC2626.svg?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An advanced, hybrid AI retrieval engine for Moroccan jurisprudence and statutory texts. Combines high-dimensional semantic vector search (`BAAI/bge-m3`) with knowledge graph relationship discovery (`Neo4j`) and multilingual translation into an institutional-grade legal tech console.

---

## 🌟 Key Features

- **🔍 Dual-Channel Hybrid Retrieval:** Simultaneously queries vector space via Qdrant for semantic relevance and Neo4j knowledge graphs for multi-hop legal references.
- **🛡️ Strict Anti-Hallucination Framework:** Prompts enforce factual grounding strictly within retrieved statutory provisions.
- **🌐 Real-Time Arabic-to-English Translation:** Integrated neural translation pipeline for Moroccan Arabic legal texts with dedicated UI toggle.
- **⚡ Context Window Expansion:** Automatically pulls neighboring clauses (`chunk_index ± 1`) to preserve full legislative articles.
- **✨ Progressive AI Reveal Interface:** Institutional UI built with React 19, Tailwind CSS, and GSAP illustrating each step of graph expansion and answer synthesis.

---

## 📐 System Architecture

```mermaid
flowchart TD
    subgraph IN["1. INGESTION & PARSING"]
        PDF["📄 Statutory Acts & Judicial Decrees"] --> OCR["Ain OCR Engine\n(PP-Structure Layout)"]
        OCR --> CHUNK["Markdown Chunker & AST Normalizer"]
    end

    subgraph STORE["2. DUAL KNOWLEDGE STORES"]
        CHUNK -->|BGE-M3 Embeddings| VEC[("Vector DB: Qdrant\n(Dense Semantic Space)")]
        CHUNK -->|Llama Entity Extractor| GRAPH[("Knowledge Graph: Neo4j\n(Entities & Legal Relations)")]
    end

    subgraph QUERY["3. RAG PIPELINE & SYNTHESIS"]
        Q["User Legal Inquiry"] --> EXP["Query Expansion (Groq / Llama-3.3)"]
        EXP -->|Semantic Top-K| VEC
        EXP -->|Cypher Subgraph Query| GRAPH
        VEC --> CTX["Neighbor Chunk Expansion (±1)"]
        CTX --> SYNTH["Synthesis Engine (Anti-Hallucination Guardrails)"]
        GRAPH --> SYNTH
    end

    subgraph OUT["4. CLIENT INTERACTION"]
        SYNTH --> RES["Verified Arabic Response"]
        RES --> TRANS["Neural Legal Translation (English)"]
        RES --> UI["Interactive Institutional Console"]
    end
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- Running Qdrant and Neo4j instances

### 2. Backend Installation

```bash
# Clone the repository
git clone https://github.com/Rib4ko/Legal-GraphRag.git
cd Legal-GraphRag

# Create environment configuration
cat <<EOF > .env
HF_TOKEN=hf_your_huggingface_token
GROQ_API_KEY=gsk_your_groq_key
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
EOF

# Install dependencies using uv or pip
pip install -e .

# Launch FastAPI ASGI server
uvicorn api:app --reload --port 8000
```

### 3. Frontend Installation

```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:3000` to interact with the legal search console.

---

## 📄 License
This repository is open-source and released under the [MIT License](LICENSE).
