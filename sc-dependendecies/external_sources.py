"""Reviewed integration probes for official registries and repositories outside GitHub/GitLab."""
import base64
import logging
import re
import time

LOG = logging.getLogger('softcatala-reuse')


def scan_external_sources(client, probes, findings, warnings, checkpoint=None):
    for probe in probes:
        LOG.info('External source: %s', probe['id'])
        try:
            evidence_url = probe['evidence_url']
            supporting_evidence = []
            if probe['kind'] == 'gitiles_text':
                url = probe['url']
                if probe.get('dependency_url'):
                    encoded = client.get(probe['dependency_url'], text_response=True)
                    dependency = base64.b64decode(encoded).decode('utf-8')
                    match = re.search(probe['dependency_revision_pattern'], dependency)
                    if not match:
                        raise ValueError('The consumer no longer declares the dictionary repository dependency')
                    revision = match.group(1)
                    url = url.replace('/+/HEAD/', '/+/' + revision + '/')
                    evidence_url = evidence_url.replace('/+/HEAD/', '/+/' + revision + '/')
                    supporting_evidence.append({'url': probe['dependency_evidence_url'], 'text': match.group(0)})
                encoded = client.get(url, text_response=True)
                content = base64.b64decode(encoded).decode(probe.get('encoding', 'utf-8'))
                if not all(term.casefold() in content.casefold() for term in probe['expected_terms']):
                    raise ValueError('Expected origin/attribution is missing')
                hits = [{'line': number, 'text': line.strip()[:500]}
                        for number, line in enumerate(content.splitlines(), 1)
                        if any(term.casefold() in line.casefold() for term in probe['expected_terms'])]
                version = probe.get('source_version', '')
            elif probe['kind'] == 'mozilla_addon':
                data = client.get(probe['url'])
                authors = [author['name'] for author in data.get('authors', [])]
                version_data = data.get('current_version') or {}
                compatibility = version_data.get('compatibility', {})
                if (data.get('type') != 'dictionary' or 'firefox' not in compatibility
                        or not any(probe['author_contains'].casefold() in name.casefold() for name in authors)):
                    raise ValueError('Dictionary origin or Firefox compatibility is missing')
                version = version_data['version']
                hits = [{'line': 0, 'text': f'type=dictionary; authors={", ".join(authors)}; Firefox compatibility={compatibility["firefox"]}; version={version}'}]
            else:
                raise ValueError('Unknown source probe kind: ' + probe['kind'])
            findings.append({'platform': 'Altres', 'project': probe['project'],
                             'project_url': probe['project_url'], 'resource': probe['resource'],
                             'status': 'confirmed', 'type': 'third_party_integration',
                             'path': probe['path'], 'evidence_url': evidence_url,
                             'hits': hits, 'fork': False, 'stars': None,
                             'source_probe': probe['id'], 'source_version': version,
                             'integration_context': probe['integration_context'],
                             'integration_note': probe['integration_note'],
                             'supporting_evidence': supporting_evidence,
                             'verified_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())})
        except Exception as exc:
            # A failed probe must not leave an old positive result in a refreshed report.
            warnings.append(f'External source could not be verified ({probe["id"]}): {exc}')
        if checkpoint:
            checkpoint('External source: ' + probe['id'])
