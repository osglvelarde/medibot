import os
import re
import random
import requests
import chromadb
from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

router = APIRouter()

# Setup ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="medibot_chunks")

# Embedding model
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class GenerateRequest(BaseModel):
    query: str
    k: int = 5
    num_questions: int = 3

def jaccard_similarity(a: str, b: str) -> float:
    """Simple Jaccard similarity based on words."""
    a_set = set(a.lower().split())
    b_set = set(b.lower().split())
    intersection = a_set.intersection(b_set)
    union = a_set.union(b_set)
    if not union:
        return 0
    return len(intersection) / len(union)

@router.post("/")
async def generate_questions(request: GenerateRequest):
    # Step 1: Embed query
    query_embedding = model.encode([request.query]).tolist()[0]

    # Step 2: Over-query lots of documents
    overquery_k = request.k * 5
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=overquery_k,
        include=["documents"]
    )

    all_docs = results["documents"][0]
    random.shuffle(all_docs)  # Shuffle to randomize concepts

    # Step 3: Deduplicate (diverse documents)
    selected_docs = []
    used_docs = []

    for doc in all_docs:
        if len(selected_docs) >= request.k:
            break
        too_similar = False
        for prev in used_docs:
            if jaccard_similarity(doc, prev) > 0.3:  # 30% similarity threshold
                too_similar = True
                break
        if not too_similar:
            selected_docs.append(doc)
            used_docs.append(doc)

    if not selected_docs:
        return {"error": "No diverse matching content found."}

    questions = []

    for context in selected_docs[:request.num_questions]:
        prompt = f"""
You are a professional USMLE Step 1 and Step 2 CK question writer.

Using ONLY the context below:
- Write one high-quality multiple-choice question (MCQ) with 4 answer choices (A, B, C, D).
- Randomize the patient age, gender, setting (clinic, ER, ICU).
- Focus on clinical reasoning, not trivia.
- Ensure each answer choice sounds plausible but only one is truly correct.
- Format response exactly like:

Stem: <clinical case and question here>
A: <first option>
B: <second option>
C: <third option>
D: <fourth option>
Correct Answer: <letter A-D>

Context:
{context}
"""

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
            response_json = response.json()

            if "choices" not in response_json:
                continue

            raw_text = response_json["choices"][0]["message"]["content"]

            # Parse
            stem_match = re.search(r"Stem:\s*(.+?)(?:A:|\nA:)", raw_text, re.DOTALL)
            a_match = re.search(r"A:\s*(.+?)\n", raw_text)
            b_match = re.search(r"B:\s*(.+?)\n", raw_text)
            c_match = re.search(r"C:\s*(.+?)\n", raw_text)
            d_match = re.search(r"D:\s*(.+?)\n", raw_text)
            correct_match = re.search(r"Correct Answer:\s*([A-D])", raw_text)

            parsed = {
                "stem": stem_match.group(1).strip() if stem_match else "Stem not found",
                "choices": {
                    "A": a_match.group(1).strip() if a_match else "A not found",
                    "B": b_match.group(1).strip() if b_match else "B not found",
                    "C": c_match.group(1).strip() if c_match else "C not found",
                    "D": d_match.group(1).strip() if d_match else "D not found",
                },
                "correct_answer": correct_match.group(1) if correct_match else "Answer not found"
            }

            questions.append(parsed)

        except Exception as e:
            continue

    return {"questions": questions}
