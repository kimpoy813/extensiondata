# ISPSC Extension & Outreach Programs Dashboard

A self-contained dashboard for the **CHED Form U8 — Complete Listing and Description of
Outreach Programs** of **Ilocos Sur Polytechnic State College** (115 programs, 7 campuses,
school years 2014–2026).

## Files

| File | Purpose |
|---|---|
| `index.html` | **The dashboard** — single self-contained file (HTML + CSS + JS + data). Double-click to open, or host anywhere. No internet connection required. |
| `template.html` | Source template with a `__DATA__` placeholder |
| `parse.py` | Parses `raw.csv` (exported from the published Google Sheet) into clean `data.json` |
| `build.py` | Injects `data.json` into `template.html` and writes `index.html` |
| `raw.csv` | Raw CSV export of the source Google Sheet |
| `data.json` | Cleaned, structured program records |

## How to refresh the data

1. Re-export the Google Sheet as CSV (replace `raw.csv`):
   `.../pub?output=csv&gid=102814479`
2. Run: `python3 parse.py && python3 build.py`
3. Reload `index.html`.

## Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Features

- **KPI cards** — programs, campuses reached, beneficiaries (15,859), students (2,983),
  faculty (715), research staff (27); all recompute when filters are active.
- **Interactive charts** — programs per year, per campus, and donuts for extension type,
  research basis, and proponent. Clicking any chart element toggles a filter (multi-select).
- **Two result views** — card grid or a sortable, sticky-header **table** (click any column
  header to sort; click a row for full details). The choice is remembered on the device.
- **Field / column picker** — a **Columns** dropdown chooses exactly which of the 16 fields
  appear, with **Minimal** (Year · Campus · Program title), **Default** (11 fields) and
  **All 16** presets, plus per-field checkboxes (at least one field always remains).
  The same selection drives the on-screen table, the **Print/PDF** report and the **CSV**
  export, so every output contains only the details you picked. The choice is remembered
  across visits and safely ignored if it becomes invalid.
- **Strong, combinable filters** (AND across filter groups, OR within each):
  - multi-select dropdowns for campus, year, extension type, research basis, proponent,
    each with per-option counts and select-all / clear
  - keyword search where **every word must match**; `"quoted text"` matches an exact phrase
  - document filter (with linked document / no document — 8 of 115 have none)
  - minimum-threshold inputs for beneficiaries and student participants
  - removable active-filter chips and one-click reset
- **Print / PDF report** — `Print / PDF` renders the current filtered list as a
  landscape A4 report **grouped by campus and then by school year**, with group subtotals,
  participation counts, the active-filter summary, a list of the fields included, and full
  document URLs. Only the fields ticked in the Columns picker are shown — e.g. pick
  **Minimal** to print just Year, Campus and Program title. Use the browser's
  "Save as PDF" destination to produce a shareable file.
- **Detail modal** with every Form U8 field and a link to the supporting Google Drive /
  TinyURL document.
- **Export CSV** of the currently filtered results (Excel-friendly UTF-8 BOM).
- Fully responsive; works offline; no external libraries or fonts.
- **Sandbox-safe**: storage access is wrapped in a try/catch with an in-memory
  fallback, so the dashboard fully renders and stays interactive in sandboxed preview
  iframes and `file://` contexts where `localStorage` is blocked (opaque origins).
