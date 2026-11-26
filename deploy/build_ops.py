#!/usr/bin/env python3
"""Build the db_write batches that publish the Agency Portfolio page.

usage: python3 deploy/build_ops.py --blob-url /_blob/<id> [--versions versions.json]

Writes deploy/out/batch-1.json (small documents), batch-2.json (index.html) and batch-3.json (app.js).
Each file is {"ops": [...]}: send its ops array as the `ops` of one db_write call (arguments must stay under
64 KB, so the page files go in their own calls). `--versions` is an optional JSON map of document path to
current version, needed (as ifVersion) when the document already exists in the artifact.
"""
import argparse, datetime, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, '..', 'page')
OUT = os.path.join(HERE, 'out')


def load(name):
    return open(os.path.join(PAGE, name), encoding='utf-8').read()


def op(path, data, versions):
    o = {'op': 'set', 'path': path, 'data': data}
    if path in versions:
        o['ifVersion'] = versions[path]
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blob-url', required=True, help='/_blob/<id> returned by uploading data/snapshot.json')
    ap.add_argument('--versions', help='JSON file mapping document path to its current version')
    a = ap.parse_args()
    versions = json.load(open(a.versions)) if a.versions else {}
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    ds = json.loads(load('dataset-snapshot.json').replace('{{BLOB_URL}}', a.blob_url).replace('{{UPDATED_AT}}', now))
    batches = {
        'batch-1.json': [op('dash/meta', json.loads(load('meta.json')), versions),
                         op('dash/params', json.loads(load('params.json')), versions),
                         op('dash/look', json.loads(load('look.json')), versions),
                         op('datasets/snapshot', ds, versions)],
        'batch-2.json': [op('files/index.html', {'text': load('index.html')}, versions)],
        'batch-3.json': [op('files/app.js', {'text': load('app.js')}, versions)],
    }
    os.makedirs(OUT, exist_ok=True)
    for name, ops in batches.items():
        body = json.dumps({'ops': ops}, ensure_ascii=False)
        size = len(body.encode('utf-8'))
        assert size < 60000, f'{name} is {size} bytes; split it'
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(body)
        print(name, size, 'bytes,', len(ops), 'op(s)')


if __name__ == '__main__':
    main()
