import http.server, json, os, threading, unittest
from datetime import datetime
from urllib.parse import parse_qs
from tests.test_pipeline import Base, NOW, TZ
from immo import pipeline
from immo.util import read_json

CALLS = []


class H(http.server.BaseHTTPRequestHandler):
    n = 0

    def do_GET(s):
        CALLS.append(("GET", s.path))
        s.send_response(200); s.end_headers(); s.wfile.write(b'{"status_code":"FINISHED"}')

    def do_POST(s):
        body = s.rfile.read(int(s.headers["Content-Length"]))
        CALLS.append(("POST", s.path, s.headers["Content-Type"].split(";")[0], body))
        H.n += 1
        s.send_response(200); s.end_headers(); s.wfile.write(json.dumps({"id": f"id{H.n}"}).encode())

    def log_message(*a): pass


class TestMeta(Base):
    def test_fb_and_ig_publish_rest_manual(self):
        CALLS.clear()
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        os.environ["META_ACCESS_TOKEN"] = "tok"
        self.add("bien-a")
        self.cfg["plateformes"] = {
            "facebook": {"formats": ["carousel"], "par_semaine": 7, "heures": ["09:00"]},
            "instagram": {"formats": ["carousel"], "par_semaine": 7, "heures": ["09:30"]},
            "linkedin": {"formats": ["carousel"], "par_semaine": 7, "heures": ["10:00"]}}
        self.cfg["publication"] = {"mode": "manual", "par_plateforme": {"facebook": "meta", "instagram": "meta"},
            "meta": {"page_id": "P1", "ig_user_id": "I1", "graph_base": f"http://127.0.0.1:{srv.server_port}",
                     "media_base_url": "https://cdn.example/out"}}
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=datetime(2026, 11, 3, 23, 0, tzinfo=TZ), log=lambda *_: None)
        srv.shutdown()
        st = read_json(self.out / "state.json", {})
        by = {}
        for i in st["schedule"]:
            by.setdefault(i["platform"], set()).add(i["status"])
        self.assertIn("published", by["facebook"]); self.assertIn("published", by["instagram"])
        self.assertIn("ready", by["linkedin"])
        paths = [c[1] for c in CALLS if c[0] == "POST"]
        self.assertTrue(any("/P1/photos" in p for p in paths) and any("/P1/feed" in p for p in paths))
        self.assertTrue(any("/I1/media_publish" in p for p in paths))
        ig_media = [c for c in CALLS if c[0] == "POST" and c[1].endswith("/I1/media")]
        self.assertTrue(any(b"https%3A%2F%2Fcdn.example%2Fout%2Fassets" in c[3] for c in ig_media))
        self.assertTrue(any(b"CAROUSEL" in c[3] for c in ig_media))

    def test_missing_token_marks_error_not_crash(self):
        os.environ.pop("META_ACCESS_TOKEN", None)
        self.add("bien-a")
        self.cfg["plateformes"] = {"facebook": {"formats": ["carousel"], "par_semaine": 7, "heures": ["09:00"]}}
        self.cfg["publication"] = {"mode": "meta", "meta": {"page_id": "P1"}}
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=NOW, log=lambda *_: None)
        pipeline.run_daily(self.cfg, self.inbox, self.out, now=datetime(2026, 11, 3, 23, 0, tzinfo=TZ), log=lambda *_: None)
        st = read_json(self.out / "state.json", {})
        errs = [i for i in st["schedule"] if i["status"] == "error"]
        self.assertTrue(errs and "META_ACCESS_TOKEN" in errs[0]["error"])


if __name__ == "__main__":
    unittest.main()
