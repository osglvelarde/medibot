from fastapi import APIRouter, UploadFile, File
import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb

router = APIRouter()

# Use the new client init
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="medibot_chunks")

model = SentenceTransformer("all-MiniLM-L6-v2")

@router.post("/")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Please upload a PDF file."}

    with pdfplumber.open(file.file) as pdf:
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

    tokens = full_text.split()
    chunk_size = 500
    overlap = 50
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = " ".join(tokens[i:i+chunk_size])
        chunks.append(chunk)

    embeddings = model.encode(chunks).tolist()
    ids = [f"{file.filename}_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

    return {
        "filename": file.filename,
        "num_chunks": len(chunks),
        "stored_in_vector_db": True
    }
