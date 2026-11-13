import unittest
from pathlib import Path


class BlenderPilotTests(unittest.TestCase):
    def test_blender_pilot_script_is_valid_python_and_contains_four_shots(self):
        script = Path("scripts/blender/keeladi_pilot.py")
        source = script.read_text(encoding="utf-8")
        compile(source, str(script), "exec")
        for token in ("SHOT_1", "SHOT_2", "SHOT_3", "SHOT_4", "keeladi-pilot-visual.mp4"):
            self.assertIn(token, source)
        self.assertIn("BLENDER_EEVEE_NEXT", source)


if __name__ == "__main__":
    unittest.main()
