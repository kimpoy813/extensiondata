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

## Deploy on Render

This repo is a **static site** — there is no server and no runtime dependencies. Render
just needs to be told where the finished page is.

`render.yaml` in the repo root is a ready-made Blueprint that does this. If your service
was created by hand in the dashboard instead, open **Settings → Build & Deploy** and set:

| Setting | Value |
|---|---|
| **Runtime** | Static Site |
| **Build Command** | `mkdir -p build && cp index.html build/index.html` |
| **Publish Directory** | `build` |

Then **Manual Deploy → Deploy latest commit**.

> **Why the original deploy failed.** Render reported
> `Empty build command; skipping build` and `Publish directory build does not exist!`.
> The service was pointed at a `build/` folder, but nothing in the repo ever created
> one — the finished dashboard is `index.html` in the repository root. Publishing the
> root (`.`) also works, but it would also expose `raw.csv`, `parse.py`, etc.

If you would rather have Render regenerate the page from `data.json` + `template.html`
on every deploy, use this build command instead (it needs Python in the build image):

```bash
python3 build.py --out-dir build
```

Locally, `python3 build.py --out-dir build` produces the same `build/index.html`, so
you can preview exactly what will be deployed with:

```bash
python3 -m http.server 8080 --directory build
```

## Features

- **KPI cards** — programs, campuses reached, beneficiaries (15,859), students (2,983),
  faculty (715), research staff (27); all recompute when filters are active.
- **Interactive charts that follow your filters** — programs per year, per campus, and
  donuts for extension type, research basis, and proponent. Clicking any chart element
  toggles a filter (multi-select). Every chart is cross-filtered: it counts the rows that
  pass **all the other** filters, so selecting a campus immediately redraws the year,
  extension-type, research-basis and proponent charts (while the campus chart keeps
  listing every campus so you can switch or add another). The option counts in each
  dropdown behave the same way, and options that would return nothing are dimmed and
  disabled.
- **Two result views** — card grid or a sortable, sticky-header **table** (click any column
  header to sort; click a row for full details). Title sorting uses the visible title with
  the year prefix stripped, and compares case-insensitively and numerically. The choice is remembered on the device.
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
- **Print / PDF report** — `Print / PDF` renders the current filtered list as a clean,
  compact landscape A4 document: a one-block masthead, four summary figures
  (programs · campuses · participants · beneficiaries), the active filters only when set,
  and **one table per campus** sorted newest-first. The campus table header repeats
  automatically if it runs onto another page, and long prose fields are clipped with an
  ellipsis so the report stays readable instead of running to dozens of pages.
  **Document URLs are never printed** — a ✓ means a document is linked (open the dashboard
  or the CSV for the actual link). Only the fields ticked in the Columns picker appear —
  pick **Minimal** to print just Year, Campus and Program title. Use the browser's
  "Save as PDF" destination to produce the file.
- **Charts print too** — the visual summary is rebuilt for paper as **pure SVG**
  (programs per year, type of extension, research basis, led by, programs by campus),
  because browsers do not print CSS backgrounds and the on-screen bars would come out
  blank. Every figure is computed from the **filtered** list, so the charts and the tables
  always agree, and each value is labelled so they still read in black and white.
- **Page space is budgeted** — landscape A4 with 10mm margins gives ~190mm of usable
  height, and the masthead + summary + charts are held to ~107mm, so the charts and the
  first ~12 table rows share page 1 (~93% of it used). The year and campus charts sit side
  by side at half width, where 500 SVG units still render text at 7.6pt or larger. There
  are no forced page breaks.
- **Detail modal** with every Form U8 field and a link to the supporting Google Drive /
  TinyURL document.
- **Export CSV** of the currently filtered results (Excel-friendly UTF-8 BOM).
- Fully responsive; works offline; no external libraries or fonts.
- **Sandbox-safe**: storage access is wrapped in a try/catch with an in-memory
  fallback, so the dashboard fully renders and stays interactive in sandboxed preview
  iframes and `file://` contexts where `localStorage` is blocked (opaque origins).
