"""Export Debian package evidence for explicitly reviewed product identities."""
import argparse
from copy import deepcopy
from pathlib import Path
from storage import read_json, write_json


def reviewed_integrations(report, identities, catalog):
    """Group relationships by evidence file so report deduplication loses no targets."""
    catalog = deepcopy(catalog)
    findings = {}
    seen_relations = set()
    seed_metadata = {p['Package']: p for p in report['seeds']}
    for identity in identities:
        if not identity.get('reviewed'):
            continue
        urls = []
        for row in report['relations']:
            if row['binary_package'] not in identity['packages'] or row['target_package'] not in identity['allowed_targets']:
                continue
            url = f'https://packages.debian.org/{report["suite"]}/{row["binary_package"]}'
            urls.append(url)
            relation = {'Depends': 'obligatori', 'Pre-Depends': 'obligatori',
                        'Recommends': 'recomanat', 'Suggests': 'suggerit', 'Enhances': 'opcional'}[row['field']]
            if row['relation_kind'] == 'alternative':
                relation += ' com a alternativa'
            # Two targets in one alternative group are one product relationship.
            relation_key = (url, row["field"], row["expression"])
            if relation_key in seen_relations:
                continue
            seen_relations.add(relation_key)
            note = f'{row["target_package"]} {relation} a Debian'
            if identity['id'] == 'debian':
                note = f'{row["binary_package"]}: {note}'
            attribution = seed_metadata.get(row['target_package'], {}).get('Homepage', '')
            supporting = [{'url': report['index_url'], 'description': 'Dependència exacta a Packages'}]
            if row['target_package'] == 'mythes-ca':
                attribution = 'https://metadata.ftp-master.debian.org/changelogs/main/libr/libreoffice-dictionaries/stable_copyright'
                note += ' · tesaurus amb atribució Softcatalà'
            if attribution:
                supporting.append({'url': attribution, 'description': 'Origen o atribució del recurs'})
            key = (url, row['field'])
            hit = dict(line=0, text=f'{row["field"]}: {row["expression"]}')
            if key not in findings:
                findings[key] = dict(platform='Debian', project=identity['name'], project_name=identity['name'],
                                     project_url=url, resource='catalan-dict-tools', status='confirmed',
                                     type='third_party_integration', path=f'{row["binary_package"]}/{row["field"]}',
                                     evidence_url=url, hits=[], fork=False, stars=0, integration_note='',
                                     integration_kind=row['relation_kind'], package_version=row['version'],
                                     index_url=report['index_url'], index_sha256=report['index_sha256'],
                                     supporting_evidence=[])
            finding = findings[key]
            finding['hits'].append(hit)
            finding['integration_note'] += ('; ' if finding['integration_note'] else '') + note
            if finding['integration_kind'] != row['relation_kind']:
                finding['integration_kind'] = 'mixed'
            existing_urls = {s['url'] for s in finding['supporting_evidence']}
            finding['supporting_evidence'].extend(s for s in supporting if s['url'] not in existing_urls)
        if urls:
            product = next((p for p in catalog if p['id'] == identity['id']), None)
            if product is None:
                product = {k: identity[k] for k in ('id', 'name', 'organization', 'url', 'kind', 'reviewed')}
                product.update(repositories=[], identity_source=urls[0])
                catalog.append(product)
            product['repositories'] = sorted(set(product['repositories'] + urls))
    return list(findings.values()), catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path('debian-report/dependencies.json'))
    parser.add_argument('--identities', type=Path, default=Path('debian-products.json'))
    parser.add_argument('--catalog', type=Path, default=Path('products_catalog.json'))
    parser.add_argument('--output', type=Path, default=Path('debian-report/reviewed-integrations.json'))
    args = parser.parse_args()
    findings, catalog = reviewed_integrations(read_json(args.report), read_json(args.identities), read_json(args.catalog))
    write_json(args.output, findings)
    write_json(args.catalog, catalog)
    print(f'{len(findings)} reviewed Debian evidence records exported')


if __name__ == '__main__':
    main()
