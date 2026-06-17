"""Blends live web search with the curated corpus into raw evidence, tagged with provenance.
Ranking (rank/) scores reliability afterward; this module only fetches and tags."""
from __future__ import annotations

from urllib.parse import urlparse

from ..config import settings
from ..schema import EvidenceChunk, Provenance, ReliabilitySignals
from . import corpus
from .web_search import WebSearchProvider


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except ValueError:
        return ""


async def retrieve_evidence(claim_text: str, web_search: WebSearchProvider) -> list[EvidenceChunk]:
    """Returns raw evidence chunks with placeholder reliability scores of 0 — rank.score_evidence
    fills in the real scores. Kept here so retrieval stays a pure fetch step."""
    chunks: list[EvidenceChunk] = []

    web_results = await web_search.search(claim_text, max_results=settings.web_search_results)
    for r in web_results:
        if not r["content"] or not r["url"]:
            continue
        chunks.append(
            EvidenceChunk(
                content=r["content"],
                source_url=r["url"],
                source_domain=_domain(r["url"]),
                title=r.get("title"),
                published_date=r.get("published_date"),
                provenance=Provenance.WEB,
                reliability_score=0.0,
                signals=ReliabilitySignals(domain_reputation=0, recency=0, corroboration=0),
            )
        )

    for r in corpus.query_corpus(claim_text):
        if not r.content or not r.url:
            continue
        chunks.append(
            EvidenceChunk(
                content=r.content,
                source_url=r.url,
                source_domain=_domain(r.url),
                title=r.title,
                published_date=r.published_date,
                provenance=Provenance.CORPUS,
                reliability_score=0.0,
                signals=ReliabilitySignals(domain_reputation=0, recency=0, corroboration=0),
            )
        )

    return chunks
