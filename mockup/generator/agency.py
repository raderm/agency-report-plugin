import json, os
from common import *
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output') + os.sep
os.makedirs(OUT, exist_ok=True)

# name, sector, director, ytd, ly_to_date (None = no comparable year), proj factor lo/hi, ly_full factor,
# new donors, new ly, run rate/mo, costed revenue, tracked cost, traced share, high DQ issues, flags
C = [
    ('Client A', 'National political committee', 'M. Ortiz', 6586163, 7120000, 1.167, 1.202, 1.167, 31460, 36900, 127900, 1730000, 606300, .859, 3),
    ('Client B', 'National advocacy org', 'K. Tran', 5840000, 5210000, 1.172, 1.198, 1.171, 24310, 21980, 118400, 1410000, 318000, .912, 0),
    ('Client C', 'U.S. Senate campaign', 'J. Lewis', 4920000, 2100000, 1.31, 1.42, 1.40, 38120, 17400, 46200, 2160000, 1240000, .884, 1),
    ('Client D', 'Environmental nonprofit', 'S. Patel', 3710000, 3880000, 1.214, 1.238, 1.228, 12840, 14210, 96300, 640000, 152000, .937, 0),
    ('Client E', 'Civil rights org', 'K. Tran', 3260000, 2940000, 1.205, 1.226, 1.219, 11920, 10450, 71800, 520000, 131000, .901, 0),
    ('Client F', 'House caucus PAC', 'M. Ortiz', 2850000, 3470000, 1.158, 1.181, 1.172, 9840, 13120, 38600, 910000, 486000, .802, 2),
    ('Client G', 'Health research charity', 'S. Patel', 2410000, 2360000, 1.236, 1.262, 1.251, 7210, 7480, 64100, 310000, 74000, .948, 0),
    ('Client H', 'State party', 'J. Lewis', 2180000, 2660000, 1.149, 1.171, 1.164, 8930, 11870, 29700, 640000, 312000, .768, 2),
    ('Client I', 'Voting rights group', 'K. Tran', 1970000, 1520000, 1.188, 1.214, 1.196, 10410, 7320, 41200, 480000, 166000, .893, 0),
    ('Client J', 'Animal welfare nonprofit', 'S. Patel', 1630000, 1710000, 1.226, 1.249, 1.237, 5120, 5640, 52800, 190000, 61000, .926, 1),
    ('Client K', 'Gubernatorial campaign', 'J. Lewis', 1420000, None, 1.35, 1.48, None, 14260, None, 12400, 880000, 512000, .861, 1),
    ('Client L', 'Local news nonprofit', 'M. Ortiz', 880000, 790000, 1.231, 1.257, 1.244, 3310, 2980, 33600, 90000, 24000, .957, 0),
]
rows = []
for nm, sec, ad, ytd, ly, plo, phi, lyf, nd, ndly, rr, crev, cost, tr, hi in C:
    lo, hi_ = ytd * plo, ytd * phi
    lyfull = ly * lyf if ly else None
    vs = (ytd - ly) / ly if ly else None
    pvs = ((lo + hi_) / 2 - lyfull) / lyfull if ly else None
    if pvs is None: status = 'New this cycle'
    elif pvs < -.15: status = 'At risk'
    elif pvs < -.05 or hi >= 1: status = 'Watch'
    else: status = 'On track'
    rows.append(dict(nm=nm, sec=sec, ad=ad, ytd=ytd, ly=ly, lo=lo, hi=hi_, lyfull=lyfull, vs=vs, pvs=pvs, nd=nd, ndly=ndly, rr=rr,
                     rpd=crev / cost, tr=tr, dq=hi, status=status))
TOT = sum(r['ytd'] for r in rows); TLY = sum(r['ly'] for r in rows if r['ly'])
COMP = [r for r in rows if r['ly']]
LFL_TY = sum(r['ytd'] for r in COMP); LFL_LY = sum(r['ly'] for r in COMP)
PLO = sum(r['lo'] for r in rows); PHI = sum(r['hi'] for r in rows); LYFULL = sum(r['lyfull'] for r in COMP)
PLO_C = sum(r['lo'] for r in COMP); PHI_C = sum(r['hi'] for r in COMP)
NEW = sum(r['nd'] for r in rows); NEWLY = sum(r['ndly'] for r in COMP); NEW_C = sum(r['nd'] for r in COMP)
RR = sum(r['rr'] for r in rows)
CREV = sum(c[11] for c in C); CCOST = sum(c[12] for c in C)
TRACED = sum(r['ytd'] * r['tr'] for r in rows) / TOT
GROW = sum(1 for r in COMP if r['vs'] > 0)
cnt = {s: sum(1 for r in rows if r['status'] == s) for s in ['On track', 'Watch', 'At risk', 'New this cycle']}
top3 = sum(sorted([r['ytd'] for r in rows], reverse=True)[:3]) / TOT
STC = {'On track': '#2E7D4A', 'Watch': '#9A5B00', 'At risk': '#B3261E', 'New this cycle': MUT}
SHAPE = {'On track': '●', 'Watch': '■', 'At risk': '▲', 'New this cycle': '◆'}

def pc(v): return '—' if v is None else ('+' if v >= 0 else '−') + f'{abs(v) * 100:.0f}%'
jsrows = []
for r in rows:
    jsrows.append({'st': r['status'], 'k_ytd': r['ytd'], 'k_vs': r['vs'], 'k_pvs': r['pvs'],
                   'k_nd': r['nd'], 'k_rpd': r['rpd'], 'k_tr': r['tr'],
                   'c0': r['nm'], 'c1': r['sec'], 'c2': r['ad'], 'c3': mk(r['ytd']), 'c4': pc(r['vs']) if r['vs'] is not None else 'No prior year', 'c5': pct(r['ytd'] / TOT),
                   'c6': f"{mk(r['lo'])}–{mk(r['hi'])}", 'c7': pc(r['pvs']) if r['pvs'] is not None else '—', 'c8': n(r['nd']), 'c9': mk(r['rr']), 'c10': m2(r['rpd']),
                   'c11': pct(r['tr'], 0), 'c12': SHAPE[r['status']] + ' ' + r['status'],
                   'vc': ('#2E7D4A' if (r['vs'] or 0) >= 0 else '#B3261E') if r['vs'] is not None else MUT,
                   'pc': ('#2E7D4A' if (r['pvs'] or 0) >= -.05 else ('#9A5B00' if r['pvs'] >= -.15 else '#B3261E')) if r['pvs'] is not None else MUT,
                   'sc': STC[r['status']]})
COLS = {'ytd': 'raised', 'vs': 'change on last year', 'pvs': 'projected year-end against last year', 'nd': 'new donors', 'rpd': 'raised per $1 of tracked cost', 'tr': 'revenue traced to a channel'}

# ---------- scatter: where each account stands ----------
def scatter():
    X0, X1, Y0, Y1 = 70, 980, 30, 330
    xmax = 7.0; ymin, ymax = -.30, .45
    x = lambda v: X0 + (X1 - X0) * v / xmax
    y = lambda v: Y1 - (Y1 - Y0) * (v - ymin) / (ymax - ymin)
    out = ''
    for t in [-.3, -.15, 0, .15, .3, .45]:
        out += f'<line x1="{X0}" x2="{X1}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID if t else INK}"{" stroke-width=\"1.5\"" if not t else ""}/><text x="{X0 - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{pc(t) if t else "0%"}</text>'
    out += f'<line x1="{X0}" x2="{X1}" y1="{y(-.15):.1f}" y2="{y(-.15):.1f}" stroke="#B3261E" stroke-dasharray="6 4" stroke-width="1.5"/><text x="{X1}" y="{y(-.15) + 16:.1f}" text-anchor="end" style="fill:#B3261E;font-weight:700">At-risk line: 15% behind last year</text>'
    out += f'<line x1="{X0}" x2="{X1}" y1="{y(-.05):.1f}" y2="{y(-.05):.1f}" stroke="#9A5B00" stroke-dasharray="2 4" stroke-width="1.5"/><text x="{X1}" y="{y(-.05) + 16:.1f}" text-anchor="end" style="fill:#9A5B00;font-weight:700">Watch line: 5% behind</text>'
    for v in range(0, 8):
        out += f'<text x="{x(v):.1f}" y="{Y1 + 20}" text-anchor="middle">${v}M</text>'
    out += f'<text x="{(X0 + X1) / 2}" y="{Y1 + 40}" text-anchor="middle" style="fill:{INK}">Raised so far this year</text>'
    out += f'<text x="16" y="{(Y0 + Y1) / 2}" text-anchor="middle" transform="rotate(-90 16 {(Y0 + Y1) / 2})" style="fill:{INK}">Projected year-end vs last year</text>'
    for r in rows:
        if r['pvs'] is None: continue
        cx, cy = x(r['ytd'] / 1e6), y(max(ymin, min(ymax, r['pvs'])))
        col = STC[r['status']]
        if r['status'] == 'On track': mark = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{col}"/>'
        elif r['status'] == 'Watch': mark = f'<rect x="{cx - 7:.1f}" y="{cy - 7:.1f}" width="14" height="14" fill="{col}"/>'
        else: mark = f'<polygon points="{cx:.1f},{cy - 9:.1f} {cx + 9:.1f},{cy + 7:.1f} {cx - 9:.1f},{cy + 7:.1f}" fill="{col}"/>'
        off = r['pvs'] > ymax
        out += mark + f'<text x="{cx + 12:.1f}" y="{cy + (14 if off else 4):.1f}" style="fill:{INK};font-weight:700">{r["nm"].replace("Client ", "")}{" ↑ " + pc(r["pvs"]) + ", off scale" if off else ""}</text>'
    lab = 'Each comparable account placed by money raised this year (across) and projected year-end against last year (up and down). ' + '; '.join(
        f'{r["nm"]}: {mk(r["ytd"])}, {pc(r["pvs"])}, {r["status"].lower()}' for r in rows if r['pvs'] is not None) + '. Client K has no prior year and is left off.'
    return f'<svg viewBox="0 0 1000 380" width="100%" role="img" aria-label="{H.escape(lab)}" style="{SVGSTYLE}">{out}</svg>'

# ---------- monthly portfolio ----------
ty_m = [2.31, 2.52, 2.94, 2.88, 2.79, 3.46, 2.71, 3.18, 3.62, 4.58, 6.67]
ly_m = [2.18, 2.37, 2.71, 2.62, 2.66, 3.14, 2.55, 2.86, 3.31, 4.21, 5.46]
sc = TOT / 1e6 / sum(ty_m); ty_m = [v * sc for v in ty_m]
sl = TLY / 1e6 / sum(ly_m); ly_m = [v * sl for v in ly_m]
mchart = bars('Portfolio revenue by month this year, all accounts, with a tick for the same month last year. This year ran ahead of last year in every month; the gap widened from September.',
              MONS[:11], [('This year', TEAL, ty_m, None)], 7.5, [0, 2.5, 5, 7.5], lambda v: f'${v:.1f}M' if v else '$0', ly=ly_m, top=[f'${v:.1f}M' for v in ty_m])

ch = [('Email', 15.12, 14.48, 7, 'Client B'), ('Texts', 6.41, 5.12, 10, 'Client C'), ('Paid ads', 5.38, 4.31, 8, 'Client C'),
      ('Rented lists', 2.04, 1.88, 5, 'Client A'), ('Website and organic', 3.11, 2.96, 6, 'Client D'), ('Direct mail', 1.06, 1.31, 2, 'Client G')]
rest = TOT / 1e6 - sum(c[1] for c in ch); restly = TLY / 1e6 - sum(c[2] for c in ch)
ch.append(('Unattributed', rest, restly, 4, '—'))
chrows = [[a, f'${b:.2f}M', pct(b / (TOT / 1e6)), chg(b, cly), f'{u} of 11', best] for a, b, cly, u, best in ch]
chrows.append(['__tot__', 'All channels', mk(TOT), '100%', chg(TOT, TLY), f'{GROW} of 11', '—'])

att = [r for r in rows if r['status'] in ('At risk', 'Watch')]
reasons = {'Client A': ('Revenue 7% behind last year; 3 high data-quality issues, including $715K with no source code', 'Fix refcodes on top ActBlue pages; review year-end email calendar', 'Dec 1'),
           'Client F': ('Projected 18% behind last year; ads return $0.79 per $1', 'Cut lowest-return Meta campaigns; add a December match', 'Nov 26'),
           'Client H': ('Projected 18% behind; new donors down 25%; uncoded revenue 23%', 'Rebuild acquisition plan with state-party partners', 'Dec 3'),
           'Client C': ('Growing fast but cost per new donor up 31%; 1 high data-quality issue', 'Agree a cost-per-donor ceiling for the runoff', 'Nov 30'),
           'Client J': ('1 high data-quality issue: rented-list costs not entered', 'Enter rental costs so payback can be reported', 'Dec 5'),
           'Client K': ('First cycle on record; 1 high data-quality issue', 'Confirm prior-cycle data import', 'Dec 2')}
attrows = []
for r in sorted(att, key=lambda r: (0 if r['status'] == 'At risk' else 1, -r['ytd'])):
    w, nx, due = reasons.get(r['nm'], ('', '', ''))
    attrows.append([f'<b>{r["nm"]}</b>', f'<b style="color:{STC[r["status"]]}">{SHAPE[r["status"]]} {r["status"]}</b>', w, nx, r['ad'], due])
k = [r for r in rows if r['status'] == 'New this cycle'][0]
w, nx, due = reasons['Client K']
attrows.append([f'<b>{k["nm"]}</b>', f'<b style="color:{MUT}">{SHAPE[k["status"]]} {k["status"]}</b>', w, nx, k['ad'], due])

cov = [['Cost tracked for texts and ads', '12 of 12', '—', 'Return per $1 covers texts and ads only, at every account'],
       ['Cost tracked for rented lists', '3 of 5 that rent', 'Clients A, J', 'Rented-list payback missing at 2 accounts'],
       ['Email list table connected', '11 of 12', 'Client L', 'List growth blank for 1 account'],
       ['A full prior year on record', '11 of 12', 'Client K', 'Left out of year-on-year totals'],
       ['Revenue traced to a channel, 85% or more', '10 of 12', 'Clients F, H', 'Channel mix less certain at 2 accounts'],
       [f'High-severity data-quality issues', f'{sum(r["dq"] for r in rows)} issues at {sum(1 for r in rows if r["dq"])} accounts', 'Clients A, C, F, H, J, K', 'From each account\'s weekly Data Quality snapshot']]

PP = '{{perPhrase}}'
FILTERS = [('all', 'All', len(rows)), ('risk', 'At risk', cnt['At risk']), ('watch', 'Watch', cnt['Watch']), ('ok', 'On track', cnt['On track']), ('new', 'New this cycle', cnt['New this cycle'])]
FMAP = {'risk': 'At risk', 'watch': 'Watch', 'ok': 'On track', 'new': 'New this cycle'}

head = [('Client', None), ('Sector', None), ('Account director', None), ('Raised', 'ytd'), ('vs last year', 'vs'), ('Share of portfolio', None),
        ('Projected year-end', None), ('Projected vs last year', 'pvs'), ('New donors', 'nd'), ('Monthly run rate', None), ('Raised per $1 tracked cost', 'rpd'),
        ('Traced to a channel', 'tr'), ('Status', None)]
hh = ''
for i, (lab, ckey) in enumerate(head):
    st = ' style="text-align:left"' if i in (0, 1, 2, 12) else ''
    if ckey:
        hh += f'<th scope="col" aria-sort="{{{{as_{ckey}}}}}"{st}><button type="button" class="sb" onClick="{{{{sort_{ckey}}}}}">{lab} <span aria-hidden="true">{{{{ar_{ckey}}}}}</span></button></th>'
    else:
        hh += f'<th scope="col"{st}>{lab}</th>'
tds = ''
for i in range(13):
    if i == 0: tds += '<td><b>{{r.c0}}</b></td>'
    elif i in (1, 2): tds += f'<td class="l">{{{{r.c{i}}}}}</td>'
    elif i == 4: tds += '<td style="color:{{r.vc}};font-weight:700">{{r.c4}}</td>'
    elif i == 7: tds += '<td style="color:{{r.pc}};font-weight:700">{{r.c7}}</td>'
    elif i == 12: tds += '<td style="text-align:left;color:{{r.sc}};font-weight:700">{{r.c12}}</td>'
    else: tds += f'<td>{{{{r.c{i}}}}}</td>'
filt = ('<div style="display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:16px;font-size:13px;color:#3F4945"><span id="flt-lab">Show</span>'
        '<div role="group" aria-labelledby="flt-lab" style="display:inline-flex;flex-wrap:wrap;border:1px solid #212529">'
        '<sc-for list="{{filters}}" as="f" hint-placeholder-count="5"><button type="button" aria-pressed="{{f.pressed}}" onClick="{{f.pick}}" '
        'style="font-family:Outfit,sans-serif;font-weight:700;font-size:12px;letter-spacing:.06em;text-transform:uppercase;border:0;border-left:{{f.bl}};padding:0 14px;min-height:44px;cursor:pointer;background:{{f.bg}};color:{{f.fg}}">{{f.label}}</button></sc-for></div>'
        '<span>{{shownTxt}}</span></div>')
acct_table = (filt + '<p aria-live="polite" class="sr">{{tblMsg}}</p>'
              '<div role="region" aria-label="Accounts in the portfolio (scrolls sideways)" tabindex="0" class="scr"><table class="t" style="min-width:1380px">'
              '<caption class="sr">Accounts in the portfolio. Column headings with arrows sort the table; the Show buttons filter it by status.</caption>'
              f'<thead><tr>{hh}</tr></thead><tbody><sc-for list="{{{{acctRows}}}}" as="r" hint-placeholder-count="12"><tr>{tds}</tr></sc-for>'
              f'<tr class="tot"><td>Portfolio</td><td class="l">12 accounts</td><td class="l">4 directors</td><td>{mk(TOT)}</td><td>{pc((TOT - TLY) / TLY)}</td><td>100%</td>'
              f'<td>{mk(PLO)}–{mk(PHI)}</td><td>{pc(((PLO_C + PHI_C) / 2 - LYFULL) / LYFULL)}</td><td>{n(NEW)}</td><td>{mk(RR)}</td><td>{m2(CREV / CCOST)}</td><td>{pct(TRACED, 0)}</td><td style="text-align:left">{cnt["At risk"]} at risk · {cnt["Watch"]} watch</td></tr>'
              '</tbody></table></div>')

js = f'''
  extraVals(s) {{
    const ROWS = {json.dumps(jsrows)};
    const COLS = {json.dumps(COLS)};
    const FILTERS = {json.dumps(FILTERS)};
    const FMAP = {json.dumps(FMAP)};
    const flt = s.flt || 'all', sk = s.sk || 'ytd', dir = s.sd || 'descending';
    let rows = ROWS.filter((r) => flt === 'all' || r.st === FMAP[flt]);
    rows = rows.slice().sort((a, b) => {{ const x = a['k_' + sk], y = b['k_' + sk]; if (x == null) return 1; if (y == null) return -1; return dir === 'descending' ? y - x : x - y; }});
    const out = {{ acctRows: rows, tblMsg: s.tblMsg || '', shownTxt: 'Showing ' + rows.length + ' of ' + ROWS.length + ' accounts' }};
    out.filters = FILTERS.map((f, i) => ({{
      label: f[1] + ' (' + f[2] + ')', pressed: f[0] === flt ? 'true' : 'false',
      bg: f[0] === flt ? '{INK}' : '#ffffff', fg: f[0] === flt ? '#ffffff' : '{INK}', bl: i ? '1px solid {INK}' : '0',
      pick: () => this.setState({{ flt: f[0], tblMsg: 'Showing ' + f[2] + (f[0] === 'all' ? ' accounts.' : ' ' + f[1].toLowerCase() + ' accounts.') }})
    }}));
    Object.keys(COLS).forEach((c) => {{
      out['as_' + c] = c === sk ? dir : 'none';
      out['ar_' + c] = c === sk ? (dir === 'descending' ? '▼' : '▲') : '↕';
      out['sort_' + c] = () => {{
        const nd = c === sk && dir === 'descending' ? 'ascending' : 'descending';
        this.setState({{ sk: c, sd: nd, tblMsg: 'Sorted by ' + COLS[c] + ', ' + (nd === 'descending' ? 'highest' : 'lowest') + ' first.' }});
      }};
    }});
    return out;
  }}'''

body = (f'<header><div class="lab">[AGENCY NAME] · Portfolio · {{{{perLabel}}}} · Partners and account leadership · Sample data</div>'
        f'<h1 style="font-family:Outfit,sans-serif;font-weight:500;font-size:36px;line-height:1.15;margin:8px 0 0">Agency Portfolio</h1>'
        f'<p style="font-size:16px;line-height:1.55;margin:10px 0 0;max-width:82ch">Client accounts raised <b>{mk(TOT)}</b> {PP}, <b>{pc((TOT - TLY) / TLY)}</b> on the same dates last year '
        f'(<b>{pc((LFL_TY - LFL_LY) / LFL_LY)}</b> like for like, leaving out the one account with no prior year). <b>{GROW} of 11</b> comparable accounts are growing. '
        f'<b>{cnt["At risk"]}</b> are at risk of finishing more than 15% behind last year and <b>{cnt["Watch"]}</b> need watching.</p>'
        f'<p style="font-size:13px;color:{MUT};margin:8px 0 0;max-width:82ch">Every figure is the sum, or a weighted average, of the same metric in each client’s Fundraising Report, for the same dates. Accounts sit at different points in the election cycle, so compare each one with its own last year before comparing accounts with each other.</p></header>')
body += tiles([('Raised, all accounts', mk(TOT), f'Same dates last year {mk(TLY)} <span class="up">▲ {(TOT - TLY) / TLY * 100:.0f}%</span> · like for like ▲ {(LFL_TY - LFL_LY) / LFL_LY * 100:.0f}%'),
               ('Projected year-end', f'{mk(PLO)}–{mk(PHI)}', f'Last year, full: {mk(LYFULL)} (11 comparable accounts)'),
               ('Accounts growing', f'{GROW} of 11', f'Revenue up on the same dates last year · {cnt["At risk"]} at risk, {cnt["Watch"]} watch'),
               ('New donors', n(NEW), f'Comparable accounts {n(NEW_C)} vs {n(NEWLY)} last year <span class="dn">▼ {abs((NEW_C - NEWLY) / NEWLY) * 100:.0f}%</span>'),
               ('Monthly recurring run rate', mk(RR), 'Latest payment of each active monthly donor, all accounts'),
               ('Raised per $1 of tracked cost', m2(CREV / CCOST), 'Texts and paid ads, all accounts · tracked cost ' + mk(CCOST)),
               ('Revenue traced to a channel', pct(TRACED, 1), 'Weighted by revenue · 2 accounts under 85%'),
               ('Top 3 accounts’ share', pct(top3, 0), 'Clients A, B and C · concentration risk')], 230)
body += card('Where each account stands', 'Across: money raised so far this year. Up and down: projected year-end against that account’s own last year. Status uses both the shape and the word: ● on track, ■ watch, ▲ at risk. Accounts on or below the dashed lines are flagged.',
             legend(key(f'width:12px;height:12px;border-radius:50%;background:{STC["On track"]}', 'On track'), key(sw(STC['Watch']), 'Watch (5–15% behind, or a high data issue)'),
                    key(f'width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-bottom:12px solid {STC["At risk"]}', 'At risk (more than 15% behind)'))
             + f'<div style="margin-top:8px">{scatter()}</div>' + '<p class="note" style="margin-top:6px">Point at, or tab to, an account for its figures. Arrow keys move between accounts in order of revenue; Escape closes the details. In the live dashboard, selecting an account opens its Fundraising Report.</p>'
             + alt(['Client', 'Raised', 'Projected vs last year', 'Status'], [[r['nm'], mk(r['ytd']), pc(r['pvs']), r['status']] for r in rows]))
body += card('Accounts', 'One row per client account. Status: on track, watch (projected 5–15% behind last year, or a high-severity data-quality issue), at risk (projected more than 15% behind), or new this cycle (no prior year to compare). Select a column heading with an arrow to sort; select it again to reverse.', acct_table
             + caption(f'Client C’s Senate race explains the portfolio’s growth: without it, comparable accounts are {pc(((LFL_TY - 4920000) - (LFL_LY - 2100000)) / (LFL_LY - 2100000))} on last year.'))
body += card('Needs attention', 'Accounts at risk or on watch, with what changed, the agreed next step and who owns it. Next steps and dates are entered by account directors; the rest comes from each account’s report.',
             table('Accounts that need attention', ['Client', 'Status', 'What changed', 'Next step', 'Owner', 'Review by'], attrows, 1000, left=(1, 2, 3, 4)))
body += ('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:24px">'
         + card('Portfolio revenue by month', 'All accounts added together. The dark tick is the same month last year, counted only up to today’s date. This chart always covers the whole year to date.',
                legend(key(sw(TEAL), 'This year'), key(f'width:18px;height:0;border-top:3px solid {INK}', 'Same month last year'))
                + f'<div style="margin-top:8px">{mchart}</div>' + chart_focus_hint()
                + alt(['Month', 'This year', 'Last year'], [[MONS[i], f'${ty_m[i]:.2f}M', f'${ly_m[i]:.2f}M'] for i in range(11)]))
         + card('Channel mix across the portfolio', 'Revenue by channel, all accounts, by the Fundraising Report’s channel rules. “Accounts up” counts comparable accounts where that channel grew.',
                table('Channel mix across the portfolio', ['Channel', 'Raised', 'Share', 'vs last year', 'Accounts up', 'Biggest account'], chrows, 600, left=(5,)))
         + '</div>')
body += card('Reporting coverage', 'How complete the data is behind these numbers. Gaps here don’t mean an account is doing badly; they mean a figure for it is missing or less certain.',
             table('Reporting coverage across accounts', ['Check', 'Accounts', 'Gaps at', 'What it affects'], cov, 900, left=(2, 3))
             + f'<p style="{COVN}"><b>Shown only when it applies:</b> an account that fails to load, or whose report has no data for the period, is listed here by name and left out of the totals above, with a count beside the headline figures.</p>')
body += gaps('Reading the portfolio', [
    ('Each account is compared with its own last year first.', 'Campaigns peak in election years and committees between them, so raw growth rates across accounts aren’t like for like.'),
    ('Like for like leaves out accounts with no prior year.', 'Client K started this cycle, so it counts in totals but not in growth rates, projections against last year or new-donor change.'),
    ('Raised per $1 covers texts and ads only,', 'the costs engine9 tracks at every account. Rented lists, agency fees and staff time aren’t in it.'),
    ('Projections are pacing estimates,', 'each account’s Scorecard projection added up, not a forecast.')])
body += defs(['<b>Audience.</b> This page is for partners, owners and account leadership. It shows account-level results only; message-level detail stays in each client’s Fundraising Report.',
              '<b>Where each figure comes from.</b> Raised and vs last year: All Donations. Projected year-end: the Scorecard projection. New donors: Acquisition. Monthly run rate: All Donations, recurring donors. Raised per $1: Scorecard, texts and ads. Traced to a channel and data-quality issues: Data Quality.',
              '<b>Period.</b> The picker sets the period for every figure except the projection, which always covers the calendar year. Each compares with the same dates a year earlier.',
              '<b>Status.</b> At risk: projected more than 15% behind last year. Watch: 5–15% behind, or one or more high-severity data-quality issues. New this cycle: no full prior year on record.'])

# ---------- shell (no report tabs) ----------
per = ('<sc-for list="{{periods}}" as="p" hint-placeholder-count="4"><button type="button" aria-pressed="{{p.pressed}}" onClick="{{p.pick}}" '
       'style="font-family:Outfit,sans-serif;font-weight:700;font-size:12px;letter-spacing:.06em;text-transform:uppercase;border:0;'
       'border-left:{{p.bl}};padding:0 14px;min-height:44px;cursor:pointer;background:{{p.bg}};color:{{p.fg}}">{{p.label}}</button></sc-for>')
doc = shell('Main.dc.html', 'Agency Portfolio', None, body, js, h=4600)
# replace the report tab bar and brand with the portfolio header
import re
doc = re.sub(r'<nav aria-label="Report pages".*?</nav>', '', doc, flags=re.S)
doc = doc.replace('Fundraising Report</span></div>', 'Agency Portfolio</span></div>')
doc = doc.replace('The period picker changes the highlighted period and labels only.', 'The period picker changes the highlighted period and labels only. Client names are placeholders.')
open(OUT + 'Main.dc.html', 'w').write(doc)
print([round(a-b,2) for a,b in zip(ty_m,ly_m)]); print(len(doc), mk(TOT), mk(TLY), cnt, GROW, mk(PLO), mk(PHI), mk(LYFULL), pc(((PLO_C + PHI_C) / 2 - LYFULL) / LYFULL), m2(CREV / CCOST), pct(TRACED), pct(top3))
for r in rows: print(r['nm'], mk(r['ytd']), pc(r['vs']), pc(r['pvs']), r['status'])
