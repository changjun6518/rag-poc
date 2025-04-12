from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.services.rag_service import RAGService
import os
from typing import Dict, Any
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize FastAPI app
app = FastAPI(
    title="Rental Loan Q&A API",
    description="API for RAG-based Q&A system for rental loans",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize RAG service
rag_service = RAGService()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """문서를 업로드하고 벡터 저장소를 업데이트합니다."""
    try:
        # 임시 파일 경로 생성
        temp_file_path = os.path.join(DATA_DIR, file.filename)
        
        # 파일 저장
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # RAG 서비스에 문서 업로드
        success = rag_service.upload_document(temp_file_path)
        
        # 임시 파일 삭제
        os.remove(temp_file_path)
        
        if success:
            return {"status": "success", "message": "Document uploaded successfully"}
        else:
            return {"status": "error", "message": "Failed to process document"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/ask")
async def ask_question(question: Dict[str, str]) -> Dict[str, Any]:
    """질문에 대한 답변을 생성합니다."""
    try:
        answer, sources, logs = rag_service.get_answer(question["text"])
        return {
            "answer": answer,
            "sources": sources,
            "logs": logs
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """API 상태를 확인합니다."""
    return {"status": "healthy"} 