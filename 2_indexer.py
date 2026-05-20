"""
2_indexer.py — Phase 2: Vector Database Indexer
================================================
Reads human-approved Markdown files from data/approved_data/,
chunks them by legal headers (# / ##), embeds each chunk via
the Hugging Face Serverless API (BAAI/bge-m3, 1024D multilingual),
and upserts into a local Qdrant database.

Designed for 8GB RAM / no-GPU machines:
  - No heavy models loaded locally
  - Batch upserts to control memory
  - Rate-limited API calls for free-tier HF
  - try/finally to always release Qdrant lock

Usage:
    uv run python 2_indexer.py
"""
import os
import sys
import time
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Fix Windows terminal encoding for emoji/Arabic
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("❌ HF_TOKEN not found in .env file.")
    print("   Get your token at: https://huggingface.co/settings/tokens")
    print("   Then add it to .env: HF_TOKEN=hf_xxxxx")
    sys.exit(1)

MODEL_ID = "BAAI/bge-m3"                     # 1024D multilingual embeddings
DB_PATH = "./data/qdrant_legal_db"            # Local Qdrant storage
COLLECTION_NAME = "moroccan_legal_corpus"
VECTOR_DIM = 1024
INPUT_DIR = Path("data/ready_for_db")        # Extracted .md files
API_DELAY = 0.3                               # Seconds between HF API calls
BATCH_SIZE = 10                               # Chunks per Qdrant upsert

# Markdown headers that map to legal structure
HEADERS_TO_SPLIT = [
    ("#", "chapter"),     # الفصل / Chapitre
    ("##", "article"),    # المادة / Article
]

# ---------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------
hf_client = InferenceClient(token=HF_TOKEN)


def get_embedding(text: str) -> list[float] | None:
    """Fetch a 1024D embedding from HF Serverless API."""
    try:
        result = hf_client.feature_extraction(text, model=MODEL_ID)
        # API may return nested list or flat list
        if isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], list) else result
        return result
    except Exception as e:
        print(f"  ⚠️ Embedding API error: {e}")
        return None


def make_point_id(filename: str, chunk_index: int) -> int:
    """
    Deterministic numeric ID from filename + chunk index.
    Ensures re-running the indexer updates existing points
    instead of creating duplicates.
    """
    key = f"{filename}::{chunk_index}"
    # Use first 8 bytes of SHA256 → 64-bit positive integer
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return int(digest, 16) % (2**63)


def load_markdown_files(directory: Path) -> list[tuple[str, str]]:
    """
    Load all .md files from the directory.
    Returns list of (filename, content) tuples.
    """
    files = sorted(directory.glob("*.md"))
    if not files:
        print(f"  ⚠️ No .md files found in {directory}")
        return []
    result = []
    import re
    for f in files:
        content = f.read_text(encoding="utf-8")
        if content.strip():
            # Clean OCR artifacts for better header chunking
            content = re.sub(r'م\s*ال\s*ادة\s*(\d+)', r'## المادة \1', content)
            content = re.sub(r'ال\s*م\s*ادة\s*(\d+)', r'## المادة \1', content)
            content = re.sub(r'ف\s*ص\s*ل\s*(\d+)', r'## الفصل \1', content)
            content = re.sub(r'ال\s*ف\s*ص\s*ل\s*(\d+)', r'## الفصل \1', content)
            
            result.append((f.name, content))
            print(f"  📄 Loaded: {f.name} ({len(content)} chars)")
    return result


def chunk_document(text: str) -> list[dict]:
    """
    Split a Markdown document by legal headers.
    Returns list of dicts with 'content' and 'metadata'.
    """
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT
    )
    md_header_splits = splitter.split_text(text)
    
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    raw_chunks = char_splitter.split_documents(md_header_splits)

    chunks = []
    for chunk in raw_chunks:
        content = chunk.page_content.strip()
        if not content:
            continue
        meta = dict(chunk.metadata)  # e.g. {"chapter": "...", "article": "..."}
        chunks.append({"content": content, "metadata": meta})
    return chunks


# ---------------------------------------------------------
# 3. MAIN INDEXING PIPELINE
# ---------------------------------------------------------
def main():
    print("⚖️  Moroccan Legal Indexer — Phase 2")
    print("=" * 50)

    # Ensure input directory exists
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load files
    print(f"\n📂 Scanning {INPUT_DIR}/ ...")
    files = load_markdown_files(INPUT_DIR)
    if not files:
        print("\n✅ Nothing to index. Add .md files to data/approved_data/")
        return

    # Initialize Qdrant
    print(f"\n🗄️  Opening Qdrant database at {DB_PATH}")
    q_client = QdrantClient(path=DB_PATH)

    try:
        # Ensure collection exists
        collections = q_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)

        if not exists:
            print(f"  📦 Creating collection '{COLLECTION_NAME}' (dim={VECTOR_DIM})")
            q_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_DIM,
                    distance=Distance.COSINE,
                ),
            )
        else:
            info = q_client.get_collection(COLLECTION_NAME)
            print(f"  ✅ Collection ready ({info.points_count} existing points)")

        # Process each file
        total_indexed = 0
        total_skipped = 0

        for filename, content in files:
            print(f"\n{'─' * 40}")
            print(f"📄 Processing: {filename}")

            chunks = chunk_document(content)
            print(f"  ✂️  Split into {len(chunks)} chunks")

            if not chunks:
                print("  ⚠️ No meaningful chunks found, skipping.")
                continue

            # Embed and upsert in batches
            batch: list[models.PointStruct] = []

            for i, chunk in enumerate(chunks):
                point_id = make_point_id(filename, i)

                # Build rich payload for future RAG retrieval
                payload = {
                    "text": chunk["content"],
                    "source_file": filename,
                    "chunk_index": i,
                    **chunk["metadata"],  # chapter, article headers
                }

                # Get embedding
                vector = get_embedding(chunk["content"])
                time.sleep(API_DELAY)  # Rate limit

                if vector is None:
                    print(f"  ⚠️ Skipped chunk {i} (embedding failed)")
                    total_skipped += 1
                    continue

                batch.append(
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                )

                # Flush batch
                if len(batch) >= BATCH_SIZE:
                    q_client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=batch,
                    )
                    total_indexed += len(batch)
                    print(f"  💾 Upserted batch ({len(batch)} chunks)")
                    batch = []

            # Flush remaining
            if batch:
                q_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch,
                )
                total_indexed += len(batch)
                print(f"  💾 Upserted final batch ({len(batch)} chunks)")

        # Summary
        print(f"\n{'=' * 50}")
        print(f"✅ Indexing complete!")
        print(f"   📊 Indexed: {total_indexed} chunks")
        print(f"   ⚠️ Skipped: {total_skipped} chunks")

        # Verify
        info = q_client.get_collection(COLLECTION_NAME)
        print(f"   🗄️  Total points in DB: {info.points_count}")

    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        raise

    finally:
        q_client.close()
        print("\n🔒 Database session closed safely.")


if __name__ == "__main__":
    main()
