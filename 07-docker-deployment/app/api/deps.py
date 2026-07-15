from fastapi import Request, Depends
import httpx


async def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    Dependency: returns shared httpx client from app.state.
    
    Why DI?
    - In tests we can override this to return a mock client
    - Routers don't know WHERE the client comes from
    - Easy to add per-request logic (e.g., auth, tracing)
    """
    return request.app.state.http_client


async def get_request_id(request: Request) -> str:
    """
    Dependency: extracts or generates request_id for tracing.
    """
    # Если фронтенд передал свой ID — используем его
    # Иначе генерируем свой
    return request.headers.get("X-Request-ID") or str(__import__("uuid").uuid4())
