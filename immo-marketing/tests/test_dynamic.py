import csv, http.server, json, os, subprocess, threading, unittest
from pathlib import Path
from tests.test_pipeline import Base
from immo import avatar, dynamic, learn, video


def ffprobe(p, entries):
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "csv=p=0", str(p)],
                          capture_output=True, text=True).stdout.strip()


class TestDynamic(Base):
    def test_timing_covers_audio_and_words(self):
        t = dynamic.plan_timing(["Un deux trois", "Quatre cinq"], total=6.0)
        self.assertAlmostEqual(t[-1][0] + t[-1][1], 6.0, places=3)
        self.assertEqual(sum(len(x[2]) for x in t), 5)

    def test_reel_has_cuts_captions_and_voice(self):
        self.cfg["voix"] = {"commande": "ffmpeg -y -loglevel error -f lavfi -i sine=d=6 {out}", "musique": None}
        out = self.tmp / "r.mp4"
        video.build_reel(["Tu cherches un T3 ?", "Regarde ce balcon", "Écris-moi vite"], [], self.cfg, out)
        self.assertEqual(ffprobe(out, "stream=width,height").split("\n")[0], "1080,1920")
        self.assertIn("audio", ffprobe(out, "stream=codec_type"))
        d = float(ffprobe(out, "format=duration"))
        self.assertTrue(5.5 < d < 7, d)

    def test_relative_output_path(self):
        import os
        old = os.getcwd()
        os.chdir(self.tmp)
        try:
            video.build_reel(["Un deux", "Trois quatre"], [], self.cfg, "rel/out.mp4")
        finally:
            os.chdir(old)
        self.assertTrue((self.tmp / "rel" / "out.mp4").stat().st_size > 1000)

    def test_text_only_format_for_linkedin(self):
        from tests.test_pipeline import NOW
        from immo import pipeline
        self.add("b")
        self.cfg["plateformes"] = {"linkedin": {"formats": ["texte"], "par_semaine": 7, "heures": ["08:30"]}}
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        st = json.load(open(self.out / "state.json"))["schedule"]
        self.assertTrue(st and all(i["format"] == "texte" and i["media"] == [] and i["caption"] for i in st))

    def test_avatar_clip_mode_with_fake_presenter(self):
        d = self.tmp / "brand" / "avatar"
        d.mkdir(parents=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=720x1280:rate=25:duration=8",
                        "-f", "lavfi", "-i", "sine=d=8", "-shortest", "-pix_fmt", "yuv420p", str(d / "p.mp4")], check=True)
        self.cfg["avatar"] = {"provider": "clip", "dossier": "brand/avatar"}
        av = avatar.make(self.cfg, "x", self.tmp / "a.mp4", "k")
        out = self.tmp / "r.mp4"
        video.build_reel(["Bonjour à tous", "Voici mon conseil du jour", "Un bon prix se justifie", "Écris-moi"], [], self.cfg, out, avatar=av)
        self.assertIn("audio", ffprobe(out, "stream=codec_type"))
        self.assertAlmostEqual(float(ffprobe(out, "format=duration")), 8.3, delta=0.6)

    def test_did_provider_against_fake_server(self):
        calls = []

        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(s):
                calls.append(json.loads(s.rfile.read(int(s.headers["Content-Length"])))); calls.append(s.headers["Authorization"])
                s.send_response(200); s.end_headers(); s.wfile.write(b'{"id":"t1"}')
            def do_GET(s):
                s.send_response(200); s.end_headers()
                if s.path.endswith("/talks/t1"):
                    s.wfile.write(json.dumps({"status": "done", "result_url": f"http://127.0.0.1:{srv.server_port}/v.mp4"}).encode())
                else:
                    s.wfile.write(b"VIDEO")
            def log_message(*a): pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        os.environ["DID_API_KEY"] = "k"
        self.cfg["avatar"] = {"provider": "did", "photo_url": "https://x/me.jpg", "api_base": f"http://127.0.0.1:{srv.server_port}"}
        r = avatar.make(self.cfg, "Bonjour", self.tmp / "o.mp4", "k")
        srv.shutdown()
        self.assertEqual(Path(r).read_bytes(), b"VIDEO")
        self.assertEqual(calls[0]["script"]["input"], "Bonjour")
        self.assertEqual(calls[1], "Basic k")

    def test_missing_avatar_falls_back_to_faceless(self):
        from datetime import datetime
        from tests.test_pipeline import NOW
        from immo import pipeline
        self.cfg["avatar"] = {"provider": "clip", "dossier": "brand/avatar"}  # dossier vide
        self.cfg["plateformes"] = {"tiktok": {"formats": ["reel"], "par_semaine": 7, "heures": ["10:00"]}}
        self.cfg["mix_biens"] = 0.0
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        st = json.load(open(self.out / "state.json"))["schedule"]
        self.assertTrue(st and Path(st[0]["media"][0]).exists())


class TestLearn(Base):
    def test_learning_reorders_formats(self):
        self.out.mkdir()
        sched = [{"id": f"p{i}", "platform": "instagram", "format": "reel" if i % 2 else "carousel",
                  "category": "biens", "when": "x", "status": "ready", "ref": "r", "media": []} for i in range(8)]
        json.dump({"schedule": sched}, open(self.out / "state.json", "w"))
        with open(self.out / "metrics.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "vues", "likes", "commentaires", "enregistrements", "partages"])
            for s in sched:
                w.writerow([s["id"], 1000, 100 if s["format"] == "reel" else 10, 5, 20 if s["format"] == "reel" else 1, 10])
        res = learn.run_learning(self.out)
        self.assertGreater(res["instagram|reel"]["score"], res["instagram|carousel"]["score"])
        self.assertEqual(learn.format_order(self.out, "instagram", ["carousel", "reel"])[0], "reel")
        self.assertEqual(learn.format_order(self.out, "tiktok", ["carousel", "reel"]), ["carousel", "reel"])


if __name__ == "__main__":
    unittest.main()
