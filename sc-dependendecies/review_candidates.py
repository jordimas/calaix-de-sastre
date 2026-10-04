"""Fetch review material for currently confirmed, unmapped resource candidates."""
from pathlib import Path
from api_client import Client, github_token
from github_review import decode_contents, fetch_file
from storage import read_json, write_json


def main():
    report = read_json('softcatala-reuse-report/reuse.json')
    findings = [f for f in report['findings'] if f['status'] == 'confirmed' and
                f['resource'] in ('open-dubbing', 'nmt-softcatala', 'sinonims-cat')]
    client = Client('https://api.github.com', github_token(), Path('.cache/github'))
    result = {}
    for repository in sorted({f['project'] for f in findings} | {'ZalozbaDev/open-dubbing'}):
        print(repository, flush=True)
        record = {}
        for key, endpoint in [('metadata', f'/repos/{repository}'), ('readme', f'/repos/{repository}/readme')]:
            try:
                data = client.get(endpoint)
                record[key] = (decode_contents(data)
                               if key == 'readme' else data)
            except Exception as exc:
                record[key + '_error'] = str(exc)
        record['evidence_files'] = []
        for finding in findings:
            if finding['project'] != repository:
                continue
            revision = finding['evidence_url'].split('/blob/')[1].split('/')[0]
            try:
                content = fetch_file(client, repository, finding['path'], revision)['content']
                record['evidence_files'].append({'finding': finding, 'content': content})
            except Exception as exc:
                record['evidence_files'].append({'finding': finding, 'error': str(exc)})
        result[repository] = record
        write_json('research/candidate-review-material.json', result)


if __name__ == '__main__':
    main()
