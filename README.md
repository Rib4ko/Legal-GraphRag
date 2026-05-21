# Moroccan Legal GraphRAG

An advanced AI-powered semantic search and knowledge graph engine for Moroccan legal texts, providing hallucination-free answers using vector embeddings and Neo4j.

## 🚀 Overview

Moroccan Legal GraphRAG is designed to be a highly advanced digital instrument used by top-tier lawyers and legal tech professionals. It blends the strict, determinative nature of a traditional supreme court with the cutting-edge capabilities of a modern AI lab. 

By combining dense vector embeddings (HuggingFace BGE-M3) with a robust Knowledge Graph (Neo4j), the system uncovers hidden relationships between laws, ministries, and entities. A strict anti-hallucination framework ensures factual accuracy, strictly anchoring LLM answers to retrieved documents.

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite, Tailwind CSS v3.4.17, GSAP 3 (ScrollTrigger, Animations), Lucide React
- **Backend API:** FastAPI, Python 3.12
- **Vector Database:** Qdrant (Local)
- **Knowledge Graph:** Neo4j (AuraDB Cloud)
- **Embeddings:** `BAAI/bge-m3` via HuggingFace Inference Client
- **LLM Synthesis:** `llama-3.3-70b-versatile` via Groq

## 📦 Project Structure

```
├── frontend/                  # Vite + React 19 Frontend application
│   ├── src/                   
│   │   ├── components/        # React components (e.g., HeroAnimation)
│   │   ├── App.jsx            # Main application logic and UI pipeline
│   │   └── index.css          # Tailwind CSS configuration and theming
├── api.py                     # FastAPI backend serving the GraphRAG pipeline
├── 1_extractor.py             # Basic PDF scraping pipeline
├── run_image_ocr.py           # Ain OCR Engine (Advanced PP-Structure for Arabic OCR)
├── 2_indexer.py               # Vector database indexer (Qdrant)
├── 5_graph_extractor.py       # Knowledge Graph entity/relation extractor (Neo4j)
└── docs/                      # Additional documentation
```

## ⚙️ Quick Start

### 1. Backend Setup
Install the Python dependencies and configure your `.env` file in the root directory:
```env
HF_TOKEN=hf_your_token
GROQ_API_KEY=gsk_your_token
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

Start the FastAPI server:
```bash
uv run uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup
Navigate to the `frontend` folder, install dependencies, and start the development server:
```bash
cd frontend
npm install
npm run dev
```

## ✨ Key Features

- **Semantic Vector Search:** Deep understanding of legal nuances in Arabic.
- **GraphRAG Expansion:** Resolves complex multi-hop entity relationships using Cypher queries.
- **Anti-Hallucination Guardrails:** Strict prompt engineering ensures the LLM admits "I don't know" when documents lack sufficient context.
- **Progressive UI Reveal:** A sleek, animated dashboard that progressively reveals LLM Query Expansion -> Vector Retrieval -> Graph Extraction -> Final Synthesis.

## 📖 Architecture Details

For a detailed dive into the architecture and pipeline flow, please refer to [ARCHITECTURE.md](ARCHITECTURE.md).