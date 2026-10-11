"""Keep separate music and lyrics choices aligned with Dify."""

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "suno_comfy", ROOT / "__init__.py", submodule_search_locations=[str(ROOT)]
)
package = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = package
spec.loader.exec_module(package)
nodes = sys.modules["suno_comfy.nodes"]


class SunoNodeTests(unittest.TestCase):
    def test_all_dify_model_ids_have_correct_operation(self):
        audio = nodes.AceSunoGenerate.INPUT_TYPES()["required"]["model"][0]
        lyrics = nodes.AceSunoGenerateLyrics.INPUT_TYPES()["required"]["model"][0]
        self.assertEqual(len(audio), 10)
        self.assertEqual(set(lyrics), {"default", "remi-v1"})
        self.assertEqual(len(set(audio) | set(lyrics)), 12)

    def test_lyrics_task_id_is_visible_without_claiming_completion(self):
        with patch.object(nodes, "generate_lyrics", return_value=("pending", "lyrics-123", "", "trace-123")):
            value = nodes.AceSunoGenerateLyrics().run("hope", "remi-v1")
        self.assertEqual(value["result"], ("pending", "lyrics-123", "", "trace-123"))
        self.assertIn("lyrics-123", " ".join(value["ui"]["text"]))


if __name__ == "__main__":
    unittest.main()
