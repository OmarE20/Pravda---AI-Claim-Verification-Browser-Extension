import pytest

from app.extract.extractor import extract_claims


@pytest.mark.asyncio
async def test_extract_claims_shape(fake_llm):
    llm = fake_llm(
        [
            {
                "claims": [
                    {"text": "The Eiffel Tower is 330 meters tall.", "checkable": True, "reason": "verifiable fact"},
                    {"text": "Paris is beautiful.", "checkable": False, "reason": "subjective opinion"},
                ]
            }
        ]
    )
    claims = await extract_claims(llm, "The Eiffel Tower is 330 meters tall and Paris is beautiful.")
    assert len(claims) == 2
    assert claims[0].checkable is True
    assert claims[0].text == "The Eiffel Tower is 330 meters tall."
    assert claims[1].checkable is False


@pytest.mark.asyncio
async def test_extract_claims_empty_input_short_circuits(fake_llm):
    llm = fake_llm([{"claims": []}])
    claims = await extract_claims(llm, "   ")
    assert claims == []
    assert llm.calls == []


@pytest.mark.asyncio
async def test_extract_claims_handles_malformed_json(fake_llm):
    llm = fake_llm(["not valid json"])
    claims = await extract_claims(llm, "some text")
    assert claims == []
