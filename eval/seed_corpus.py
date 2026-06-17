"""Seeds the curated ChromaDB corpus with a small set of trusted reference snippets.

Deliberately small per project scope — v1 leans on live web search for breadth and uses
the corpus only for stable, high-reliability ground truth. Run with:
    python -m eval.seed_corpus
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.retrieve.corpus import add_documents  # noqa: E402

SEED_DOCS = [
    {
        "content": "The Eiffel Tower stands 330 metres (1,083 ft) tall, including antennas, "
        "and was completed in 1889 for the World's Fair in Paris.",
        "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
        "title": "Eiffel Tower - Wikipedia",
        "published_date": None,
    },
    {
        "content": "Mount Everest, at 8,849 metres (29,032 ft), is Earth's highest mountain "
        "above sea level, located in the Mahalangur Himal sub-range of the Himalayas.",
        "url": "https://en.wikipedia.org/wiki/Mount_Everest",
        "title": "Mount Everest - Wikipedia",
        "published_date": None,
    },
    {
        "content": "The claim that the Great Wall of China is visible from the Moon with the "
        "naked eye is a common misconception; it is not visible from the Moon without aid.",
        "url": "https://en.wikipedia.org/wiki/Great_Wall_of_China",
        "title": "Great Wall of China - Wikipedia",
        "published_date": None,
    },
    {
        "content": "The myth that humans only use 10% of their brains is false. Brain imaging "
        "studies show that the vast majority of the brain is active over the course of a day.",
        "url": "https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/",
        "title": "Do People Only Use 10 Percent of Their Brains?",
        "published_date": "2008-02-08",
    },
    {
        "content": "COVID-19 mRNA vaccines do not alter a person's DNA. mRNA from the vaccine "
        "never enters the nucleus of the cell, where DNA is kept, and is degraded soon after "
        "the cell uses the instructions.",
        "url": "https://www.cdc.gov/coronavirus/2019-ncov/vaccines/facts.html",
        "title": "Myths and Facts about COVID-19 Vaccines",
        "published_date": "2023-01-01",
    },
    {
        "content": "At standard atmospheric pressure (1 atm), water boils at 100 degrees Celsius "
        "(212 degrees Fahrenheit).",
        "url": "https://www.nist.gov/pml/owm/si-units-temperature",
        "title": "SI Units - Temperature",
        "published_date": None,
    },
    {
        "content": "Photosynthesis is the process by which plants, algae, and some bacteria "
        "convert carbon dioxide and water into glucose and oxygen using light energy, typically "
        "from the sun.",
        "url": "https://www.nasa.gov/centers-and-facilities/marshall/photosynthesis/",
        "title": "Photosynthesis Overview",
        "published_date": None,
    },
    {
        "content": "The United States Declaration of Independence was adopted by the Second "
        "Continental Congress on July 4, 1776.",
        "url": "https://www.archives.gov/founding-docs/declaration-of-independence",
        "title": "Declaration of Independence - National Archives",
        "published_date": None,
    },
    {
        "content": "The claim that Albert Einstein failed mathematics in school is a popular myth. "
        "School records show Einstein excelled at mathematics from an early age.",
        "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
        "title": "Albert Einstein - Wikipedia",
        "published_date": None,
    },
]


def main() -> None:
    add_documents(
        documents=[d["content"] for d in SEED_DOCS],
        urls=[d["url"] for d in SEED_DOCS],
        titles=[d["title"] for d in SEED_DOCS],
        published_dates=[d["published_date"] for d in SEED_DOCS],
    )
    print(f"Seeded {len(SEED_DOCS)} documents into the curated corpus.")


if __name__ == "__main__":
    main()
