(function () {
  const fmt = {
    money: (v) => v == null || isNaN(v) ? '—' : Math.abs(v) >= 1e6 ? '$' + (v / 1e6).toFixed(2) + 'M' : Math.abs(v) >= 1e3 ? '$' + Math.round(v / 1e3).toLocaleString('en-US') + 'K' : '$' + Math.round(v).toLocaleString('en-US'),
    int: (v) => v == null || isNaN(v) ? '—' : Math.round(v).toLocaleString('en-US'),
    pct: (v, d) => v == null || isNaN(v) ? '—' : (v * 100).toFixed(d == null ? 0 : d) + '%',
    chg: (v) => v == null || isNaN(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(v * 100).toFixed(0) + '%',
    unit: (v) => v == null || isNaN(v) ? '—' : '$' + v.toFixed(2)
  };
  const STATUS = { 'On track': ['●', 'ap-good'], 'Watch': ['■', 'ap-warn'], 'At risk': ['▲', 'ap-bad'], 'New this cycle': ['◆', 'ap-mu'] };
  const TYPES = { candidate: 'Candidate', pac: 'PAC', nonprofit: 'Nonprofit', state_party: 'State party' };
  const typeLabel = (t) => TYPES[t] || String(t || '').replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());
  const range = (lo, hi) => lo == null ? '—' : fmt.money(lo) === fmt.money(hi) ? fmt.money(lo) : fmt.money(lo) + '–' + fmt.money(hi);
  const FILT = { all: null, risk: 'At risk', watch: 'Watch', ok: 'On track', new: 'New this cycle' };
  const sort = { k: 'ytd', d: 'descending', msg: '' };
  const SORTNAME = { ytd: 'raised', vs: 'change on last year', pvs: 'projected year-end against last year', nd: 'new donors', rr: 'monthly run rate', rpd: 'raised per $1', tr: 'revenue traced to a channel' };

  dash.calc('port', {
    title: 'Accounts with portfolio metrics', description: 'One row per loaded account: year to date, last year, projection, status.',
    inputs: ['snapshot'],
    fn: (snapshot) => {
      const rows = snapshot.filter((r) => r.state === 'loaded');
      return rows.map((r) => {
        const yr = Number(String(r.as_of).slice(0, 4));
        const ok = (y) => r.first_gift && String(r.first_gift).slice(0, 10) <= y + '-01-07';
        const lyv = ok(yr - 1) && r.ly_ytd > 0, mtv = ok(yr - 4) && r.mt_ytd > 0;
        const pl = lyv ? r.ytd * (1 + r.ly_rest / r.ly_ytd) : null, pm = mtv ? r.ytd * (1 + r.mt_rest / r.mt_ytd) : null;
        const ps = [pl, pm].filter((x) => x != null);
        const lo = ps.length ? Math.min(...ps) : null, hi = ps.length ? Math.max(...ps) : null;
        const lyfull = lyv ? r.ly_ytd + r.ly_rest : null;
        const pvs = lyv && lo != null ? ((lo + hi) / 2 - lyfull) / lyfull : null;
        const status = pvs == null ? 'New this cycle' : pvs < -0.15 ? 'At risk' : pvs < -0.05 ? 'Watch' : 'On track';
        return {
          id: r.account_id, name: r.name, type: r.type, ytd: r.ytd, ly: lyv ? r.ly_ytd : null, lyfull, lo, hi, vs: lyv ? (r.ytd - r.ly_ytd) / r.ly_ytd : null, pvs,
          nd: r.new_ty, nd_ly: lyv ? r.new_ly : null, rr: r.run_rate, ta_rev: r.ta_rev, ta_cost: r.ta_cost, rpd: r.ta_cost > 0 ? r.ta_rev / r.ta_cost : null,
          unattrib: r.unattrib, all_rev: r.all_rev, tr: r.all_rev > 0 ? 1 - r.unattrib / r.all_rev : null, status, chan: r.chan, mon: r.mon
        };
      });
    }
  });

  dash.calc('totals', {
    title: 'Portfolio totals', description: 'Sums and weighted averages across loaded accounts.',
    inputs: ['port', 'snapshot'],
    fn: (port, snapshot) => {
      const sum = (a, f) => a.reduce((t, r) => t + (f(r) || 0), 0);
      const comp = port.filter((r) => r.ly != null), cost = port.filter((r) => r.ta_cost > 0);
      const lflLy = sum(comp, (r) => r.ly), lflTy = sum(comp, (r) => r.ytd);
      const withP = comp.filter((r) => r.lo != null);
      const ytd = sum(port, (r) => r.ytd), top3 = [...port].sort((a, b) => b.ytd - a.ytd).slice(0, 3).reduce((t, r) => t + r.ytd, 0);
      return [{
        nloaded: port.length, npending: snapshot.filter((r) => r.state === 'pending').length, nexcluded: snapshot.filter((r) => r.state === 'excluded').length,
        ncomp: comp.length, ytd, lfl: lflLy > 0 ? (lflTy - lflLy) / lflLy : null, lfl_ty: lflTy, lfl_ly: lflLy,
        proj_lo: sum(withP, (r) => r.lo), proj_hi: sum(withP, (r) => r.hi), proj_ly: sum(withP, (r) => r.lyfull), nproj: withP.length,
        nd: sum(port, (r) => r.nd), nd_c: sum(comp, (r) => r.nd), nd_c_ly: sum(comp, (r) => r.nd_ly), rr: sum(port, (r) => r.rr),
        rpd: sum(cost, (r) => r.ta_cost) > 0 ? sum(cost, (r) => r.ta_rev) / sum(cost, (r) => r.ta_cost) : null,
        tr: sum(port, (r) => r.all_rev) > 0 ? 1 - sum(port, (r) => r.unattrib) / sum(port, (r) => r.all_rev) : null,
        top3: ytd > 0 ? top3 / ytd : null,
        nrisk: port.filter((r) => r.status === 'At risk').length, nwatch: port.filter((r) => r.status === 'Watch').length,
        ngrow: comp.filter((r) => r.vs > 0).length, top3names: [...port].sort((a, b) => b.ytd - a.ytd).slice(0, 3).map((r) => r.name).join(', '),
        nok: port.filter((r) => r.status === 'On track').length, nnew: port.filter((r) => r.status === 'New this cycle').length
      }];
    }
  });

  dash.calc('selected', {
    title: 'Accounts matching the filters', description: 'Totals for the accounts shown by the Status and Account type filters.',
    inputs: ['port'],
    fn: (port) => {
      const p = dash.params(), st = { risk: 'At risk', watch: 'Watch', ok: 'On track', new: 'New this cycle' }[p.st] || null, cat = p.cat && p.cat !== 'all' ? p.cat : null;
      const rows = port.filter((r) => (!st || r.status === st) && (!cat || r.type === cat));
      const sum = (a, f) => a.reduce((t, r) => t + (f(r) || 0), 0);
      const comp = rows.filter((r) => r.ly != null), all = sum(port, (r) => r.ytd);
      return [{ n: rows.length, nall: port.length, ytd: sum(rows, (r) => r.ytd), share: all > 0 ? sum(rows, (r) => r.ytd) / all : null,
        vs: comp.length && sum(comp, (r) => r.ly) > 0 ? (sum(comp, (r) => r.ytd) - sum(comp, (r) => r.ly)) / sum(comp, (r) => r.ly) : null, ncomp: comp.length,
        nd: sum(rows, (r) => r.nd), rr: sum(rows, (r) => r.rr), filtered: !!(st || cat) }];
    }
  });

  dash.calc('months', {
    title: 'Revenue by month', description: 'Accounts with a full prior year, summed by month.', inputs: ['port'],
    fn: (port) => {
      const m = {};
      port.filter((r) => r.ly != null).forEach((r) => String(r.mon || '').split('|').filter(Boolean).forEach((x) => {
        const [k, ty, ly] = x.split(':'); m[k] = m[k] || { month: Number(k), ty: 0, ly: 0 }; m[k].ty += Number(ty); m[k].ly += Number(ly);
      }));
      return Object.values(m).filter((r) => r.ty > 0 || r.ly > 0).sort((a, b) => a.month - b.month);
    }
  });
  dash.calc('channels', {
    title: 'Revenue by channel', description: 'Accounts with a full prior year, summed by channel.', inputs: ['port'],
    fn: (port) => {
      const c = {};
      port.filter((r) => r.ly != null).forEach((r) => String(r.chan || '').split('|').filter(Boolean).forEach((x) => {
        const p = x.split(':'), ly = Number(p.pop()), ty = Number(p.pop()), k = p.join(':'); c[k] = c[k] || { channel: k, ty: 0, ly: 0, a: [] }; c[k].ty += ty; c[k].ly += ly; c[k].a.push({ name: r.name, ty, ly });
      }));
      const rows = Object.values(c), tot = rows.reduce((t, r) => t + r.ty, 0);
      return rows.map((r) => ({ channel: r.channel, ty: r.ty, ly: r.ly, share: tot > 0 ? r.ty / tot : null, chg: r.ly > 0 ? (r.ty - r.ly) / r.ly : null,
        up: r.a.filter((x) => x.ty > x.ly).length + ' of ' + r.a.length, best: [...r.a].sort((x, y) => y.ty - x.ty)[0].name })).sort((a, b) => b.ty - a.ty);
    }
  });
  dash.calc('coverage', {
    title: 'Reporting coverage', description: 'How complete the data behind the portfolio is.', inputs: ['port', 'snapshot'],
    fn: (port, snapshot) => {
      const nm = (r) => r.name || r.account_id;
      const list = (a) => a.length ? (a.length > 4 ? a.slice(0, 4).map(nm).join(', ') + ' and ' + (a.length - 4) + ' more' : a.map(nm).join(', ')) : '—';
      const typed = snapshot.filter((r) => r.state !== 'excluded'), ex = snapshot.filter((r) => r.state === 'excluded'), pend = snapshot.filter((r) => r.state === 'pending');
      const g = (pred) => port.filter((r) => !pred(r));
      return [
        { check: 'Account type set in Engine 9', accounts: typed.length + ' of ' + snapshot.length, gaps: list(ex), affects: 'Accounts with no type are left out of the portfolio' },
        { check: 'Account included in this snapshot', accounts: port.length + ' of ' + typed.length, gaps: list(pend), affects: 'Accounts not yet loaded are not in any total' },
        { check: 'A full prior year on record', accounts: port.filter((r) => r.ly != null).length + ' of ' + port.length, gaps: list(g((r) => r.ly != null)), affects: 'Left out of year-on-year totals, the monthly chart and the channel table' },
        { check: 'Cost tracked for texts and ads', accounts: port.filter((r) => r.ta_cost > 0).length + ' of ' + port.length, gaps: list(g((r) => r.ta_cost > 0)), affects: 'Raised per $1 is blank for these accounts' },
        { check: 'Revenue traced to a channel, 85% or more', accounts: port.filter((r) => r.tr != null && r.tr >= 0.85).length + ' of ' + port.length, gaps: list(g((r) => r.tr != null && r.tr >= 0.85)), affects: 'Channel mix is less certain' }
      ];
    }
  });

  const setState = (el, st) => { el.classList.toggle('dash-skeleton', st === 'loading'); };
  const get = (id) => { const d = dash.data(id); return d.status === 'ok' && d.data ? d.data : null; };
  const one = (id) => { const d = get(id); return d && d[0] ? d[0] : null; };
  const dashes = (el, id) => { el.textContent = '—'; setState(el, dash.data(id).status); };
  const scalar = (name, id, fn) => dash.draw(name, (el) => { const r = one(id); if (!r) return dashes(el, id); setState(el, 'ok'); const v = fn(r); el.textContent = v == null ? '—' : v; });
  const T = 'totals';
  scalar('t_nloaded', T, (r) => fmt.int(r.nloaded)); scalar('t_ytd', T, (r) => fmt.money(r.ytd)); scalar('t_ncomp', T, (r) => fmt.int(r.ncomp));
  scalar('t_lfl', T, (r) => fmt.chg(r.lfl)); scalar('t_nrisk', T, (r) => fmt.int(r.nrisk)); scalar('t_nwatch', T, (r) => fmt.int(r.nwatch));
  scalar('t_pendingnote', T, (r) => (r.npending ? r.npending + ' further accounts are not yet in this snapshot and are named under Reporting coverage.' : '') + (r.nexcluded ? ' ' + r.nexcluded + ' accounts with no account type are left out.' : ''));
  scalar('k_ytd', T, (r) => fmt.money(r.ytd)); scalar('k_lfl', T, (r) => fmt.chg(r.lfl));
  scalar('k_lfl_s', T, (r) => fmt.money(r.lfl_ty) + ' vs ' + fmt.money(r.lfl_ly) + ', ' + r.ncomp + ' comparable accounts');
  scalar('k_proj', T, (r) => r.nproj ? fmt.money(r.proj_lo) + '–' + fmt.money(r.proj_hi) : '—');
  scalar('k_new', T, (r) => fmt.int(r.nd)); scalar('k_new_s', T, (r) => 'Comparable accounts ' + fmt.int(r.nd_c) + ' vs ' + fmt.int(r.nd_c_ly) + ' last year, ' + fmt.chg(r.nd_c_ly > 0 ? (r.nd_c - r.nd_c_ly) / r.nd_c_ly : null));
  scalar('k_rr', T, (r) => fmt.money(r.rr)); scalar('k_rpd', T, (r) => fmt.unit(r.rpd)); scalar('k_tr', T, (r) => fmt.pct(r.tr, 1)); scalar('k_top3', T, (r) => fmt.pct(r.top3));
  scalar('k_grow', T, (r) => r.ncomp ? r.ngrow + ' of ' + r.ncomp : '—'); scalar('k_grow_s', T, (r) => 'Revenue up on the same dates last year · ' + r.nrisk + ' at risk, ' + r.nwatch + ' watch');
  scalar('t_ngrow', T, (r) => fmt.int(r.ngrow)); scalar('t_ncomp2', T, (r) => fmt.int(r.ncomp)); scalar('k_top3_s', T, (r) => r.top3names + ' · concentration');
  scalar('c_all', T, (r) => r.nloaded); scalar('c_risk', T, (r) => r.nrisk); scalar('c_watch', T, (r) => r.nwatch); scalar('c_ok', T, (r) => r.nok); scalar('c_new', T, (r) => r.nnew);
  dash.draw('asof', (el) => { const d = dash.data('snapshot'); if (d.status !== 'ok' || !d.data.length) return dashes(el, 'snapshot'); setState(el, 'ok'); const l = d.data.find((x) => x.as_of); el.textContent = l ? l.as_of : '—'; });

  const mkTip = () => { const t = document.createElement('div'); t.className = 'ap-tip'; t.hidden = true; return t; };
  const tipApi = (box, t) => ({ show(txt, x, y) { t.textContent = txt; t.hidden = false; const w = box.clientWidth; t.style.left = Math.max(0, Math.min(w - t.offsetWidth, x + 10)) + 'px'; t.style.top = Math.max(0, y - 36) + 'px'; }, hide() { t.hidden = true; } });
  const altTable = (cols, rows) => {
    const d = document.createElement('details'); const t = document.createElement('table'); const h = document.createElement('tr');
    cols.forEach((c, i) => { const th = document.createElement('th'); th.scope = 'col'; if (!i) th.className = 'l'; th.textContent = c; h.appendChild(th); }); t.appendChild(h);
    rows.forEach((r) => { const tr = document.createElement('tr'); r.forEach((c, i) => { const td = document.createElement('td'); if (!i) td.className = 'l'; td.textContent = c; tr.appendChild(td); }); t.appendChild(tr); });
    const s = document.createElement('summary'); s.textContent = 'View as table'; const w = document.createElement('div'); w.className = 'ap-scroll'; w.appendChild(t);
    d.append(s, w); return d;
  };
  const msg = (text) => Object.assign(document.createElement('div'), { className: 'ap-empty', textContent: text });

  dash.draw('scatter', (box) => {
    const st = dash.data('port').status;
    const rows = get('port'); if (!rows) { box.replaceChildren(msg(st === 'error' ? 'Couldn’t load the accounts.' : '—')); setState(box, st); return; }
    setState(box, 'ok');
    const pts = rows.filter((r) => r.pvs != null && r.ytd > 0);
    if (!pts.length) { box.replaceChildren(msg('No loaded account has a full prior year to compare with yet.')); return; }
    const W = Math.max(320, box.clientWidth || 900), H = 380, m = { l: 62, r: 20, t: 16, b: 52 };
    const ymin = -0.3, ymax = 0.45, xs = pts.map((r) => r.ytd);
    const x = d3.scaleLog().domain([Math.max(Math.min(...xs) / 2, 1e4), Math.max(Math.max(...xs) * 2, 1e5)]).range([m.l, W - m.r]);
    const y = d3.scaleLinear().domain([ymin, ymax]).range([H - m.b, m.t]);
    const svg = d3.create('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
      .attr('aria-label', 'Each account with a full prior year, placed by money raised so far this year (across, log scale) and projected year-end against last year (up and down). ' + pts.map((r) => `${r.name}: ${fmt.money(r.ytd)}, ${fmt.chg(r.pvs)}, ${r.status.toLowerCase()}`).join('; ') + '.');
    [-0.3, -0.15, 0, 0.15, 0.3, 0.45].forEach((v) => { svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(v)).attr('y2', y(v)).attr('stroke', v ? 'var(--cds-chart-grid)' : 'var(--color-fg)').attr('stroke-width', v ? 1 : 1.5); svg.append('text').attr('x', m.l - 8).attr('y', y(v) + 4).attr('text-anchor', 'end').text(v ? fmt.chg(v) : '0%'); });
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(-0.15)).attr('y2', y(-0.15)).style('stroke', 'var(--color-bad)').attr('stroke-dasharray', '6 4').attr('stroke-width', 1.5);
    svg.append('text').attr('x', W - m.r).attr('y', y(-0.15) - 6).attr('text-anchor', 'end').style('fill', 'var(--color-bad)').style('font-weight', 700).text('At-risk line: 15% behind last year');
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(-0.05)).attr('y2', y(-0.05)).style('stroke', 'var(--color-warn)').attr('stroke-dasharray', '2 4').attr('stroke-width', 1.5);
    svg.append('text').attr('x', W - m.r).attr('y', y(-0.05) - 5).attr('text-anchor', 'end').style('fill', 'var(--color-warn)').style('font-weight', 700).text('Watch line: 5% behind');
    const xd = x.domain(); [1e5, 3e5, 1e6, 3e6, 1e7, 3e7, 1e8].filter((t) => t >= xd[0] && t <= xd[1]).forEach((t) => { svg.append('text').attr('x', x(t)).attr('y', H - m.b + 18).attr('text-anchor', 'middle').text(fmt.money(t)); });
    svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 8).attr('text-anchor', 'middle').text('Raised so far this year (log scale)');
    const tipEl = mkTip(), tp = tipApi(box, tipEl);
    pts.forEach((r) => {
      const cx = x(r.ytd), cy = y(Math.max(ymin, Math.min(ymax, r.pvs))), col = r.status === 'At risk' ? 'var(--color-bad)' : r.status === 'Watch' ? 'var(--color-warn)' : 'var(--color-ok)';
      const g = svg.append('g').attr('tabindex', 0).attr('role', 'img').attr('aria-label', `${r.name}: raised ${fmt.money(r.ytd)}, projected ${fmt.chg(r.pvs)} against last year, ${r.status.toLowerCase()}`);
      if (r.status === 'On track') g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 8).style('fill', col);
      else if (r.status === 'Watch') g.append('rect').attr('x', cx - 7).attr('y', cy - 7).attr('width', 14).attr('height', 14).style('fill', col);
      else g.append('polygon').attr('points', `${cx},${cy - 9} ${cx + 9},${cy + 7} ${cx - 9},${cy + 7}`).style('fill', col);
      const left = cx > W * 0.6;
      g.append('text').attr('x', left ? cx - 14 : cx + 14).attr('y', cy + 4).attr('text-anchor', left ? 'end' : 'start').style('fill', 'var(--color-fg)').style('font-weight', 700).text(r.name + (r.pvs > ymax ? ' ↑ ' + fmt.chg(r.pvs) + ', off scale' : ''));
      const on = () => tp.show(`${r.name}: ${fmt.money(r.ytd)} raised, projected ${fmt.chg(r.pvs)} vs last year (${r.status})`, cx, cy);
      g.on('mouseenter', on).on('focus', on).on('mouseleave', tp.hide).on('blur', tp.hide);
    });
    box.replaceChildren(svg.node(), tipEl, altTable(['Account', 'Raised', 'Projected vs last year', 'Status'], pts.map((r) => [r.name, fmt.money(r.ytd), fmt.chg(r.pvs), r.status])));
  });

  const cell = (tr, text, cls, color) => { const td = document.createElement('td'); td.className = [cls, color].filter(Boolean).join(' '); td.textContent = text; tr.appendChild(td); return td; };
  dash.draw('rows', (body) => {
    const port = get('port'), tot = one('totals'), sel = one('selected');
    if (!port || !tot || !sel) { body.replaceChildren(); return; }
    const p = dash.params(), st = FILT[p.st] || null, cat = p.cat && p.cat !== 'all' ? p.cat : null;
    const rows = port.filter((r) => (!st || r.status === st) && (!cat || r.type === cat))
      .sort((a, b) => { const x = a[sort.k], y = b[sort.k]; if (x == null && y == null) return 0; if (x == null) return 1; if (y == null) return -1; return sort.d === 'descending' ? y - x : x - y; });
    const out = [];
    if (!rows.length) { const tr = document.createElement('tr'); cell(tr, 'No accounts match these filters. Use Clear filters.', 'l', 'ap-mu').colSpan = 12; out.push(tr); }
    rows.forEach((r) => {
      const tr = document.createElement('tr'); tr.setAttribute('data-key', encodeURIComponent(r.id));
      cell(tr, r.name, 'l').style.fontWeight = 700; cell(tr, typeLabel(r.type), 'l'); cell(tr, fmt.money(r.ytd)); cell(tr, r.vs == null ? 'No full prior year' : fmt.chg(r.vs), '', r.vs == null ? 'ap-mu' : r.vs >= 0 ? 'ap-good' : 'ap-bad');
      cell(tr, fmt.pct(tot.ytd > 0 ? r.ytd / tot.ytd : null, 1)); cell(tr, range(r.lo, r.hi));
      cell(tr, fmt.chg(r.pvs), '', r.pvs == null ? 'ap-mu' : r.pvs >= -0.05 ? 'ap-good' : r.pvs >= -0.15 ? 'ap-warn' : 'ap-bad');
      cell(tr, fmt.int(r.nd)); cell(tr, fmt.money(r.rr)); cell(tr, fmt.unit(r.rpd)); cell(tr, fmt.pct(r.tr)); cell(tr, STATUS[r.status][0] + ' ' + r.status, 'l', STATUS[r.status][1]);
      out.push(tr);
    });
    if (sel.filtered && rows.length) {
      const tr = document.createElement('tr'); tr.className = 'sel'; cell(tr, 'Selected accounts', 'l'); cell(tr, (cat ? typeLabel(cat) : 'All types') + (st ? ', ' + st.toLowerCase() : ''), 'l'); cell(tr, fmt.money(sel.ytd));
      cell(tr, sel.vs == null ? 'No full prior year' : fmt.chg(sel.vs) + (sel.ncomp < sel.n ? ' (comparable only)' : '')); cell(tr, fmt.pct(sel.share, 1)); cell(tr, '—'); cell(tr, '—'); cell(tr, fmt.int(sel.nd)); cell(tr, fmt.money(sel.rr)); cell(tr, '—'); cell(tr, '—'); cell(tr, sel.n + ' accounts', 'l'); out.push(tr);
    }
    const tr = document.createElement('tr'); tr.className = 'tot'; cell(tr, 'Portfolio', 'l'); cell(tr, tot.nloaded + ' accounts', 'l'); cell(tr, fmt.money(tot.ytd)); cell(tr, fmt.chg(tot.lfl) + ' (comparable only)'); cell(tr, '100%');
    cell(tr, tot.nproj ? fmt.money(tot.proj_lo) + '–' + fmt.money(tot.proj_hi) : '—'); cell(tr, tot.nproj && tot.proj_ly > 0 ? fmt.chg(((tot.proj_lo + tot.proj_hi) / 2 - tot.proj_ly) / tot.proj_ly) : '—');
    cell(tr, fmt.int(tot.nd)); cell(tr, fmt.money(tot.rr)); cell(tr, fmt.unit(tot.rpd)); cell(tr, fmt.pct(tot.tr)); cell(tr, tot.nrisk + ' at risk · ' + tot.nwatch + ' watch', 'l'); out.push(tr);
    body.replaceChildren(...out);
  });
  dash.draw('shown', (el) => { const s = one('selected'); if (!s) return dashes(el, 'port'); setState(el, 'ok'); el.textContent = 'Showing ' + s.n + ' of ' + s.nall + ' accounts'; });
  dash.draw('sortmsg', (el) => { el.textContent = sort.msg; });
  dash.draw('cats', (box) => {
    const port = get('port'); if (!port) return;
    const types = [...new Set(port.map((r) => r.type))].sort(), cur = dash.params().cat || 'all';
    const mk = (v, label, n) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = label + ' (' + n + ')'; b.setAttribute('aria-pressed', v === cur ? 'true' : 'false'); b.addEventListener('click', () => dash.setParams({ cat: v })); return b; };
    box.replaceChildren(mk('all', 'All', port.length), ...types.map((t) => mk(t, typeLabel(t), port.filter((r) => r.type === t).length)));
  });

  document.querySelectorAll('[data-f]').forEach((b) => b.addEventListener('click', () => dash.setParams({ st: b.getAttribute('data-f') })));
  const clear = document.getElementById('ap-clear'); if (clear) clear.addEventListener('click', () => dash.setParams({ st: 'all', cat: 'all' }));
  document.querySelectorAll('.ap-sb[data-sort]').forEach((b) => b.addEventListener('click', () => {
    const k = b.getAttribute('data-sort'); sort.d = sort.k === k && sort.d === 'descending' ? 'ascending' : 'descending'; sort.k = k;
    sort.msg = 'Sorted by ' + SORTNAME[k] + ', ' + (sort.d === 'descending' ? 'highest' : 'lowest') + ' first.';
    document.querySelectorAll('th[data-field]').forEach((h) => { if (h.querySelector('.ap-sb')) h.setAttribute('aria-sort', h.getAttribute('data-field') === sort.k ? sort.d : 'none'); });
    dash.draw('rows'); dash.draw('sortmsg');
  }));
  dash.onData(() => { const p = dash.params(); document.querySelectorAll('[data-f]').forEach((b) => b.setAttribute('aria-pressed', (p.st || 'all') === b.getAttribute('data-f') ? 'true' : 'false')); });

  dash.draw('attn', (body) => {
    const port = get('port'); if (!port) { body.replaceChildren(); return; }
    const order = { 'At risk': 0, 'Watch': 1, 'New this cycle': 2 };
    const rows = port.filter((r) => r.status in order).sort((a, b) => order[a.status] - order[b.status] || b.ytd - a.ytd);
    if (!rows.length) { const tr = document.createElement('tr'); cell(tr, 'No account is at risk, on watch or new this cycle.', 'l', 'ap-mu').colSpan = 3; body.replaceChildren(tr); return; }
    body.replaceChildren(...rows.map((r) => {
      const tr = document.createElement('tr'); tr.setAttribute('data-key', encodeURIComponent(r.id)); cell(tr, r.name, 'l').style.fontWeight = 700; cell(tr, STATUS[r.status][0] + ' ' + r.status, 'l', STATUS[r.status][1]);
      cell(tr, r.pvs != null ? 'Projected ' + fmt.chg(r.pvs) + ' against last year, ' + range(r.lo, r.hi) + ' vs ' + fmt.money(r.lyfull) : 'No full prior year on record, so no comparison yet. ' + fmt.money(r.ytd) + ' raised so far.', 'l'); return tr;
    }));
  });

  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  dash.draw('months', (box) => {
    const st = dash.data('months').status;
    const rows = get('months'); if (!rows) { box.replaceChildren(msg(st === 'error' ? 'Couldn’t load the months.' : '—')); setState(box, st); return; }
    setState(box, 'ok');
    if (!rows.length) { box.replaceChildren(msg('No account with a full prior year has monthly revenue yet.')); return; }
    const W = Math.max(320, box.clientWidth || 520), H = 300, m = { l: 56, r: 10, t: 14, b: 30 };
    const ymax = d3.max(rows, (r) => Math.max(r.ty, r.ly)) * 1.1 || 1, x = d3.scaleBand().domain(rows.map((r) => r.month)).range([m.l, W - m.r]).padding(0.25), y = d3.scaleLinear().domain([0, ymax]).nice().range([H - m.b, m.t]);
    const svg = d3.create('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Revenue by month this year for accounts with a full prior year, with a tick for the same month last year. ' + rows.map((r) => `${MON[r.month - 1]}: ${fmt.money(r.ty)} this year, ${fmt.money(r.ly)} last year`).join('; ') + '.');
    y.ticks(4).forEach((t) => { svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).attr('stroke', 'var(--cds-chart-grid)'); svg.append('text').attr('x', m.l - 6).attr('y', y(t) + 4).attr('text-anchor', 'end').text(fmt.money(t)); });
    const tipEl = mkTip(), tp = tipApi(box, tipEl);
    rows.forEach((r) => {
      const g = svg.append('g').attr('tabindex', 0).attr('role', 'img').attr('aria-label', `${MON[r.month - 1]}: ${fmt.money(r.ty)} this year, ${fmt.money(r.ly)} last year`);
      g.append('rect').attr('x', x(r.month)).attr('y', y(r.ty)).attr('width', x.bandwidth()).attr('height', y(0) - y(r.ty)).style('fill', dash.colors[0]);
      g.append('line').attr('x1', x(r.month) - 2).attr('x2', x(r.month) + x.bandwidth() + 2).attr('y1', y(r.ly)).attr('y2', y(r.ly)).style('stroke', 'var(--color-fg)').attr('stroke-width', 3);
      svg.append('text').attr('x', x(r.month) + x.bandwidth() / 2).attr('y', H - 10).attr('text-anchor', 'middle').text(MON[r.month - 1]);
      const on = () => tp.show(`${MON[r.month - 1]}: ${fmt.money(r.ty)} this year, ${fmt.money(r.ly)} last year`, x(r.month), y(r.ty));
      g.on('mouseenter', on).on('focus', on).on('mouseleave', tp.hide).on('blur', tp.hide);
    });
    box.replaceChildren(svg.node(), tipEl, altTable(['Month', 'This year', 'Last year'], rows.map((r) => [MON[r.month - 1], fmt.money(r.ty), fmt.money(r.ly)])));
  });
  dash.draw('chans', (body) => {
    const rows = get('channels'); if (!rows) { body.replaceChildren(); return; }
    if (!rows.length) { const tr = document.createElement('tr'); cell(tr, 'No account with a full prior year has channel revenue yet.', 'l', 'ap-mu').colSpan = 6; body.replaceChildren(tr); return; }
    body.replaceChildren(...rows.map((r) => { const tr = document.createElement('tr'); tr.setAttribute('data-key', encodeURIComponent(r.channel)); cell(tr, r.channel, 'l'); cell(tr, fmt.money(r.ty)); cell(tr, fmt.pct(r.share, 1)); cell(tr, fmt.chg(r.chg), '', r.chg == null ? 'ap-mu' : r.chg >= 0 ? 'ap-good' : 'ap-bad'); cell(tr, r.up); cell(tr, r.best, 'l'); return tr; }));
  });
  dash.draw('cov', (body) => {
    const rows = get('coverage'); if (!rows) { body.replaceChildren(); return; }
    body.replaceChildren(...rows.map((r) => { const tr = document.createElement('tr'); tr.setAttribute('data-key', encodeURIComponent(r.check)); cell(tr, r.check, 'l'); cell(tr, r.accounts); cell(tr, r.gaps, 'l'); cell(tr, r.affects, 'l'); return tr; }));
  });
})();
