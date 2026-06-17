"""Curated vector corpus of trusted reference sources, backed by ChromaDB.

v1 is seeded with a small handful of sources (see eval/seed_corpus.py) rather than an
exhaustive curated set — exhaustive curation is explicitly out of scope per project plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from ..config import settings


@dataclass
class CorpusResult:
    content: str
    url: str
    title: str | None
    published_date: str | None
    distance: float


_client: chromadb.ClientAPI | None = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


def _get_collection():
    client = _get_client()
    kwargs = {}
    if settings.openai_api_key:
        # Falls back to Chroma's bundled default embedding function when no key is set,
        # so the corpus still works (with lower-quality embeddings) for local smoke testing.
        kwargs["embedding_function"] = OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key, model_name=settings.embedding_model
        )
    return client.get_or_create_collection(name=settings.corpus_collection_name, **kwargs)


def add_documents(
    documents: list[str],
    urls: list[str],
    titles: list[str | None],
    published_dates: list[str | None],
) -> None:
    collection = _get_collection()
    ids = [f"doc-{i}-{urlparse(u).netloc}" for i, u in enumerate(urls)]
    metadatas = [
        {"url": u, "title": t or "", "published_date": d or ""}
        for u, t, d in zip(urls, titles, published_dates)
    ]
    collection.upsert(documents=documents, ids=ids, metadatas=metadatas)


def query_corpus(query: str, top_k: int | None = None) -> list[CorpusResult]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    top_k = top_k or settings.corpus_top_k
    result = collection.query(query_texts=[query], n_results=min(top_k, collection.count()))
    results: list[CorpusResult] = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        results.append(
            CorpusResult(
                content=doc,
                url=meta.get("url", ""),
                title=meta.get("title") or None,
                published_date=meta.get("published_date") or None,
                distance=dist,
            )
        )
    return results
