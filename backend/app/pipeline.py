"""Orchestrates highlight -> claim extraction -> retrieval -> ranking -> verdict."""
from __future__ import annotations

import asyncio
import time

from .extract.extractor import extract_claims
from .llm.base import LLMProvider
from .rank.reliability import score_evidence
from .retrieve.retriever import retrieve_evidence
from .retrieve.web_search import WebSearchProvider
from .schema import CheckResponse, EvidenceChunk, Verdict
from .verdict.generator import generate_verdict


async def run_check(
    text: str, llm: LLMProvider, web_search: WebSearchProvider
) -> CheckResponse:
    start = time.perf_counter()

    claims = await extract_claims(llm, text)
    checkable_claims = [c for c in claims if c.checkable]

    all_evidence: list[EvidenceChunk] = []
    verdicts: list[Verdict] = []

    if checkable_claims:
        evidence_per_claim = await asyncio.gather(
            *(retrieve_evidence(c.text, web_search) for c in checkable_claims)
        )
        for claim, raw_evidence in zip(checkable_claims, evidence_per_claim):
            ranked = score_evidence(raw_evidence)
            all_evidence.extend(ranked)
            verdict = await generate_verdict(llm, claim.text, ranked)
            verdicts.append(verdict)

    latency_ms = (time.perf_counter() - start) * 1000
    return CheckResponse(
        claims=claims, verdicts=verdicts, evidence=all_evidence, latency_ms=latency_ms
    )
