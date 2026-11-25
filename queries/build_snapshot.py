"""Builds data/snapshot.json from data/raw/<account_id>.json (one `portfolio.py` result per account) and data/catalog.json
(account_id, name, type from the Engine 9 account catalog). Accounts with no type are left out by decision; accounts with a
type but no raw file yet are listed as `pending`. Usage: python3 queries/build_snapshot.py"""
import json, os, glob
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
cat = json.load(open(os.path.join(root, 'data/catalog.json')))
rows, as_of = [], ''
for aid, name, typ in cat:
    r = {'account_id': aid, 'name': name, 'type': typ}
    p = os.path.join(root, 'data/raw', aid + '.json')
    if typ is None:
        r['state'] = 'excluded'            # no account type in Engine 9: left out of the portfolio
    elif os.path.exists(p):
        raw = json.load(open(p)); as_of = raw['as_of']
        r['state'] = 'loaded'
        for k, v in raw.items():
            if k in ('chan', 'mon', 'first_gift', 'as_of'): r[k] = v
            else: r[k] = float(v)
    else:
        r['state'] = 'pending'
    rows.append(r)
meta = [{'label': 'Query', 'value': 'queries/portfolio.py, run on each account with the Engine 9 sql tool'},
        {'label': 'Account type', 'value': 'Engine 9 account catalog (account search), type field'},
        {'label': 'As of', 'value': as_of}]
json.dump({'rows': rows, 'meta': meta}, open(os.path.join(root, 'data/snapshot.json'), 'w'), separators=(',', ':'))
print(len(rows), {s: sum(1 for r in rows if r['state'] == s) for s in ('loaded', 'pending', 'excluded')}, as_of)
