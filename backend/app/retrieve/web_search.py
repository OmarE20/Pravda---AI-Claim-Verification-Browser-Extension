"""Web-search interface for live evidence. Degrades to an empty list when no key is configured,
so the pipeline falls back to corpus-only retrieval instead of failing."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

import httpx


class WebResult(TypedDict):
    content: str
    url: str
    title: str
    published_date: str | None


class WebSearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        raise NotImplementedError


class TavilyProvider(WebSearchProvider):
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        results: list[WebResult] = []
        for item in data.get("results", []):
            results.append(
                WebResult(
                    content=item.get("content", ""),
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    published_date=item.get("published_date"),
                )
            )
        return results


class BraveProvider(WebSearchProvider):
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": max_results},
                headers={"X-Subscription-Token": self._api_key, "Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
        results: list[WebResult] = []
        for item in data.get("web", {}).get("results", []):
            results.append(
                WebResult(
                    content=item.get("description", ""),
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    published_date=item.get("age"),
                )
            )
        return results


class NullWebSearchProvider(WebSearchProvider):
    """Used when no search API key is configured. Backend degrades to corpus-only retrieval."""

    async def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        return []


def get_web_search_provider() -> WebSearchProvider:
    from ..config import settings

    if settings.search_provider == "tavily" and settings.tavily_api_key:
        return TavilyProvider(settings.tavily_api_key)
    if settings.search_provider == "brave" and settings.brave_api_key:
        return BraveProvider(settings.brave_api_key)
    return NullWebSearchProvider()
