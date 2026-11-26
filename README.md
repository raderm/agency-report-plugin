# Agency Portfolio report

A one-page dashboard for partners, owners and account leadership. It shows how each client
account performs as part of the agency portfolio. Every figure is derived from the same metric in that
client's [Fundraising Report](https://github.com/raderm/fundraising-report-plugin), so the two always agree.

**Status: draft.** This repo holds the design mockup (sample data, placeholder client names). The live report is not built yet. See `docs/build-plan.md`.

## What's here

| Path | What it is |
|---|---|
| `mockup/output/Main.dc.html`, `canvas.json` | The mockup as published to the Design canvas (one artboard, nine annotation notes) |
| `mockup/generator/agency.py`, `common.py` | Python that generates the mockup. `cd mockup/generator && python3 agency.py` rewrites `mockup/output/Main.dc.html` |
| `docs/build-plan.md` | Metric lineage, status rules and the plan for the live report |

Design canvas: https://claude.ai/artifact/BhrzHnqk1MpYUoHcLFh5yx

## The page

Header with period picker, headline KPIs (raised, vs last year, projected year-end, new donors, monthly run
rate, raised per $1), account status chart, accounts table you can sort and filter by status and by client category (Engine 9 account type), with a fixed portfolio
row and a row totaling the filtered accounts, "Needs attention" list, coverage and missing-data table, definitions. Accessibility is part of the
design: status is shape plus word plus color, filters (status and category) are `aria-pressed` toggles with a visible and announced
count, sortable headings are buttons with `aria-sort`, charts have keyboard stepping and a table alternative.

## Layout

- `page/`: source of the live page (index.html, app.js) and its settings, and `deploy/`: how to publish it. Start with `deploy/DEPLOY.md`.
- `queries/`: per-account SQL and the snapshot builder. `data/`: raw results and `snapshot.json`.
- `mockup/`: the design mockup and its generator.
