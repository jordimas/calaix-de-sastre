"""Resolve repositories to reviewed software products using explicit identities."""
from collections import defaultdict

USAGE_TYPES = {'dependency', 'installation', 'distribution', 'bundled_dictionary',
               'code_usage', 'third_party_integration'}
DEFAULT_KINDS = ('application', 'service', 'distribution', 'library', 'developer-tool', 'model')


def is_usage(finding):
    return (not finding.get('fork') and finding['status'] == 'confirmed'
            and finding['type'] in USAGE_TYPES)


def product_report(report, catalog, kinds=DEFAULT_KINDS):
    by_repository = {}
    for product in catalog:
        if not product.get('reviewed') or product.get('kind') not in kinds:
            continue
        for repository in product['repositories']:
            key = repository.rstrip('/').casefold()
            if key in by_repository and by_repository[key]['id'] != product['id']:
                raise ValueError(f'Repository assigned to two products: {repository}')
            by_repository[key] = product
    grouped = defaultdict(list)
    identities, unassigned = {}, {}
    for finding in report['findings']:
        if not is_usage(finding):
            continue
        key = finding['project_url'].rstrip('/').casefold()
        product = by_repository.get(key)
        if product is None:
            unassigned[key] = {'project': finding['project'], 'project_url': finding['project_url']}
            continue
        identities[product['id']] = product
        grouped[product['id']].append(finding)
    products, graph_findings = [], []
    priority = {'code_usage': 0, 'third_party_integration': 1, 'dependency': 2,
                'installation': 3, 'bundled_dictionary': 4, 'distribution': 5}
    for product_id in sorted(grouped):
        identity, evidence = identities[product_id], grouped[product_id]
        resources = sorted({f['resource'] for f in evidence})
        products.append({**identity, 'resources': resources,
                         'matched_repositories': sorted({f['project_url'] for f in evidence}),
                         'integration_notes': sorted({f['integration_note'] for f in evidence if f.get('integration_note')}),
                         'evidence': evidence})
        for resource in resources:
            matches = [f for f in evidence if f['resource'] == resource]
            # Prefer runtime code over test fixtures when selecting the click target.
            matches.sort(key=lambda f: (f['path'].startswith(('test/', 'tests/', 'packages/tests/')),
                                        priority[f['type']], f['project'], f['path']))
            representative = matches[0]
            graph_findings.append({**representative, 'product_id': product_id,
                                   'product_name': identity['name'], 'project_name': identity['name'],
                                   'product_organization': identity['organization'],
                                   'product_url': identity['url'],
                                   'matched_repositories': sorted({f['project_url'] for f in matches}),
                                   'evidence': matches})
    return {**report, 'view': 'products', 'findings': graph_findings,
            'products': products, 'product_kinds': list(kinds),
            'unassigned_repositories': sorted(unassigned.values(), key=lambda f: f['project'].casefold()),
            'identity_policy': 'Reviewed catalog identities; no inference from vendored paths or repository names'}


def products_html(report):
    """A static landing page; product evidence stays in the downloadable JSON."""
    import html
    count = len(report['products'])
    unassigned = len(report['unassigned_repositories'])
    status = 'Parcial: la cerca continua.' if report.get('run_status') == 'running' else 'Cerca finalitzada; el catàleg de productes continua sent parcial.'
    rows = []
    for product in report['products']:
        links = ' · '.join(f'<a href="{html.escape(f["evidence_url"], quote=True)}">{html.escape(f["project"] + "/" + f["path"])}</a>' for f in product['evidence'])
        links += ''.join(f' · <a href="{html.escape(s["url"], quote=True)}">Dependència declarada pel producte</a>'
                         for f in product['evidence'] for s in f.get('supporting_evidence', []))
        notes = '; '.join(product.get('integration_notes', []))
        rows.append(f'<tr><td>{html.escape(product["name"])} '
                    f'(<a href="{html.escape(product["url"], quote=True)}">{html.escape(product["url"])}</a>)'
                    f'<br>{html.escape(notes)}</td>'
                    f'<td>{html.escape(", ".join(product["resources"]))}</td><td>{links}</td></tr>')
    return f'''<!doctype html><html lang="ca"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Productes que reutilitzen Softcatalà</title><style>body{{font:16px system-ui;margin:30px;color:#17283b;background:#f6f8fc}}a{{color:#185fa9}}td,th{{text-align:left;padding:12px;border-bottom:1px solid #cdd8e6}}table{{border-collapse:collapse;width:100%}}object{{width:100%;height:85vh}}</style>
<h1>Productes que reutilitzen Softcatalà</h1><p>{count} productes amb identitat revisada i evidència d’ús o integració. Cada producte apareix una vegada per recurs, encara que tingui diversos repositoris.</p>
<p>{html.escape(status)} {unassigned} repositoris amb indicis d’ús queden fora d’aquesta vista perquè no tenen una identitat revisada dins les categories seleccionades.</p>
<p><a href="graph-products.svg">Obre el gràfic estàtic</a> · <a href="products.json">Dades i evidències</a> · <a href="index.html">Auditoria de repositoris</a></p>
<object type="image/svg+xml" data="graph-products.svg"><a href="graph-products.svg">Gràfic SVG</a></object>
<table><thead><tr><th>Producte</th><th>Recursos</th><th>Evidències als repositoris</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>La identitat del producte es revisa al catàleg; la classificació de l’ús és una regla sobre el codi i requereix revisió abans de publicar conclusions. No estima usuaris ni prova desplegaments en producció.</p></html>'''
