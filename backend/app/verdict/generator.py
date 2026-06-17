"""Grounded verdict generation: supported / contradicted / insufficient, with citations.

The LLM is only allowed to choose a label from the ranked evidence it's given — it must not
introduce facts not present in the evidence. Thin or conflicting evidence is steered toward
"insufficient" both by the prompt and by a hard rule below, since the abstain path is the
feature that distinguishes a fact-checker from a hallucination machine.
"""
from __future__ import annotations

import json

from ..llm.base import LLMProvider
from ..schema import Citation, EvidenceChunk, Verdict, VerdictLabel

SYSTEM_PROMPT = """You are a careful fact-checker. You are given a claim and a list of ranked \
evidence chunks, each with a reliability score (0-1) and source URL. Decide whether the \
evidence as a whole SUPPORTS the claim, CONTRADICTS it, or is INSUFFICIENT to decide.

Rules:
- Only use the provided evidence. Never use outside knowledge.
- If evidence is sparse, low-reliability, or conflicting (some supports, some contradicts, \
without a clear high-reliability majority), choose "insufficient" rather than guessing.
- List only the source URLs that you actually relied on as citations.
- confidence is your certainty in the label, 0-1.

Respond with ONLY valid JSON of this exact shape:
{"label": "supported" | "contradicted" | "insufficient", "confidence": 0.0, "rationale": "...", \
"cited_urls": ["..."]}
"""

MIN_EVIDENCE_FOR_DECISION = 1
MIN_RELIABILITY_FOR_DECISION = 0.3


def _format_evidence(evidence: list[EvidenceChunk]) -> str:
    lines = []
    for i, chunk in enumerate(evidence, start=1):
        lines.append(
            f"[{i}] url={chunk.source_url} reliability={chunk.reliability_score:.2f} "
            f"provenance={chunk.provenance.value}\n{chunk.content[:800]}"
        )
    return "\n\n".join(lines) if lines else "(no evidence retrieved)"


def _parse_verdict(raw: str, claim_text: str, evidence: list[EvidenceChunk]) -> Verdict:
    by_url = {c.source_url: c for c in evidence}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    label_raw = str(data.get("label", "insufficient")).lower()
    try:
        label = VerdictLabel(label_raw)
    except ValueError:
        label = VerdictLabel.INSUFFICIENT

    cited_urls = [u for u in data.get("cited_urls", []) if u in by_url]
    citations = [
        Citation(
            source_url=u, title=by_url[u].title, reliability_score=by_url[u].reliability_score
        )
        for u in cited_urls
    ]

    return Verdict(
        claim=claim_text,
        label=label,
        confidence=float(data.get("confidence", 0.0) or 0.0),
        rationale=str(data.get("rationale", "")),
        citations=citations,
    )


async def generate_verdict(
    llm: LLMProvider, claim_text: str, evidence: list[EvidenceChunk]
) -> Verdict:
    usable = [e for e in evidence if e.reliability_score >= MIN_RELIABILITY_FOR_DECISION]

    if len(usable) < MIN_EVIDENCE_FOR_DECISION:
        return Verdict(
            claim=claim_text,
            label=VerdictLabel.INSUFFICIENT,
            confidence=1.0 if not evidence else 0.6,
            rationale=(
                "No evidence retrieved for this claim."
                if not evidence
                else "Only low-reliability evidence was retrieved; not enough to support a verdict."
            ),
            citations=[],
        )

    user_prompt = f"Claim: {claim_text}\n\nEvidence:\n{_format_evidence(usable)}"
    raw = await llm.complete_json(SYSTEM_PROMPT, user_prompt)
    return _parse_verdict(raw, claim_text, usable)
