# System Architecture: Moroccan Legal GraphRAG

The Moroccan Legal GraphRAG project utilizes a robust hybrid retrieval architecture that combines Semantic Vector Search with Knowledge Graph exploration to effectively map and retrieve Moroccan Legal documents without hallucination.

## The Data Pipeline

### 1. Document Extraction (`1_extractor.py` & `run_image_ocr.py`)
- Raw legal texts, PDFs, and images are ingested.
- The **Ain OCR Engine** (based on Advanced PP-Structure) handles complex layout analysis and accurate Arabic text extraction from images and scanned documents.
- Basic text extraction is handled for digital PDFs.
- Output is structured as Markdown chunks for indexing, pending human review.

### 2. Vector Indexing (`2_indexer.py`)
- **Model:** `BAAI/bge-m3` via HuggingFace is used to generate high-dimensional text embeddings for each document chunk.
- **Storage:** Chunks and metadata are upserted into **Qdrant**, a local vector database, enabling ultra-fast, dense semantic similarity searches.

### 3. Knowledge Graph Extraction (`5_graph_extractor.py`)
- **LLM-based Extraction:** Llama-3.3-70b processes chunks to extract core Legal Entities (e.g., ministries, laws, decrees) and relationships (e.g., MENTIONS, MODIFIES, SUPERSEDES).
- **Storage:** Extracted data is ingested into **Neo4j** (AuraDB Cloud). This maps the explicit connections and cross-references between different Moroccan legal doctrines.

## The Search Pipeline (`api.py`)

When a user submits a legal query via the React interface, it follows a deterministic pipeline:

1. **Query Expansion:** The original query is sent to Groq (Llama-3.3) to expand keywords and synonyms, optimizing the graph search scope.
2. **Vector Retrieval:** The *original, strict query* is embedded and queried against **Qdrant** to retrieve the Top-K most semantically relevant text chunks.
3. **Context Window Expansion:** For each retrieved chunk, the API automatically retrieves the chunk immediately before and after it (`chunk_index - 1` and `chunk_index + 1`) to provide the LLM with full context.
4. **Graph Extraction:** The expanded query is parsed for entities. These entities are mapped against **Neo4j** using Cypher queries to find related nodes and paths, providing a relationship map.
5. **RAG Synthesis:** Both the expanded vector texts and the graph relationship contexts are fed into the LLM with a strict **Anti-Hallucination prompt**, resulting in a highly accurate, formal Arabic response.

## Frontend UI (`frontend/src/App.jsx`)

The interface is built with Vite, React, and Tailwind CSS.
- Designed with an **"Institutional Tech"** aesthetic (Deep Navy, Legal Gold).
- Uses **GSAP animations** to progressively reveal the search pipeline to the user step-by-step (Query Expansion -> Vectors -> Graph -> Answer), visualizing the AI "thinking" process.
- Features a Canvas-based interactive hero animation representing the Knowledge Graph.
