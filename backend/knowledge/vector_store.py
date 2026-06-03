"""Qdrant vector store — multi-collection CRUD and search operations."""

import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

logger = logging.getLogger(__name__)


class VectorStore:
    """Qdrant-backed vector store supporting multiple collections."""
    """向量存储类, 支持多个集合的CRUD操作和搜索操作。"""

    def __init__(self, host: str = "localhost", port: int = 6333, grpc_port: int = 6334,
                 prefer_grpc: bool = False, vector_size: int = 768):
        self.client = QdrantClient(host=host, port=port, grpc_port=grpc_port, prefer_grpc=prefer_grpc)
        self.vector_size = vector_size

    # ── Collection Management ─────────────────────────────────────────── #

    async def create_collection(self, name: str, overwrite: bool = False) -> bool:
        """Create a named collection. Returns True if created, False if already exists."""
        try:
            existing = self.client.collection_exists(name)
            if existing:
                if overwrite:
                    self.client.delete_collection(name)
                    logger.info("Overwritten collection: %s", name)
                else:
                    logger.debug("Collection already exists: %s", name)
                    return False

            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            logger.info("Created collection: %s (size=%d)", name, self.vector_size)
            return True
        except Exception as e:
            logger.error("Failed to create collection %s: %s", name, e)
            return False

    async def delete_collection(self, name: str) -> bool:
        try:
            self.client.delete_collection(name)
            return True
        except Exception:
            return False

    def list_collections(self) -> list[str]:
        try:
            collections = self.client.get_collections()
            return [c.name for c in collections.collections]
        except Exception:
            return []

    # ── Upsert ────────────────────────────────────────────────────────── #

    async def upsert_chunks(self, collection: str, chunks: list[dict[str, Any]],
                            embeddings: list[list[float]]) -> int:
        """Insert or update chunks with their embeddings. Returns count inserted."""
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch")

        points = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            point_id = hash(chunk.get("text", str(i))) & 0x7FFFFFFFFFFFFFFF
            points.append(models.PointStruct(
                id=point_id,
                vector=emb,
                payload={
                    "text": chunk.get("text", ""),
                    "source": chunk.get("metadata", {}).get("source", ""),
                    "metadata": chunk.get("metadata", {}),
                },
            ))

        if points:
            try:
                self.client.upsert(collection_name=collection, points=points)
                logger.debug("Upserted %d points to %s", len(points), collection)
            except Exception as e:
                logger.error("Upsert failed for %s: %s", collection, e)
                return 0

        return len(points)

    # ── Search ────────────────────────────────────────────────────────── #

    async def search(self, collection: str, vector: list[float], limit: int = 10,
                     score_threshold: float | None = None) -> list[dict[str, Any]]:
        """Search a collection by vector similarity."""
        try:
            results = self.client.search(
                collection_name=collection,
                query_vector=vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            return [
                {
                    "text": r.payload.get("text", ""),
                    "score": r.score,
                    "source": r.payload.get("source", ""),
                    "metadata": r.payload.get("metadata", {}),
                }
                for r in results
            ]
        except Exception as e:
            logger.error("Search failed on %s: %s", collection, e)
            return []

    async def search_batch(self, collections: list[str], vector: list[float],
                           limit_per_source: int = 10) -> dict[str, list[dict]]:
        """Search multiple collections in parallel. Returns {collection_name: results}."""
        results = {}
        for coll in collections:
            results[coll] = await self.search(coll, vector, limit=limit_per_source)
        return results

    # ── Health ────────────────────────────────────────────────────────── #

    async def health_check(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
