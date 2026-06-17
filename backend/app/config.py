from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    llm_provider: str = "openai"  # "openai" | "anthropic"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # Embeddings
    embedding_model: str = "text-embedding-3-small"

    # Web search
    search_provider: str = "tavily"  # "tavily" | "brave" | "none"
    tavily_api_key: str | None = None
    brave_api_key: str | None = None
    web_search_results: int = 5

    # Retrieval / corpus
    chroma_persist_dir: str = "./chroma_data"
    corpus_collection_name: str = "pravda_corpus"
    corpus_top_k: int = 5

    # Ranking
    reliability_recency_halflife_days: float = 365.0

    # Misc
    cors_origins: list[str] = ["*"]


settings = Settings()
