#!/usr/bin/env python3
"""Find explicit Catalan-resource reverse dependencies in Debian Packages indexes.

Results are package-level discovery evidence, not confirmed product integrations.
Only named Catalan resources count; generic hunspell dependencies are excluded.
"""
import argparse
import hashlib
import lzma
import re
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from storage import atomic_write, write_csv, write_json

SEEDS = ('hunspell-ca', 'aspell-ca', 'hyphen-ca', 'mythes-ca', 'icatalan', 'wcatalan', 'myspell-ca')
FIELDS = ('Pre-Depends', 'Depends', 'Recommends', 'Suggests', 'Enhances')


def records(text):
    record = {}
    key = None
    for line in text.splitlines() + ['']:
        if not line:
            if record:
                yield record
            record, key = {}, None
        elif line[0].isspace() and key:
            record[key] += ' ' + line.strip()
        elif ':' in line:
            key, value = line.split(':', 1)
            record[key] = value.strip()


def dependencies(packages, seeds=SEEDS):
    targets = set(seeds)
    rows = []
    for package in packages:
        if package['Package'] in targets:
            continue  # Dependencies within the resource family are not external reuse.
        for field in FIELDS:
            for group in package.get(field, '').split(','):
                alternatives = group.strip().split('|')
                for alternative in alternatives:
                    match = re.match(r'\s*([a-z0-9][a-z0-9+.-]*)(?::[a-z0-9-]+)?', alternative)
                    if not match or match[1] not in targets:
                        continue
                    kind = ('alternative' if len(alternatives) > 1 else
                            'mandatory' if field in ('Depends', 'Pre-Depends') else
                            'recommended' if field == 'Recommends' else
                            'suggested' if field == 'Suggests' else 'enhancement')
                    rows.append(dict(binary_package=package['Package'],
                                     source_package=package.get('Source', package['Package']).split()[0],
                                     version=package.get('Version', ''),
                                     homepage=package.get('Homepage', ''),
                                     target_package=match[1], field=field,
                                     relation_kind=kind, expression=group.strip()))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', default='stable')
    parser.add_argument('--architecture', default='amd64')
    parser.add_argument('--component', default='main')
    parser.add_argument('--output', type=Path, default=Path('debian-report'))
    parser.add_argument('--cache', type=Path, default=Path('.cache/debian'))
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    for value in (args.suite, args.architecture, args.component):
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', value):
            parser.error('Invalid index path component')
    url = f'https://deb.debian.org/debian/dists/{args.suite}/{args.component}/binary-{args.architecture}/Packages.xz'
    args.cache.mkdir(parents=True, exist_ok=True)
    cached = args.cache / f'{args.suite}-{args.component}-{args.architecture}-Packages.xz'
    if args.offline and not cached.exists():
        parser.error('No cached index; run once without --offline')
    if not args.offline and (args.refresh or not cached.exists()):
        print(f'Downloading {url}', flush=True)
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        lzma.decompress(data)  # Validate before replacing the previous cache.
        atomic_write(cached, data)
    index_bytes = cached.read_bytes()
    packages = list(records(lzma.decompress(index_bytes).decode('utf-8')))
    rows = dependencies(packages)
    report = dict(index_url=url, suite=args.suite, architecture=args.architecture,
                  index_sha256=hashlib.sha256(index_bytes).hexdigest(),
                  index_cached_at=datetime.fromtimestamp(cached.stat().st_mtime, timezone.utc).isoformat(),
                  generated_at=datetime.now(timezone.utc).isoformat(),
                  scope='Explicit package relationships; optional and alternative dependencies do not prove installation or use. Binary/source packages are not products.',
                  seeds=[p for p in packages if p['Package'] in SEEDS],
                  missing_seeds=sorted(set(SEEDS) - {p['Package'] for p in packages}),
                  relations=rows,
                  relationship_count=len({(r['binary_package'], r['field'], r['expression']) for r in rows}),
                  binary_packages=sorted({r['binary_package'] for r in rows}),
                  source_packages=sorted({r['source_package'] for r in rows}))
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / 'dependencies.json', report)
    write_csv(args.output / 'dependencies.csv', rows,
              ['binary_package', 'source_package', 'version', 'homepage', 'target_package', 'field', 'relation_kind', 'expression'])
    print(f'{report["relationship_count"]} relationships ({len(rows)} target references); {len(report["binary_packages"])} binary packages; {len(report["source_packages"])} source packages.')


if __name__ == '__main__':
    main()
