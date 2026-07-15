import httpx
import json
import logging
from json_repair import repair_json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.schemas.api import FAQAnswer  # 🔥 ИСПРАВЛЕНО: правильный импорт

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate_raw(self, prompt: str) -> str:
        """Базовый запрос к Ollama."""
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json", 
                "options": {"temperature": 0.1, "top_p": 0.9}
            }
        )
        response.raise_for_status()
        return response.json()["response"]

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10), 
        retry=retry_if_exception_type((ValueError, httpx.ReadTimeout, httpx.ConnectError))
    )
    async def generate_structured(self, prompt: str, previous_error: str = None) -> FAQAnswer:
        """Генерация с самоисправлением (Self-Correction)."""
        
        if previous_error:
            correction_prompt = f"""Ты ранее вернул невалидный JSON или нарушил схему. 
Ошибка валидации: {previous_error}
Исправь и верни СТРОГО валидный JSON. Не добавляй никаких комментариев."""
            final_prompt = prompt + "\n\n" + correction_prompt
        else:
            final_prompt = prompt

        raw_text = await self.generate_raw(final_prompt)
        
        repaired_text = repair_json(raw_text, ensure_ascii=False)
        
        try:
            data = json.loads(repaired_text)
            return FAQAnswer(**data) 
        except Exception as e:
            logger.warning(f"Validation failed. Retrying with feedback. Error: {str(e)}")
            raise ValueError(str(e)) 

ollama_client = OllamaClient()
