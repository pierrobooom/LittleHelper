from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    ollama_host: str = os.getenv("LL_OLLAHA_HOST", "http://localhost:11434")
    model: str = os.getenv("LL_MODEL", "qwen2.5:14b-instruct")
    timeout_s: int = int(os.getenv("LH_TIMEOUT_S", "120"))

settings = Settings()