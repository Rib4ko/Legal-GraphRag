# Moroccan LegalTech Ingestion Pipeline

Welcome to the data ingestion pipeline for your LegalTech SaaS! This project is designed to automatically grab legal documents from Moroccan portals, extract the text accurately, and structure it so it can be fed into an AI (like an LLM or Vector Database) later.

## 📚 Project Overview & Guide

If you're feeling lost, don't worry! I've created a comprehensive, easy-to-understand guide that explains how everything in this project works together.

👉 **[Read the Project Overview Guide](docs/project_overview.md)** 👈

## Quick Start & Testing

Make sure you have your dependencies installed first:
```bash
uv sync
```

You must also have a `.env` file in the root directory containing your Hugging Face token:
```
HF_TOKEN=hf_your_token_here
```

### 1. Test Phase 1: The OCR Engine
This command takes an image (like a screenshot of a legal PDF), performs layout analysis and Arabic-aware OCR, and generates a structured Markdown file in `data/pending_review/`.

```bash
uv run run_image_ocr.py "data/sample_image.png" --lang ar
```
*(You can replace `"data/sample_image.png"` with any image path, like `"C:\Users\zdxta\Pictures\Screenshots\Screenshot.png"`)*

### 2. Test Phase 2: The Vector Database Indexer
After reviewing the Markdown files, move them to `data/approved_data/`. Then, run the indexer. This script reads the Markdown files, chunks them by legal headers, embeds the text using the Hugging Face API, and stores the vectors in the local Qdrant database.

```bash
uv run python 2_indexer.py
```

### 3. Test Semantic Search
Once the indexer has successfully run, you can test if the database is actually returning the correct legal articles based on a semantic query.

```bash
uv run python 3_search_test.py
```
### 4. Run the Search Interface (UI)
For a beautiful, interactive web interface where you can type your questions and see the legal text formatted correctly with Right-to-Left (RTL) support, launch the Streamlit app:

```bash
uv run streamlit run 4_search_ui.py
```
*(This will open a local website in your default browser where you can test the RAG engine interactively.)*
