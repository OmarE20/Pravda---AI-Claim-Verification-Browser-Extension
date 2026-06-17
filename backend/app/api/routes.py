from __future__ import annotations

from fastapi import APIRouter

from ..llm import get_llm_provider
from ..pipeline import run_check
from ..retrieve.web_search import get_web_search_provider
from ..schema import CheckRequest, CheckResponse

router = APIRouter()


@router.post("/check", response_model=CheckResponse)
async def check(request: CheckRequest) -> CheckResponse:
    llm = get_llm_provider()
    web_search = get_web_search_provider()
    return await run_check(request.text, llm, web_search)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
