import os
from pathlib import Path

import sounddevice
from dotenv import load_dotenv, set_key, unset_key

_ENV_PATH = Path(__file__).parent.parent.parent / ".env"

load_dotenv(dotenv_path=_ENV_PATH)


def find_blackhole_device() -> int | None:
    devices = sounddevice.query_devices()
    for i, d in enumerate(devices):
        if "BlackHole" in d["name"] and d["max_input_channels"] > 0:
            return i
    return None


def get_input_device_index() -> int | None:
    saved = os.getenv("AUDIO_INPUT_DEVICE")
    if saved is not None and saved.strip():
        try:
            return int(saved)
        except ValueError:
            pass

    blackhole = find_blackhole_device()
    if blackhole is not None:
        save_audio_config(input_device_index=blackhole)
        return blackhole

    return None


def save_audio_config(input_device_index: int | None) -> None:
    _ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if input_device_index is not None:
        set_key(str(_ENV_PATH), "AUDIO_INPUT_DEVICE", str(input_device_index))
    else:
        unset_key(str(_ENV_PATH), "AUDIO_INPUT_DEVICE")
