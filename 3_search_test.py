"""
3_search_test.py — Phase 2: Vector Search Test
================================================
A simple script to test semantic search against the local Qdrant DB.
It takes a query, embeds it via Hugging Face, and retrieves the closest matches.

Usage:
    uv run python 3_search_test.py
"""
import os
import sys
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from qdrant_client import QdrantClient

# Fix Windows terminal encoding for Arabic
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("❌ HF_TOKEN not found in .env file.")
    sys.exit(1)

MODEL_ID = "BAAI/bge-m3"
DB_PATH = "./data/qdrant_legal_db"
COLLECTION_NAME = "moroccan_legal_corpus"

hf_client = InferenceClient(token=HF_TOKEN)

def get_embedding(text: str) -> list[float] | None:
    try:
        result = hf_client.feature_extraction(text, model=MODEL_ID)
        if isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], list) else result
        return result
    except Exception as e:
        print(f"⚠️ Embedding API error: {e}")
        return None

def main():
    print("🔍 Testing Qdrant Semantic Search")
    print("=" * 50)
    
    query = "ما هي نسبة الضريبة على الإيجار؟" # What is the tax rate for rent?
    print(f"Question: {query}\n")
    
    print("1️⃣  Embedding the query via Hugging Face...")
    query_vec = get_embedding(query)
    
    if query_vec is None:
        print("❌ Failed to get embedding for query.")
        return
        
    print(f"2️⃣  Searching Qdrant Database at '{DB_PATH}'...")
    q_client = QdrantClient(path=DB_PATH)
    
    try:
        # Check if collection exists
        collections = q_client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            print(f"❌ Collection '{COLLECTION_NAME}' does not exist. Run 2_indexer.py first.")
            return

        # Perform the search
        results = q_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            limit=2  # Get top 2 results
        )
        
        print("\n" + "=" * 50)
        print("⚖️  TOP LEGAL MATCHES")
        print("=" * 50)
        
        if not results:
            print("❌ No matches found.")
            return
            
        for i, hit in enumerate(results, 1):
            score = hit.score
            payload = hit.payload
            
            # Reconstruct context from headers
            context = []
            if "chapter" in payload: context.append(payload["chapter"])
            if "article" in payload: context.append(payload["article"])
            context_str = " > ".join(context) if context else "General Context"
            
            print(f"\nMatch #{i} (Score: {score:.4f})")
            print(f"Source: {payload.get('source_file', 'Unknown')}")
            print(f"Context: {context_str}")
            print("-" * 40)
            print(payload.get("text", "No text payload found."))
            
    finally:
        q_client.close()

if __name__ == "__main__":
    main()
