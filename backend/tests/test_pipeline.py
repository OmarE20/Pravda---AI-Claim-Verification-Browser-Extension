import pytest

from app.pipeline import run_check
from app.schema import VerdictLabel


@pytest.mark.asyncio
async def test_run_check_skips_retrieval_for_uncheckable_claims(fake_llm, fake_web_search):
    llm = fake_llm([{"claims": [{"text": "Paris is beautiful.", "checkable": False, "reason": "opinion"}]}])
    web_search = fake_web_search([])
    response = await run_check("Paris is beautiful.", llm, web_search)
    assert response.claims[0].checkable is False
    assert response.verdicts == []
    assert response.evidence == []


@pytest.mark.asyncio
async def test_run_check_end_to_end_with_supporting_evidence(fake_llm, fake_web_search):
    llm = fake_llm(
        [
            {"claims": [{"text": "The Eiffel Tower is 330 meters tall.", "checkable": True, "reason": "fact"}]},
            {
                "label": "supported",
                "confidence": 0.85,
                "rationale": "Reuters confirms the height.",
                "cited_urls": ["https://reuters.com/eiffel"],
            },
        ]
    )
    web_search = fake_web_search(
        [
            {
                "content": "The Eiffel Tower stands 330 meters tall including antennas.",
                "url": "https://reuters.com/eiffel",
                "title": "Eiffel Tower facts",
                "published_date": None,
            }
        ]
    )
    response = await run_check("The Eiffel Tower is 330 meters tall.", llm, web_search)
    assert len(response.verdicts) == 1
    assert response.verdicts[0].label == VerdictLabel.SUPPORTED
    assert response.latency_ms > 0
    assert len(response.evidence) == 1
