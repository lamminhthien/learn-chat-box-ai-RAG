import json
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, logger
from qdrant_client import QdrantClient
from qdrant_client import models  # Import models explicitly
from sentence_transformers import SentenceTransformer
import uuid
from typing import List
from PyPDF2 import PdfReader
from docx import Document
import requests
from fastapi.middleware.cors import CORSMiddleware
from database import create_note, init_db_tables

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def query_gemini_api(prompt, api_key):
    # Gemini API endpoint (adjust version if needed, e.g., v1beta)
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,  # Adjust as needed
            "topP": 0.9,
            "maxOutputTokens": 2048  # Adjust based on your needs
        }
    }

    # Set headers with API key
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "key": api_key  # Pass API key as a query parameter
    }

    try:
        # Make the API request
        res = requests.post(url, json=payload, headers=headers, params=params, stream=False)
        res.raise_for_status()

        # Process the response
        response_json = res.json()
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            answer = response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.warning("No valid response from Gemini API")
            answer = ""

    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Gemini API: {e}")
        answer = ""

    # Save Q&A as a note if there's an answer
    if answer.strip():
        try:
            note_text = f"Q: {prompt}\nA: {answer}"
            create_note(note_text)  # Assuming create_note is defined elsewhere
        except Exception as e:
            logger.error(f"Error saving note: {e}")

    return {"reply": answer.strip() or "Không tạo được câu trả lời từ tài liệu."}

# Ensure database tables exist at startup
init_db_tables()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:8080")],  # Use env or default
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,  # Only if you need cookies/auth headers
)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Qdrant client và model embedding
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)  # Nếu chạy Docker Compose: host="vectordb"
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Initialize FastAPI logger
logger = logging.getLogger("fastapi")  # Use FastAPI's logger

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "documents_v6")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 384))
VECTOR_NAME = os.getenv("VECTOR_NAME", "vector")  # Explicit vector name for Qdrant
from qdrant_client.models import VectorParams, Distance

if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={VECTOR_NAME: VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)},
    )

def extract_text(file_path: str) -> str:
    """Extract text from a file based on its extension."""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            logger.warning(f"Unsupported file extension: {ext}")
            return ""
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """Split text into chunks with specified size and overlap."""
    try:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks
    except Exception as e:
        logger.error(f"Error chunking text: {e}")
        return []

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(await file.read())
        text = extract_text(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Không đọc được nội dung file hoặc file không được hỗ trợ.")
        chunks = chunk_text(text, chunk_size=300, overlap=50)
        if not chunks:
            raise HTTPException(status_code=400, detail="Không tạo được chunks từ nội dung file.")
        vectors = model.encode(chunks, show_progress_bar=True, batch_size=16).tolist()
        if vectors and len(vectors[0]) != VECTOR_SIZE:
            raise HTTPException(status_code=500, detail=f"Vector size mismatch: expected {VECTOR_SIZE}, got {len(vectors[0])}")
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector={VECTOR_NAME: vectors[i]},
                payload={
                    "text": chunks[i],
                    "file": file.filename,
                    "file_id": file_id,
                    "chunk_index": i
                }
            )
            for i in range(len(chunks))
        ]
        collections = qdrant.get_collections().collections
        collection_exists = COLLECTION_NAME in [c.name for c in collections]
        if collection_exists:
            collection_info = qdrant.get_collection(COLLECTION_NAME)
            vector_params = collection_info.config.params.vectors
            if isinstance(vector_params, dict) and VECTOR_NAME in vector_params:
                if vector_params[VECTOR_NAME].size != VECTOR_SIZE:
                    qdrant.delete_collection(COLLECTION_NAME)
                    collection_exists = False
                    logger.warning(f"Deleted collection {COLLECTION_NAME} due to vector size mismatch")
            elif isinstance(vector_params, models.VectorParams) and vector_params.size != VECTOR_SIZE:
                qdrant.delete_collection(COLLECTION_NAME)
                collection_exists = False
                logger.warning(f"Deleted collection {COLLECTION_NAME} due to vector size mismatch")
            else:
                qdrant.delete_collection(COLLECTION_NAME)
                collection_exists = False
                logger.warning(f"Deleted collection {COLLECTION_NAME} due to vector name mismatch")
        if not collection_exists:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={
                    VECTOR_NAME: models.VectorParams(
                        size=VECTOR_SIZE,
                        distance=models.Distance.COSINE
                    )
                }
            )
            logger.info(f"Created collection {COLLECTION_NAME} with vector name {VECTOR_NAME}")
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Upserted {len(points)} points for file {file.filename}")
        return {"message": "File uploaded and indexed!"}
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Updated /ask endpoint
@app.post("/ask")
async def ask_question(payload: dict):
    try:
        question = payload.get("text", "")
        if not question.strip():
            raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")

        # Encode the question
        q_vector = model.encode([question])[0].tolist()

        # Search for relevant chunks in Qdrant
        hits = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=(VECTOR_NAME, q_vector),  # Use correct vector name
            limit=5
        )
        logger.info(f"Found {len(hits)} relevant chunks for question: {question}")
        if not hits:
            logger.info(f"No relevant chunks found for question: {question}")
            return {"reply": "Không tìm thấy thông tin liên quan trong tài liệu."}

        # Build context from search results
        context = "\n".join([hit.payload["text"] for hit in hits])
        prompt = f"Dựa trên các đoạn sau, hãy trả lời câu hỏi một cách chính xác và ngắn gọn nhất.\n{context}\nCâu hỏi: {question}\nTrả lời:"

        # return {"reply": answer.strip() or "Không tạo được câu trả lời từ tài liệu."}
        api_key = os.getenv("GEMINI_API_KEY")
        result = query_gemini_api(prompt, api_key)
        # Save Q&A as a note if there's an answer
        if result["reply"]:
            try:
                note_text = f"Q: {prompt}\nA: {result['reply']}"
                create_note(note_text)
            except Exception as e:
                logger.error(f"Error saving note: {e}")
        return {"reply": result["reply"]}

    except Exception as e:
        logger.error(f"Error processing question '{question}': {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")