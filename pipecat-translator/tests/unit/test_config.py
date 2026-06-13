import os
import sys

sys.path.insert(0, "src")

from pipecat_translator.config import Config


def test_missing_api_key():
    c = Config(openai_api_key="")
    errors = c.validate()
    assert len(errors) == 1
    assert "OPENAI_API_KEY" in errors[0]


def test_valid_config():
    c = Config(openai_api_key="sk-test")
    errors = c.validate()
    assert len(errors) == 0


def test_default_values():
    c = Config(openai_api_key="sk-test")
    assert c.source_language == "pl"
    assert c.target_language == "en"
    assert c.llm_model == "gpt-4o"
    assert c.stt_model == "whisper-large-v3"
    assert c.tts_model == "sonic-3"
