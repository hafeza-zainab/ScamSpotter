"""Tests for optional demo narration assets and missing-audio behavior."""

from pathlib import Path

import demo


def test_every_scene_has_narration_and_a_matching_filename():
    assert len(demo.SCENES) == 10
    for scene_number, scene in enumerate(demo.SCENES, start=1):
        assert scene["narration"].strip()
        audio_path = demo.scene_audio_path(scene_number)
        assert audio_path.name == f"scene_{scene_number:02d}.mp3"
        assert audio_path.is_file()


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
    monkeypatch.setattr(demo.st, "markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(demo.st, "success", lambda _text: None)
    monkeypatch.setattr(demo, "analyze_message", lambda _text: {"risk": "Medium"})
    monkeypatch.setattr(
        demo,
        "render_result",
        lambda text, container, **kwargs: rendered_messages.append(text),
    )

    demo.run_demo(speed=0.0, sound_enabled=True)

    assert rendered_messages == [message_scene["message"]]
