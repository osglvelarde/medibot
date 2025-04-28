📚 LicenPrep AI
===============

An **AI-driven study platform** that converts any set of learning resources into _exam-style_ practice material, delivering a fully personalized, data-driven path to licensure success.

🔎 At a Glance
--------------

**Tech Stack**_FastAPI · React + TypeScript · ChromaDB · SentenceTransformers · DeepSeek (Instruct) · LangChain / LlamaIndex · Docker · Kubernetes_**Focus Exams**USMLE · NCLEX · CPA · PE · Bar Exam · Series 7 _(extensible)_**Pipeline**PDF → /ingest → Tokenizer / Chunker → Embeddings → Vector DB → LLM (RAG) → MCQ & Analytics

📑 Table of Contents
--------------------

1.  [Key Features](#key-features)
    
2.  [System Architecture](#system-architecture)
    
3.  [API Reference](#api-reference)
    
4.  [Getting Started (Local)](#getting-started-local)
    
5.  [Deployment (Cloud/K8s)](#deployment-cloudk8s)
    
6.  [Roadmap](#roadmap)
    
7.  [Contributing](#contributing)
    
8.  [License](#license)
    

Key Features
------------

*   **Automatic RAG-based question generation**: Ingest PDFs, PPTs, or notes and instantly generate high-quality MCQs, flash-cards or cloze items.
    
*   **Adaptive quiz engine**: Item selection is driven by Bayesian proficiency-estimation and spaced-repetition (_SM-2_) scheduling.
    
*   **Blueprint alignment**: Each generated item is auto-tagged to the exam’s official content outline for coverage tracking.
    
*   **Real-time analytics**: Per-topic mastery curves, “time-to-competency” estimations, and cohort benchmarking.
    
*   **Plug-n-play LLMs**: Swap DeepSeek-Instruct for GPT-4o, Mistral-Large, or any local GGUF model via an abstract LLMInterface.
    

System Architecture
-------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEdit┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌───────────────┐  │  Frontend   │ ← │   REST/WS    │ ← │   Quiz &      │ ← │  Retrieval +  │  │  (React)    │   │   FastAPI    │   │  Analytics    │   │ Generation    │  └─────────────┘   └──────────────┘   └───────────────┘   └───────────────┘         ▲                                            ▲         │                                            │         │                               ┌──────────────────────────┐         │                               │  Vector DB (ChromaDB)    │         │                               └──────────────────────────┘         │                                            ▲         │                 ┌──────────────┐           │         └─/ingest/upload→ │  Ingestion   │ ––chunks––┘                           │  (PDF/OCR)   │                           └──────────────┘   `

### 🔧 Service Breakdown

ServiceDescriptionKey Dependencies**ingest**Parse PDFs & slides, split into ~500-token windows (overlap = 50), persist to /data/chunks/._pdfminer.six_, _pymupdf_, _tesseract-OCR_**embed**Compute embeddings with sentence-transformers/all-MiniLM-L6-v2 (~384 d); fallback to OpenAI text-embedding-3-small._Faiss_, _ChromaDB_**retriever**k-NN (k = 8) + MMR diversification, filter by cosine > 0.75._LangChain Retriever_**generator**RAG prompt → DeepSeek-Instruct (33B) via **vLLM**; max\_tokens = 350; temperature = 0.7._vllm_, _huggingface-hub_**validator**Self-consistency vote + GPT-4o optional validation; drop dupes via Jaccard > 0.82._rapidfuzz_

### ⚙️ Data Flow

1.  **Student upload** triggers /ingest → chunks persisted & embedded.
    
2.  **Quiz request** hits /generate → relevant chunks retrieved → prompt stuffed & sent to LLM.
    
3.  LLM returns **JSON-schema-validated** items (stem + 4 options + rationale).
    
4.  Items stored; /quiz WebSocket streams them to UI.
    
5.  /submit grades responses, updates PostgreSQL analytics tables, returns mastery deltas.
    

API Reference
-------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   hCopyEditPOST /ingest  BODY: multipart/form-data (file)  RES: { file_id }  POST /generate  BODY: { "file_id": "...", "num_items": 15, "exam": "USMLE" }  RES: { quiz_id, items[] }  WS  /quiz/{quiz_id}  STREAM: { "item_id": "...", "stem": "...", "choices": [...] }  POST /submit  BODY: { "quiz_id": "...", "answers": { "item_id": "B", ... } }  RES: { score_pct, mastery_delta }   `

OpenAPI docs are auto-generated at **/docs** (Swagger) and **/redoc**.

Getting Started (Local)
-----------------------

### Prerequisites

*   Python 3.11+
    
*   Node 20+ (for UI)
    
*   **CUDA 11.8** & ≥ 12 GB GPU VRAM _(recommended)_
    

### Quick Start

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   bashCopyEdit# clone repo  git clone https://github.com/YourOrg/LicenPrepAI.git && cd LicenPrepAI  # backend  python -m venv .venv && source .venv/bin/activate  pip install -r requirements.txt  cp .env.example .env        # edit LLM or DB creds  uvicorn licenprep.main:app --reload  # frontend  cd ui && npm i && npm run dev   `

Visit [**http://localhost:5173**](http://localhost:5173) and start uploading study material!

Deployment (Cloud/K8s)
----------------------

*   **Docker-Compose** for single-node POCs.
    
*   **Helm Chart** charts/licenprep-ai — three Deployments (api, worker, frontend) plus GPU-enabled generator Deployment using the _NVIDIA_ runtime.
    
*   **KEDA** ScaledObject auto-scales the generator Pods based on RabbitMQ queue length.
    
*   Persistent volumes: /data/chroma, /data/uploads, /data/postgres.
    

Roadmap
-------

*   **Vision OS** companion app _(flashcards on the go)_
    
*   Add **image-based** questions via BLIP-2 captioning + vision-LLM.
    
*   Secure sharing of anonymized analytics with faculty dashboards.
    

Contributing
------------

We ♥ pull requests! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and open an issue before large changes.

License
-------

Distributed under the **MIT License** — see [LICENSE](LICENSE) for details.
