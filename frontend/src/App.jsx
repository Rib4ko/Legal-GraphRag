import React, { useEffect, useState, useRef } from "react";
import { 
  Scale, 
  Search, 
  Share2, 
  ShieldCheck, 
  Database, 
  GitBranch, 
  Layers, 
  Cpu, 
  ArrowUpRight, 
  Activity, 
  ArrowLeft,
  ChevronRight,
  Sparkles,
  Terminal,
  FileText,
  Lock,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CornerDownLeft,
  ArrowDown
} from "lucide-react";
import gsap from "gsap";
import HeroAnimation from "./components/HeroAnimation";

export default function App() {
  const [isAppActive, setIsAppActive] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Results State
  const [answer, setAnswer] = useState("");
  const [expandedQuery, setExpandedQuery] = useState("");
  const [hits, setHits] = useState([]);
  const [graphRelationships, setGraphRelationships] = useState([]);
  
  // Progressive Reveal States
  const [revealStep, setRevealStep] = useState(0); // 0: Idle/loading, 1: Expanded, 2: Vector, 3: Graph, 4: Answer
  const [expandedHits, setExpandedHits] = useState({});
  const [expandedRelations, setExpandedRelations] = useState({});

  // Refs for animation targets
  const step1Ref = useRef(null);
  const step2Ref = useRef(null);
  const step3Ref = useRef(null);
  const step4Ref = useRef(null);

  useEffect(() => {
    // Initial GSAP Entrances for Landing Page
    if (!isAppActive) {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
      tl.fromTo(".nav-island", { y: -20, opacity: 0 }, { y: 0, opacity: 1, duration: 1 })
        .fromTo(".hero-tag", { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6 }, "-=0.6")
        .fromTo(".hero-title", { y: 25, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8 }, "-=0.5")
        .fromTo(".hero-desc", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8 }, "-=0.6")
        .fromTo(".hero-ctas", { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6 }, "-=0.6")
        .fromTo(".hero-canvas", { opacity: 0 }, { opacity: 1, duration: 1.5 }, "-=0.8");
    } else {
      // Entrances for Dashboard Search View
      gsap.fromTo(".dashboard-content", { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" });
    }
  }, [isAppActive]);

  // Handle step-by-step GSAP animation trigger on reveal change
  useEffect(() => {
    if (revealStep === 1 && step1Ref.current) {
      gsap.fromTo(step1Ref.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" });
    }
    if (revealStep === 2 && step2Ref.current) {
      gsap.fromTo(step2Ref.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" });
    }
    if (revealStep === 3 && step3Ref.current) {
      gsap.fromTo(step3Ref.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" });
    }
    if (revealStep === 4 && step4Ref.current) {
      gsap.fromTo(step4Ref.current, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" });
    }
  }, [revealStep]);

  const toggleHitExpansion = (id) => {
    setExpandedHits(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const toggleRelationExpansion = (idx) => {
    setExpandedRelations(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setRevealStep(0);
    setAnswer("");
    setExpandedQuery("");
    setHits([]);
    setGraphRelationships([]);
    setExpandedRelations({});

    try {
      const response = await fetch("http://localhost:8000/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();

      // Store data in state
      setAnswer(data.answer);
      setExpandedQuery(data.expanded_query);
      setHits(data.hits || []);
      setGraphRelationships(data.graph_relationships || []);
      
      // Stop general loading and start sequential reveal animation
      setLoading(false);
      
      // Step 1: Expanded Question
      setRevealStep(1);
      
      // Step 2: Vector Results (after 800ms)
      await new Promise(r => setTimeout(r, 800));
      setRevealStep(2);
      
      // Step 3: Graph Results (after 800ms)
      await new Promise(r => setTimeout(r, 800));
      setRevealStep(3);
      
      // Step 4: Final Synthesis Answer (after 800ms)
      await new Promise(r => setTimeout(r, 800));
      setRevealStep(4);

    } catch (err) {
      console.error(err);
      setError("Failed to query the backend database. Make sure 'uv run uvicorn api:app' is running on port 8000.");
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#F8FAFC]">
      {/* Noise Overlay */}
      <div className="noise-overlay" />

      {/* Landing Page Navbar */}
      {!isAppActive && (
        <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-5xl">
          <div className="nav-island glass rounded-full px-6 py-3 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-legalNavy flex items-center justify-center text-white">
                <Scale size={16} className="text-legalGold" />
              </div>
              <span className="font-serif font-bold text-legalNavy tracking-wide text-sm md:text-base">
                Moroccan Legal <span className="text-legalGold font-sans font-bold text-xs uppercase tracking-widest ml-1">GraphRAG</span>
              </span>
            </div>

            <div className="hidden md:flex items-center gap-8 text-xs font-semibold uppercase tracking-wider text-slate-600">
              <a href="#features" className="hover:text-legalNavy transition-colors">Features</a>
              <a href="#architecture" className="hover:text-legalNavy transition-colors">Architecture</a>
              <a href="#tech" className="hover:text-legalNavy transition-colors">Tech Stack</a>
              <a href="#security" className="hover:text-legalNavy transition-colors">Security</a>
            </div>

            <button 
              onClick={() => setIsAppActive(true)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-legalNavy text-white hover:bg-slate-800 transition-all text-xs font-bold shadow-sm group"
            >
              Launch App
              <ArrowUpRight size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        </nav>
      )}

      {/* LANDING PAGE VIEW */}
      {!isAppActive ? (
        <>
          {/* Hero Section */}
          <section className="relative min-h-screen pt-32 flex items-center overflow-hidden border-b border-borderLight bg-white">
            <div className="container mx-auto px-6 md:px-12 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
              
              {/* Left Column */}
              <div className="lg:col-span-7 flex flex-col items-start text-left">
                <div className="hero-tag mb-4 px-3 py-1 rounded-full bg-legalGoldLight border border-[#E9E2D5] flex items-center gap-1.5">
                  <Sparkles size={12} className="text-legalGold" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#9E7A31]">Next-Gen Legal AI</span>
                </div>
                
                <h1 className="hero-title font-serif text-4xl sm:text-5xl lg:text-6xl text-legalNavy font-bold leading-[1.1] mb-6">
                  Navigate Moroccan Law with <span className="text-legalGold italic font-serif">Mathematical Precision</span>
                </h1>
                
                <p className="hero-desc text-slate-600 text-sm sm:text-base lg:text-lg max-w-2xl leading-relaxed mb-8">
                  A hybrid AI RAG engine. Combining deep semantic vector search with a deterministic Neo4j knowledge graph to deliver hallucination-free legal analysis in formal Arabic.
                </p>
                
                <div className="hero-ctas flex flex-wrap gap-4">
                  <button 
                    onClick={() => setIsAppActive(true)}
                    className="px-6 py-3 rounded-xl bg-legalNavy text-white hover:bg-slate-800 transition-all font-semibold text-sm shadow-md shadow-slate-200"
                  >
                    Open Search Interface
                  </button>
                  <a 
                    href="#features" 
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white border border-borderLight hover:border-slate-300 transition-all font-semibold text-sm text-slate-700"
                  >
                    Explore Tech Pipeline
                  </a>
                </div>
              </div>

              {/* Right Column (Canvas Animation) */}
              <div className="lg:col-span-5 relative w-full h-[350px] lg:h-[550px] rounded-3xl bg-slate-50/50 border border-slate-100 overflow-hidden hero-canvas shadow-inner">
                <div className="absolute top-4 left-4 z-20 flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/80 backdrop-blur-md border border-slate-200/50 text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                  <Activity size={10} className="text-legalGold animate-pulse" />
                  Interactive GraphRAG Simulation
                </div>
                <HeroAnimation />
              </div>

            </div>
          </section>

          {/* Features Section */}
          <section id="features" className="py-24 border-b border-borderLight relative bg-[#F8FAFC]">
            <div className="container mx-auto px-6 md:px-12">
              
              <div className="max-w-2xl mx-auto text-center mb-16">
                <h2 className="font-serif text-3xl md:text-4xl text-legalNavy font-bold mb-4">
                  The Triple-Layer AI Pipeline
                </h2>
                <p className="text-slate-600 text-sm md:text-base">
                  Standard RAG systems hallucinate. We enforce factual accuracy through overlapping vector matches and graph relationships.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Card 1: Vector Indexing */}
                <div className="group bg-white p-8 rounded-3xl border border-borderLight hover:border-slate-300 transition-all duration-300 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center mb-6 text-saasBlue group-hover:scale-110 transition-transform">
                      <Database size={22} />
                    </div>
                    <h3 className="font-semibold text-lg text-legalNavy mb-3">1. Semantic Vector Index</h3>
                    <p className="text-slate-600 text-xs md:text-sm leading-relaxed mb-6">
                      Processes and clean Adala PDFs using <code>arabic_reshaper</code>. Texts are split by Articles and embedded into 1024D vectors with <strong>BAAI/bge-m3</strong>, stored locally in Qdrant.
                    </p>
                  </div>
                  
                  <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100/80 font-mono text-[10px] text-slate-500">
                    <div className="flex justify-between items-center mb-2 pb-1 border-b border-slate-200/50">
                      <span className="text-legalNavy font-semibold">QDRANT MATCHES</span>
                      <span className="text-saasBlue">LIMIT=8</span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between bg-white px-2 py-1 rounded border border-slate-100">
                        <span>مقال 12.pdf</span>
                        <span className="text-[#10B981]">0.8920</span>
                      </div>
                      <div className="flex justify-between bg-white px-2 py-1 rounded border border-slate-100">
                        <span>ظهير 81.pdf</span>
                        <span className="text-[#10B981]">0.8541</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card 2: Graph Extraction */}
                <div className="group bg-white p-8 rounded-3xl border border-borderLight hover:border-slate-300 transition-all duration-300 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-12 h-12 rounded-2xl bg-amber-50 flex items-center justify-center mb-6 text-legalGold group-hover:scale-110 transition-transform">
                      <GitBranch size={22} />
                    </div>
                    <h3 className="font-semibold text-lg text-legalNavy mb-3">2. Knowledge Graph</h3>
                    <p className="text-slate-600 text-xs md:text-sm leading-relaxed mb-6">
                      Extracts ministries, entities, and cross-references using Llama-3. These nodes and explicit relationships are saved into **Neo4j** to resolve complex structural queries.
                    </p>
                  </div>

                  <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100/80 font-mono text-[10px] text-slate-500 flex flex-col justify-center items-center h-[76px] relative overflow-hidden">
                    <div className="absolute top-2 left-2 text-[8px] text-slate-400">NEO4J SCHEMA</div>
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold">قانون</span>
                      <span className="h-0.5 w-8 bg-slate-300 relative flex items-center justify-center">
                        <span className="absolute text-[8px] text-slate-500 -top-2.5">MENTIONS</span>
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold">وزارة</span>
                    </div>
                  </div>
                </div>

                {/* Card 3: Streamlit Interface */}
                <div className="group bg-white p-8 rounded-3xl border border-borderLight hover:border-slate-300 transition-all duration-300 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mb-6 text-legalNavy group-hover:scale-110 transition-transform">
                      <Terminal size={22} />
                    </div>
                    <h3 className="font-semibold text-lg text-legalNavy mb-3">3. Context Window Expansion</h3>
                    <p className="text-slate-600 text-xs md:text-sm leading-relaxed mb-6">
                      When a vector is retrieved, the RAG engine automatically retrieves the parent/adjacent chunks (e.g. <code>chunk - 1</code> & <code>chunk + 1</code>) to prevent data truncation.
                    </p>
                  </div>

                  <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100/80 font-mono text-[10px] text-slate-500">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-slate-600">STITCHED CONTEXT</span>
                    </div>
                    <div className="bg-emerald-50/50 border border-emerald-100 rounded px-2 py-1 text-emerald-800 text-[8px] truncate">
                      [المادة 7] + [المادة 8 (MATCH)] + [المادة 9]
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Architecture Section */}
          <section id="architecture" className="py-24 border-b border-borderLight bg-white">
            <div className="container mx-auto px-6 md:px-12">
              <div className="max-w-2xl mx-auto text-center mb-16">
                <h2 className="font-serif text-3xl md:text-4xl text-legalNavy font-bold mb-4">
                  Deterministic RAG Workflow
                </h2>
                <p className="text-slate-600 text-sm md:text-base">
                  How queries are dynamically routed and processed to ensure pure Arabic outputs without hallucinated tax rates or regulations.
                </p>
              </div>

              <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-4 items-center">
                <div className="relative bg-[#F8FAFC] border border-borderLight p-6 rounded-2xl text-left">
                  <div className="absolute -top-3 left-6 px-2.5 py-0.5 rounded bg-legalNavy text-white font-mono text-[10px]">
                    01_INGESTION
                  </div>
                  <h4 className="font-semibold text-legalNavy text-sm mb-2 mt-2">API Scraping & Cleaning</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Connects to Adala, extracts Arabic text from raw PDFs, fixes layouts via PyMuPDF, and stores them in Markdown.
                  </p>
                </div>

                <div className="hidden md:flex justify-center text-slate-400">
                  <ChevronRight size={24} />
                </div>

                <div className="relative bg-[#F8FAFC] border border-borderLight p-6 rounded-2xl text-left">
                  <div className="absolute -top-3 left-6 px-2.5 py-0.5 rounded bg-legalNavy text-white font-mono text-[10px]">
                    02_DATABASES
                  </div>
                  <h4 className="font-semibold text-legalNavy text-sm mb-2 mt-2">Hybrid Storage Setup</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Generates 1024D vector embeddings for Qdrant and parses cross-references to extract relationships into Neo4j.
                  </p>
                </div>

                <div className="hidden md:flex justify-center text-slate-400">
                  <ChevronRight size={24} />
                </div>

                <div className="relative bg-[#F8FAFC] border border-borderLight p-6 rounded-2xl text-left">
                  <div className="absolute -top-3 left-6 px-2.5 py-0.5 rounded bg-legalNavy text-white font-mono text-[10px]">
                    03_RETRIEVAL
                  </div>
                  <h4 className="font-semibold text-legalNavy text-sm mb-2 mt-2">LLM Strict Generation</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Queries Neo4j + Qdrant, stitches context together, and prompts Llama-3 at temperature 0.0 to reply strictly in formal Arabic.
                  </p>
                </div>
              </div>

              <div className="mt-16 text-center text-slate-500 text-xs italic font-serif">
                "Most legal AI hallucinates. We map the law deterministically."
              </div>
            </div>
          </section>

          {/* Tech Stack Details */}
          <section id="tech" className="py-24 border-b border-borderLight bg-[#F8FAFC]">
            <div className="container mx-auto px-6 md:px-12">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                <div className="lg:col-span-5 text-left">
                  <h2 className="font-serif text-3xl md:text-4xl text-legalNavy font-bold mb-4">
                    The Infrastructure
                  </h2>
                  <p className="text-slate-600 text-sm leading-relaxed mb-8">
                    Designed to run locally on resource-constrained hardware by offloading embeddings and generation to scalable APIs while keeping database storage local.
                  </p>
                  
                  <div className="space-y-4">
                    <div className="flex gap-4">
                      <div className="w-10 h-10 rounded-xl bg-white border border-borderLight flex items-center justify-center text-legalNavy shrink-0">
                        <Database size={18} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-sm text-legalNavy">Qdrant Vector Database</h4>
                        <p className="text-slate-500 text-xs">Fast local cosine-similarity lookups on BGE-M3 embedded vectors.</p>
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <div className="w-10 h-10 rounded-xl bg-white border border-borderLight flex items-center justify-center text-legalNavy shrink-0">
                        <Share2 size={18} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-sm text-legalNavy">Neo4j Graph DB</h4>
                        <p className="text-slate-500 text-xs">Links legal entities to prevent context isolation and maintain structural references.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-7 bg-white border border-borderLight rounded-3xl p-6 md:p-8 text-left shadow-sm">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                      <Terminal size={16} className="text-slate-400" />
                      <span className="font-mono text-xs text-slate-500 uppercase tracking-widest">pipeline_config.json</span>
                    </div>
                    <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
                      <div className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
                      <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
                    </div>
                  </div>
                  
                  <pre className="font-mono text-xs text-slate-600 bg-slate-50 p-6 rounded-2xl overflow-x-auto leading-relaxed border border-slate-100">
{`{
  "embedding_model": "BAAI/bge-m3",
  "vector_dimensions": 1024,
  "vector_distance_metric": "cosine",
  "knowledge_graph": {
    "provider": "Neo4j AuraDB",
    "indices": ["entity_name_index"]
  },
  "generation": {
    "llm": "llama-3.3-70b-versatile",
    "temperature": 0.0,
    "system_prompt_language": "ar-MA",
    "context_window_expansion": true
  }
}`}
                  </pre>
                </div>
              </div>
            </div>
          </section>

          {/* Security Section */}
          <section id="security" className="py-24 bg-white border-b border-borderLight">
            <div className="container mx-auto px-6 md:px-12">
              <div className="max-w-3xl mx-auto text-center mb-16">
                <div className="inline-flex p-3 rounded-full bg-emerald-50 text-emerald-600 mb-4">
                  <ShieldCheck size={28} />
                </div>
                <h2 className="font-serif text-3xl md:text-4xl text-legalNavy font-bold mb-4">
                  Enterprise Security Hardening
                </h2>
                <p className="text-slate-600 text-sm md:text-base">
                  Designed from the ground up to prevent common RAG attack vectors and UI vulnerabilities.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
                <div className="p-6 rounded-2xl border border-slate-100 bg-[#F8FAFC]">
                  <Lock className="text-emerald-600 mb-3" size={20} />
                  <h4 className="font-semibold text-legalNavy text-sm mb-2">Prompt Injection Guardrails</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Enforces strict separation of system configuration and user inputs. Input validations ensure prompt formatting is not compromised by malicious queries.
                  </p>
                </div>
                
                <div className="p-6 rounded-2xl border border-slate-100 bg-[#F8FAFC]">
                  <ShieldCheck className="text-emerald-600 mb-3" size={20} />
                  <h4 className="font-semibold text-legalNavy text-sm mb-2">Safe HTML Encoding</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    The UI elements render all retrieved text through safe DOM binding to fully prevent Reflected Cross-Site Scripting (XSS).
                  </p>
                </div>

                <div className="p-6 rounded-2xl border border-slate-100 bg-[#F8FAFC]">
                  <Layers className="text-emerald-600 mb-3" size={20} />
                  <h4 className="font-semibold text-legalNavy text-sm mb-2">Path Traversal Defense</h4>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Scraped legal documents undergo filename sanitization (using strictly checked alpha-numeric regex filters) before saving onto the disk.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Launch CTA Panel */}
          <section className="py-20 bg-legalNavy text-white relative overflow-hidden">
            <div className="absolute top-0 right-1/4 w-[350px] h-[350px] bg-legalGold opacity-10 rounded-full blur-[100px] pointer-events-none" />
            <div className="container mx-auto px-6 md:px-12 relative z-10">
              <div className="max-w-2xl mx-auto text-center">
                <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4">
                  Access the Moroccan Legal Search Engine
                </h2>
                <p className="text-slate-300 text-xs md:text-sm leading-relaxed mb-8">
                  Experience the RAG interface locally. Make sure the backend FastAPI service is running before querying.
                </p>
                <div className="flex justify-center gap-4">
                  <button 
                    onClick={() => setIsAppActive(true)}
                    className="flex items-center gap-2 px-6 py-3 rounded-xl bg-legalGold text-legalNavy hover:bg-[#c29f2f] transition-all font-semibold text-sm shadow-md"
                  >
                    Launch RAG Dashboard
                    <ArrowUpRight size={16} />
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Footer */}
          <footer className="bg-white border-t border-borderLight py-12">
            <div className="container mx-auto px-6 md:px-12 flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="text-left">
                <span className="font-serif font-bold text-legalNavy tracking-wide">
                  Moroccan Legal <span className="text-legalGold font-sans font-bold text-xs uppercase tracking-widest ml-1">GraphRAG</span>
                </span>
                <p className="text-slate-400 text-xs mt-1">© {new Date().getFullYear()} Moroccan Legal GraphRAG Project. Built for institutional precision.</p>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 text-[10px] font-mono text-emerald-800">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  SYSTEM OPERATIONAL
                </div>
                <a href="https://github.com/Rib4ko/Legal-GraphRag" target="_blank" rel="noopener noreferrer" className="text-xs text-slate-500 hover:text-legalNavy transition-colors font-semibold">GitHub Repo</a>
              </div>
            </div>
          </footer>
        </>
      ) : (
        /* ACTIVE SEARCH ENGINE DASHBOARD VIEW */
        <div className="container mx-auto px-4 md:px-12 py-12 max-w-4xl dashboard-content">
          
          {/* Dashboard Header Bar */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-10 pb-6 border-b border-borderLight">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => {
                  setIsAppActive(false);
                  setRevealStep(0);
                  setError(null);
                }}
                className="w-10 h-10 rounded-full border border-borderLight bg-white flex items-center justify-center text-slate-500 hover:text-legalNavy hover:border-slate-300 transition-colors shadow-sm"
              >
                <ArrowLeft size={16} />
              </button>
              <div>
                <h2 className="font-serif text-2xl text-legalNavy font-bold flex items-center gap-2">
                  ⚖️ Moroccan Legal GraphRAG
                </h2>
                <p className="text-slate-500 text-xs text-left">Fact-Checked Legal Knowledge Search Engine</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 text-[10px] font-mono text-emerald-800 self-end md:self-auto">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              API ACTIVE (PORT 8000)
            </div>
          </div>

          {/* Search bar card */}
          <div className="bg-white border border-borderLight rounded-3xl p-6 md:p-8 shadow-sm mb-12 text-left">
            <h3 className="font-serif text-lg font-bold text-legalNavy mb-3">Ask your legal question</h3>
            <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-3">
              <div className="relative flex-grow">
                <input
                  type="text"
                  placeholder="مثال: ما هي المعلومات التي يطلبها نموذج تصريح الأولاد القاصرين؟"
                  value={searchQuery}
                  disabled={loading}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-5 py-3.5 pr-12 rounded-2xl border border-borderLight focus:border-slate-400 focus:outline-none bg-slate-50/50 text-slate-800 text-sm placeholder-slate-400 font-sans shadow-inner disabled:opacity-75"
                  dir="rtl"
                />
                <Search size={18} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400" />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3.5 rounded-2xl bg-legalNavy text-white hover:bg-slate-800 transition-all font-semibold text-sm shadow-md flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
              >
                {loading ? "Initializing API..." : "Execute Search"}
              </button>
            </form>
            
            {/* Quick suggestions */}
            <div className="mt-4 flex flex-wrap gap-2 items-center">
              <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 mr-2">Sample Queries:</span>
              <button 
                onClick={() => { setSearchQuery("ما هي مسؤولية القاضي؟"); }}
                disabled={loading}
                className="px-3 py-1 rounded-full border border-borderLight bg-slate-50 text-[11px] text-slate-600 hover:bg-slate-100 transition-colors disabled:opacity-50"
              >
                مسؤولية القاضي
              </button>
              <button 
                onClick={() => { setSearchQuery("ما هي المعلومات التي يطلبها نموذج تصريح الأولاد القاصرين؟"); }}
                disabled={loading}
                className="px-3 py-1 rounded-full border border-borderLight bg-slate-50 text-[11px] text-slate-600 hover:bg-slate-100 transition-colors disabled:opacity-50"
              >
                تصريح الأولاد القاصرين
              </button>
            </div>
          </div>

          {/* Initial Loading Spinner (Before data returns) */}
          {loading && (
            <div className="bg-white border border-borderLight rounded-3xl p-8 shadow-sm mb-8 text-center flex flex-col items-center justify-center min-h-[200px]">
              <div className="w-10 h-10 rounded-full border-4 border-slate-100 border-t-legalGold animate-spin mb-4" />
              <h4 className="font-semibold text-legalNavy text-xs uppercase tracking-wider font-mono">Running RAG Pipeline...</h4>
              <p className="text-slate-500 text-xs mt-2">Connecting to Qdrant & Neo4j databases</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-100 text-red-800 rounded-3xl p-6 shadow-sm mb-8 text-left flex items-start gap-3">
              <AlertCircle size={20} className="shrink-0 text-red-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1">Database Connection Failed</h4>
                <p className="text-xs leading-relaxed">{error}</p>
                <div className="mt-4 bg-white/70 p-3 rounded-lg border border-red-100/50 font-mono text-[10px] text-red-700">
                  Run command in terminal to launch backend: <br />
                  <code className="font-bold select-all">uv run uvicorn api:app --reload --port 8000</code>
                </div>
              </div>
            </div>
          )}

          {/* PROGRESSIVE PIPELINE REVEAL */}
          {!loading && revealStep > 0 && (
            <div className="flex flex-col items-center w-full space-y-6">
              
              {/* STEP 1: Query Expansion */}
              <div ref={step1Ref} className="w-full bg-white border border-borderLight rounded-2xl p-6 shadow-sm text-left relative overflow-hidden">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-amber-50 flex items-center justify-center text-[10px] font-mono text-legalGold font-semibold border border-amber-200">
                      1
                    </div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">Step 01 / LLM Query Expansion</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 text-[8px] font-mono border border-emerald-100 font-bold uppercase">Success</span>
                </div>
                <h4 className="font-semibold text-legalNavy text-sm mb-2">Expanded Semantic Search Terms:</h4>
                <p className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs font-mono text-slate-600 leading-relaxed text-right" dir="rtl">
                  {expandedQuery || searchQuery}
                </p>
              </div>

              {/* Arrow 1 */}
              {revealStep >= 1 && (
                <div className="flex justify-center py-1 text-legalGold animate-bounce">
                  <ArrowDown size={20} className="stroke-[2.5]" />
                </div>
              )}

              {/* STEP 2: Vector Search Results */}
              {revealStep >= 2 && (
                <div ref={step2Ref} className="w-full bg-white border border-borderLight rounded-2xl p-6 shadow-sm text-left relative">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-blue-50 flex items-center justify-center text-[10px] font-mono text-saasBlue font-semibold border border-blue-200">
                        2
                      </div>
                      <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">Step 02 / Qdrant Similarity Search</span>
                    </div>
                    <span className="text-[9px] font-mono text-saasBlue font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-100">MATCH_LIMIT=5</span>
                  </div>

                  <div className="space-y-3">
                    {hits.map((hit, index) => {
                      const isExpanded = !!expandedHits[hit.id];
                      return (
                        <div key={hit.id} className="border border-borderLight rounded-xl overflow-hidden transition-all bg-slate-50/50">
                          <button
                            onClick={() => toggleHitExpansion(hit.id)}
                            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-mono font-semibold text-slate-500">
                                {index + 1}
                              </span>
                              <div>
                                <span className="font-semibold text-slate-800 text-[11px] block">{hit.context_str}</span>
                                <span className="text-[9px] text-slate-400 font-mono">{hit.filename}</span>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2.5">
                              <span className="px-2 py-0.5 rounded-md bg-white border border-borderLight font-mono text-[9px] text-slate-500 font-semibold">
                                Score: {hit.score.toFixed(4)}
                              </span>
                              {isExpanded ? <ChevronUp size={14} className="text-slate-400" /> : <ChevronDown size={14} className="text-slate-400" />}
                            </div>
                          </button>

                          {isExpanded && (
                            <div className="px-4 pb-4 pt-1.5 border-t border-borderLight bg-white font-sans text-xs text-slate-600 leading-relaxed text-right" dir="rtl">
                              <div className="mb-2 text-[8px] font-mono text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100 inline-block">
                                ℹ️ Context Expanded (Parent document chunks stitched to prevent text clipping)
                              </div>
                              <p className="whitespace-pre-line">{hit.text}</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Arrow 2 */}
              {revealStep >= 2 && (
                <div className="flex justify-center py-1 text-legalGold animate-bounce">
                  <ArrowDown size={20} className="stroke-[2.5]" />
                </div>
              )}

              {/* STEP 3: Graph RAG (Neo4j) */}
              {revealStep >= 3 && (
                <div ref={step3Ref} className="w-full bg-white border border-borderLight rounded-2xl p-6 shadow-sm text-left relative">
                  <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-amber-50 flex items-center justify-center text-[10px] font-mono text-legalGold font-semibold border border-amber-200">
                        3
                      </div>
                      <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">Step 03 / Neo4j Knowledge Graph Connections</span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 text-[8px] font-mono border border-amber-100 font-bold uppercase">Click path to view chunk</span>
                  </div>

                  {graphRelationships.length > 0 ? (
                    <div className="space-y-4">
                      {graphRelationships.map((r, idx) => {
                        const isExpanded = !!expandedRelations[idx];
                        return (
                          <div 
                            key={idx} 
                            onClick={() => toggleRelationExpansion(idx)}
                            className="flex flex-col bg-slate-50/50 p-4 rounded-xl border border-slate-100/70 hover:border-slate-200 hover:bg-slate-50 transition-all duration-300 group cursor-pointer"
                          >
                            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-0 w-full">
                              
                              {/* Entity 1 Node (Source) */}
                              <div className="flex items-center gap-2 bg-white px-3.5 py-2 rounded-xl border border-slate-200 shadow-sm shrink-0 min-w-[150px] justify-center sm:justify-start">
                                <div className="w-2.5 h-2.5 rounded-full bg-legalGold animate-ping absolute" />
                                <div className="w-2.5 h-2.5 rounded-full bg-legalGold relative" />
                                <span className="text-xs font-semibold text-legalNavy">{r.entity}</span>
                              </div>

                              {/* Connecting Path line & Rel Name */}
                              <div className="flex-grow mx-4 relative flex items-center justify-center w-full sm:w-auto">
                                {/* Visual Shimmering Path Line */}
                                <div className="absolute left-0 right-0 h-0.5 bg-slate-200 rounded-full overflow-hidden hidden sm:block">
                                  <div className="h-full bg-legalGold w-1/3 rounded-full animate-shimmer-line" />
                                </div>
                                
                                {/* Down Arrow for Mobile / Line Overlay for Desktop */}
                                <span className="relative z-10 px-3 py-1 rounded-full bg-legalNavy text-white font-mono text-[9px] font-bold uppercase tracking-wider shadow-sm scale-95 group-hover:scale-100 transition-transform">
                                  {r.relation}
                                </span>
                              </div>

                              {/* Entity 2 Node (Target) */}
                              <div className="flex items-center gap-2 bg-white px-3.5 py-2 rounded-xl border border-slate-200 shadow-sm shrink-0 min-w-[150px] justify-center sm:justify-end">
                                <span className="text-xs font-semibold text-slate-700">{r.related_entity}</span>
                                <div className="w-2.5 h-2.5 rounded-full bg-[#2563EB]" />
                              </div>
                              
                            </div>

                            {/* Collapsible Chunk Source Text */}
                            {isExpanded && (
                              <div 
                                className="mt-4 w-full bg-white border border-slate-200/60 rounded-xl p-4 text-right shadow-inner transition-all duration-300"
                                dir="rtl"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <div className="flex items-center justify-between mb-2.5 pb-1.5 border-b border-slate-100 text-[10px] font-mono text-slate-400">
                                  <span className="font-semibold text-slate-500">📖 السياق المرجعي المستخرج (Neo4j Source Chunk)</span>
                                  <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-100 text-[8px] font-bold">SOURCE CONTEXT</span>
                                </div>
                                <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line select-text">
                                  {r.chunk_text || "لا يوجد نص مرجعي متوفر لهذه العلاقة."}
                                </p>
                              </div>
                            )}

                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="py-4 text-center text-slate-400 text-xs">
                      No matching graph nodes found for query entities. Context window isolated to vector space.
                    </div>
                  )}
                </div>
              )}

              {/* Arrow 3 */}
              {revealStep >= 3 && (
                <div className="flex justify-center py-1 text-legalGold animate-bounce">
                  <ArrowDown size={20} className="stroke-[2.5]" />
                </div>
              )}

              {/* STEP 4: LLM Final Answer */}
              {revealStep >= 4 && (
                <div ref={step4Ref} className="w-full bg-white border-2 border-legalGold rounded-3xl p-6 md:p-8 shadow-md relative overflow-hidden">
                  <div className="absolute top-0 left-0 bg-legalGold text-legalNavy font-mono text-[9px] font-bold px-4 py-1.5 rounded-br-2xl uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles size={10} /> Fact-Checked Legal Output
                  </div>
                  
                  <div className="mt-6 text-right">
                    <h3 className="font-serif text-xl font-bold text-legalNavy mb-4">الإجابة القانونية المقترحة</h3>
                    <div 
                      className="text-slate-800 text-sm md:text-base leading-loose font-sans space-y-4 rtl-content"
                      dir="rtl"
                      style={{ whiteSpace: "pre-line" }}
                    >
                      {answer}
                    </div>
                  </div>

                  {/* Metadata inside card */}
                  <div className="mt-8 pt-4 border-t border-slate-100 flex flex-wrap justify-between items-center gap-2 text-[10px] text-slate-400 font-mono">
                    <span>LLM MODEL: llama-3.3-70b</span>
                    <span>TEMPERATURE: 0.0</span>
                    <span>RETRIEVAL: STITCHED VECTORS + NEO4J</span>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      )}
    </div>
  );
}
