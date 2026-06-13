from pathlib import Path
from unittest.mock import patch

import pytest

from pipecat_translator.audio_config import (
    find_blackhole_device,
    get_input_device_index,
    save_audio_config,
)


class FakeDevices:
    @staticmethod
    def query_devices():
        return [
            {"name": "MacBook Microphone", "max_input_channels": 1},
            {"name": "BlackHole 2ch", "max_input_channels": 2},
            {"name": "MacBook Speakers", "max_input_channels": 0},
        ]


class FakeDevicesNoBlackHole:
    @staticmethod
    def query_devices():
        return [
            {"name": "MacBook Microphone", "max_input_channels": 1},
            {"name": "MacBook Speakers", "max_input_channels": 0},
        ]


class FakeDevicesOutputOnlyBlackHole:
    @staticmethod
    def query_devices():
        return [
            {"name": "BlackHole 2ch", "max_input_channels": 0},
        ]


@patch("pipecat_translator.audio_config.sounddevice", FakeDevicesNoBlackHole)
def test_find_blackhole_returns_none_when_not_present():
    assert find_blackhole_device() is None


@patch("pipecat_translator.audio_config.sounddevice", FakeDevices)
def test_find_blackhole_returns_index_when_present():
    assert find_blackhole_device() == 1


@patch("pipecat_translator.audio_config.sounddevice", FakeDevicesOutputOnlyBlackHole)
def test_find_blackhole_ignores_output_only():
    assert find_blackhole_device() is None


def test_save_and_load_config(tmp_path):
    from pipecat_translator import audio_config
    audio_config._ENV_PATH = tmp_path / ".env"
    save_audio_config(input_device_index=3)
    content = tmp_path.joinpath(".env").read_text()
    assert "AUDIO_INPUT_DEVICE" in content


@patch("pipecat_translator.audio_config.sounddevice", FakeDevices)
def test_get_input_device_index_prefers_env(monkeypatch, tmp_path):
    from pipecat_translator import audio_config
    audio_config._ENV_PATH = tmp_path / ".env"
    env_path = tmp_path / ".env"
    env_path.write_text("AUDIO_INPUT_DEVICE=42\n")
    monkeypatch.setenv("AUDIO_INPUT_DEVICE", "42")
    assert get_input_device_index() == 42


@patch("pipecat_translator.audio_config.sounddevice", FakeDevices)
def test_get_input_device_index_auto_detects_blackhole(tmp_path):
    from pipecat_translator import audio_config
    env_path = tmp_path / ".env"
    env_path.write_text("")
    audio_config._ENV_PATH = env_path
    result = get_input_device_index()
    assert result == 1
    assert "AUDIO_INPUT_DEVICE" in env_path.read_text()


@patch("pipecat_translator.audio_config.sounddevice", FakeDevicesNoBlackHole)
def test_get_input_device_index_returns_none_when_no_blackhole_and_no_env():
    assert get_input_device_index() is None
