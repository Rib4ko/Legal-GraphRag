# Moroccan LegalTech GraphRAG Architecture

This document outlines the architecture, data flow, and components of the Moroccan LegalTech GraphRAG project. The system is designed to scrape Moroccan legal texts, process them into both semantic vector embeddings and a knowledge graph, and provide a secure, hallucination-free Search UI using large language models.

## 🏗️ System Architecture

The pipeline is split into four distinct phases: Data Ingestion, Vector Indexing, Graph Extraction, and the User Interface.

### Phase 1: Data Ingestion & OCR (`1_extractor.py`)
This script acts as the entry point for the pipeline, responsible for acquiring the raw legal documents.
* **Scraping:** Connects to the Moroccan Ministry of Justice (Adala) portal API to recursively discover and download legal PDFs.
* **Text Extraction:** Uses `PyMuPDF` (`fitz`) to extract text from the PDFs.
* **Arabic Cleaning:** Moroccan legal PDFs often have broken Arabic text (disconnected or reversed). The script uses `arabic_reshaper` and `bidi` to fix the text layout.
* **Output:** Saves the clean text as Markdown (`.md`) files in the `data/ready_for_db/` directory.

### Phase 2: Vector Database Indexer (`2_indexer.py`)
This script converts the flat Markdown files into a searchable semantic database.
* **OCR Artifact Cleaning:** Uses Regex to fix broken markdown headers (e.g. converting `م ال ادة 8` to `## المادة 8`) to ensure accurate document chunking.
* **Chunking:** Uses LangChain's `MarkdownHeaderTextSplitter` to split the document logically by legal Chapters and Articles, followed by a `RecursiveCharacterTextSplitter`.
* **Embedding:** Uses the HuggingFace Serverless API (`BAAI/bge-m3` model) to generate 1024-dimensional embeddings for each chunk.
* **Storage:** Upserts the chunks and embeddings into a local **Qdrant** database, utilizing deterministic IDs to prevent duplication on re-runs.

### Phase 2.5: Knowledge Graph Extraction (`5_graph_extractor.py`)
This script builds the semantic relationships between legal entities.
* **Entity Extraction:** Reads the same Markdown chunks from `data/ready_for_db/`.
* **LLM Processing:** Uses Groq (`llama-3.3-70b-versatile`) to extract structured entities (e.g., Ministries, Laws, Penalties) and relationships (e.g., `REGULATES`, `SUPERSEDES`). It uses `Literal` types to strictly validate relationship schemas and prevent data poisoning.
* **Storage:** Upserts these nodes and relationships into a **Neo4j** Graph Database.

### Phase 3: The Search Engine UI (`4_search_ui.py`)
This is the front-end Streamlit application that users interact with.
* **Query Expansion:** The user's query is first sent to an LLM to generate synonyms and expand the search scope.
* **Vector Search:** The query is embedded (using HF) and sent to Qdrant to find the Top 8 most semantically relevant legal chunks.
* **Context Expansion (Parent Document Retrieval):** The system dynamically fetches the adjacent chunks (`chunk - 1` and `chunk + 1`) from Qdrant to ensure no information is accidentally truncated.
* **Graph Search:** The system extracts entities from the user's query and searches the Neo4j database (using a Cypher full-text index query) to pull in related graph knowledge.
* **LLM Synthesis:** The expanded vector context and the graph context are fed to the Llama-3 model (`temperature=0.0`) with a highly restrictive system prompt forcing it to answer *strictly* in formal Arabic without any hallucinations.

---

## 📂 Directory Structure

```text
/
├── 1_extractor.py         # Phase 1: Downloads and extracts PDFs
├── 2_indexer.py           # Phase 2: Chunks and embeds text into Qdrant
├── 4_search_ui.py         # Phase 3: Streamlit UI and LLM query processing
├── 5_graph_extractor.py   # Phase 2.5: Extracts Entities/Relations to Neo4j
├── architecture.md        # You are here!
├── evaluation_questions.md# List of test questions to evaluate RAG performance
├── qdrant_guide.md        # Instructions for the vector DB setup
├── .env                   # API Keys (HuggingFace, Neo4j, Groq)
│
├── data/
│   ├── raw_pdfs/          # Original PDFs scraped from Adala
│   ├── ready_for_db/      # Cleaned Markdown files ready for indexing
│   └── qdrant_legal_db/   # Local Qdrant vector database storage
│
└── src/ingestion/         # (Future/Experimental) Advanced "Ain OCR" engine using PaddleOCR
    └── run_image_ocr.py   
```

## 🔒 Security & Performance Features
* **Anti-Hallucination:** API calls are locked to `temperature=0.0` and system prompts explicitly ban outside knowledge or alternative languages.
* **XSS Prevention:** Streamlit UI utilizes CSS for Right-to-Left (RTL) alignment rather than injecting unsafe HTML (`unsafe_allow_html=False`).
* **Path Traversal Protection:** Filenames generated from scraped URLs are sanitized using Python Regex in `1_extractor.py`.
