#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(ROOT, "media")
CONFIG_PATH = os.path.join(ROOT, "config.json")
KEYS = list("abcdefghij")

IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff"}


def empty_config():
    return {k: None for k in KEYS}


def file_kind(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext in {"mp4", "webm", "mov", "m4v"}:
        return "video"
    if ext in {"mp3", "wav", "wave", "ogg", "m4a", "aac", "flac"}:
        return "audio"
    if ext in IMAGE_EXTS:
        return "image"
    return None


def normalize_entry(val):
    if not isinstance(val, dict):
        return None

    images = val.get("images")
    if isinstance(images, list):
        images = [img for img in images if isinstance(img, str) and img][:10]
        if images:
            return {
                "images": images,
                "title": val.get("title", ""),
                "subtitle": val.get("subtitle", ""),
                "text": val.get("text", ""),
            }

    file = val.get("file")
    if not file:
        return None

    if file_kind(file) == "image":
        return {
            "images": [file],
            "title": val.get("title", ""),
            "subtitle": val.get("subtitle", ""),
            "text": val.get("text", ""),
        }

    entry = {
        "file": file,
        "title": val.get("title", ""),
        "subtitle": val.get("subtitle", ""),
        "text": val.get("text", ""),
    }
    if val.get("image"):
        entry["image"] = val["image"]
    return entry


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return empty_config()
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    config = empty_config()
    for key in KEYS:
        config[key] = normalize_entry(data.get(key))
    return config


def save_config(data):
    config = empty_config()
    for key in KEYS:
        config[key] = normalize_entry(data.get(key))
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")


def list_media():
    files = []
    if not os.path.isdir(MEDIA_DIR):
        return files
    for name in sorted(os.listdir(MEDIA_DIR)):
        if name.startswith("."):
            continue
        path = os.path.join(MEDIA_DIR, name)
        if os.path.isfile(path):
            kind = file_kind(f"media/{name}") or "other"
            files.append({"name": name, "path": f"media/{name}", "kind": kind})
    return files


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/media":
            self.send_json(list_media())
        elif self.path == "/api/config":
            self.send_json(load_config())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/config":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
            save_config(data)
            self.send_json({"ok": True})
        except (json.JSONDecodeError, TypeError, OSError) as e:
            self.send_json({"ok": False, "error": str(e)}, status=400)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(format % args)


if __name__ == "__main__":
    os.chdir(ROOT)
    print(f"Serving on http://localhost:{PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()
