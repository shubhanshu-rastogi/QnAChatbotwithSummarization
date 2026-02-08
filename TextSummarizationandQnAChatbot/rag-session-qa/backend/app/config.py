import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _get_env_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass
class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBED_MODEL: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    MAX_CHUNKS_FOR_SUMMARY: int = _get_env_int("MAX_CHUNKS_FOR_SUMMARY", 12)
    TOP_K: int = _get_env_int("TOP_K", 5)
    CHUNK_SIZE: int = _get_env_int("CHUNK_SIZE", 800)
    CHUNK_OVERLAP: int = _get_env_int("CHUNK_OVERLAP", 120)
    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        ]
    )


settings = Settings()
