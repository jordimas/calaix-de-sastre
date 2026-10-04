"""Save GitHub files and metadata as review material, without cloning repositories."""
import argparse
from pathlib import Path
from api_client import Client, github_token
from github_review import fetch_file
from storage import read_json, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository')
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--ref')
    args = parser.parse_args()
    client = Client('https://api.github.com', github_token(), Path('.cache/github'))
    metadata = client.get('/repos/' + args.repository)
    ref = args.ref or client.get('/repos/' + args.repository + '/commits/' + metadata['default_branch'])['sha']
    result = dict(metadata=metadata, revision=ref, files=[])
    output = Path('research/hf-review')
    output.mkdir(parents=True, exist_ok=True)
    dest = output / (args.repository.replace('/', '__') + '.json')
    if dest.exists():
        previous = read_json(dest)
        if previous.get('revision') == ref:
            result['files'] = [f for f in previous['files'] if f['path'] not in args.paths]
    for path in args.paths:
        try:
            result['files'].append(fetch_file(client, args.repository, path, ref))
        except Exception as exc:
            result['files'].append(dict(path=path, error=str(exc)))
    write_json(dest, result)
    print(dest)


if __name__ == '__main__':
    main()
