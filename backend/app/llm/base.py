"""Provider-agnostic LLM interface. extract/ and verdict/ depend on this, not on a vendor SDK."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def complete_json(self, system: str, user: str) -> str:
        """Send a prompt and return the raw text response, expected to be JSON."""
        raise NotImplementedError
