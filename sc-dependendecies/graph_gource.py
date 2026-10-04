"""Deterministic static SVG tree inspired by Gource; no external dependencies."""
from collections import defaultdict
import html
import json
import math
from pathlib import Path
from urllib.parse import urlparse
from product_catalog import is_usage


def project_names(report):
    """Display labels are aliases, not a claim that repositories are one product."""
    mapping_path = Path(__file__).resolve().with_name('project_names.json')
    aliases = json.loads(mapping_path.read_text(encoding='utf-8')) if mapping_path.exists() else {}
    aliases = {key.casefold(): value for key, value in aliases.items()}
    return {f['project_url']: f.get('product_name') or aliases.get(f['project_url'].casefold(), aliases.get(f['project'].casefold(),
            f.get('project_name') or f['project'].rsplit('/', 1)[-1])) for f in report['findings']}


def resource_url(metadata):
    """Use explicit provenance, including older reports with GitHub URL terms."""
    if metadata.get('source_url'):
        return metadata['source_url']
    for term in metadata.get('terms', []):
        if term.startswith(('https://github.com/', 'http://github.com/')):
            return term
        if term.startswith('github.com/'):
            return 'https://' + term
    return None


def resource_label(name, metadata):
    lines = [name]
    source_url = resource_url(metadata)
    if source_url:
        lines.append('(' + source_url + ')')
    if metadata.get('maintenance_relationship'):
        lines.append('(manteniment Softcatalà · OpenNMT)')
    return '\n'.join(lines)


def gource_svg(report):
    labels = project_names(report)
    if report.get('view') == 'products':
        labels = {f['project_url']: labels[f['project_url']] + (' · ' + f['integration_note'] if f.get('integration_note') else '')
                  for f in report['findings']}
    labels = {f['project_url']: labels[f['project_url']] +
              '\n(' + (f.get('product_url') or f['project_url']) + ')'
              for f in report['findings']}
    groups = defaultdict(dict)
    for finding in report['findings']:
        if not is_usage(finding):
            continue
        groups[finding['resource']].setdefault(finding.get('product_id') or finding['project_url'], finding)
    resources = sorted(groups, key=lambda name: (-len(groups[name]), name))
    resource_metadata = {r['name']: r for r in report.get('resources', [])}
    resource_labels = {r: resource_label(r, resource_metadata.get(r, {})) for r in resources}
    links = sum(len(group) for group in groups.values())
    projects = {url for group in groups.values() for url in group}
    product_view = report.get('view') == 'products'
    unit = 'productes amb identitat revisada' if product_view else 'repositoris'
    leaf_font = 24 if product_view and links < 40 else 16
    label_space = max(400 if product_view else 530, max((max(map(len, labels[f['project_url']].splitlines())) for group in groups.values() for f in group.values()), default=0) * leaf_font * 0.65 + 50)
    branch_label_width = max((len(line) * (21 if index == 0 else 16.8) * 0.65
                              for text in resource_labels.values() for index, line in enumerate(text.splitlines())), default=0)
    branch_radius = max(600 if product_view else 700, (links + len(resources) * 7) * 4,
                        (branch_label_width + 60) / 0.66)
    size = math.ceil(max(2200 if product_view else 2800, 2 * (label_space + branch_radius)))
    height = size + 220
    cx, cy = size / 2, size / 2 + 120
    radius = size / 2 - label_space
    slots = max(1, links + len(resources) * 7)
    palette = ['#54e0b2', '#70b7ff', '#f9ba65', '#ce94ff', '#fb83ad', '#a5e770', '#64dbe8']
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{height}" viewBox="0 0 {size} {height}" role="img" aria-labelledby="title description">',
             '<title id="title">Reutilització de Softcatalà · arbre estàtic</title>',
             '<desc id="description">Softcatalà al centre, recursos com a branques, organitzacions i projectes com a fulles. Només ús o integració amb evidència; sense forks.</desc>',
             '<defs><radialGradient id="bg"><stop stop-color="#14283b"/><stop offset="1" stop-color="#060c14"/></radialGradient><filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter></defs>',
             '<rect width="100%" height="100%" fill="url(#bg)"/>',
             '<g fill="#dce9f8" font-family="sans-serif">',
             '<text x="64" y="72" font-size="42" font-weight="700">Softcatalà · un ecosistema compartit</text>',
             f'<text x="66" y="115" font-size="21" fill="#91a6bf">{len(projects)} {unit} · {len(resources)} recursos · {links} connexions amb evidència d’ús o integració · sense forks</text>',
             f'<text x="66" y="151" font-size="17" fill="#91a6bf">{"Informe parcial · " if report.get("run_status") == "running" else ""}{html.escape(report.get("generated_at", ""))}</text></g>']
    branches, nodes = [], []

    def point(angle, distance):
        return cx + math.cos(angle) * distance, cy + math.sin(angle) * distance

    def branch(start, end, color, width):
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        # Bend branches slightly to suggest the organic tree layout of Gource.
        mx += (end[1] - start[1]) * 0.09
        my -= (end[0] - start[0]) * 0.09
        branches.append(f'<path d="M {start[0]:.2f} {start[1]:.2f} Q {mx:.2f} {my:.2f} {end[0]:.2f} {end[1]:.2f}" fill="none" stroke="{color}" stroke-opacity="0.5" stroke-width="{width}"/>')

    def dot(x, y, color, r):
        return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r*1.8}" fill="{color}" opacity="0.42" filter="url(#glow)"/>'
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{color}"/>')

    def label(x, y, angle, text, color, font_size=17, offset=12):
        degrees = math.degrees(angle)
        left = math.cos(angle) < 0
        rotation = degrees + (180 if left else 0)
        dx = -offset if left else offset
        anchor = 'end' if left else 'start'
        lines = text.splitlines()
        content = html.escape(lines[0]) + ''.join(
            f'<tspan x="{dx}" dy="1.3em" font-size="{font_size * 0.8:g}" fill="#91a6bf">{html.escape(line)}</tspan>'
            for line in lines[1:])
        return (f'<text transform="translate({x:.2f} {y:.2f}) rotate({rotation:.2f})" x="{dx}" y="5" '
                f'text-anchor="{anchor}" font-family="sans-serif" font-size="{font_size}" fill="{color}" '
                f'stroke="#09111c" stroke-width="4" paint-order="stroke">{content}</text>')

    cursor = 0
    for index, resource in enumerate(resources):
        color = palette[index % len(palette)]
        # Keep each organization's leaves contiguous so shared branches do not
        # cross the leaves belonging to other organizations.
        rows = sorted(groups[resource].values(), key=lambda f: (
            (f.get('product_organization') or f['project'].split('/')[0]).casefold(),
            (f.get('product_name') or f['project']).casefold()))
        positions = []
        for offset, finding in enumerate(rows):
            angle = -math.pi / 2 + 2 * math.pi * (cursor + offset + 0.5) / slots
            positions.append((finding, angle))
        angle = (positions[0][1] + positions[-1][1]) / 2
        rx, ry = point(angle, radius * 0.34)
        branch(point(angle, 90), (rx, ry), color, 3.2)
        nodes.append(dot(rx, ry, color, 10))
        nodes.append(label(rx, ry, angle, resource_labels[resource], color, 21, 18))
        organizations = defaultdict(list)
        for finding, leaf_angle in positions:
            organizations[finding.get('product_organization') or finding['project'].split('/')[0]].append((finding, leaf_angle))
        for organization, leaves in organizations.items():
            org_angle = sum(a for _, a in leaves) / len(leaves)
            ox, oy = point(org_angle, radius * 0.66)
            branch((rx, ry), (ox, oy), color, 1.7)
            nodes.append(f'<g><title>{html.escape(organization)} · {len(leaves)} projectes</title>{dot(ox, oy, color, 5)}</g>')
            for finding, leaf_angle in leaves:
                x, y = point(leaf_angle, radius)
                branch((ox, oy), (x, y), color, 1)
                url = finding['evidence_url']
                if urlparse(url).scheme not in ('https', 'http'):
                    url = '#'
                title = f"{labels[finding['project_url']]} · {finding['project']} · {finding['platform']} · {finding['type']}\n{finding['path']}"
                if finding.get('evidence'):
                    title += f"\n{len(finding['evidence'])} evidències · {len(finding['matched_repositories'])} repositoris"
                nodes.append(f'<a href="{html.escape(url, quote=True)}" target="_blank"><title>{html.escape(title)}</title>'
                             + dot(x, y, color, 4)
                             + label(x, y, leaf_angle, labels[finding['project_url']], '#e4eef9', leaf_font)
                             + '</a>')
        cursor += len(rows) + 7
    parts.extend(branches)
    parts.extend(nodes)
    parts += [f'<circle cx="{cx}" cy="{cy}" r="83" fill="#ffcb70" opacity="0.15" filter="url(#glow)"/>',
              f'<circle cx="{cx}" cy="{cy}" r="78" fill="#122031" stroke="#ffd17b" stroke-width="2"/>',
              f'<text x="{cx}" y="{cy+8}" text-anchor="middle" font-family="sans-serif" font-size="27" font-weight="700" fill="#ffe1a2">Softcatalà</text>',
              f'<text x="64" y="{height-68}" font-family="sans-serif" font-size="18" fill="#91a6bf">Centre: Softcatalà · branques: recursos · nodes intermedis: organitzacions · fulles: projectes</text>',
              f'<text x="64" y="{height-36}" font-family="sans-serif" font-size="16" fill="#91a6bf">Cada projecte enllaça a una evidència. Les connexions no estimen usuaris ni proven ús en producció.</text>', '</svg>']
    return '\n'.join(parts)
