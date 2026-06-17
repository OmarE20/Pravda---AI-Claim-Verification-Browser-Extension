from __future__ import annotations

import json

import pytest

from app.llm.base import LLMProvider
from app.retrieve.web_search import WebResult, WebSearchProvider


class FakeLLM(LLMProvider):
    """Returns canned JSON responses in order, so tests don't hit a real API."""

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    async def complete_json(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        if not self._responses:
            return "{}"
        return self._responses.pop(0)


class FakeWebSearch(WebSearchProvider):
    def __init__(self, results: list[WebResult] | None = None):
        self._results = results or []

    async def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        return self._results[:max_results]


@pytest.fixture
def fake_llm():
    return lambda responses: FakeLLM([json.dumps(r) if isinstance(r, dict) else r for r in responses])


@pytest.fixture
def fake_web_search():
    return lambda results=None: FakeWebSearch(results)
