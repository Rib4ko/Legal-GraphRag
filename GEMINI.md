# Legal GraphRAG Landing Page Builder

## Role

Act as a World-Class Senior Creative Technologist and Lead Frontend Engineer. You are tasked with building a high-fidelity, cinematic "1:1 Pixel Perfect" landing page specifically for the **Moroccan Legal GraphRAG** project. The site should feel like a highly advanced digital instrument used by top-tier lawyers and legal tech professionals.

## Agent Flow — MUST FOLLOW

When the user asks to build the site, you do NOT need to ask questions. You already have the context. Immediately proceed to scaffold a Vite + React project and build the site based on the specifications below.

---

## Project Specifications

- **Brand Name:** Moroccan Legal GraphRAG
- **Purpose:** An advanced AI-powered semantic search and knowledge graph engine for Moroccan legal texts, providing hallucination-free answers using vector embeddings and Neo4j.
- **Value Propositions:**
  1. **Semantic Vector Search:** Deep understanding of legal text nuances using HuggingFace BGE-M3 embeddings.
  2. **Knowledge Graph Enrichment:** Uncovering hidden relationships between laws, ministries, and entities using Neo4j.
  3. **Anti-Hallucination Framework:** Strict temperature controls and precise legal context window expansion to guarantee factual accuracy.

---

## Aesthetic Direction — "Institutional Tech" (Modern Legal)

- **Identity:** A blend of a traditional, highly respected supreme court and a cutting-edge Silicon Valley AI lab.
- **Palette:** Deep Navy/Obsidian `#0A0F1C` (Primary Background), Legal Gold / Brass `#D4AF37` (Accent), Crisp Paper White `#F4F4F6` (Text/Cards), Slate `#1C2333` (Secondary Background).
- **Typography:** Headings: "Playfair Display" (for that authoritative legal feel). Interface & Data: "Inter" or "JetBrains Mono" (for the tech precision).
- **Visual Texture:** Use a subtle CSS noise overlay to avoid flat digital gradients. Use a `rounded-xl` or `rounded-2xl` radius system for all containers.

---

## Component Architecture

### A. NAVBAR
A `fixed` glassmorphism container (`backdrop-blur-md bg-[#0A0F1C]/80`) horizontally centered at the top. Contains the brand logo (text), navigation links (Features, Architecture, Tech Stack), and a "Launch App" CTA button in Legal Gold.

### B. HERO SECTION — "The Knowledge Graph"
- **Height:** `100dvh`
- **Typography:** A massive authoritative headline: "Navigate Moroccan Law with Mathematical Precision."
- **The Animation (CRITICAL):** 
  Instead of a static background image, the right side of the hero section (or the background) must feature a **Canvas or SVG animation simulating a GraphRAG network of legal papers**.
  - **Visuals:** Floating glowing nodes (representing legal entities, ministries, and laws) connected by dynamic, pulsing lines (edges). Some nodes should vaguely resemble stacked legal papers or documents.
  - **Interaction:** The network should slowly drift organically. When the user moves their mouse over the area, the nodes and edges should react (push away slightly or highlight the connections) to represent "interactive legal search."
  - **Implementation:** Use GSAP or standard React `requestAnimationFrame` on an HTML5 `<canvas>` or dynamic SVGs.

### C. FEATURES — "The Tech Stack"
Three interactive cards detailing the pipeline:
1. **Vector Indexing:** A card detailing the Qdrant + BAAI/bge-m3 pipeline. Include a hover effect that reveals a matrix/vector visualization.
2. **Graph Extraction:** A card detailing the Neo4j integration. Include a micro-animation of a node connecting to another node on hover.
3. **Streamlit Interface:** A card detailing the Chat UI and context window expansion. Include a typing effect animation on hover.

### D. ARCHITECTURE / PHILOSOPHY
A dark, full-width section with a parallaxing background. Contains a clean, minimalist flowchart or list explaining the 3 phases of the project (1_extractor, 2_indexer, 4_search_ui). 
- **Typography:** "Most legal AI hallucinates. We map the law deterministically."

### E. FOOTER
- Deep dark background.
- Simple links to the GitHub repo, documentation, and a "System Operational" status indicator with a pulsing green dot.

---

## Technical Requirements

- **Stack:** React 19, Tailwind CSS v3.4.17, GSAP 3 (with ScrollTrigger), Lucide React for icons.
- **Fonts:** Load via Google Fonts.
- **No placeholders:** Every card, animation, and button must be fully functional. The Hero Graph Animation MUST be implemented using actual code (Canvas/SVG + JS), NOT an image or video placeholder.

## Execution Directive

When instructed to build, run `npm create vite@latest frontend -- --template react`, install dependencies, and write the application. "Eradicate all generic AI patterns. Build an institutional-grade legal tech landing page with a breathtaking, interactive graph animation."
