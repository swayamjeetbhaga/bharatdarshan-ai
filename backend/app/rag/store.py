import chromadb

from app.config import settings
from app.rag.documents import SEED_DOCUMENTS
from app.rag.embeddings import embed_documents, embed_query

COLLECTION_NAME = "travel_guide"

_client: chromadb.ClientAPI | None = None
_collection = None
# Once we've confirmed the collection is seeded, skip re-checking collection.count()
# (a synchronous local DB call) on every single retrieve() — it never becomes
# unseeded at runtime, so this check only ever needs to do real work once.
_seeded = False

def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(COLLECTION_NAME)
    return _collection

async def ensure_seeded() -> None:
    global _seeded
    if _seeded:
        return
    collection = _get_collection()
    existing = collection.get()
    existing_ids = set(existing.get("ids", []))
    missing_docs = [doc for doc in SEED_DOCUMENTS if doc["id"] not in existing_ids]

    if missing_docs:
        embeddings = await embed_documents([doc["text"] for doc in missing_docs])
        collection.add(
            ids=[doc["id"] for doc in missing_docs],
            embeddings=embeddings,
            documents=[doc["text"] for doc in missing_docs],
            metadatas=[{"title": doc["title"]} for doc in missing_docs],
        )
    _seeded = True

async def retrieve(query: str, top_k: int = 4) -> list[dict]:
    await ensure_seeded()
    collection = _get_collection()
    query_embedding = await embed_query(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    return [
        {"title": metadata.get("title", ""), "text": document}
        for document, metadata in zip(documents, metadatas)
    ]
