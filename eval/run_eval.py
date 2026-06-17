"""Runs Pravda's pipeline against the labeled claim set and reports:
  - verdict accuracy on claims with a known true/false answer
  - abstention rate: how often "insufficient" is correctly chosen for unverifiable claims
  - p50/p95 latency per check

Requires OPENAI_API_KEY (or ANTHROPIC_API_KEY with LLM_PROVIDER=anthropic) to produce real
numbers; a search API key is optional (falls back to corpus-only retrieval). Run with:
    python -m eval.run_eval
"""
from __future__ import annotations

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.llm import get_llm_provider  # noqa: E402
from app.pipeline import run_check  # noqa: E402
from app.retrieve.web_search import get_web_search_provider  # noqa: E402

CLAIMS_PATH = Path(__file__).parent / "labeled_claims.json"


async def main() -> None:
    claims = json.loads(CLAIMS_PATH.read_text())
    llm = get_llm_provider()
    web_search = get_web_search_provider()

    correct = 0
    total_decidable = 0
    abstain_correct = 0
    total_unverifiable = 0
    latencies: list[float] = []
    rows = []

    for item in claims:
        start = time.perf_counter()
        response = await run_check(item["text"], llm, web_search)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        predicted = response.verdicts[0].label.value if response.verdicts else "insufficient"
        expected = item["expected_label"]

        if expected == "insufficient":
            total_unverifiable += 1
            if predicted == "insufficient":
                abstain_correct += 1
        else:
            total_decidable += 1
            if predicted == expected:
                correct += 1

        rows.append((item["text"], expected, predicted, round(elapsed_ms, 1)))

    print(f"{'Claim':<60} {'Expected':<12} {'Predicted':<12} {'ms':>8}")
    for text, expected, predicted, ms in rows:
        print(f"{text[:58]:<60} {expected:<12} {predicted:<12} {ms:>8}")

    accuracy = correct / total_decidable if total_decidable else float("nan")
    abstention_rate = abstain_correct / total_unverifiable if total_unverifiable else float("nan")
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 2 else latencies[0]

    print("\n--- Summary ---")
    print(f"Verdict accuracy (true/false claims): {accuracy:.1%} ({correct}/{total_decidable})")
    print(
        f"Correct abstention rate (unverifiable claims): {abstention_rate:.1%} "
        f"({abstain_correct}/{total_unverifiable})"
    )
    print(f"Latency p50: {p50:.0f} ms, p95: {p95:.0f} ms")


if __name__ == "__main__":
    asyncio.run(main())
