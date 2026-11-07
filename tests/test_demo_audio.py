"""Tests for optional demo narration assets and missing-audio behavior."""

from pathlib import Path
from contextlib import nullcontext
import base64

import demo


def test_every_scene_has_narration_and_a_matching_filename():
    assert len(demo.SCENES) == 10
    for scene_number, scene in enumerate(demo.SCENES, start=1):
        assert scene["narration"].strip()
        audio_path = demo.scene_audio_path(scene_number)
        assert audio_path.name == f"scene_{scene_number:02d}.mp3"
        assert audio_path.is_file()


def test_scene_target_is_typing_or_audio_plus_only_a_short_pause():
    message = "A short typed sample."
    speed = 0.35
    audio_duration = 6.0
    target = demo.scene_target_duration(message, speed, audio_duration, pause=1.4)

    assert target >= audio_duration
    assert target <= max(len(message) * 0.018 * speed, audio_duration) + 0.3


def test_audio_html_uses_hidden_player_free_component_and_swallows_autoplay_errors():
    markup = demo._audio_html("data:audio/mp3;base64,ZmFrZQ==")
    assert "new Audio('data:audio/mp3;base64,ZmFrZQ==')" in markup
    assert "audio.play().catch(() => {})" in markup
    assert "pagehide" in markup and "audio.pause()" in markup
    assert "controls" not in markup


def test_audio_data_uri_is_cached_per_file():
    audio_file = demo.scene_audio_path(1)
    demo._audio_data_uri.cache_clear()

    expected = "data:audio/mp3;base64," + base64.b64encode(audio_file.read_bytes()).decode("ascii")
    assert demo._audio_data_uri(str(audio_file)) == expected
    assert demo._audio_data_uri(str(audio_file)) == expected
    assert demo._audio_data_uri.cache_info().misses == 1
    assert demo._audio_data_uri.cache_info().hits == 1


def test_sound_off_clears_placeholder_without_creating_component(monkeypatch):
    audio_file = demo.scene_audio_path(1)
    monkeypatch.setattr(demo, "scene_audio_path", lambda _number: audio_file)
    calls = []
    monkeypatch.setattr(demo.components, "html", lambda *args, **kwargs: calls.append(args))

    class Placeholder:
        def __init__(self):
            self.cleared = 0

        def empty(self):
            self.cleared += 1

    placeholder = Placeholder()
    assert demo.play_scene_audio(placeholder, 1, sound_enabled=False) == 0.0
    assert placeholder.cleared == 1
    assert calls == []


def test_demo_runs_silently_when_audio_files_are_missing(monkeypatch):
    class FakePlaceholder:
        def empty(self):
            pass

        def caption(self, _text):
            pass

        def info(self, _text):
            pass

        def markdown(self, _text, **_kwargs):
            pass

        def audio(self, *_args, **_kwargs):
            raise AssertionError("missing audio must be skipped")

        def container(self):
            return nullcontext()

    class FakeProgress(FakePlaceholder):
        def progress(self, _value):
            pass

    rendered_messages = []
    message_scene = {
        "caption": "A local demo scene.",
        "narration": "This is a local demo scene.",
        "message": "Fictional bank alert: share your OTP now.",
        "wait_time": 0.0,
    }
    monkeypatch.setattr(demo, "SCENES", [message_scene])
    monkeypatch.setattr(demo, "AUDIO_DIR", Path(__file__).parent / "audio_that_is_not_present")
    monkeypatch.setattr(demo.st, "empty", FakePlaceholder)
    monkeypatch.setattr(demo.st, "progress", lambda _value: FakeProgress())
    monkeypatch.setattr(demo.st, "spinner", lambda _text: nullcontext())
    monkeypatch.setattr(demo.st, "markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(demo.st, "success", lambda _text: None)
    monkeypatch.setattr(demo, "warm_model", lambda: None)
    monkeypatch.setattr(demo, "analyze_message", lambda _text: {"risk": "Medium"})
    monkeypatch.setattr(
        demo,
        "render_result",
        lambda text, container, **kwargs: rendered_messages.append(text),
    )

    demo.run_demo(speed=0.0, sound_enabled=True)

    assert rendered_messages == [message_scene["message"]]
