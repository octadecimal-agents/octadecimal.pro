import os
import sys

sys.path.insert(0, "src")

import pytest

from pipecat_translator.config import Config
from pipecat_translator.poc import TranslatorPOC

API_KEY = os.getenv("OPENAI_API_KEY", "")

pytestmark = pytest.mark.skipif(not API_KEY, reason="OPENAI_API_KEY required")


@pytest.fixture
def translator():
    config = Config(openai_api_key=API_KEY, source_language="pl", target_language="en")
    return TranslatorPOC(config)


def test_translate_pl_to_en(translator):
    result = translator.translate_and_suggest("Dzień dobry, jak się masz?")
    assert "translation" in result
    assert "suggestion" in result
    assert len(result["translation"]) > 0
    assert len(result["suggestion"]) > 0


def test_translate_en_to_pl():
    config = Config(openai_api_key=API_KEY, source_language="en", target_language="pl")
    t = TranslatorPOC(config)
    result = t.translate_and_suggest("Hello, how are you?")
    assert "translation" in result
    assert len(result["translation"]) > 0


def test_conversation_history(translator):
    translator.translate_and_suggest("Cześć")
    translator.translate_and_suggest("Co słychać?")
    assert len(translator.conversation_history) >= 4
