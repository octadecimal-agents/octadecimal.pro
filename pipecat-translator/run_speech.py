import argparse
import asyncio
import os
import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv
from loguru import logger

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineWorker, PipelineParams
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.openai.stt import OpenAISTTService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams
from pipecat.workers.runner import WorkerRunner

from pipecat_translator.audio_config import find_blackhole_device, get_input_device_index, save_audio_config
from pipecat_translator.speech_pipeline import ContextInjector, ResponseHandler
from pipecat_translator.overlay.display import EventKind, OverlayEvent, TranslationOverlay
from pipecat_translator.overlay.processor import OverlayProcessor
from pipecat_translator.rag.embedder import Embedder
from pipecat_translator.rag.processor import RAGProcessor
from pipecat_translator.rag.store import VectorStore

load_dotenv()

ENV_LANG_MAP = {"pl": "PL", "en": "EN"}


async def run_overlay(overlay: TranslationOverlay, stop_event: asyncio.Event):
    overlay_task = asyncio.create_task(overlay.run())
    await stop_event.wait()
    overlay_task.cancel()
    try:
        await overlay_task
    except asyncio.CancelledError:
        pass


async def main():
    parser = argparse.ArgumentParser(description="Speech-to-speech translation PL↔EN")
    parser.add_argument("source_lang", nargs="?", default="pl", help="Source language (pl/en)")
    parser.add_argument("target_lang", nargs="?", default="en", help="Target language (en/pl)")
    parser.add_argument(
        "--input-device", type=int, default=None,
        help="Input device index. Overrides AUDIO_INPUT_DEVICE from .env. "
        "Use --list-devices to see available devices."
    )
    parser.add_argument(
        "--output-device", type=int, default=None,
        help="Output device index (default: system default speaker)"
    )
    parser.add_argument(
        "--list-devices", action="store_true",
        help="List available audio devices and exit"
    )
    parser.add_argument(
        "--save-config", action="store_true",
        help="Save current audio device config to .env and exit"
    )
    args = parser.parse_args()

    if args.list_devices:
        import sounddevice
        print("Dostepne urzadzenia audio:")
        print()
        for i, d in enumerate(sounddevice.query_devices()):
            blackhole_mark = " <<< BlackHole" if "BlackHole" in d["name"] else ""
            print(f"  [{i}] {d['name']}{blackhole_mark}")
            print(f"       in:{d['max_input_channels']} out:{d['max_output_channels']}")
        print()
        print("Usage: uv run python run_speech.py --input-device <indeks>")
        return

    source_lang = args.source_lang
    target_lang = args.target_lang

    # Determine input device: CLI arg > .env > auto-detect > default
    input_device = args.input_device
    if input_device is None:
        input_device = get_input_device_index()

    if args.save_config:
        if input_device is not None:
            save_audio_config(input_device_index=input_device)
            logger.info(f"Zapisano AUDIO_INPUT_DEVICE={input_device} do .env")
        else:
            logger.warning("Nie znaleziono urzadzenia do zapisania")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is required")
        sys.exit(1)

    overlay = TranslationOverlay(
        source_lang=ENV_LANG_MAP.get(source_lang, source_lang.upper()),
        target_lang=ENV_LANG_MAP.get(target_lang, target_lang.upper()),
    )

    if input_device is not None:
        logger.info(f"Uzywam wejscia audio: [{input_device}]")

    transport_params = LocalAudioTransportParams(
        audio_in_sample_rate=16000,
        audio_out_sample_rate=24000,
        audio_in_channels=1,
        audio_out_channels=1,
        input_device_index=input_device,
        output_device_index=args.output_device,
    )
    transport = LocalAudioTransport(params=transport_params)

    vad_processor = VADProcessor(
        vad_analyzer=SileroVADAnalyzer(sample_rate=16000),
    )

    stt = OpenAISTTService(api_key=api_key)

    embedder = Embedder(api_key=api_key)
    vector_store = VectorStore(embedder=embedder)
    import json
    from pathlib import Path
    seed_path = Path(__file__).parent / "src" / "pipecat_translator" / "rag" / "seed_phrases.json"
    if seed_path.exists():
        with open(seed_path) as f:
            phrases = json.load(f)
        sample = [p["pl"] + " " + p["en"] for p in phrases[:3]]
        vector_store.initialize(sample)
        vector_store.upsert(phrases)
        logger.info(f"RAG: zaindeksowano {len(phrases)} fraz")

    rag_processor = RAGProcessor(store=vector_store)

    context_injector = ContextInjector(
        source_lang=source_lang,
        target_lang=target_lang,
        rag_context_provider=lambda: rag_processor.last_context,
    )
    response_handler = ResponseHandler(
        context=context_injector.context,
        target_lang=target_lang,
    )

    llm = OpenAILLMService(
        api_key=api_key,
        settings=OpenAILLMService.Settings(model="gpt-4o"),
    )

    tts = OpenAITTSService(api_key=api_key)

    overlay_processor = OverlayProcessor(
        overlay=overlay,
        target_lang=ENV_LANG_MAP.get(target_lang, target_lang.upper()),
    )

    pipeline = Pipeline([
        transport.input(),
        vad_processor,
        stt,
        rag_processor,
        context_injector,
        llm,
        response_handler,
        overlay_processor,
        tts,
        transport.output(),
    ])

    worker = PipelineWorker(
        pipeline=pipeline,
        name="translation-worker",
        params=PipelineParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
        ),
        idle_timeout_secs=None,
    )

    runner = WorkerRunner()
    await runner.add_workers(worker)

    stop_event = asyncio.Event()
    overlay_task = asyncio.create_task(run_overlay(overlay, stop_event))

    input_label = f"urzadzenie [{input_device}]" if input_device is not None else "mikrofon (domyslny)"
    await overlay.push(OverlayEvent(
        kind=EventKind.STATUS,
        text=f"Gotowy. Źródło: {input_label}.",
    ))

    try:
        await runner.run()
    except asyncio.CancelledError:
        pass
    finally:
        stop_event.set()
        await overlay_task
        logger.info("Zatrzymywanie...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
