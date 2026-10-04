"""Discover public Hugging Face resources for the reuse scanner, with pagination."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from storage import cache_path, read_json, write_json


def resource(kind, identifier):
    prefix = {'model': '', 'dataset': 'datasets/', 'space': 'spaces/'}[kind]
    url = 'https://huggingface.co/' + prefix + identifier
    return dict(name=f'HF {kind}: {identifier}', terms=[identifier, url],
                queries=[identifier], source_platform='Hugging Face',
                source_kind=kind, source_url=url, identifier=identifier)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--org', default='softcatala')
    parser.add_argument('--output', type=Path, default=Path('huggingface-resources.json'))
    parser.add_argument('--cache', type=Path, default=Path('.cache/huggingface'))
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--fallback-file', type=Path, help='Reviewed web snapshot to use if the API is unavailable; coverage remains partial')
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    resources = []
    for kind in ('model', 'dataset', 'space'):
        url = 'https://huggingface.co/api/' + kind + 's?' + urlencode({'author': args.org, 'limit': 100})
        seen = set()
        while url:
            if url in seen or urlparse(url).hostname != 'huggingface.co':
                raise ValueError('Invalid or repeated pagination URL')
            seen.add(url)
            cached = cache_path(args.cache, url)
            if cached.exists() and (args.offline or not args.refresh):
                page = read_json(cached)
            else:
                try:
                    if args.offline:
                        raise ValueError('Missing offline cache: ' + url)
                    with urlopen(Request(url, headers={'User-Agent': 'softcatala-reuse-audit/1.0'}), timeout=15) as response:
                        data = json.load(response)
                        link = response.headers.get('Link', '')
                except Exception as exc:
                    if not args.fallback_file:
                        raise
                    print(f'Partial Hugging Face discovery: {kind} API unavailable ({exc}); using reviewed web snapshot', file=sys.stderr)
                    resources.extend(r for r in read_json(args.fallback_file) if r['source_kind'] == kind
                                     and r['identifier'].split('/')[0].casefold() == args.org.casefold())
                    break
                match = re.search(r'<([^>]+)>;\s*rel="next"', link)
                page = dict(items=data, next=match[1] if match else None)
                write_json(cached, page, indent=None)
            resources.extend(resource(kind, item['id']) for item in page['items']
                             if item['id'].split('/')[0].casefold() == args.org.casefold())
            url = page['next']
    resources = list({r['name']: r for r in resources}.values())
    write_json(args.output, resources)
    print({kind: sum(r['source_kind'] == kind for r in resources) for kind in ('model', 'dataset', 'space')})


if __name__ == '__main__':
    main()
