"""Claim extraction: turns a highlighted passage into zero or more atomic, falsifiable claims.

v1 is a single prompted LLM call (see README "Limitations & Future Work" — a fine-tuned
classifier is future work, deliberately not built for v1 per project scope).
"""
from __future__ import annotations

import json

from ..llm.base import LLMProvider
from ..schema import Claim

SYSTEM_PROMPT = """You are a fact-checking assistant. Given a passage of text highlighted by a \
reader, identify the distinct, atomic, factually checkable claims it makes.

Rules:
- Split compound statements into separate atomic claims.
- A claim is "checkable" only if it asserts a verifiable fact about the world (a statistic, \
an event, a causal or historical statement). Opinions, value judgments, predictions about the \
far future, and pure subjective statements ("this is beautiful") are NOT checkable.
- If the passage contains no checkable claims, return an empty "claims" list.
- For each claim, state the reason it is or isn't checkable.

Respond with ONLY valid JSON of this exact shape:
{"claims": [{"text": "...", "checkable": true, "reason": "..."}]}
"""


def _parse_claims(raw: str) -> list[Claim]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    items = data.get("claims", []) if isinstance(data, dict) else []
    claims: list[Claim] = []
    for item in items:
        if not isinstance(item, dict) or "text" not in item:
            continue
        claims.append(
            Claim(
                text=str(item["text"]).strip(),
                checkable=bool(item.get("checkable", False)),
                reason=item.get("reason"),
            )
        )
    return claims


async def extract_claims(llm: LLMProvider, highlighted_text: str) -> list[Claim]:
    highlighted_text = highlighted_text.strip()
    if not highlighted_text:
        return []
    raw = await llm.complete_json(SYSTEM_PROMPT, f"Highlighted passage:\n{highlighted_text}")
    return _parse_claims(raw)
