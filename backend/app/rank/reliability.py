"""Transparent, explainable source-reliability scoring.

Score = weighted blend of three inspectable signals (no opaque ML model):
  - domain_reputation: a tiered lookup table (.gov/.edu/major fact-checkers > mainstream
    outlets > general web > known-unreliable)
  - recency: exponential decay so older evidence counts for less on time-sensitive claims
  - corroboration: how many *independent* domains in the retrieved set back the same chunk

Each signal is stored on the EvidenceChunk so the UI can show *why* a score is what it is.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from dateutil import parser as date_parser

from ..config import settings
from ..schema import EvidenceChunk, ReliabilitySignals

# Tiered domain reputation. Deliberately small and inspectable rather than a learned model.
HIGH_TRUST_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "nature.com", "science.org",
    "who.int", "cdc.gov", "nih.gov", "nasa.gov", "noaa.gov", "census.gov", "sec.gov",
    "imf.org", "worldbank.org", "un.org",
}
MEDIUM_TRUST_DOMAINS = {
    "wikipedia.org", "nytimes.com", "washingtonpost.com", "theguardian.com", "npr.org",
    "economist.com", "wsj.com", "bloomberg.com", "factcheck.org", "snopes.com",
    "politifact.com",
}
LOW_TRUST_SUFFIXES = (".blogspot.com", ".wordpress.com")


def _domain_reputation(domain: str) -> float:
    domain = domain.lower()
    if domain in HIGH_TRUST_DOMAINS or domain.endswith(".gov") or domain.endswith(".edu"):
        return 0.95
    if domain in MEDIUM_TRUST_DOMAINS:
        return 0.75
    if any(domain.endswith(suf) for suf in LOW_TRUST_SUFFIXES):
        return 0.2
    return 0.5  # unknown general web source — neutral default, not penalized or trusted


def _recency(published_date: str | None, halflife_days: float) -> float:
    if not published_date:
        return 0.5  # unknown date — neutral, neither rewarded nor penalized
    try:
        published = date_parser.parse(published_date)
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
    except (ValueError, OverflowError):
        return 0.5
    age_days = (datetime.now(timezone.utc) - published).days
    if age_days < 0:
        return 1.0
    return math.pow(0.5, age_days / halflife_days)


def _corroboration(domain: str, all_domains: list[str]) -> float:
    distinct_others = {d for d in all_domains if d and d != domain}
    if not distinct_others:
        return 0.0
    # Saturating: 3+ independent corroborating domains is treated as full corroboration.
    return min(1.0, len(distinct_others) / 3)


def score_evidence(chunks: list[EvidenceChunk]) -> list[EvidenceChunk]:
    """Fills in reliability_score + signals on each chunk in place and returns them sorted
    by score descending."""
    all_domains = [c.source_domain for c in chunks]
    halflife = settings.reliability_recency_halflife_days

    for chunk in chunks:
        domain_reputation = _domain_reputation(chunk.source_domain)
        recency = _recency(chunk.published_date, halflife)
        corroboration = _corroboration(chunk.source_domain, all_domains)
        chunk.signals = ReliabilitySignals(
            domain_reputation=domain_reputation, recency=recency, corroboration=corroboration
        )
        chunk.reliability_score = round(
            0.5 * domain_reputation + 0.2 * recency + 0.3 * corroboration, 4
        )

    return sorted(chunks, key=lambda c: c.reliability_score, reverse=True)
