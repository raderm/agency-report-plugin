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
1. Connect Engine 9 and list the Liftoff sub-accounts; confirm the list with the account owner.
2. Per account, run the Fundraising Report probes (`cols.sql`, `codes.sql`, `coverage.sql` in the
   fundraising-report skill) and the datasets for the four periods.
3. Build per-account rows and portfolio calcs as an Artifact Data dashboard, reusing the Fundraising Report's
   coverage and fallback states (including `list-other`).
4. Apply the Frakture look (`assets/frakture-look.json` in the skill).
5. Check totals against each account's own report; run the page check; restrict access.
