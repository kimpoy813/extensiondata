#!/usr/bin/env python3
"""Inject data.json into template.html -> self-contained index.html.

Usage:
    python3 build.py                 # writes ./index.html
    python3 build.py --out-dir build # writes ./build/index.html (what Render runs)
"""
import argparse
import json
import os

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--out-dir",
    default=".",
    help="directory to write index.html into (created if missing); default: current dir",
)
args = parser.parse_args()

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

payload = json.dumps(data, ensure_ascii=False)
# Prevent "</script>" sequences inside data from breaking the inline script.
payload = payload.replace("</", "<\\/")

with open("template.html", encoding="utf-8") as f:
    html = f.read()

assert "__DATA__" in html, "placeholder missing in template"
html = html.replace("__DATA__", payload)

out_dir = args.out_dir or "."
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "index.html")

with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"{out_path} written: {len(html):,} bytes, {len(data['programs'])} programs")
