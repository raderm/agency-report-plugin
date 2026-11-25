import json, html as H

TEAL = '#007A99'; INK = '#212529'; MUT = '#3F4945'; LINE = '#D9DEDC'; GRID = '#E6EAE8'
TINT = '#F4F8F7'; PURP = '#9B2FC9'; CYAN = '#01CCFF'; ORNG = '#F89800'; ORNG_D = '#8A5200'
GRN = '#3E8E58'; GREY = '#C9D1CE'
MONS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

TABS = [('Scorecard', 'Report.dc.html'), ('All Donations', 'Donations.dc.html'), ('Email', 'Email.dc.html'),
        ('SMS', 'SMS.dc.html'), ('Advertising', 'Ads.dc.html'), ('Acquisition', 'Acquisition.dc.html'),
        ('Data Quality', 'Quality.dc.html')]

# ---------- formatting ----------
def m(v): return '${:,.0f}'.format(v)
def m2(v): return '${:,.2f}'.format(v)
def mk(v):
    if abs(v) >= 1e6: return '${:.2f}M'.format(v / 1e6)
    if abs(v) >= 1e3: return '${:,.0f}K'.format(v / 1e3)
    return '${:,.0f}'.format(v)
def n(v): return '{:,.0f}'.format(v)
def pct(v, d=1): return ('{:.%df}%%' % d).format(v * 100)
def chg(t, l, lower_better=False):
    if not l: return '<span class="mu">—</span>'
    c = (t - l) / l
    good = (c >= 0) != lower_better
    return f'<span class="{"up" if good else "dn"}">{"▲" if c >= 0 else "▼"} {abs(c) * 100:.0f}%</span>'
MU = '<span class="mu">—</span>'
def nt(txt='Not tracked'): return f'<span class="mu">{txt}</span>'

# ---------- building blocks ----------
H2 = 'font-family:Outfit,sans-serif;font-weight:500;font-size:22px;margin:0;color:#212529'
SUB = f'font-size:14px;line-height:1.5;color:{MUT};margin:6px 0 0;max-width:82ch'
CARD = f'background:#fff;border:1px solid {LINE};padding:24px;min-width:0'
CALL = f'margin:16px 0 0;padding:14px 16px;border-left:3px solid {ORNG};background:{TINT};font-size:14px;line-height:1.55;max-width:92ch'
COVN = f'margin:16px 0 0;padding:12px 16px;border:1px dashed {MUT};background:#fff;font-size:14px;line-height:1.5;max-width:92ch'
LEG = f'display:flex;flex-wrap:wrap;gap:20px;font-size:13px;color:{MUT};margin-top:12px'

def tile(label, val, note, acc=TEAL):
    return (f'<div class="tile" style="border-top:3px solid {acc}"><div class="lab">{label}</div>'
            f'<div class="val">{val}</div><div class="note">{note}</div></div>')
def tiles(items, minw=210):
    return (f'<section aria-label="Headline numbers" style="display:grid;grid-template-columns:repeat(auto-fit,minmax({minw}px,1fr));gap:12px">'
            + ''.join(tile(*i) for i in items) + '</section>')
def mini(label, val, note):
    return (f'<div style="min-width:0"><div class="lab">{label}</div><div style="font-family:Outfit,sans-serif;font-weight:500;'
            f'font-size:24px;margin-top:4px;font-variant-numeric:tabular-nums">{val}</div><div class="note">{note}</div></div>')
def minis(items):
    return (f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-top:16px;'
            f'padding-top:16px;border-top:1px solid {GRID}">' + ''.join(mini(*i) for i in items) + '</div>')
def key(style, label):
    return f'<span style="display:inline-flex;align-items:center;gap:6px"><i aria-hidden="true" style="display:inline-block;{style}"></i>{label}</span>'
def sw(color, stroke=None):
    return f'width:12px;height:12px;background:{color};box-sizing:border-box' + (f';border:1px solid {stroke}' if stroke else '')
def legend(*keys): return f'<div style="{LEG}">' + ''.join(keys) + '</div>'

def table(label, head, rows, minw=860, left=(), cls=''):
    """head: list of str; rows: list of lists (html strings) or raw '<tr>' strings."""
    hh = ''.join(f'<th scope="col"{" style=\"text-align:left\"" if i in left else ""}>{h}</th>' for i, h in enumerate(head))
    body = ''
    for r in rows:
        if isinstance(r, str): body += r; continue
        tot = r and r[0] == '__tot__'
        if tot: r = r[1:]
        tds = ''.join(f'<td{" class=\"l\"" if i in left else ""}>{c}</td>' for i, c in enumerate(r))
        body += f'<tr{" class=\"tot\"" if tot else ""}>{tds}</tr>'
    return (f'<div role="region" aria-label="{H.escape(label)} (scrolls sideways)" tabindex="0" class="scr">'
            f'<table class="t{cls}" style="min-width:{minw}px"><caption class="sr">{H.escape(label)}</caption>'
            f'<thead><tr>{hh}</tr></thead><tbody>{body}</tbody></table></div>')

def alt(head, rows, title='View chart data as a table'):
    hh = ''.join(f'<th scope="col">{h}</th>' for h in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return (f'<details style="margin-top:8px;font-size:13px;color:{MUT}"><summary class="sum">{title}</summary>'
            f'<div class="scr" tabindex="0" role="region" aria-label="Chart data"><table class="t" style="min-width:480px"><thead><tr>{hh}</tr></thead><tbody>{body}</tbody></table></div></details>')

def card(title, sub, inner, hid=None):
    idattr = f' aria-labelledby="{hid}"' if hid else ''
    h = f'<h2 id="{hid}" style="{H2}">{title}</h2>' if hid else f'<h2 style="{H2}">{title}</h2>'
    return f'<section style="{CARD}"{idattr}>{h}' + (f'<p style="{SUB}">{sub}</p>' if sub else '') + inner + '</section>'
def h3(t): return f'<h3 style="font-size:15px;font-weight:700;margin:24px 0 0">{t}</h3>'
def caption(t): return f'<p style="font-size:14px;margin:12px 0 0;max-width:82ch">{t}</p>'
def callout(title, body): return f'<p style="{CALL}"><b>{title}</b> {body}</p>'
def gaps(title, items):
    lis = ''.join(f'<li><b>{a}</b> {b}</li>' for a, b in items)
    return (f'<section aria-label="{H.escape(title)}" style="padding:18px 20px;border-left:3px solid {ORNG};background:{TINT};font-size:14px;line-height:1.55">'
            f'<h2 style="font-family:Outfit,sans-serif;font-weight:500;font-size:18px;margin:0">{title}</h2>'
            f'<ul style="margin:10px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px;max-width:100ch">{lis}</ul></section>')
def defs(paras):
    ps = ''.join(f'<p style="max-width:88ch;margin:6px 0">{p}</p>' for p in paras)
    return (f'<details style="font-size:14px;color:{MUT};line-height:1.55"><summary class="sum" style="color:{INK};font-weight:700;font-size:14px">'
            f'How to read this page</summary>{ps}</details>')
def summary(paras, bullets):
    lis = ''.join(f'<li>{b}</li>' for b in bullets)
    return (f'<section aria-labelledby="sum-h" style="{CARD};border-left:3px solid {INK}">'
            f'<h2 id="sum-h" style="{H2}">Executive summary</h2><p style="font-size:15px;font-weight:700;line-height:1.5;margin:10px 0 0;max-width:82ch">{paras}</p>'
            f'<ul style="margin:8px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px;font-size:15px;line-height:1.5;max-width:82ch">{lis}</ul>'
            f'<p class="note" style="margin-top:10px">Written by Claude from this tab\'s numbers for the selected period and rewritten once a day overnight, so it can trail the live figures below. Last written Nov 24, 2:10 AM.</p></section>')
def header(eyebrow, title, lede, recon=None):
    r = f'<p style="font-size:13px;color:{MUT};margin:8px 0 0;max-width:82ch">{recon}</p>' if recon else ''
    return (f'<header><div class="lab">[ACCOUNT NAME] · {eyebrow} · {{{{perLabel}}}} · Sample data</div>'
            f'<h1 style="font-family:Outfit,sans-serif;font-weight:500;font-size:36px;line-height:1.15;margin:8px 0 0">{title}</h1>'
            f'<p style="font-size:16px;line-height:1.55;margin:10px 0 0;max-width:80ch">{lede}</p>{r}</header>')

# ---------- svg charts ----------
SVGSTYLE = f"display:block;font-family:'Nunito Sans',sans-serif;font-size:12px;fill:{MUT}"
def _yaxis(x0, x1, ybase, h, vmax, ticks, fmt):
    out = ''
    for t in ticks:
        yy = ybase - h * t / vmax
        out += f'<line x1="{x0}" x2="{x1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{GRID}"/><text x="{x0 - 8}" y="{yy + 4:.1f}" text-anchor="end">{fmt(t)}</text>'
    return out

def bars(label, cats, series, vmax, ticks, fmt, mode='stack', under=None, ly=None, top=None, h=190, gapw=0.55, mark=None):
    """series: list of (name, fill, values, stroke). under: list of strings shown under axis. ly: tick values."""
    X0, X1, YB = 64, 990, 20 + h
    W = (X1 - X0) / len(cats)
    out = _yaxis(X0, X1, YB, h, vmax, ticks, fmt)
    for i, c in enumerate(cats):
        cx = X0 + W * i + W / 2
        if mode == 'stack':
            bw = W * gapw; acc = 0
            for nm, fill, vals, st in series:
                v = vals[i]; hh = h * v / vmax
                out += f'<rect x="{cx - bw / 2:.1f}" y="{YB - h * (acc + v) / vmax:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{fill}"' + (f' stroke="{st}"' if st else '') + '/>'
                acc += v
        else:
            k = len(series); bw = W * gapw / k
            for j, (nm, fill, vals, st) in enumerate(series):
                v = vals[i]; hh = h * v / vmax
                xx = cx - W * gapw / 2 + j * bw
                out += f'<rect x="{xx:.1f}" y="{YB - hh:.1f}" width="{bw - 1:.1f}" height="{hh:.1f}" fill="{fill}"' + (f' stroke="{st}"' if st else '') + '/>'
        if mark and mark[i]:
            out += f'<text x="{cx:.1f}" y="{YB - h * mark[i][0] / vmax - 6:.1f}" text-anchor="middle" style="fill:{INK};font-weight:700">{mark[i][1]}</text>'
        if ly is not None and ly[i] is not None:
            yy = YB - h * ly[i] / vmax
            out += f'<line x1="{cx - W * 0.36:.1f}" x2="{cx + W * 0.36:.1f}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="2.5"/>'
        if top:
            tot = sum(s[2][i] for s in series) if mode == 'stack' else max(s[2][i] for s in series)
            out += f'<text x="{cx:.1f}" y="{YB - h * tot / vmax - 6:.1f}" text-anchor="middle" style="fill:{INK}">{top[i]}</text>'
        if c: out += f'<text x="{cx:.1f}" y="{YB + 16}" text-anchor="middle">{c}</text>'
        if under: out += f'<text x="{cx:.1f}" y="{YB + 34}" text-anchor="middle" style="fill:{INK};font-weight:700">{under[i]}</text>'
    out += f'<line x1="{X0}" x2="{X1}" y1="{YB}" y2="{YB}" stroke="{INK}"/>'
    H_ = YB + (44 if under else 26)
    return f'<svg viewBox="0 0 1000 {H_}" width="100%" role="img" aria-label="{H.escape(label)}" style="{SVGSTYLE}">{out}</svg>'

def diverge(label, cats, up, dn, vmax, ticks, fmt, upc, dnc, dnst=None, under=None, h=110, top_series=None):
    X0, X1, Z = 64, 990, 20 + h
    W = (X1 - X0) / len(cats)
    out = ''
    for t in ticks:
        for sgn in (1, -1):
            yy = Z - sgn * h * t / vmax
            out += f'<line x1="{X0}" x2="{X1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{GRID}"/><text x="{X0 - 8}" y="{yy + 4:.1f}" text-anchor="end">{fmt(t)}</text>'
    for i, c in enumerate(cats):
        cx = X0 + W * i + W / 2; bw = W * 0.55
        hu = h * up[i] / vmax; hd = h * dn[i] / vmax
        out += f'<rect x="{cx - bw / 2:.1f}" y="{Z - hu:.1f}" width="{bw:.1f}" height="{hu:.1f}" fill="{upc}"/>'
        out += f'<rect x="{cx - bw / 2:.1f}" y="{Z:.1f}" width="{bw:.1f}" height="{hd:.1f}" fill="{dnc}"' + (f' stroke="{dnst}"' if dnst else '') + '/>'
        if under: out += f'<text x="{cx:.1f}" y="{Z + hd + 15:.1f}" text-anchor="middle" style="fill:{INK};font-weight:700">{under[i]}</text>'
        if c: out += f'<text x="{cx:.1f}" y="{Z + h + 38}" text-anchor="middle">{c}</text>'
    out += f'<line x1="{X0}" x2="{X1}" y1="{Z}" y2="{Z}" stroke="{INK}" stroke-width="1.5"/>'
    return f'<svg viewBox="0 0 1000 {Z + h + 48}" width="100%" role="img" aria-label="{H.escape(label)}" style="{SVGSTYLE}">{out}</svg>'

def lines(label, cats, series, vmax, ticks, fmt, refline=None, h=170, dots=None):
    """series: (name, color, values, width, dash)"""
    X0, X1, YB = 64, 990, 20 + h
    W = (X1 - X0) / len(cats)
    out = _yaxis(X0, X1, YB, h, vmax, ticks, fmt)
    if refline:
        v, lab = refline; yy = YB - h * v / vmax
        out += f'<line x1="{X0}" x2="{X1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 4"/><text x="{X1}" y="{yy - 6:.1f}" text-anchor="end" style="fill:{INK};font-weight:700">{lab}</text>'
    for nm, col, vals, wd, dash in series:
        pts = ' '.join(f'{X0 + W * i + W / 2:.1f},{YB - h * v / vmax:.1f}' for i, v in enumerate(vals) if v is not None)
        out += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{wd}"' + (f' stroke-dasharray="{dash}" stroke-linecap="round"' if dash else '') + ' stroke-linejoin="round"/>'
    if dots:
        for i, (v, txt) in dots.items():
            cx = X0 + W * i + W / 2; cy = YB - h * v / vmax
            out += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="#fff" stroke="{INK}" stroke-width="2"/><text x="{cx:.1f}" y="{cy - 10:.1f}" text-anchor="middle" style="fill:{INK};font-weight:700">{txt}</text>'
    every = max(1, len(cats) // 12)
    for i, c in enumerate(cats):
        if i % every == 0 and c: out += f'<text x="{X0 + W * i + W / 2:.1f}" y="{YB + 16}" text-anchor="middle">{c}</text>'
    out += f'<line x1="{X0}" x2="{X1}" y1="{YB}" y2="{YB}" stroke="{INK}"/>'
    return f'<svg viewBox="0 0 1000 {YB + 26}" width="100%" role="img" aria-label="{H.escape(label)}" style="{SVGSTYLE}">{out}</svg>'

def sharebar(label, value_txt, frac, color=TEAL, note=''):
    return (f'<div><div style="display:flex;justify-content:space-between;gap:8px;font-size:15px"><span>{label}</span><b>{value_txt}</b></div>'
            f'<div role="img" aria-label="{H.escape(label)}: {value_txt}" style="height:10px;background:{GRID};margin-top:6px"><div style="height:10px;width:{frac * 100:.1f}%;background:{color}"></div></div>'
            + (f'<div class="note">{note}</div>' if note else '') + '</div>')

def chart_focus_hint():
    return (f'<p class="note" style="margin-top:6px">Point at, or tab to, a bar for details. Arrow keys move between bars; Escape closes the details.</p>')

# ---------- page shell ----------
PERIODS = [('ytd', 'Year to date', 'so far this year'), ('qtd', 'FEC quarter', 'so far this quarter'),
           ('mtd', 'Month to date', 'so far this month'), ('30d', 'Past 30 days', 'in the past 30 days')]
PERLONG = {'ytd': 'Year to date', 'qtd': 'FEC quarter to date', 'mtd': 'Month to date', '30d': 'Past 30 days'}

HELMET = '''<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&amp;family=Outfit:wght@500;700&amp;display=swap" rel="stylesheet">
<style>
body{margin:0;background:#fff}
a{color:#007A99}a:hover{color:#005A72}
a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid #007A99;outline-offset:2px}
.t{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums;font-family:'Nunito Sans',sans-serif;color:#212529}
.t th{font-family:Outfit,sans-serif;font-weight:700;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:#3F4945;text-align:right;padding:0 10px 8px;white-space:nowrap;border-bottom:2px solid #212529;vertical-align:bottom}
.t td{text-align:right;padding:9px 10px;border-top:1px solid #E6EAE8;white-space:nowrap}
.t th:first-child,.t td:first-child,.t td.l{text-align:left}
.t td.l{white-space:normal;color:#3F4945;min-width:18ch}
.t tr.tot td{font-weight:700;border-top:2px solid #212529}
.scr{overflow-x:auto;margin-top:16px}
.mu{color:#3F4945} .up{color:#2E7D4A} .dn{color:#B3261E}
.lab{font-family:Outfit,sans-serif;font-weight:700;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#3F4945}
.note{font-size:13px;color:#3F4945;margin-top:4px;line-height:1.4}
.tile{background:#fff;border:1px solid #D9DEDC;padding:16px 18px;min-width:0}
.val{font-family:Outfit,sans-serif;font-weight:500;font-size:30px;line-height:1.15;margin-top:6px;font-variant-numeric:tabular-nums}
.sum{cursor:pointer;min-height:44px;display:inline-flex;align-items:center}
.sb{font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;background:none;border:0;padding:6px 0;min-height:32px;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.code{font-family:ui-monospace,Menlo,monospace;font-size:12px}
</style>'''

def shell(fname, title, active, body, js_extra='', h=4000):
    tabhtml = ''
    for name, f in TABS:
        on = name == active
        cur = ' aria-current="page"' if on else ''
        tabhtml += (f'<a href="{f}"{cur} style="display:inline-flex;align-items:center;font-size:15px;text-decoration:none;'
                    f'border-bottom:3px solid {TEAL if on else "transparent"};margin-bottom:-1px;padding:0 16px;min-height:44px;'
                    f'color:{INK if on else MUT};font-weight:{700 if on else 400}">{name}</a>')
    per = ('<sc-for list="{{periods}}" as="p" hint-placeholder-count="4"><button type="button" aria-pressed="{{p.pressed}}" onClick="{{p.pick}}" '
           'style="font-family:Outfit,sans-serif;font-weight:700;font-size:12px;letter-spacing:.06em;text-transform:uppercase;border:0;'
           'border-left:{{p.bl}};padding:0 14px;min-height:44px;cursor:pointer;background:{{p.bg}};color:{{p.fg}}">{{p.label}}</button></sc-for>')
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{HELMET}
</helmet>
<div style="font-family:'Nunito Sans',sans-serif;color:{INK};background:#fff;width:100%">
<div aria-hidden="true" style="height:4px;background:linear-gradient(90deg,{CYAN},#6AC481)"></div>
<div style="max-width:1240px;margin:0 auto;padding:0 32px 48px;box-sizing:border-box;display:flex;flex-direction:column;gap:24px">
<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding-top:16px">
<div style="display:flex;align-items:baseline;gap:12px"><span style="font-family:Outfit,sans-serif;font-weight:700;font-size:20px">frakture<span style="color:{ORNG_D}">.</span></span><span style="font-size:14px;color:{MUT}">Fundraising Report</span></div>
<div style="display:flex;align-items:center;gap:10px;font-size:13px;color:{MUT}"><span id="per-lab">Period</span><div role="group" aria-labelledby="per-lab" style="display:inline-flex;border:1px solid {INK}">{per}</div></div>
</div>
<p aria-live="polite" class="sr">{{{{perAnnounce}}}}</p>
<nav aria-label="Report pages" style="display:flex;flex-wrap:wrap;border-bottom:1px solid {LINE};margin-top:-8px">{tabhtml}</nav>
{body}
<div style="border-top:1px solid {LINE};padding-top:12px;font-size:13px;color:{MUT}">Mockup with sample figures, not live data. Totals match the year-to-date account totals; splits are illustrative. The period picker changes the highlighted period and labels only.</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1360,"height":{h}}}}}'>
const PERIODS = {json.dumps([[a, b, c, PERLONG[a]] for a, b, c in PERIODS])};
class Component extends DCLogic {{
  renderVals() {{
    const s = this.state || {{}};
    const per = s.per || 'ytd';
    const cur = PERIODS.find((p) => p[0] === per);
    const periods = PERIODS.map((p, i) => ({{
      label: p[1], pressed: p[0] === per ? 'true' : 'false',
      bg: p[0] === per ? '{INK}' : '#ffffff', fg: p[0] === per ? '#ffffff' : '{INK}',
      bl: i ? '1px solid {INK}' : '0',
      pick: () => this.setState({{ per: p[0], perAnnounce: 'Period set to ' + p[3] + '. Every tab now shows ' + p[3].toLowerCase() + '.' }})
    }}));
    const base = {{ periods, perLabel: cur[3], perPhrase: cur[2], perAnnounce: s.perAnnounce || '' }};
    return Object.assign(base, this.extraVals ? this.extraVals(s) : {{}});
  }}
{js_extra}
}}
</script>
</body>
</html>
'''
    return doc

def sortable_js(key, rows, cols, default):
    """rows: list of dicts with raw sort values under 'k_<col>' and display strings 'c0'..; cols: {col: label}."""
    return f'''
  extraVals_{key}(s) {{
    const ROWS = {json.dumps(rows)};
    const COLS = {json.dumps(cols)};
    const sk = s.sk_{key} || '{default}', dir = s.sd_{key} || 'descending';
    const rows = ROWS.slice().sort((a, b) => dir === 'descending' ? b['k_' + sk] - a['k_' + sk] : a['k_' + sk] - b['k_' + sk]);
    const out = {{ rows_{key}: rows, msg_{key}: s.msg_{key} || '' }};
    Object.keys(COLS).forEach((c) => {{
      out['as_{key}_' + c] = c === sk ? dir : 'none';
      out['ar_{key}_' + c] = c === sk ? (dir === 'descending' ? '▼' : '▲') : '↕';
      out['sort_{key}_' + c] = () => {{
        const nd = c === sk && dir === 'descending' ? 'ascending' : 'descending';
        this.setState({{ ['sk_{key}']: c, ['sd_{key}']: nd, ['msg_{key}']: 'Sorted by ' + COLS[c] + ', ' + (nd === 'descending' ? 'highest' : 'lowest') + ' first.' }});
      }};
    }});
    return out;
  }}'''

def sortable_table(key, label, head, sortcols, ncols, minw=1000, left=()):
    """head: list of (label, colkey or None)."""
    hh = ''
    for i, (lab, ck) in enumerate(head):
        st = ' style="text-align:left"' if i in left else ''
        if ck:
            hh += (f'<th scope="col" aria-sort="{{{{as_{key}_{ck}}}}}"{st}><button type="button" class="sb" onClick="{{{{sort_{key}_{ck}}}}}">'
                   f'{lab} <span aria-hidden="true">{{{{ar_{key}_{ck}}}}}</span></button></th>')
        else:
            hh += f'<th scope="col"{st}>{lab}</th>'
    tds = ''.join(f'<td{" class=\"l\"" if i in left else ""}>{{{{r.c{i}}}}}</td>' for i in range(ncols))
    return (f'<p aria-live="polite" class="sr">{{{{msg_{key}}}}}</p>'
            f'<div role="region" aria-label="{H.escape(label)} (scrolls sideways)" tabindex="0" class="scr"><table class="t" style="min-width:{minw}px">'
            f'<caption class="sr">{H.escape(label)}. Column headers with arrows sort the table.</caption><thead><tr>{hh}</tr></thead>'
            f'<tbody><sc-for list="{{{{rows_{key}}}}}" as="r" hint-placeholder-count="10"><tr>{tds}</tr></sc-for></tbody></table></div>')
