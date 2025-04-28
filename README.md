# 📚 LicenPrep AI  
[![CI](https://img.shields.io/github/actions/workflow/status/YourOrg/LicenPrepAI/ci.yml?label=CI)](./.github/workflows/ci.yml)
[![License](https://img.shields.io/github/license/YourOrg/LicenPrepAI)](LICENSE)

An **AI-driven study platform** that converts any set of learning resources into *exam-style* practice material, delivering a fully personalized, data-driven path to licensure success.

---

## 🔎 At a Glance
| | |
|---|---|
| **Tech Stack** | *FastAPI · React + TypeScript · ChromaDB · SentenceTransformers · DeepSeek (Instruct) · LangChain / LlamaIndex · Docker · Kubernetes* |
| **Focus Exams** | USMLE · NCLEX · CPA · PE · Bar Exam · Series 7 *(extensible)* |
| **Pipeline** | PDF → `/ingest` → Tokenizer / Chunker → Embeddings → Vector DB → LLM (RAG) → MCQ & Analytics |

---

## 📑 Table of Contents
1. [Key Features](#key-features)  
2. [System Architecture](#system-architecture)  
3. [API Reference](#api-reference)  
4. [Getting Started (Local)](#getting-started-local)  
5. [Deployment (Cloud/K8s)](#deployment-cloudk8s)  
6. [Roadmap](#roadmap)  
7. [Contributing](#contributing)  
8. [License](#license)  

---

## Key Features
- **Automatic RAG-based question generation**: Ingest PDFs, PPTs, or notes and instantly generate high-quality MCQs, flash-cards or cloze items.  
- **Adaptive quiz engine**: Item selection is driven by Bayesian proficiency-estimation and spaced-repetition (*SM-2*) scheduling.  
- **Blueprint alignment**: Each generated item is auto-tagged to the exam’s official content outline for coverage tracking.  
- **Real-time analytics**: Per-topic mastery curves, “time-to-competency” estimations, and cohort benchmarking.  
- **Plug-n-play LLMs**: Swap DeepSeek-Instruct for GPT-4o, Mistral-Large, or any local GGUF model via an abstract `LLMInterface`.  

---

## System Architecture
