import os
import json
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from qdrant_client import QdrantClient
from openai import OpenAI
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

app = FastAPI(title="Moroccan Legal GraphRAG API")

# Configure CORS so our Vite frontend can query the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this. For local dev, "*" is fine.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clients Initialization ---
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN missing in environment variables.")

hf_client = InferenceClient(token=HF_TOKEN)
q_client = QdrantClient(path="./data/qdrant_legal_db")

# Neo4j Driver setup
neo4j_uri = os.getenv("NEO4J_URI")
if neo4j_uri and neo4j_uri.startswith("neo4j+s://"):
    neo4j_uri = neo4j_uri.replace("neo4j+s://", "neo4j+ssc://")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_pass = os.getenv("NEO4J_PASSWORD")

neo4j_client = None
if neo4j_uri and neo4j_user and neo4j_pass:
    try:
        neo4j_client = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
    except Exception as e:
        print(f"Warning: Failed to connect to Neo4j: {e}")

# Groq LLM setup
groq_token = os.getenv("GROQ_API_KEY")
llm_client = None
if groq_token:
    llm_client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=groq_token,
    )

MODEL_ID = "BAAI/bge-m3"
COLLECTION_NAME = "moroccan_legal_corpus"

class SearchRequest(BaseModel):
    query: str

class QueryEntities(BaseModel):
    entities: list[str] = Field(description="List of core legal entities, laws, or concepts mentioned in the query.")

def make_point_id(filename: str, chunk_index: int) -> int:
    key = f"{filename}::{chunk_index}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return int(digest, 16) % (2**63)

def get_embedding(text: str) -> list[float] | None:
    try:
        result = hf_client.feature_extraction(text, model=MODEL_ID)
        if isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], list) else result
        return result
    except Exception as e:
        print(f"Embedding generation error: {e}")
        return None

@app.post("/api/search")
async def search_endpoint(request: SearchRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    search_query = query
    expanded_query = ""

    # 1. Query Expansion (using Groq LLM)
    if llm_client:
        try:
            exp_res = llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Rewrite the user's legal question into a comprehensive search query, expanding keywords and synonyms. Keep it in the same language. Return ONLY the rewritten query, nothing else."},
                    {"role": "user", "content": query}
                ],
                temperature=0.0
            )
            expanded = exp_res.choices[0].message.content.strip()
            if expanded:
                search_query = expanded
                expanded_query = expanded
        except Exception as e:
            print(f"Query expansion failed: {e}")

    # 2. Vector Search (using Qdrant)
    query_vec = get_embedding(query)
    if query_vec is None:
        raise HTTPException(status_code=500, detail="Failed to generate query embeddings.")

    try:
        results = q_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            limit=5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Qdrant search failed: {e}")

    hits_data = []
    contexts_for_llm = []

    # 3. Context Window Expansion (retrieve surrounding chunks)
    for i, hit in enumerate(results):
        payload = hit.payload
        score = hit.score
        
        context = []
        if "chapter" in payload: context.append(payload["chapter"])
        if "article" in payload: context.append(payload["article"])
        context_str = " > ".join(context) if context else "General Context"
        
        filename = payload.get('source_file')
        chunk_idx = payload.get('chunk_index')
        expanded_text = payload.get('text', '')
        
        if filename and chunk_idx is not None:
            ids_to_fetch = []
            if chunk_idx > 0:
                ids_to_fetch.append(make_point_id(filename, chunk_idx - 1))
            ids_to_fetch.append(make_point_id(filename, chunk_idx + 1))
            
            try:
                surrounding = q_client.retrieve(
                    collection_name=COLLECTION_NAME,
                    ids=ids_to_fetch
                )
                prev_text = ""
                next_text = ""
                for p in surrounding:
                    if p.payload.get('chunk_index') == chunk_idx - 1:
                        prev_text = p.payload.get('text', '') + "\n\n"
                    elif p.payload.get('chunk_index') == chunk_idx + 1:
                        next_text = "\n\n" + p.payload.get('text', '')
                expanded_text = prev_text + expanded_text + next_text
            except Exception as e:
                print(f"Context expansion failed for chunk {chunk_idx}: {e}")

        hits_data.append({
            "id": hit.id,
            "score": score,
            "filename": filename or "Unknown",
            "context_str": context_str,
            "text": expanded_text
        })
        contexts_for_llm.append(f"Source: {filename} | {context_str}\nText: {expanded_text}")

    # 4. Neo4j Graph Search (extracting entities, looking up relations)
    graph_context = ""
    graph_relationships = []
    if neo4j_client and llm_client:
        try:
            ent_res = llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Extract the key legal entities and concepts from the user's query.\nRespond STRICTLY in raw JSON format matching this schema:\n{\n    \"entities\": [\"entity1\", \"entity2\", ...]\n}\nDo NOT wrap the JSON in markdown formatting or backticks."},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(ent_res.choices[0].message.content)
            query_entities = data.get("entities", [])
            
            if query_entities:
                with neo4j_client.session() as session:
                    cypher = """
                    UNWIND $entities AS ent
                    CALL db.index.fulltext.queryNodes("entity_name_index", ent) YIELD node AS e, score
                    MATCH (e)-[r]-(related:Entity)
                    
                    // Match a chunk that mentions both entities, or fallback to one mentioning the primary entity
                    OPTIONAL MATCH (c:Chunk)
                    WHERE (c)-[:MENTIONS]->(e) AND (c)-[:MENTIONS]->(related)
                    
                    OPTIONAL MATCH (c_fallback:Chunk)-[:MENTIONS]->(e)
                    
                    WITH e, r, related, score, COALESCE(c.text, c_fallback.text, "لا يوجد نص مرجعي متوفر لهذه العلاقة.") AS chunk_text
                    
                    RETURN e.name AS entity, type(r) AS relation, related.name AS related_entity, score, chunk_text
                    ORDER BY score DESC
                    LIMIT 10
                    """
                    res = session.run(cypher, entities=query_entities)
                    for record in res:
                        graph_relationships.append({
                            "entity": record["entity"],
                            "relation": record["relation"],
                            "related_entity": record["related_entity"],
                            "score": record["score"],
                            "chunk_text": record["chunk_text"]
                        })
                
                if graph_relationships:
                    graph_lines = [
                        f"**{r['entity']}**  *{r['relation']}*  **{r['related_entity']}** (Score: {r['score']:.2f})"
                        for r in graph_relationships
                    ]
                    graph_context = "### Graph Relationships:\n" + "\n".join(graph_lines)
        except Exception as e:
            print(f"Neo4j graph query failed: {e}")

    # 5. RAG Synthesis (Groq LLM Llama-3.3-70b)
    answer = "No contexts found to answer your question."
    if contexts_for_llm:
        context_block = "\n\n---\n\n".join(contexts_for_llm)
        system_instruction = f"""You are a strict Moroccan legal assistant. Your ONLY task is to answer the user's question based on the legal contexts below. 
You MUST NOT use any external knowledge, and you MUST NOT hallucinate numbers, rates, or laws that are not explicitly written in the provided text.
However, you MAY infer lists, fields, or form requirements from fragmented text, dotted lines (e.g., .......), or broken formatting if it logically answers the question based on the context.
If the answer cannot be reasonably deduced from the contexts, you must reply: "لا أتوفر على معلومات كافية للإجابة بناءً على الوثائق المتاحة."
Respond ONLY in pure, formal Arabic. Do not use any other languages (like French, Spanish, or English), not even for single words.

Vector Search Contexts:
{context_block}

{graph_context}"""

        try:
            response = llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": query}
                ],
                temperature=0.0
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Error generating answer: {e}"

    return {
        "query": query,
        "expanded_query": expanded_query,
        "answer": answer,
        "hits": hits_data,
        "graph_relationships": graph_relationships
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "neo4j_connected": neo4j_client is not None, "llm_connected": llm_client is not None}
