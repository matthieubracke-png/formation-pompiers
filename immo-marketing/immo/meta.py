"""Publication directe Facebook (Page) + Instagram (compte pro) via l'API Graph de Meta.
ÉCRIT D'APRÈS LA DOC PUBLIQUE, TESTÉ UNIQUEMENT CONTRE UN FAUX SERVEUR (tests/test_meta.py).
Jamais exécuté contre le vrai Meta : jeton, permissions et validation d'app restent à ta charge.
Instagram exige des URL publiques pour les médias -> publication.meta.media_base_url."""
import json, os, time
from pathlib import Path
import requests


class MetaError(RuntimeError):
    pass


class Meta:
    def __init__(self, cfg, outroot):
        m = cfg["publication"].get("meta") or {}
        self.m = m
        self.out = Path(outroot)
        self.base = (m.get("graph_base") or "https://graph.facebook.com").rstrip("/")
        self.ver = m.get("graph_version", "v21.0")
        self.token = os.environ.get(m.get("token_env", "META_ACCESS_TOKEN"))
        if not self.token:
            raise MetaError(f"variable {m.get('token_env', 'META_ACCESS_TOKEN')} absente")

    def _post(self, path, **kw):
        data = dict(kw.pop("data", {}))
        data["access_token"] = self.token
        r = requests.post(f"{self.base}/{self.ver}/{path}", data=data, timeout=300, **kw)
        try:
            j = r.json()
        except ValueError:
            j = {}
        if r.status_code >= 400 or "error" in j:
            raise MetaError(f"Meta {path}: {str(j.get('error', r.text))[:300]}")
        return j

    def _get(self, path, **params):
        params["access_token"] = self.token
        r = requests.get(f"{self.base}/{self.ver}/{path}", params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def _url(self, media):
        base = self.m.get("media_base_url")
        if not base:
            raise MetaError("publication.meta.media_base_url requis pour Instagram (URL publique des médias)")
        return base.rstrip("/") + "/" + Path(media).resolve().relative_to(self.out.resolve()).as_posix()

    # ---- Facebook ----
    def facebook(self, item):
        page = self.m["page_id"]
        media, cap = item["media"], item["caption"]
        if item["format"] == "reel":
            with open(media[0], "rb") as f:
                return self._post(f"{page}/videos", data={"description": cap}, files={"source": f})["id"]
        if len(media) == 1:
            with open(media[0], "rb") as f:
                return self._post(f"{page}/photos", data={"caption": cap}, files={"source": f})["id"]
        ids = []
        for p in media[:10]:
            with open(p, "rb") as f:
                ids.append(self._post(f"{page}/photos", data={"published": "false"}, files={"source": f})["id"])
        att = {f"attached_media[{i}]": json.dumps({"media_fbid": x}) for i, x in enumerate(ids)}
        return self._post(f"{page}/feed", data={"message": cap, **att})["id"]

    # ---- Instagram ----
    def _wait(self, cid, tries=30, delay=5):
        for _ in range(tries):
            s = self._get(cid, fields="status_code").get("status_code")
            if s == "FINISHED":
                return
            if s in ("ERROR", "EXPIRED"):
                raise MetaError(f"traitement Instagram en échec ({s})")
            time.sleep(delay)
        raise MetaError("traitement Instagram trop long")

    def instagram(self, item, delay=5):
        ig = self.m["ig_user_id"]
        media, cap = item["media"], item["caption"]
        if item["format"] == "reel":
            cid = self._post(f"{ig}/media", data={"media_type": "REELS", "video_url": self._url(media[0]),
                                                  "caption": cap})["id"]
            self._wait(cid, delay=delay)
        elif len(media) == 1:
            cid = self._post(f"{ig}/media", data={"image_url": self._url(media[0]), "caption": cap})["id"]
        else:
            kids = [self._post(f"{ig}/media", data={"image_url": self._url(p), "is_carousel_item": "true"})["id"]
                    for p in media[:10]]
            cid = self._post(f"{ig}/media", data={"media_type": "CAROUSEL", "children": ",".join(kids),
                                                  "caption": cap})["id"]
        return self._post(f"{ig}/media_publish", data={"creation_id": cid})["id"]

    def publish(self, item):
        p = item["platform"]
        if p == "facebook":
            return self.facebook(item)
        if p == "instagram":
            return self.instagram(item)
        raise MetaError(f"Meta ne gère pas {p}")
