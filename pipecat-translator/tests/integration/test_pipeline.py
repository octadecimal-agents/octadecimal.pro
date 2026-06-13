import os
import sys

sys.path.insert(0, "src")

import pytest

from pipecat.pipeline.pipeline import Pipeline

from pipecat_translator.pipeline import (
    build_translation_pipeline,
    create_translation_context,
    LLMResponseCollector,
)

API_KEY = os.getenv("OPENAI_API_KEY", "")

pytestmark = pytest.mark.skipif(not API_KEY, reason="OPENAI_API_KEY required")


def test_pipeline_is_pipeline():
    pipeline = build_translation_pipeline()
    assert isinstance(pipeline, Pipeline)


def test_context_has_system_prompt():
    ctx = create_translation_context("pl", "en")
    messages = ctx.messages
    assert len(messages) >= 1
    assert messages[0]["role"] == "system"
    assert "PL" in messages[0]["content"] or "EN" in messages[0]["content"]


def test_pipeline_with_on_response():
    collected = []

    async def callback(text):
        collected.append(text)

    pipeline = build_translation_pipeline(on_response=callback)
    assert isinstance(pipeline, Pipeline)
