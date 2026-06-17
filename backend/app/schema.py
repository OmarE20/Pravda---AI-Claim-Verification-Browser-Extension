"""Core data types shared across the extraction -> retrieval -> ranking -> verdict pipeline."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Provenance(str, Enum):
    WEB = "web"
    CORPUS = "corpus"


class VerdictLabel(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT = "insufficient"


class CheckRequest(BaseModel):
    text: str = Field(..., description="The highlighted passage from the page")
    url: Optional[str] = Field(None, description="URL of the page the highlight came from")


class Claim(BaseModel):
    text: str = Field(..., description="The atomic, falsifiable claim as extracted from the highlight")
    checkable: bool = Field(..., description="Whether this claim is factually checkable at all")
    reason: Optional[str] = Field(
        None, description="Why the claim is/isn't checkable, set by the extractor for transparency"
    )


class ReliabilitySignals(BaseModel):
    """The individual signals behind a source's reliability score, kept explicit so the
    score is explainable rather than a black box."""

    domain_reputation: float = Field(..., ge=0, le=1, description="Trust tier of the domain (0-1)")
    recency: float = Field(..., ge=0, le=1, description="How recent the evidence is, decayed over time (0-1)")
    corroboration: float = Field(
        ..., ge=0, le=1, description="How many independent domains support the same chunk (0-1)"
    )


class EvidenceChunk(BaseModel):
    content: str
    source_url: str
    source_domain: str
    title: Optional[str] = None
    published_date: Optional[str] = None
    provenance: Provenance
    reliability_score: float = Field(..., ge=0, le=1)
    signals: ReliabilitySignals
    stance: Optional[str] = Field(
        None, description="LLM-assessed stance of this chunk toward the claim: support | contradict | neutral"
    )


class Citation(BaseModel):
    source_url: str
    title: Optional[str] = None
    reliability_score: float


class Verdict(BaseModel):
    claim: str
    label: VerdictLabel
    confidence: float = Field(..., ge=0, le=1)
    rationale: str
    citations: list[Citation]


class CheckResponse(BaseModel):
    claims: list[Claim]
    verdicts: list[Verdict]
    evidence: list[EvidenceChunk]
    latency_ms: float
