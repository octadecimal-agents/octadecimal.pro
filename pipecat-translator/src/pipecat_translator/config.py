import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")


@dataclass
class Config:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    deepgram_api_key: str = field(default_factory=lambda: os.getenv("DEEPGRAM_API_KEY", ""))
    cartesia_api_key: str = field(default_factory=lambda: os.getenv("CARTESIA_API_KEY", ""))
    daily_api_key: str = field(default_factory=lambda: os.getenv("DAILY_API_KEY", ""))
    daily_bot_username: str = field(default_factory=lambda: os.getenv("DAILY_BOT_USERNAME", "Translator Bot"))

    source_language: str = "pl"
    target_language: str = "en"

    @property
    def llm_model(self) -> str:
        return "gpt-4o"

    @property
    def stt_model(self) -> str:
        return "whisper-large-v3"

    @property
    def tts_model(self) -> str:
        return "sonic-3"

    def validate(self) -> list[str]:
        errors = []
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        return errors
