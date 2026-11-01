import http.server, json, shutil, subprocess, tempfile, threading, unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml
from PIL import Image

from immo import copy as cp, llm, pipeline, property as pm
from immo.util import load_config, read_json

TZ = ZoneInfo("Europe/Paris")
NOW = datetime(2026, 11, 2, 7, 0, tzinfo=TZ)  # lundi


def mk_photos(d, n=3):
    (d / "photos").mkdir(parents=True)
    for i in range(n):
        Image.new("RGB", (1600, 1000), (40 * i + 60, 120, 200 - 30 * i)).save(d / "photos" / f"p{i}.jpg")


BIEN = {"a_verifier": False, "ref": "A100", "transaction": "vente", "statut": "disponible",
        "type_bien": "appartement", "ville": "Lyon", "quartier": "Croix-Rousse", "prix": 345000,
        "surface": 72, "pieces": 3, "chambres": 2, "atouts": ["balcon plein sud", "parking"],
        "dpe": "C", "ges": "B", "honoraires": "Honoraires 4 % TTC à la charge de l'acquéreur",
        "description": "Bel appartement lumineux."}


class Base(unittest.TestCase):
    def setUp(self):
        llm.set_backend(None)
        self.tmp = Path(tempfile.mkdtemp())
        self.inbox, self.out = self.tmp / "inbox", self.tmp / "out"
        self.inbox.mkdir()
        self.cfg = load_config()
        self.cfg["_base"] = str(self.tmp)
        self.cfg["horizon_jours"] = 7
        self.cfg["voix"] = {"commande": None, "musique": None}

    def tearDown(self):
        llm.set_backend(None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def add(self, name, **over):
        d = self.inbox / name
        mk_photos(d)
        (d / "bien.yaml").write_text(yaml.safe_dump({**BIEN, **over}, allow_unicode=True), encoding="utf-8")
        return d


class TestGuard(unittest.TestCase):
    def test_guard_catches_invented_numbers(self):
        f = {"prix": 345000, "surface": 72, "pieces": 3}
        self.assertEqual(cp.guard("Superbe 72 m² à 345 000 €", f), [])
        self.assertTrue(cp.guard("Superbe 85 m²", f))

    def test_llm_hallucination_falls_back(self):
        llm.set_backend(lambda s, u: json.dumps({"hook": "Wow", "body": "120 m² avec piscine", "cta": "x", "script": ["a"]}))
        try:
            cfg = load_config()
            p = pm.Property(Path("/tmp/x"), dict(BIEN))
            r = cp.property_post(p, "instagram", cfg)
            self.assertNotIn("120", r["caption"])
            self.assertIn("DPE : C", r["caption"])
        finally:
            llm.set_backend(None)


class TestCompliance(Base):
    def test_missing_dpe_blocks(self):
        d = self.add("b1", dpe="", ref="B1")
        p = pm.load_properties(self.inbox)[0]
        self.assertTrue(any("DPE" in x for x in pm.problems(p)))

    def test_unreviewed_blocks(self):
        self.add("b1", a_verifier=True)
        self.assertTrue(pm.problems(pm.load_properties(self.inbox)[0]))


class TestE2E(Base):
    def test_full_daily_run_manual(self):
        self.add("bien-a")
        self.add("bien-b", ref="B200", ville="Villeurbanne", prix=210000, surface=48)
        self.add("bloque", ref="Z", dpe="")  # doit être refusé
        res = pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        self.assertIn("Z", res["blocked"])
        st = read_json(self.out / "state.json", {})
        self.assertGreater(len(st["schedule"]), 10)
        self.assertFalse([i for i in st["schedule"] if i["ref"] == "Z"])
        cats = {i["category"] for i in st["schedule"]}
        self.assertEqual(cats, {"biens", "marque"})
        fmts = {i["format"] for i in st["schedule"]}
        self.assertEqual(fmts, {"carousel", "reel", "texte"})
        for i in st["schedule"]:
            for m in i["media"]:
                self.assertTrue(Path(m).stat().st_size > 1000, m)
            if i["category"] == "biens":
                self.assertIn("DPE", i["caption"])
                self.assertIn("Honoraires", i["caption"])
        # un reel est bien un mp4 1080x1920
        reel = next(i for i in st["schedule"] if i["format"] == "reel")["media"][0]
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                             "stream=width,height", "-of", "csv=p=0", reel], capture_output=True, text=True)
        self.assertEqual(pr.stdout.strip(), "1080,1920")
        # idempotence : 2e run = 0 nouveau
        n = len(st["schedule"])
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        self.assertEqual(len(read_json(self.out / "state.json", {})["schedule"]), n)
        # publication : plus tard, les posts échus deviennent prêts
        later = datetime(2026, 11, 4, 23, 0, tzinfo=TZ)
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=later, log=lambda *_: None)
        st = read_json(self.out / "state.json", {})
        ready = [i for i in st["schedule"] if i["status"] == "ready"]
        self.assertTrue(ready)
        self.assertTrue((self.out / "ready" / "TODAY.md").exists())
        self.assertTrue((Path(ready[0]["ready_dir"]) / "legende.txt").exists())

    def test_user_video_reframed_and_voice(self):
        d = self.add("bien-v")
        (d / "videos").mkdir()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=25:duration=2",
                        "-pix_fmt", "yuv420p", str(d / "videos" / "visite.mp4")], check=True)
        self.cfg["plateformes"] = {"tiktok": {"formats": ["reel"], "par_semaine": 7, "heures": ["10:00"]}}
        self.cfg["mix_biens"] = 1.0
        # fausse "synthèse vocale" : un bip de 3 s
        self.cfg["voix"] = {"commande": f"ffmpeg -y -loglevel error -f lavfi -i sine=d=3 {{out}}", "musique": None}
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        st = read_json(self.out / "state.json", {})
        self.assertTrue(st["schedule"])
        self.assertEqual(st["schedule"][0]["category"], "biens")
        self.assertTrue(Path(st["schedule"][0]["media"][0]).exists())

    def test_voiceover_mux(self):
        from immo import video
        self.cfg["voix"] = {"commande": "ffmpeg -y -loglevel error -f lavfi -i sine=d=3 {out}", "musique": None}
        out = self.tmp / "v.mp4"
        video.build_reel(["Un", "Deux"], [], self.cfg, out)
        pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(out)],
                            capture_output=True, text=True)
        self.assertIn("audio", pr.stdout)

    def test_webhook_mode(self):
        got = []

        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(s):
                n = int(s.headers["Content-Length"])
                got.append((s.headers["Content-Type"], s.rfile.read(n)))
                s.send_response(200); s.end_headers()
            def log_message(*a): pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.add("bien-a")
        self.cfg["publication"] = {"mode": "webhook", "webhook_url": f"http://127.0.0.1:{srv.server_port}/"}
        self.cfg["plateformes"] = {"linkedin": {"formats": ["carousel"], "par_semaine": 7, "heures": ["09:00"]}}
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        later = datetime(2026, 11, 3, 12, 0, tzinfo=TZ)
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=later, log=lambda *_: None)
        srv.shutdown()
        st = read_json(self.out / "state.json", {})
        self.assertTrue([i for i in st["schedule"] if i["status"] == "published"])
        self.assertTrue(got and got[0][0].startswith("multipart/form-data"))
        self.assertIn(b"DPE", got[0][1])


class TestIntake(Base):
    def test_fiche_txt_extraction_requires_review(self):
        d = self.inbox / "nouveau"
        d.mkdir()
        (d / "fiche.txt").write_text("T3 Lyon 72m2 345000 euros DPE C")
        llm.set_backend(lambda s, u: json.dumps({"ref": "N1", "ville": "Lyon", "prix": 345000, "surface": 72, "dpe": "C"}))
        pm.extract_from_fiche(d, "m")
        data = yaml.safe_load((d / "bien.yaml").read_text(encoding="utf-8"))
        self.assertTrue(data["a_verifier"])
        self.assertTrue(pm.problems(pm.load_properties(self.inbox)[0]))


if __name__ == "__main__":
    unittest.main()
