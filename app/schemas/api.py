from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional


# === Domain model (from Stage 2) ===
class Category(str, Enum):
    HR = "hr"
    IT = "it"
    FINANCE = "finance"
    OTHER = "other"  # 🔥 ДОБАВЛЕНО: для случаев, когда ответ не найден
    UNKNOWN = "unknown"


class FAQAnswer(BaseModel):
    """Internal model — what LLM returns."""
    category: Category = Field(default=Category.UNKNOWN)
    answer: str = Field(...)
    source: str = Field(default="unknown")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


# === API DTOs ===

class AskRequest(BaseModel):
    """Request from client."""
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="User question in Russian",
        examples=["Сколько дней отпуска положено сотруднику?"]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"question": "Сколько дней отпуска положено сотруднику?"}
            ]
        }
    }


class AskResponse(BaseModel):
    """Response to client."""
    request_id: str = Field(..., description="Unique request ID for tracing")
    answer: str
    category: Category
    confidence: float
    source: str
    latency_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "answer": "Сотруднику положено 28 дней оплачиваемого отпуска.",
                    "category": "hr",
                    "confidence": 0.95,
                    "source": "hr_policy.md",
                    "latency_ms": 3420,
                    "timestamp": "2026-07-09T12:00:00"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    ollama_available: bool
    model: Optional[str] = None
    version: str = "0.3.0"
