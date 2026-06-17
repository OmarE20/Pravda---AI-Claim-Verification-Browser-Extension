import pytest

from app.rank.reliability import score_evidence
from app.schema import EvidenceChunk, Provenance, ReliabilitySignals, VerdictLabel
from app.verdict.generator import generate_verdict


def _chunk(domain: str, url: str, content: str = "evidence") -> EvidenceChunk:
    return EvidenceChunk(
        content=content,
        source_url=url,
        source_domain=domain,
        provenance=Provenance.WEB,
        reliability_score=0.0,
        signals=ReliabilitySignals(domain_reputation=0, recency=0, corroboration=0),
    )


@pytest.mark.asyncio
async def test_verdict_supported_links_citations(fake_llm):
    evidence = score_evidence([_chunk("reuters.com", "https://reuters.com/a")])
    llm = fake_llm(
        [
            {
                "label": "supported",
                "confidence": 0.9,
                "rationale": "Reuters confirms this.",
                "cited_urls": ["https://reuters.com/a"],
            }
        ]
    )
    verdict = await generate_verdict(llm, "claim text", evidence)
    assert verdict.label == VerdictLabel.SUPPORTED
    assert len(verdict.citations) == 1
    assert verdict.citations[0].source_url == "https://reuters.com/a"


@pytest.mark.asyncio
async def test_verdict_no_evidence_is_insufficient_without_calling_llm(fake_llm):
    llm = fake_llm([])
    verdict = await generate_verdict(llm, "claim text", [])
    assert verdict.label == VerdictLabel.INSUFFICIENT
    assert verdict.citations == []
    assert llm.calls == []


@pytest.mark.asyncio
async def test_verdict_only_low_reliability_evidence_is_insufficient_without_calling_llm(fake_llm):
    evidence = score_evidence([_chunk("someone.blogspot.com", "https://someone.blogspot.com/a")])
    llm = fake_llm([{"label": "supported", "confidence": 0.9, "rationale": "x", "cited_urls": []}])
    verdict = await generate_verdict(llm, "claim text", evidence)
    assert verdict.label == VerdictLabel.INSUFFICIENT
    assert llm.calls == []


@pytest.mark.asyncio
async def test_verdict_ignores_citation_urls_not_in_evidence_set(fake_llm):
    evidence = score_evidence([_chunk("reuters.com", "https://reuters.com/a")])
    llm = fake_llm(
        [
            {
                "label": "contradicted",
                "confidence": 0.8,
                "rationale": "x",
                "cited_urls": ["https://reuters.com/a", "https://made-up-source.com/fake"],
            }
        ]
    )
    verdict = await generate_verdict(llm, "claim text", evidence)
    assert len(verdict.citations) == 1
    assert verdict.citations[0].source_url == "https://reuters.com/a"


@pytest.mark.asyncio
async def test_verdict_malformed_llm_response_defaults_to_insufficient(fake_llm):
    evidence = score_evidence([_chunk("reuters.com", "https://reuters.com/a")])
    llm = fake_llm(["not json"])
    verdict = await generate_verdict(llm, "claim text", evidence)
    assert verdict.label == VerdictLabel.INSUFFICIENT
