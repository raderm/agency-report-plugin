# Deploying the Agency Portfolio page

The live report is a Claude **Data** artifact. Its page source and settings live in `page/`; `deploy/build_ops.py`
turns them into `db_write` batches. Claude runs these steps with its artifact tools (there is no CLI).

## What is where

| Path | Becomes |
|---|---|
| `page/index.html`, `page/app.js` | `files/index.html`, `files/app.js` (the page and its script) |
| `page/look.json` | `dash/look` (Frakture palette, fonts, corners) |
| `page/meta.json`, `page/params.json` | `dash/meta` (title), `dash/params` (filter defaults) |
| `page/dataset-snapshot.json` | `datasets/snapshot` (points at the uploaded snapshot file) |
| `data/snapshot.json` | uploaded as an asset; its `/_blob/<id>` URL goes in the dataset |

Page rules the code relies on: `index.html` starts with `<meta name="dash-one-writer">`; data-driven content is
written only by `dash.draw` drawings; projections, status and totals are `dash.calc`s over the snapshot rows.

## First deploy

1. **Snapshot is current.** `data/snapshot.json` is built by `queries/build_snapshot.py` from `data/raw/`.
2. **Create the artifact.** `list_types`, then `create_from_type` with the Data type
   (slug `7dfcf06e-b15d-4b48-aeaf-1d6edfc6d7a0`) and the title "Agency Portfolio". Note the slug it returns.
3. **Upload the snapshot** with `upload_asset` (name `snapshot.json`). Note the returned `/_blob/<id>`.
4. **Build the batches:** `python3 deploy/build_ops.py --blob-url /_blob/<id>`.
5. **Write them,** one `db_write` call per file in `deploy/out/`, in order (batch-1, batch-2, batch-3). Pass each
   file's `ops` array. Keep each call under 64 KB; the script refuses to emit a larger one.
6. **Check.** Read `data/users/<your id>/check` (needs `passed`) and `runs` (should not exist). `db_whoami` gives the id.
7. **Sharing is the owner's call.** The page shows every client side by side and the snapshot file is readable by
   everyone who can open it. Share with agency leadership only, never with a client.

## Update the page code

Edit `page/`, rerun `build_ops.py`. The artifact already holds these documents, so each write needs `ifVersion`:
`db_list` the `files` and `dash` collections, write `{path: version}` to a JSON file, and pass
`--versions that.json`. Then send the batches and re-check.

## Refresh the numbers only

1. Pull any new accounts: run the SQL printed by `queries/portfolio.py` on each, save to `data/raw/<id>.json`.
2. `python3 queries/build_snapshot.py` rewrites `data/snapshot.json` (state is `loaded`, `pending` or `excluded`).
3. `upload_asset` the new file, then `db_write` a `merge` on `datasets/snapshot` with the new `source.url` and
   `updated: {at, by}` (needs `ifVersion`). The page recomputes everything from the rows.
4. Re-check, and compare the headline totals with the previous run.

## Known limits

- The snapshot covers the accounts in `data/raw/`; the rest show as not yet loaded and are in no total.
- Projections, status and growth use only accounts with a full prior year (first gift on or before January 7).
- Planned, not built: account director, owner and next step columns; data-quality issues in status.
