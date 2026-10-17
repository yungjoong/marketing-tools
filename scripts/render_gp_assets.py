import argparse
import http.server
import json
import os
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    return "chrome"


def capture(chrome_path: str, url: str, out_path: Path, width: int, height: int, project_root: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={width},{height}",
        "--virtual-time-budget=3000",
        f"--screenshot={out_path}",
        url,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Captured {out_path.relative_to(project_root)} ({width}x{height})")


def render_all(project_root_str: str):
    project_root = Path(project_root_str).resolve()
    os.chdir(project_root)

    config_path = project_root / "tools" / "assets-config.json"
    if not config_path.exists():
        config_path = project_root / "assets-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    extracted_root = project_root / "store-assets" / "extracted"
    chrome_path = find_chrome()

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    devices = [
        {"id": "phone", "w": 1242, "h": 2208, "mode": "phone"},
        {"id": "tablet7", "w": 1200, "h": 1920, "mode": "tablet"},
        {"id": "tablet10", "w": 2048, "h": 2732, "mode": "tablet"},
    ]

    suffixes = config["assets"]["suffixes"]
    first_num = sorted(suffixes.keys())[0]
    first_suffix = suffixes[first_num]
    icon_url = "/" + config["assets"]["iconPath"].lstrip("/")
    rel_config = "/" + config_path.relative_to(project_root).as_posix()

    for lang in config["languages"]:
        lang_code = lang["code"]
        lang_dir = extracted_root / lang_code

        # 1. Feature Graphic (1024x500)
        first_ss = f"/store-assets/screenshots/phone/phone_{lang_code}_{first_num}_{first_suffix}.png"
        fg_params = urllib.parse.urlencode({
            "title": lang["title"],
            "subtitle": lang.get("featureSubtitle", lang.get("shortDescription", "")),
            "lang": lang_code,
            "icon": icon_url,
            "img": first_ss,
            "config": rel_config,
        })
        fg_url = f"{base_url}/tools/marketing-tools/dashboard/templates/google_play_feature_graphic.html?{fg_params}"
        capture(chrome_path, fg_url, lang_dir / f"feature_graphic_{lang_code}.png", 1024, 500, project_root)

        # 2. Device Screenshots
        for dev in devices:
            dev_id = dev["id"]
            for idx, headline in enumerate(lang["screens"], start=1):
                num = f"{idx:02d}"
                if num not in suffixes:
                    continue
                suffix = suffixes[num]
                img_path = f"/store-assets/screenshots/{dev_id}/{dev_id}_{lang_code}_{num}_{suffix}.png"
                ss_params = urllib.parse.urlencode({
                    "title": headline,
                    "img": img_path,
                    "mode": dev["mode"],
                    "config": rel_config,
                })
                ss_url = f"{base_url}/tools/marketing-tools/dashboard/templates/marketing_template.html?{ss_params}"
                out_file = lang_dir / dev_id / f"{dev_id}_{lang_code}_{num}.png"
                capture(chrome_path, ss_url, out_file, dev["w"], dev["h"], project_root)

    server.shutdown()
    print("\nAll marketing assets rendered to store-assets/extracted/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()
    render_all(args.root)
