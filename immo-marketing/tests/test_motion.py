import re, subprocess, unittest
from tests.test_pipeline import Base
from immo import motion, topics


def probe(p, e):
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", e, "-of", "csv=p=0", str(p)],
                          capture_output=True, text=True).stdout.strip()


class TestTopics(unittest.TestCase):
    def test_no_digits_and_valid_scenes(self):
        for sb in topics.STORYBOARDS:
            blob = " ".join(motion.script_lines(sb)) + " " + sb["titre"]
            self.assertFalse(re.search(r"\d", blob), f"chiffre dans « {sb['titre']} » : règle = aucun chiffre")
            self.assertEqual(sb["scenes"][0]["type"], "hook")
            self.assertEqual(sb["scenes"][-1]["type"], "cta")
            self.assertTrue(sb["points"])

    def test_at_least_a_dozen_topics_across_families(self):
        self.assertGreaterEqual(len(topics.STORYBOARDS), 12)
        self.assertGreaterEqual(len({s["famille"] for s in topics.STORYBOARDS}), 5)


class TestMotion(Base):
    def test_render_every_scene_type_with_voice(self):
        sb = {"titre": "t", "scenes": [
            topics._hook("Un *test* complet", "Test"),
            {"type": "list", "title": "Liste", "items": ["a", "b"], "checks": True, "step": 1.0, "dur": 3.0},
            {"type": "steps", "title": "Étapes", "items": ["a", "b", "c"], "step": 1.0, "dur": 4.0},
            {"type": "myth", "myth": "Faux", "fact": "Vrai", "dur": 4.0},
            topics._cta()]}
        voice = self.tmp / "v.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=d=18", str(voice)], check=True)
        out = self.tmp / "m.mp4"
        motion.render(sb, self.cfg, out, voice=voice)
        self.assertEqual(probe(out, "stream=width,height").split("\n")[0], "1080,1920")
        self.assertIn("audio", probe(out, "stream=codec_type"))
        self.assertTrue(17.5 < float(probe(out, "format=duration")) < 19.5)

    def test_planner_uses_motion_for_brand_reels(self):
        import json
        from tests.test_pipeline import NOW
        from immo import pipeline
        self.cfg["plateformes"] = {"tiktok": {"formats": ["reel"], "par_semaine": 7, "heures": ["10:00"]}}
        self.cfg["mix_biens"] = 0.0
        self.cfg["horizon_jours"] = 2
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        st = json.load(open(self.out / "state.json"))["schedule"]
        self.assertTrue(st)
        r = st[0]["media"][0]
        self.assertEqual(probe(r, "stream=width,height").split("\n")[0], "1080,1920")
        self.assertTrue(float(probe(r, "format=duration")) > 10)


if __name__ == "__main__":
    unittest.main()
