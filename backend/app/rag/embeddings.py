from huggingface_hub import AsyncInferenceClient
from app.config import settings

_client: AsyncInferenceClient | None = None

def _get_client() -> AsyncInferenceClient:
    global _client
    if _client is None:
        _client = AsyncInferenceClient(
            provider=settings.HF_EMBEDDING_PROVIDER, token=settings.HF_TOKEN, timeout=20.0
        )
    return _client

async def embed_documents(texts: list[str]) -> list[list[float]]:
    result = await _get_client().feature_extraction(texts, model=settings.HF_EMBEDDING_MODEL)
    return result.tolist()

async def embed_query(text: str) -> list[float]:
    result = await _get_client().feature_extraction(text, model=settings.HF_EMBEDDING_MODEL)
    return result.tolist()[0] if result.ndim > 1 else result.tolist()
