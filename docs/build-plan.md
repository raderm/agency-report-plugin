# Build plan: live Agency Portfolio report

## Who sees it
Partners, owners and account leadership only. It shows every client side by side, so it must never be shared
with a client. Limit access to agency leadership. Any account-director version is filtered to their own accounts.

## Metric lineage
Every figure is a sum, or a revenue-weighted average, of the same metric in each client's report, for the same
dates and channel rules.

| Figure | Source report |
|---|---|
| Raised, vs last year | All Donations |
| Projected year-end | Scorecard projection (always the calendar year) |
| New donors | Acquisition |
| Monthly run rate | All Donations, recurring donors |
| Raised per $1 (texts and ads only) | Scorecard |
| Traced to a channel, data-quality issues | Data Quality |

## Client category (Engine 9 Account Type)
Each client has a category used to filter the accounts table, alongside the status filter. The two combine,
and Clear filters resets both. **Scope: the table only.** If the filter ever scopes the whole page (headline
figures, charts, channel mix), the filter UI needs a redesign first, so that is not planned.

- **Source (confirmed):** the account's `type` in the Engine 9 account catalog. The MCP `account` tool's
  `search` command returns it for every account, along with `name` and `parent_ids`; `account` search with
  `prefix: "liftoff"` or `parents: ["liftoff"]` lists them. The report must read it from there, never from a
  name or sector.
- **Values today (Liftoff, 28 sub-accounts):** `candidate` 15, `pac` 6, `nonprofit` 6, `state_party` 1.
  `liftoff` itself is `agency`; exclude it. Show a readable label ("State party"), keep the Engine 9 value
  as the key, and build the filter buttons from the values present, with counts, so a new type appears by
  itself.
- **Accounts with no type:** `liftoff_angie_craig` and `liftoff_harry_dunn` return no name, type or parent,
  so they look unconfigured or orphaned. Do not guess; ask the account owner whether they belong in the
  portfolio. If kept, show "Uncategorized", count them in Reporting coverage ("Account type set in
  Engine 9"), and never drop them from a filter or total.
- **Selected accounts row:** when any filter is on, the table adds a row totaling what is shown (raised,
  share of portfolio, new donors, run rate). Growth uses comparable accounts only and says so. The Portfolio
  row always totals every account.

## Like for like
The headline total includes every account. Growth, projection against last year and new-donor change leave out
accounts with no full prior year; those show "New this cycle". Show both figures in the lede.

## Status rule
- At risk: projected more than 15% behind last year.
- Watch: 5 to 15% behind, or any high-severity data-quality issue.
- New this cycle: no full prior year on record.
- Otherwise on track.

Thresholds should be agency settings that partners can change, and shown in the definitions.

## Missing data
A gap never shows as zero. The coverage table names the accounts behind each gap. An account that fails to
load is listed and left out of the totals, with a count beside the headline figures.

## Steps
1. Connect Engine 9, list the Liftoff sub-accounts with their Engine 9 `type` (see Client category) and confirm the list, including the two accounts with no type, with the account owner.
2. Per account, run the Fundraising Report probes (`cols.sql`, `codes.sql`, `coverage.sql` in the
   fundraising-report skill) and the datasets for the four periods.
3. Build per-account rows (including category) and portfolio calcs as an Artifact Data dashboard, reusing the Fundraising Report's
   coverage and fallback states (including `list-other`).
4. Apply the Frakture look (`assets/frakture-look.json` in the skill).
5. Check totals against each account's own report; run the page check; restrict access.
