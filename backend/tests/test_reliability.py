from datetime import datetime, timedelta, timezone

from app.rank.reliability import score_evidence
from app.schema import EvidenceChunk, Provenance, ReliabilitySignals


def _chunk(domain: str, url: str, published_date: str | None = None) -> EvidenceChunk:
    return EvidenceChunk(
        content="some evidence text",
        source_url=url,
        source_domain=domain,
        provenance=Provenance.WEB,
        published_date=published_date,
        reliability_score=0.0,
        signals=ReliabilitySignals(domain_reputation=0, recency=0, corroboration=0),
    )


def test_high_trust_domain_scores_higher_than_unknown_domain():
    chunks = [
        _chunk("reuters.com", "https://reuters.com/a"),
        _chunk("randomblog.xyz", "https://randomblog.xyz/a"),
    ]
    ranked = score_evidence(chunks)
    assert ranked[0].source_domain == "reuters.com"
    assert ranked[0].reliability_score > ranked[1].reliability_score


def test_recent_evidence_scores_higher_than_stale_evidence_same_domain():
    today = datetime.now(timezone.utc).isoformat()
    old = (datetime.now(timezone.utc) - timedelta(days=3650)).isoformat()
    chunks = [
        _chunk("nytimes.com", "https://nytimes.com/recent", published_date=today),
        _chunk("nytimes.com", "https://nytimes.com/old", published_date=old),
    ]
    ranked = score_evidence(chunks)
    recent = next(c for c in ranked if c.source_url.endswith("recent"))
    old_chunk = next(c for c in ranked if c.source_url.endswith("old"))
    assert recent.signals.recency > old_chunk.signals.recency
    assert recent.reliability_score > old_chunk.reliability_score


def test_corroboration_increases_with_independent_domains():
    single = [_chunk("a.com", "https://a.com/1")]
    corroborated = [
        _chunk("a.com", "https://a.com/1"),
        _chunk("b.com", "https://b.com/1"),
        _chunk("c.com", "https://c.com/1"),
    ]
    single_ranked = score_evidence(single)
    corroborated_ranked = score_evidence(corroborated)
    a_alone = single_ranked[0]
    a_corroborated = next(c for c in corroborated_ranked if c.source_domain == "a.com")
    assert a_corroborated.signals.corroboration > a_alone.signals.corroboration
    assert a_corroborated.reliability_score > a_alone.reliability_score


def test_score_evidence_sorts_descending():
    chunks = [
        _chunk("randomblog.xyz", "https://randomblog.xyz/a"),
        _chunk("reuters.com", "https://reuters.com/a"),
        _chunk("wikipedia.org", "https://wikipedia.org/a"),
    ]
    ranked = score_evidence(chunks)
    scores = [c.reliability_score for c in ranked]
    assert scores == sorted(scores, reverse=True)
