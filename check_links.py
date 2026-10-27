#!/usr/bin/env python3
"""Check that every supporting-document link in the dashboard still resolves.

Google Drive file ids die when a document is deleted, moved to trash, or when a
different copy is uploaded — the sheet then keeps working while the link in this
repo 404s. This script walks the URLs in data.json (or raw.csv) and reports any
that no longer resolve.

Usage:
    python3 check_links.py                  # check links in data.json
    python3 check_links.py --raw raw.csv    # check the CSV instead
    python3 check_links.py --timeout 20 --workers 4 --verbose

Exit status is 0 when every link resolves, 1 when at least one is broken, so it
can be wired into a pre-deploy step.

Only the standard library is used, and only the first byte of a document is
requested, so a run stays quick and light.
"""
import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (compatible; ISPSC-dashboard-link-check/1.0)"


def load_urls(source):
    """Return [(id, title, url)] for programs that have a document."""
    if source.endswith(".csv"):
        rows = list(csv.reader(open(source, encoding="utf-8")))
        out, n = [], 0
        for r in rows:
            if len(r) < 14:
                continue
            title = (r[1] or "").strip()
            url = (r[13] or "").strip()
            if not title or not url.startswith("http"):
                continue
            n += 1
            out.append((n, title, url))
        return out

    data = json.load(open(source, encoding="utf-8"))
    return [(p["id"], p["title"], p["document"])
            for p in data["programs"] if (p.get("document") or "").startswith("http")]


def check(url, timeout):
    """Return (ok, detail). Any 2xx/3xx that settles on 2xx counts as ok."""
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": UA,
        # Ask for a single byte so we never download a whole PDF/DOCX.
        "Range": "bytes=0-0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, f"{resp.status} {resp.geturl()}"[:120]
    except urllib.error.HTTPError as e:
        # 416 can be returned by some hosts that dislike Range; treat as alive.
        if e.code in (200, 206, 416):
            return True, f"{e.code}"
        hint = {403: "permission denied — file is not shared publicly",
                404: "not found — deleted, trashed or replaced",
                410: "gone"}.get(e.code, "request failed")
        return False, f"{e.code} {hint}"
    except urllib.error.URLError as e:
        return False, f"unreachable: {e.reason}"
    except Exception as e:                                    # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="data.json", help="JSON file to read (default: data.json)")
    ap.add_argument("--raw", help="read raw CSV instead of JSON")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--verbose", action="store_true", help="print every link, not just failures")
    args = ap.parse_args()

    source = args.raw or args.data
    items = load_urls(source)
    if not items:
        print(f"No document links found in {source}.")
        return 2

    print(f"Checking {len(items)} document links from {source}…\n")
    broken = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(lambda it: (it, *check(it[2], args.timeout)), items))

    for (pid, title, url), ok, detail in results:
        if not ok:
            broken.append((pid, title, url, detail))
            print(f"  BROKEN  #{pid:<4} {title[:58]}")
            print(f"          {url}")
            print(f"          -> {detail}\n")
        elif args.verbose:
            print(f"  ok      #{pid:<4} {title[:58]}")

    total = len(results)
    if broken:
        print(f"{len(broken)} of {total} links are broken.")
        print("Re-export the sheet (or fix the Documents column) and re-run "
              "parse.py + build.py. See README.")
        return 1

    print(f"All {total} links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
