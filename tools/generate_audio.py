"""Generate one Indian English narration MP3 for each editable demo scene."""

import asyncio
import sys
from pathlib import Path

import edge_tts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from demo import AUDIO_DIR, SCENES, VOICE, audio_duration_seconds, scene_audio_path


async def generate_audio() -> None:
    """Read narration from demo.SCENES and save numbered audio assets."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for scene_number, scene in enumerate(SCENES, start=1):
        narration = scene.get("narration", "").strip()
        if not narration:
            raise ValueError(f"Scene {scene_number} is missing narration text")

        audio_path = scene_audio_path(scene_number)
        await edge_tts.Communicate(text=narration, voice=VOICE).save(str(audio_path))
        duration = audio_duration_seconds(audio_path)
        print(f"Created {audio_path.name} ({duration:.1f}s): {narration}")


if __name__ == "__main__":
    asyncio.run(generate_audio())
