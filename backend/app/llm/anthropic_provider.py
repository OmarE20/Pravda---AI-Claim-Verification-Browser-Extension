from __future__ import annotations

from anthropic import AsyncAnthropic

from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Same interface as OpenAIProvider so extract/ and verdict/ can swap providers freely.

    Claude has no native JSON-mode flag, so we instruct it explicitly and rely on the
    caller's JSON parsing to tolerate stray text (extract/verdict already do this).
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete_json(self, system: str, user: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            temperature=0,
            system=system + "\nRespond with ONLY a single valid JSON object, no markdown fences.",
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in response.content if block.type == "text")
