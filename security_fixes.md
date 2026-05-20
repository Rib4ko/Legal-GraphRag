# Cybersecurity Improvements Report

This document outlines the security vulnerabilities identified in the Moroccan LegalTech project and the specific fixes implemented to address them.

## 1. Cross-Site Scripting (XSS) Vulnerability
**Location:** `4_search_ui.py` (Phase 3: Semantic Search UI)

**The Issue:** 
The application was using `unsafe_allow_html=True` with Streamlit's `st.markdown()` to wrap the LLM's Arabic responses in a custom HTML `<div>` to enforce Right-To-Left (RTL) styling. This was extremely dangerous. If an attacker managed to poison a legal document with malicious HTML (e.g., `<script>alert('Hacked')</script>`), or manipulated the LLM via prompt injection, that malicious code would be executed in the browser of anyone using the search UI.

**The Fix:**
I completely removed `unsafe_allow_html=True` from the dynamic data rendering. Instead, I injected a global CSS block at the top of the file that securely targets native Streamlit chat and markdown containers (`[data-testid="stChatMessageContent"]`) to enforce RTL styling. Now, Streamlit natively sanitizes all LLM output, rendering any malicious HTML as harmless plain text.

## 2. LLM Prompt Injection
**Locations:** `4_search_ui.py` and `5_graph_extractor.py`

**The Issue:**
Both the UI and the Graph Extractor were dynamically building prompts by blindly concatenating system instructions (e.g., "You are a helpful Moroccan legal assistant") with untrusted user input and raw document text. They were sending this entire block as a single `{"role": "user"}` message. This made it trivial for an attacker to embed instructions like *"Ignore all previous instructions and do X"* within a legal text or search query, hijacking the LLM.

**The Fix:**
I strictly separated the roles. The hardcoded instructions and constraints are now passed securely in the `{"role": "system"}` message, while the untrusted user queries and document texts are isolated in the `{"role": "user"}` message. Modern LLMs heavily prioritize system prompts over user prompts, drastically reducing the success rate of injection attacks.

## 3. Data / Graph Poisoning
**Location:** `5_graph_extractor.py` (Phase 2.5: Neo4j Graph Extraction)

**The Issue:**
The application uses the LLM to extract entities and relationships, enforcing a schema using Pydantic. However, the `relation_type` field was typed simply as a generic `str`. If the LLM hallucinated, or if an attacker used prompt injection to confuse the model, it could invent arbitrary relationships (e.g., `DELETES_DATABASE`, `USER_IS_ADMIN`), permanently poisoning the Neo4j graph database schema.

**The Fix:**
I implemented Python's `typing.Literal` to enforce strict boundaries on the schema. The `relation_type` field is now strictly typed as `Literal["REFERENCES", "MODIFIES", "SUPERSEDES", "MENTIONS"]`. If the LLM attempts to return any relationship outside of these four approved types, Pydantic will reject the payload entirely, safeguarding the database integrity.

## 4. Path Traversal & Insecure File Writes
**Location:** `1_extractor.py` (Phase 1: Ingestion Pipeline)

**The Issue:**
When downloading PDFs, the script blindly trusted the URL structure to create the local filename (`filename = url.split("/")[-1]`). If the source API was compromised or returned a maliciously crafted path (e.g., `../../../etc/passwd` or `malicious.exe`), the script could have overwritten critical system files or saved dangerous executables to the server.

**The Fix:**
I introduced a robust regex-based sanitization step. Before saving, the filename is now stripped of all non-alphanumeric characters (except for safe dots, hyphens, and underscores) and cannot begin with dots or hyphens. If the resulting string is empty, it securely defaults to `document.pdf`.
