from pathlib import Path
from types import SimpleNamespace
import unittest

from src.scenes.level_scene import DEFAULT_MUSIC, LevelScene


class TestLevelMusic(unittest.TestCase):
    def test_read_level_music_from_tmx_properties(self):
        level_scene = LevelScene.__new__(LevelScene)
        level_scene.tmx_map_properties_data = SimpleNamespace(
            properties={"level_music": "sound_fx/moonlit_forest.ogg"}
        )

        self.assertEqual(
            level_scene._get_level_music_track(),
            Path("sound_fx", "moonlit_forest.ogg").resolve().absolute(),
        )

    def test_fallback_music_when_level_music_missing(self):
        level_scene = LevelScene.__new__(LevelScene)
        level_scene.tmx_map_properties_data = SimpleNamespace(properties={})

        self.assertEqual(
            level_scene._get_level_music_track(), DEFAULT_MUSIC
        )

    def test_fallback_music_when_level_music_blank(self):
        level_scene = LevelScene.__new__(LevelScene)
        level_scene.tmx_map_properties_data = SimpleNamespace(
            properties={"level_music": "   "}
        )

        self.assertEqual(
            level_scene._get_level_music_track(), DEFAULT_MUSIC
        )
