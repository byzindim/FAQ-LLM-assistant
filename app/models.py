from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Добавляем "unknown" в список, чтобы модель могла его вернуть, если не нашла источник
ALLOWED_SOURCES = {
    "hr.md", "hr_extended.md", 
    "it_access.md", "it_extended.md", 
    "equipment.md", "equipment_extended.md",
    "unknown" # 🔥 Добавляем заглушку
}

class Category(str, Enum):
    HR = "hr"
    IT = "it"
    EQUIPMENT = "equipment"
    UNKNOWN = "unknown"

class FAQAnswer(BaseModel):
    # 🔥 Задаем дефолты. Если модель забудет поле — подставится это значение.
    category: Category = Field(default=Category.UNKNOWN, description="Категория вопроса")
    answer: str = Field(description="Ответ на вопрос. Если ответа нет, напиши 'Информация не найдена'.")
    source: str = Field(default="unknown", description="Имя файла-источника")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Уверенность модели от 0.0 до 1.0")
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in ALLOWED_SOURCES:
            # Если модель вернула что-то странное, заменяем на 'unknown', а не падаем
            return "unknown"
        return v

    @field_validator('answer')
    @classmethod
    def sanitize_answer(cls, v: str) -> str:
        return v.strip().replace("\n\n\n", "\n\n")
