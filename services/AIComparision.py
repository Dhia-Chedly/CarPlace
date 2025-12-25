import os
import httpx
import pdfplumber
from sentence_transformers import SentenceTransformer
import faiss
from typing import Optional, Tuple, List
from pathlib import Path
from functools import lru_cache

# --- Config ---
BASE_DIR = Path(__file__).resolve().parent 
DEFAULT_PDF_PATH = str(BASE_DIR / "carplace_full_technical_catalog.pdf")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Load embedding model once on import
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# --- PDF Indexing ---
def build_pdf_index(pdf_path: str, chunk_size: int = 300) -> Tuple[faiss.IndexFlatL2, List[str]]:
    """Reads PDF and builds FAISS index."""
    chunks: List[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                words = text.split()
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i : i + chunk_size])
                    chunks.append(chunk)
    except Exception as e:
        print(f"[AIComparision] PDF Error: {e}")
        return None, []

    if not chunks: return None, []

    embeddings = embedder.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, chunks

@lru_cache(maxsize=10)
def get_pdf_index(pdf_path: str) -> Tuple[faiss.IndexFlatL2, List[str]]:
    if not Path(pdf_path).exists():
        print(f"[AIComparision] PDF not found: {pdf_path}")
        return None, []
    return build_pdf_index(pdf_path)

# --- Gemini Comparison Logic ---
async def generate_comparison_with_pdf(
    car1: dict,
    car2: dict,
    pdf_path: Optional[str] = None,
    k: int = 3,
) -> str:
    """
    Compare two cars using Gemini with RAG (Retrieval Augmented Generation).
    Uses a strict prompt to prevent hallucinations.
    """
    if not GEMINI_API_KEY:
        return "Comparison service unavailable (API Key missing)."

    path = pdf_path or DEFAULT_PDF_PATH
    index, chunks = get_pdf_index(path)
    
    context = "No specific technical catalog matches found."
    if index and chunks:
        # Search for context relevant to these cars
        query = f"{car1.get('brand_name')} {car1.get('model_name')} vs {car2.get('brand_name')} {car2.get('model_name')}"
        q_emb = embedder.encode([query])
        _, I = index.search(q_emb, k=k)
        context = "\n\n".join(chunks[i] for i in I[0] if i < len(chunks))

    # --- Hallucination Prevention Prompt ---
    system_instruction = (
        "You are a precision car comparison engine. Your goal is to provide a factual, objective comparison.\n"
        "STRICT RULES:\n"
        "1. GROUNDING: Use ONLY the provided 'Catalog Context' and 'Car Listing Data'.\n"
        "2. NO HALLUCINATION: If the information is not present in the context or listing data, do not invent it. "
        "Admit if a specific detail (like exact 0-60 time) is unavailable.\n"
        "3. TONE: Professional and concise. Limit response to 3-4 impactful sentences.\n"
    )

    car_data = (
        f"CAR 1: {car1.get('year')} {car1.get('brand_name')} {car1.get('model_name')} "
        f"({car1.get('horsepower')} HP, {car1.get('transmission')}, {car1.get('fuel_type')}, ${car1.get('price')})\n"
        f"Description: {car1.get('description')}\n\n"
        f"CAR 2: {car2.get('year')} {car2.get('brand_name')} {car2.get('model_name')} "
        f"({car2.get('horsepower')} HP, {car2.get('transmission')}, {car2.get('fuel_type')}, ${car2.get('price')})\n"
        f"Description: {car2.get('description')}"
    )

    gemini_prompt = (
        f"{system_instruction}\n"
        f"CATALOG CONTEXT (Technical data):\n{context}\n\n"
        f"LISTING DATA:\n{car_data}\n\n"
        "COMPARE THESE TWO VEHICLES:"
    )

    # Call Gemini REST API
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": gemini_prompt}]}]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, params={"key": GEMINI_API_KEY}, json=body)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                return f"AI Service Error: {resp.text}"
    except Exception as e:
        return f"Comparison failed due to connection error: {str(e)}"
