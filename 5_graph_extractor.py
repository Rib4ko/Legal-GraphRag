"""
5_graph_extractor.py — Phase 2.5: Neo4j Graph Extraction
========================================================
Reads chunks from the same Markdown files used in 2_indexer.py,
uses an LLM to extract structured entities and legal relationships,
and upserts them into Neo4j AuraDB.
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI
from pydantic import BaseModel, Field

# Ensure we can import from local modules or just copy the needed ones
# We'll import `make_point_id` and `chunk_document` directly to keep consistency
import importlib.util
spec = importlib.util.spec_from_file_location("indexer", "2_indexer.py")
indexer = importlib.util.module_from_spec(spec)
sys.modules["indexer"] = indexer
spec.loader.exec_module(indexer)

# Fix Windows terminal encoding
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# Neo4j Config
NEO4J_URI = os.getenv("NEO4J_URI")
if NEO4J_URI and NEO4J_URI.startswith("neo4j+s://"):
    NEO4J_URI = NEO4J_URI.replace("neo4j+s://", "neo4j+ssc://")
    
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# OpenRouter / OpenAI config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    print("❌ Neo4j credentials missing in .env")
    sys.exit(1)

if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY missing in .env")
    sys.exit(1)

INPUT_DIR = Path("data/ready_for_db")

# Pydantic schemas for structured extraction
class Entity(BaseModel):
    name: str = Field(description="Name of the entity, person, organization, location, or concept")
    type: str = Field(description="Type of entity (e.g., PERSON, ORGANIZATION, LOCATION, CONCEPT)")

class Relationship(BaseModel):
    source_entity: str = Field(description="Name of the source entity")
    target_entity: str = Field(description="Name of the target entity")
    relation_type: str = Field(description="Type of relationship: REFERENCES, MODIFIES, SUPERSEDES, or MENTIONS")

class ExtractionResult(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]

llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def extract_triples(text: str) -> ExtractionResult | None:
    prompt = f"""
    Analyze the following Moroccan legal text and extract key entities and relationships.
    Entities should be specific named concepts, organizations, people, or laws.
    Relationships MUST be one of: REFERENCES, MODIFIES, SUPERSEDES, MENTIONS.
    
    Text:
    {text}
    """
    try:
        response = llm_client.beta.chat.completions.parse(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=[{"role": "user", "content": prompt}],
            response_format=ExtractionResult
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"  ⚠️ Extraction failed: {e}")
        return None

def upsert_to_neo4j(doc_title: str, chunk_id: int, chunk_text: str, extraction: ExtractionResult):
    with driver.session() as session:
        # Upsert Document
        session.run("""
            MERGE (d:Document {title: $title})
        """, title=doc_title)
        
        # Upsert Chunk
        session.run("""
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $text
        """, chunk_id=chunk_id, text=chunk_text)
        
        # Link Document -> Chunk
        session.run("""
            MATCH (d:Document {title: $title})
            MATCH (c:Chunk {id: $chunk_id})
            MERGE (d)-[:CONTAINS]->(c)
        """, title=doc_title, chunk_id=chunk_id)
        
        # Upsert Entities and chunk->entity mentions
        for ent in extraction.entities:
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.type = $type
                WITH e
                MATCH (c:Chunk {id: $chunk_id})
                MERGE (c)-[:MENTIONS]->(e)
            """, name=ent.name, type=ent.type, chunk_id=chunk_id)
            
        # Upsert Relationships between entities
        for rel in extraction.relationships:
            session.run("""
                MATCH (source:Entity {name: $source_name})
                MATCH (target:Entity {name: $target_name})
                CALL apoc.create.relationship(source, $rel_type, {}, target) YIELD rel
                RETURN rel
            """, source_name=rel.source_entity, target_name=rel.target_entity, rel_type=rel.relation_type)

def main():
    print("🕸️ Neo4j Graph Extractor")
    print("=" * 50)
    
    # Create Full-Text Index for faster retrieval in UI
    with driver.session() as session:
        session.run("""
        CREATE FULLTEXT INDEX entity_name_index IF NOT EXISTS 
        FOR (e:Entity) ON EACH [e.name]
        """)
        print("✅ Neo4j Full-Text Index 'entity_name_index' verified.")
    
    files = indexer.load_markdown_files(INPUT_DIR)
    
    for filename, content in files:
        print(f"\n📄 Processing Graph for: {filename}")
        chunks = indexer.chunk_document(content)
        
        for i, chunk in enumerate(chunks):
            chunk_id = indexer.make_point_id(filename, i)
            text = chunk["content"]
            
            print(f"  🧠 Extracting triples for chunk {i}...")
            extraction = extract_triples(text)
            
            if extraction:
                upsert_to_neo4j(filename, chunk_id, text, extraction)
                print(f"  ✅ Upserted {len(extraction.entities)} entities and {len(extraction.relationships)} relationships.")
                
    print("\n✅ Graph extraction complete!")
    driver.close()

if __name__ == "__main__":
    main()
