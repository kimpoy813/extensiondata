#!/usr/bin/env python3
"""Parse CHED Form U8 CSV into clean extension-programs JSON."""
import csv, json, re, html

CAMPUSES = ("Main Campus", "Candon Campus", "Cervantes Campus", "Narvacan",
            "Santiago Campus", "Sta. Maria Campus", "Tagudin Campus")

def clean(s):
    if s is None:
        return ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = html.unescape(s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def to_int(s):
    """Return (number_or_None, raw_text)."""
    raw = clean(s)
    if not raw:
        return None, ""
    m = re.search(r"\d[\d,]*", raw)
    if m:
        try:
            return int(m.group(0).replace(",", "")), raw
        except ValueError:
            return None, raw
    return None, raw

def extract_year(title):
    m = re.match(r"\s*(20\d{2}|19\d{2})", title)
    return int(m.group(1)) if m else None

records = []
with open("raw.csv", encoding="utf-8") as f:
    rows = list(csv.reader(f))

campus = None
for i, r in enumerate(rows):
    if i < 12:
        continue
    first = clean(r[0]) if r else ""
    # campus section header: only first cell filled, matches a campus name
    nonempty = [c for c in r if c.strip()]
    if len(nonempty) == 1 and first in CAMPUSES:
        campus = first
        continue
    # stop at certification footer
    if first == "" and len(nonempty) <= 1 and any("Certified Correct" in c for c in r):
        break
    if not first or campus is None:
        continue
    # pad to 14 columns
    r = (r + [""] * 14)[:14]
    title = clean(r[1])
    if not title:
        continue
    students, students_raw = to_int(r[7])
    faculty, faculty_raw = to_int(r[8])
    research_staff, research_staff_raw = to_int(r[9])
    beneficiaries, beneficiaries_raw = to_int(r[10])
    rec = {
        "id": len(records) + 1,
        "campus": campus.replace("Narvacan", "Narvacan Campus"),
        "researchType": clean(r[0]),
        "title": title,
        "year": extract_year(title),
        "researchOutput": clean(r[2]),
        "objectives": clean(r[3]),
        "community": clean(r[4]),
        "duration": clean(r[5]),
        "deliverables": clean(r[6]),
        "students": students,
        "faculty": faculty,
        "researchStaff": research_staff,
        "beneficiaries": beneficiaries,
        "rawCounts": {
            "students": students_raw, "faculty": faculty_raw,
            "researchStaff": research_staff_raw, "beneficiaries": beneficiaries_raw,
        },
        "extensionType": clean(r[11]).replace("Request--based", "Request-based"),
        "ledBy": clean(r[12]),
        "document": clean(r[13]),
    }
    records.append(rec)

meta = {
    "hei": "Ilocos Sur Polytechnic State College",
    "address": "San Nicolas, Candon City, Ilocos Sur",
    "form": "CHED Form U8 — Complete Listing and Description of Outreach Programs",
    "region": "Region I",
}
out = {"meta": meta, "programs": records}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# ---- verification report ----
print("total programs:", len(records))
from collections import Counter
print("by campus:", dict(Counter(p["campus"] for p in records)))
print("by extension type:", dict(Counter(p["extensionType"] or "(blank)" for p in records)))
print("by research type:", dict(Counter(p["researchType"] or "(blank)" for p in records)))
print("by ledBy:", dict(Counter(p["ledBy"] or "(blank)" for p in records)))
years = Counter(p["year"] for p in records)
print("by year:", dict(sorted(years.items(), key=lambda kv: (kv[0] is None, kv[0]))))
print("sum students:", sum(p["students"] or 0 for p in records))
print("sum faculty:", sum(p["faculty"] or 0 for p in records))
print("sum research staff:", sum(p["researchStaff"] or 0 for p in records))
print("sum beneficiaries:", sum(p["beneficiaries"] or 0 for p in records))
print("docs missing:", sum(1 for p in records if not p["document"]))
print("non-http docs:", [p["id"] for p in records if p["document"] and not p["document"].startswith("http")])
print("blank years:", [p["id"] for p in records if p["year"] is None])
print("non-numeric beneficiary raw:", [(p["id"], p["rawCounts"]["beneficiaries"]) for p in records if p["rawCounts"]["beneficiaries"] and p["beneficiaries"] is None])
