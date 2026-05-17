"""
4_search_ui.py — Phase 3: Semantic Search User Interface
=========================================================
A beautiful, interactive web interface built with Streamlit to 
allow users to query the local Qdrant legal database.

Usage:
    uv run streamlit run 4_search_ui.py
"""
import os
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from qdrant_client import QdrantClient
import google.generativeai as genai
from neo4j import GraphDatabase
from pydantic import BaseModel, Field
import json

class QueryEntities(BaseModel):
    entities: list[str] = Field(description="List of core legal entities, laws, or concepts mentioned in the query.")

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Moroccan Legal RAG",
    page_icon="⚖️",
    layout="centered"
)

# Custom CSS for right-to-left (RTL) Arabic text
st.markdown("""
<style>
    .arabic-text {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 18px;
        line-height: 1.6;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-right: 4px solid #0056b3;
        margin-bottom: 20px;
    }
    .score-badge {
        background-color: #e9ecef;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INITIALIZATION (Cached for performance)
# ---------------------------------------------------------
@st.cache_resource
def init_clients():
    load_dotenv()
    token = os.getenv("HF_TOKEN")
    if not token:
        st.error("❌ HF_TOKEN not found in .env file. Please add it first.")
        st.stop()
        
    hf = InferenceClient(token=token)
    qd = QdrantClient(path="./data/qdrant_legal_db")
    
    neo4j_uri = os.getenv("NEO4J_URI")
    if neo4j_uri and neo4j_uri.startswith("neo4j+s://"):
        neo4j_uri = neo4j_uri.replace("neo4j+s://", "neo4j+ssc://")
        
    neo4j_user = os.getenv("NEO4J_USERNAME")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")
    
    neo4j_driver = None
    if neo4j_uri and neo4j_user and neo4j_pass:
        neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
    else:
        st.warning("⚠️ Neo4j credentials missing in .env. Graph context will be disabled.")
    
    gemini_token = os.getenv("GEMINI_API_KEY")
    llm = None
    if gemini_token:
        genai.configure(api_key=gemini_token)
        llm = genai.GenerativeModel('gemini-1.5-flash')
        
    return hf, qd, llm, neo4j_driver

hf_client, q_client, llm_client, neo4j_client = init_clients()

MODEL_ID = "BAAI/bge-m3"
COLLECTION_NAME = "moroccan_legal_corpus"

def get_embedding(text: str) -> list[float] | None:
    try:
        result = hf_client.feature_extraction(text, model=MODEL_ID)
        if isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], list) else result
        return result
    except Exception as e:
        st.error(f"Embedding error: {e}")
        return None

# ---------------------------------------------------------
# 3. UI LAYOUT
# ---------------------------------------------------------
st.title("⚖️ Moroccan Legal Search Engine")
st.markdown("Ask questions about Moroccan law in Arabic or French. The engine will search the local vector database to find the most relevant legal articles.")

# Search bar
query = st.text_input("Enter your legal question:", placeholder="مثال: ما هي نسبة الضريبة على الإيجار؟")

if query:
    with st.spinner("Searching the database..."):
        search_query = query
        
        # 0. Query Expansion
        if llm_client:
            try:
                expansion_prompt = f"Rewrite this legal question into a comprehensive search query, expanding keywords and synonyms. Keep it in the same language. Return ONLY the rewritten query, nothing else.\nOriginal: {query}"
                exp_res = llm_client.generate_content(expansion_prompt)
                expanded = exp_res.text.strip()
                if expanded:
                    search_query = expanded
                    st.info(f"🔍 Expanded Search Query: {search_query}")
            except Exception as e:
                pass # Fail silently and use original query
                
        query_vec = get_embedding(search_query)
        
        if query_vec is not None:
            try:
                # Perform the search
                results = q_client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vec,
                    limit=8  # Show top 8 matches
                )
                
                if results:
                    st.success(f"Found {len(results)} relevant results:")
                    
                    contexts_for_llm = []
                    
                    # Display results
                    for i, hit in enumerate(results, 1):
                        payload = hit.payload
                        score = hit.score
                        
                        # Reconstruct context
                        context = []
                        if "chapter" in payload: context.append(payload["chapter"])
                        if "article" in payload: context.append(payload["article"])
                        context_str = " > ".join(context) if context else "General Context"
                        
                        contexts_for_llm.append(f"Source: {payload.get('source_file', 'Unknown')} | {context_str}\nText: {payload.get('text', '')}")
                        
                        with st.expander(f"Result {i} | {context_str}", expanded=False):
                            st.markdown(f"<div class='score-badge'>Relevance Score: {score:.4f}</div>", unsafe_allow_html=True)
                            st.caption(f"Source: {payload.get('source_file', 'Unknown')}")
                            
                            # Display Arabic text with RTL styling
                            st.markdown(f"<div class='arabic-text'>{payload.get('text', '')}</div>", unsafe_allow_html=True)
                            
                    if llm_client:
                        st.markdown("### 🤖 AI Analysis")
                        
                        graph_context = ""
                        if neo4j_client:
                            # 1. Extract entities from user query
                            try:
                                extract_prompt = f"Extract the key legal entities and concepts from this query: {query}"
                                ent_res = llm_client.generate_content(
                                    extract_prompt,
                                    generation_config=genai.GenerationConfig(
                                        response_mime_type="application/json",
                                        response_schema=QueryEntities
                                    )
                                )
                                data = json.loads(ent_res.text)
                                parsed_msg = QueryEntities(**data)
                                query_entities = parsed_msg.entities if parsed_msg else []
                                
                                # 2. Query Neo4j for these entities
                                if query_entities:
                                    with neo4j_client.session() as session:
                                        cypher = """
                                        UNWIND $entities AS ent
                                        CALL db.index.fulltext.queryNodes("entity_name_index", ent) YIELD node AS e, score
                                        MATCH (e)-[r]-(related:Entity)
                                        RETURN e.name AS entity, type(r) AS relation, related.name AS related_entity, score
                                        ORDER BY score DESC
                                        LIMIT 10
                                        """
                                        res = session.run(cypher, entities=query_entities)
                                        graph_lines = [f"Graph Knowledge: '{record['entity']}' {record['relation']} '{record['related_entity']}'" for record in res]
                                        if graph_lines:
                                            graph_context = "### Graph Relationships:\n" + "\n".join(graph_lines)
                            except Exception as e:
                                st.warning(f"Graph query failed: {e}")

                        context_block = "\n\n---\n\n".join(contexts_for_llm)
                        
                        prompt = f"""You are a helpful Moroccan legal assistant. Answer the user's question based strictly on the provided legal contexts below. 
If the answer is not contained in the contexts, say you don't know based on the provided documents. 
Respond in the same language as the user's question (mostly Arabic or French).

Vector Search Contexts:
{context_block}

{graph_context}

User Question: {query}"""

                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()
                            try:
                                response = llm_client.generate_content(
                                    prompt,
                                    stream=True
                                )
                                full_response = ""
                                for chunk in response:
                                    if chunk.text:
                                        full_response += chunk.text
                                        # Use Markdown with RTL direction for Arabic text if needed
                                        message_placeholder.markdown(f"<div class='arabic-text' style='background-color: transparent; border: none; padding: 0;'>{full_response}▌</div>", unsafe_allow_html=True)
                                message_placeholder.markdown(f"<div class='arabic-text' style='background-color: transparent; border: none; padding: 0;'>{full_response}</div>", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"LLM Generation failed: {e}")
                else:
                    st.info("No matching laws found in the database. Try rephrasing your question.")
            except Exception as e:
                st.error(f"Database search failed: {e}")
                st.info("Make sure you have run the indexer (2_indexer.py) to populate the database first.")
