# Qdrant Vector Database – How It Works in the Moroccan LegalTech Project

This guide walks you through everything you need to know about the **Qdrant** vector database that powers the semantic search and Retrieval‑Augmented Generation (RAG) pipeline.

---

## 1️⃣ Why Qdrant?
- **Vector‑first** storage: Stores dense embeddings (float vectors) alongside arbitrary payload metadata.
- **Fast ANN search**: Uses HNSW (Hierarchical Navigable Small World) for low‑latency nearest‑neighbor retrieval.
- **Persisted on‑disk**: All data lives under `data/qdrant_legal_db`, making it easy to back‑up or move.
- **Python client**: The `qdrant-client` library gives a clean, typed interface that works seamlessly with the HuggingFace embeddings we generate.

---

## 2️⃣ Project Layout
```
legal/
├─ data/
│   ├─ pending_review/        # OCR output waiting for human validation
│   ├─ approved_data/         # Clean Markdown ready for indexing
│   └─ qdrant_legal_db/       # **Qdrant DB files** (persisted vectors)
├─ src/ingestion/…            # OCR and preprocessing code
├─ 2_indexer.py               # Builds the collection & uploads embeddings
├─ 4_search_ui.py             # Streamlit UI – queries Qdrant & calls LLM
└─ qdrant_guide.md            # <‑‑ **You are reading it!**
```

---

## 3️⃣ How the Collection Is Created (see `2_indexer.py`)
```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialise a local Qdrant instance (file based)
client = QdrantClient(path="./data/qdrant_legal_db")

# Define the collection schema – the fields we will store alongside each vector
VECTOR_SIZE = 1024   # BGE‑M3 outputs 1024‑dim vectors
client.recreate_collection(
    collection_name="moroccan_legal_corpus",
    vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
    hnsw_config=models.HnswConfigMef(
        ef_construct=200,   # quality‑vs‑speed trade‑off for indexing
        max_indexing_threads=4,
    ),
    # Payload schema (optional, helps with filtering)
    payload_schema={
        "source_file": models.PayloadSchemaType.KEYWORD,
        "chapter": models.PayloadSchemaType.TEXT,
        "article": models.PayloadSchemaType.TEXT,
        "text": models.PayloadSchemaType.TEXT,
    },
)
```
- **`recreate_collection`** drops any existing collection with the same name and builds a fresh one – handy during development.
- **`VECTOR_SIZE`** must match the dimensionality of the embedding model (`BAAI/bge-m3` → 1024).
- **Payload fields** let us store the original Markdown chunk, its location (chapter/article), and the source file name for later citation.

---

## 4️⃣ Indexing – Turning Markdown into Vectors (inside `2_indexer.py`)
```python
import glob, json
from pathlib import Path
from huggingface_hub import InferenceClient
from qdrant_client import QdrantClient

hf = InferenceClient(token=os.getenv("HF_TOKEN"))
client = QdrantClient(path="./data/qdrant_legal_db")

# Iterate over every approved Markdown file
for md_path in Path("data/approved_data").glob("*.md"):
    raw = md_path.read_text(encoding="utf-8")
    # Simple chunking – you can replace this with a smarter splitter
    for i, chunk in enumerate(raw.split("\n\n")):
        embedding = hf.feature_extraction(chunk, model="BAAI/bge-m3")[0]
        payload = {
            "source_file": md_path.name,
            "chapter": f"Chapter-{i}",   # placeholder – real parser extracts real headings
            "article": f"Article-{i}",
            "text": chunk,
        }
        client.upsert(
            collection_name="moroccan_legal_corpus",
            points=[models.PointStruct(id=f"{md_path.stem}_{i}",
                                       vector=embedding,
                                       payload=payload)],
        )
```
**Key take‑aways**
- Each *point* gets a unique `id` (`<filename>_<chunk_index>`).  
- The embedding is stored as the vector; the raw text and metadata become payload.
- `upsert` works both for new points and for updates if you re‑run the indexer after fixing a chunk.

---

## 5️⃣ Querying – What the UI Does (`4_search_ui.py`)
```python
# Embed the user query
query_vec = hf_client.feature_extraction(user_query, model=MODEL_ID)[0]

# Perform a nearest‑neighbor search (top‑k = 3)
results = q_client.search(
    collection_name=COLLECTION_NAME,
    query_vector=query_vec,
    limit=3,
)

# Each `hit` contains:
#   hit.id      – our internal point id
#   hit.score   – cosine similarity (higher = more similar)
#   hit.payload – the dictionary we stored during indexing
```
- The **payload** gives you the exact legal text, chapter, article, and source file – perfect for citation.
- Because we use **cosine distance**, scores range roughly `0…1`.  Higher scores mean a tighter semantic match.

---

## 6️⃣ Persistence & Portability
- All Qdrant files live in `data/qdrant_legal_db/`.  If you move the project folder, the DB moves with it – no extra service required.
- For production you could replace the local instance with a **Docker** container or a **managed Qdrant Cloud** endpoint:
```bash
# Docker example (run once)
docker run -p 6333:6333 -v $(pwd)/data/qdrant_legal_db:/qdrant/storage qdrant/qdrant
```
Then point the client at the remote address:
```python
client = QdrantClient(host="localhost", port=6333)
```
---

## 7️⃣ Quick Checklist – Getting Qdrant Up & Running
1. **Install the client** – already added via `uv sync` (`qdrant-client>=1.9.0`).
2. **Run the indexer** – `uv run python 2_indexer.py`.  This creates the collection and populates vectors.
3. **Start the UI** – `uv run streamlit run 4_search_ui.py`.  The UI will automatically connect to `./data/qdrant_legal_db`.
4. **If you delete the folder** – simply re‑run the indexer; Qdrant will rebuild from the Markdown files.

---

## 8️⃣ Troubleshooting Tips
| Symptom | Likely Cause | Fix |
|---|---|---|
| `FileNotFoundError: ./data/qdrant_legal_db` | DB folder missing | Run the indexer (`2_indexer.py`) – it creates the folder automatically |
| No results returned | Query embedding dimension mismatch | Ensure `VECTOR_SIZE` (=1024) matches the model used (`BAAI/bge-m3`). Re‑run the indexer if you changed the model |
| Very low scores (≈0) | Model token missing or invalid | Verify `HF_TOKEN` in `.env` and that it has inference access |
| UI crashes on search | `q_client` not defined | After the recent LLM integration, make sure you import `QdrantClient` and call `init_clients()` which now returns `hf, qd, llm` |

---

## 9️⃣ Going Further
- **Filtering** – you can add filters on payload fields (`source_file`, `chapter`, etc.) to narrow results.
- **Fine‑tuning** – increase `ef_construct` or `hnsw_param.ef` for higher recall at the cost of slower indexing/search.
- **Hybrid Search** – combine keyword filters with vector similarity for even richer legal retrieval.

---

### 🎉 You’re Ready!
You now understand how the Qdrant vector database fits into the overall architecture, how it’s built, indexed, and queried. Feel free to experiment with different chunking strategies or vector models – the rest of the pipeline (Streamlit UI + LLM) will automatically pick up the new embeddings.

*(If you need more examples or want to switch to a hosted Qdrant instance, just let me know!)*
