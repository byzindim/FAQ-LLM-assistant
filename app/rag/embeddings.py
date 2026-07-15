import httpx
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def get_embeddings(texts: list[str], ollama_url: str = "http://localhost:11434") -> np.ndarray:
    """
    Получение эмбеддингов батчами. 
    Ollama принимает список текстов, но мы режем на батчи по 50, 
    чтобы не переполнить VRAM и не получить таймаут.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        all_embeddings = []
        for i in range(0, len(texts), 50):
            batch = texts[i:i+50]
            response = await client.post(
                f"{ollama_url}/api/embed",
                json={"model": "nomic-embed-text", "input": batch}
            )
            response.raise_for_status()
            all_embeddings.extend(response.json()["embeddings"])
        
        return np.array(all_embeddings, dtype="float32")
