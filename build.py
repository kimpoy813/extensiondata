#!/usr/bin/env python3
"""Inject data.json into template.html -> self-contained index.html."""
import json

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

payload = json.dumps(data, ensure_ascii=False)
# Prevent "</script>" sequences inside data from breaking the inline script.
payload = payload.replace("</", "<\\/")

with open("template.html", encoding="utf-8") as f:
    html = f.read()

assert "__DATA__" in html, "placeholder missing in template"
html = html.replace("__DATA__", payload)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"index.html written: {len(html):,} bytes, {len(data['programs'])} programs")
