#!/usr/bin/env python3
"""Find public reuse of Softcatalà resources; standard library only, Python 3.10+."""
from __future__ import annotations

import argparse
import html
import json
import logging
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import quote, urlparse

from graph_gource import gource_svg, project_names
from product_catalog import DEFAULT_KINDS, USAGE_TYPES, is_usage, product_report, products_html
from external_sources import scan_external_sources
from github_search import INDEX_MAX_BYTES, github_hits
from api_client import APIError, Client, github_token
from github_review import decode_contents
from storage import atomic_write, read_json, write_csv, write_json

LOG = logging.getLogger("softcatala-reuse")
DEFAULT_NAMES = (
    "whisper-ctranslate2", "catalan-dict-tools", "open-dubbing",
    "translation-memory-tools", "nmt-softcatala", "nmt-models",
    "parallel-catalan-corpus", "ca-text-corpus", "julibert", "sinonims-cat",
    "separador-sillabes", "nombres-en-lletres", "conjugador", "adaptadorvariants",
    "adaptago", "catalan-pology-rules", "text-metrics-service",
)
# Unique package identifiers can be searched without their owner. Generic names
# are searched as repository URLs to avoid false matches (e.g. "conjugador").
UNIQUE_NAMES = {
    "whisper-ctranslate2", "catalan-dict-tools", "open-dubbing",
    "translation-memory-tools", "nmt-softcatala", "parallel-catalan-corpus",
    "ca-text-corpus", "julibert", "sinonims-cat", "catalan-pology-rules",
}
TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".go", ".rs", ".cs", ".java", ".sh", ".ps1",
    ".json", ".toml", ".yaml", ".yml", ".xml", ".md", ".txt", ".nix",
    ".spec", ".ebuild", ".cfg", ".ini", ".pl", ".r", ".c", ".cpp",
}


def resource(name: str, org: str) -> dict:
    terms = [f"{org}/{name}", f"github.com/{org}/{name}"]
    if name in UNIQUE_NAMES:
        terms += [name, name.replace("-", "_")]
    queries = [name if name in UNIQUE_NAMES else f"github.com/{org}/{name}"]
    if org.casefold() == "softcatala" and name == "catalan-dict-tools":
        legacy = ["softcatala-spell", "ispellcat", "softcatala.org/diccionaris/actualitzacions"]
        terms += legacy
        queries += legacy
    return {"name": name, "terms": list(dict.fromkeys(terms)), "queries": queries,
            "source_url": f'https://github.com/{org}/{name}'}


def is_derivative(metadata):
    """Exclude declared forks/mirrors, including mirrors without fork lineage."""
    if metadata.get("fork") or metadata.get("forked_from_project") or metadata.get("mirror") or metadata.get("mirror_url"):
        return True
    name = metadata.get("full_name", metadata.get("path_with_namespace", ""))
    description = metadata.get("description") or ""
    return bool(re.search(r"(?:^|[-_/])mirrors?(?:$|[-_/])", name, re.I) or
                re.search(r"\bmirror(?:ed)? (?:of|from)\b|^mirror\b|\bfork(?:ed)? (?:of|from)\b", description, re.I))


def dictionary_path(resource_name, path):
    p = path.casefold()
    return (resource_name in {"catalan-dict-tools", "sinonims-cat"}
            and not p.startswith(("docs/", ".docs/"))
            and (Path(p).suffix in {".dic", ".aff"} or any(part in "/" + p for part in (
                "/resource/ca/", "/dictionaries/", "/dicts/", "/hunspell/", "/dict/", "/spell/"))))


def classify(path: str, content: str, item: dict) -> tuple[str, str, list[dict]]:
    """Conservative evidence classification, not a claim of production use."""
    hits = []
    for number, line in enumerate(content.splitlines(), 1):
        if any(term.casefold() in line.casefold() for term in item["terms"]):
            hits.append({"line": number, "text": line.strip()[:500]})
    if not hits:
        return "needs_review", "unverified_match", []
    p = path.casefold()
    if p.endswith(".po") or Path(p).name in {"authors", "contributors"}:
        return "excluded", "translation_credit", hits
    if any(part in p for part in ("awesome-", "top-pypi", "dataset_card", "model_cards",
                                  "pydigger", "sbom", "inventory")):
        return "excluded", "catalogue", hits
    suffix = Path(p).suffix
    lines = [h["text"] for h in hits]
    active = [line for line in lines if not line.startswith(("#", "//", "*", "<!--", "'"))]
    if p.endswith('/metadata') or p.endswith('/pkg-info'):
        # Distribution metadata often embeds another package's README and its
        # list of third-party users. It is not evidence of installing those users.
        package_name = re.search(r'^Name:\s*(.+)$', content, re.M | re.I)
        if not package_name or package_name[1].strip().casefold().replace('_', '-') != item['name'].casefold().replace('_', '-'):
            return 'needs_review', 'package_metadata_reference', hits
    if item.get('source_platform') == 'Hugging Face' and active:
        if suffix in {'.py', '.js', '.ts', '.sh', '.ps1', '.ipynb'} and any(
            re.search(r'\b(?:from_pretrained|load_dataset|load_dataset_builder|snapshot_download|hf_hub_download|WhisperModel|pipeline|InferenceClient)\s*\(|\b(?:curl|wget|huggingface-cli|hf download)\s', line)
            for line in active):
            return 'confirmed', 'code_usage', hits
    if p.endswith(".gitmodules") or any(part in p.split("/") for part in ("third_party", "third-party", "vendor", "vendored", "external")):
        if any("github.com/" in line.casefold() for line in lines):
            return "confirmed", "third_party_integration", hits
    if dictionary_path(item["name"], p) and any(
        term in content.casefold() for term in ("license", "llicència", "copyright", "based on", "source")):
        return "confirmed", "bundled_dictionary", hits
    if any(re.search(r"\b(?:pip3?|pipx|uvx|uv tool|uv add)\b.*(?:install|run)?", line)
           for line in active) and ("dockerfile" in p or suffix in {".sh", ".ps1", ".py", ".nix", ".spec", ".ebuild", ".yaml", ".yml"}):
        return "confirmed", "installation", hits
    dependency_file = Path(p).name in {
        "pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "pipfile",
        "package.json", "pom.xml", "apkbuild", "pkgbuild", "pkgfile",
    }
    if dependency_file and active:
        if Path(p).name == "package.json":
            try:
                manifest = json.loads(content)
                dependencies = {name: value for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
                                for name, value in manifest.get(section, {}).items()}
                if any(item["name"].casefold() == name.casefold() or any(term.casefold() in str(value).casefold() for term in item["terms"])
                       for name, value in dependencies.items()):
                    return "confirmed", "dependency", hits
            except (json.JSONDecodeError, AttributeError):
                pass
            return "needs_review", "configuration_reference", hits
        package = re.escape(item["name"])
        if Path(p).name in {"apkbuild", "pkgbuild", "pkgfile"} or any(
            re.search(rf'(?:^[\s\-\[\"\']*|[\"\']){package}(?:[\"\'\s<>=!~\[;]|$)', line, re.I)
            or "git+https://" in line for line in active):
            return "confirmed", "dependency", hits
    if suffix in {".nix", ".spec", ".ebuild"} and active:
        return "confirmed", "distribution", hits
    if suffix in {".py", ".js", ".ts", ".go", ".rs", ".cs", ".java", ".sh", ".ps1", ".r", ".pl"} and active:
        if any(re.search(r"(?:^|[;\s])(?:import\s|from\s\S+\s+import\s)|\brequire\s*\(|\b(?:subprocess\.(?:run|Popen|call)|run|exec|execFile|spawn|spawnSync|execSync|system|ProcessStartInfo)\s*\(|\b(?:curl|wget)\s", line, re.I) for line in active):
            return "confirmed", "code_usage", hits
        if p.endswith((".sh", ".ps1")) and any(re.match(r"(?:[\w./-]+\s+)?whisper[-_]ctranslate2(?:\s|$)", line) for line in active):
            return "confirmed", "code_usage", hits
    if suffix in {".toml", ".yaml", ".yml", ".cfg", ".ini", ".json", ".xml"} and active:
        return "needs_review", "configuration_reference", hits
    return "needs_review", "documentation_reference", hits


def add_finding(findings, *, platform, project, project_url, path, evidence_url,
                content, item, fork=False, stars=None, project_name=None):
    status, kind, hits = classify(path, content, item)
    if fork:
        status, kind = "excluded", "fork"
    findings.append({"platform": platform, "project": project,
                     "project_url": project_url, "resource": item["name"],
                     "status": status, "type": kind, "path": path,
                     "evidence_url": evidence_url, "hits": hits,
                     "fork": fork, "stars": stars,
                     "project_name": project_name or project.rsplit("/", 1)[-1]})


def discover_github(client, org, warnings):
    return [resource(r["name"], org) for r in client.pages(
        f"/orgs/{quote(org)}/repos", {}, warnings)
        if not r.get("fork") and r.get("visibility", "public") == "public"]


def scan_github(client, resources, args, findings, warnings, checkpoint=None):
    seen = set()
    for item in resources:
        queries = ['"' + term.replace('"', '') + '" -org:' + args.org + (' repo:' + repository if repository else '')
                   for term in item['queries'] for repository in (getattr(args, 'github_repo', None) or [None])]
        for query in queries:
            stats = {"files_read": 0, "files_skipped": 0}
            ledger = getattr(args, "github_searches", None)
            if ledger is not None:
                ledger[:] = [entry for entry in ledger if entry["query"] != query]
                ledger.append(stats)
            for hit in github_hits(client, query, warnings, max_pages=args.max_pages, stats=stats, checkpoint=checkpoint):
                repo = hit["repository"]
                project = repo["full_name"]
                if repo.get("private") or project.casefold().startswith(args.org.casefold() + "/"):
                    stats["files_skipped"] += 1
                    continue
                key = (project, hit["path"], item["name"])
                if key in seen:
                    continue
                seen.add(key)
                try:
                    metadata = client.get("/repos/" + project)
                    if is_derivative(metadata):
                        stats["files_skipped"] += 1
                        continue
                    match = re.search(r"/blob/([^/]+)/", hit["html_url"])
                    params = {"ref": match.group(1)} if match else {}
                    data = client.get(f"/repos/{project}/contents/" + quote(hit["path"], safe="/"), params)
                    if data.get("size", 0) > args.max_file_bytes:
                        stats["files_skipped"] += 1
                        warnings.append(f"File size limit: GitHub {project}/{hit['path']}"); continue
                    if data.get("encoding") != "base64":
                        stats["files_skipped"] += 1
                        warnings.append(f"Unsupported content: GitHub {project}/{hit['path']}"); continue
                    content = decode_contents(data)
                    stats["files_read"] += 1
                    add_finding(findings, platform="GitHub", project=project,
                        project_url=metadata["html_url"], path=hit["path"],
                        evidence_url=hit["html_url"], content=content, item=item,
                        stars=metadata.get("stargazers_count"), project_name=metadata.get("name"))
                except (APIError, KeyError, ValueError) as exc:
                    stats["files_skipped"] += 1
                    warnings.append(f"File read failed: {project}/{hit['path']}: {exc}")
            # Replace the legacy unpartitioned-cap warning with current coverage
            # warnings, even when the index changed during the partitioned scan.
            warnings[:] = [w for w in warnings if not w.startswith(f"GitHub search cap: {query}:")]


def gitlab_file(client, project, path, ref, resources, args, findings, warnings):
    try:
        data = client.get(f"/projects/{project['id']}/repository/files/" + quote(path, safe=""), {"ref": ref})
        if data.get("size", 0) > args.max_file_bytes:
            warnings.append(f"File size limit: {project['web_url']}/{path}"); return
        content = decode_contents(data)
        for item in resources:
            if any(t.casefold() in content.casefold() for t in item["terms"]):
                add_finding(findings, platform="GitLab", project=project["path_with_namespace"],
                    project_url=project["web_url"], path=path,
                    evidence_url=project["web_url"] + "/-/blob/" + quote(data.get("commit_id", ref), safe="") + "/" + quote(path, safe="/"),
                    content=content, item=item,
                    fork=is_derivative(project),
                    stars=project.get("star_count"), project_name=project.get("name"))
    except (APIError, KeyError, ValueError) as exc:
        warnings.append(f"GitLab file read failed: {project['web_url']}/{path}: {exc}")


def scan_gitlab(client, resources, args, findings, warnings, checkpoint=None):
    host = client.base.removesuffix("/api/v4")
    projects, matched_paths = {}, {}
    # Global blob search availability depends on authentication, tier and server
    # configuration. Never silently report a failed search as zero adoption.
    if client.token and not args.gitlab_projects_only:
        for item in resources:
            term = item["name"] if item["name"] in UNIQUE_NAMES else f"{args.org}/{item['name']}"
            try:
                for hit in client.pages("/search", {"scope": "blobs", "search": term}, warnings,
                                        max_pages=args.max_pages, label=host + " blob search"):
                    if "project_id" in hit and (hit.get("path") or hit.get("filename")):
                        pid = hit["project_id"]
                        matched_paths.setdefault(pid, set()).add((hit.get("path") or hit["filename"], hit.get("ref")))
            except APIError as exc:
                warnings.append(f"Global GitLab code search unavailable ({host}): {exc}")
                if checkpoint:
                    checkpoint("GitLab code search: " + term)
                break
            if checkpoint:
                checkpoint("GitLab code search: " + term)
        for pid in matched_paths:
            try:
                projects[pid] = client.get(f"/projects/{pid}")
            except APIError as exc:
                warnings.append(str(exc))
    elif not args.gitlab_projects_only:
        warnings.append(f"No global GitLab code search ({host}): no token; project discovery and repository scans only")
    terms = sorted({r["name"] for r in resources if r["name"] in UNIQUE_NAMES} | {args.org} | set(args.gitlab_search or []))
    if args.gitlab_projects_only:
        terms = []
    for term in terms:
        LOG.info("GitLab %s project search: %s", host, term)
        try:
            for project in client.pages("/projects", {"search": term, "simple": "true", "visibility": "public"},
                                        warnings, max_pages=args.max_pages, label=host + " project discovery"):
                projects[project["id"]] = project
        except APIError as exc:
            warnings.append(str(exc))
        if checkpoint:
            checkpoint("GitLab project search: " + term)
    for value in args.gitlab_project:
        parsed = urlparse(value)
        if parsed.scheme:
            if parsed.netloc != urlparse(host).netloc:
                continue
            value = parsed.path.strip("/").split("/-/")[0]
        try:
            project = client.get("/projects/" + quote(value, safe=""))
            projects[project["id"]] = project
        except APIError as exc:
            warnings.append(str(exc))

    for pid in sorted(projects):
        # Discovery uses simple=true, which omits fork lineage. Read full
        # metadata before deciding whether the adoption is independent.
        try:
            project = client.get(f"/projects/{pid}")
        except APIError as exc:
            warnings.append(f"GitLab project metadata unavailable: {exc}")
            continue
        if project.get("visibility") not in (None, "public"):
            continue
        if is_derivative(project):
            continue
        if project["path_with_namespace"].casefold().startswith(args.org.casefold() + "/"):
            continue
        ref = project.get("default_branch")
        if not ref:
            continue
        LOG.info("GitLab: reading %s", project["path_with_namespace"])
        for path, hit_ref in sorted(matched_paths.get(pid, set()), key=lambda p: p[0]):
            gitlab_file(client, project, path, hit_ref or ref, resources, args, findings, warnings)
        try:
            tree = client.pages(f"/projects/{pid}/repository/tree", {"ref": ref, "recursive": "true"},
                                warnings, max_pages=args.max_pages, label=project["web_url"] + " tree")
            count = 0
            for entry in tree:
                path = entry["path"]
                if entry["type"] != "blob" or (Path(path).suffix.casefold() not in TEXT_SUFFIXES and
                    Path(path).name.casefold() not in {"dockerfile", "makefile", "apkbuild", "pkgbuild", ".gitmodules"}):
                    continue
                if args.max_gitlab_files and count >= args.max_gitlab_files:
                    warnings.append(f"GitLab file scan limited: {project['web_url']}, {count} files"); break
                count += 1
                gitlab_file(client, project, path, ref, resources, args, findings, warnings)
        except APIError as exc:
            warnings.append(str(exc))
        if checkpoint:
            checkpoint("GitLab repository: " + project["path_with_namespace"])


def deduplicate(findings):
    """Keep one record per evidence file and resource, merging repeated searches."""
    result = {}
    for f in findings:
        if f.get("fork") or f.get("type") == "fork":
            continue
        if f.get("type") == "code_reference" and f.get("status") == "confirmed":
            f = {**f, "status": "needs_review"}
        if f.get("type") == "bundled_dictionary" and not dictionary_path(f["resource"], f["path"]):
            f = {**f, "status": "needs_review", "type": "documentation_reference"}
        key = (f["project_url"].rstrip("/").casefold(), f["resource"], f["path"])
        previous = result.get(key)
        if previous and previous.get('manually_reviewed') and not f.get('manually_reviewed') and previous['evidence_url'] == f['evidence_url']:
            continue
        result[key] = f
    return sorted(result.values(), key=lambda f: (f["resource"], f["project"], f["path"]))


def merge_reports(*reports):
    """Accumulate report evidence and coverage without discarding source scopes."""
    if not reports:
        return {}
    merged = dict(reports[0])
    merged['findings'] = deduplicate([f for report in reports for f in report.get('findings', [])])
    for field, key in [('resources', 'name'), ('github_searches', 'query')]:
        merged[field] = list({item[key]: item for report in reports for item in report.get(field, [])}.values())
    merged['warnings'] = sorted({warning for report in reports for warning in report.get('warnings', [])})
    scope, source_scopes = {}, []
    for report in reports:
        source = report.get('scope', {})
        for key, value in source.items():
            if key != 'merged_scopes':
                scope.setdefault(key, value)
        for item in source.get('merged_scopes', []) or [{k: v for k, v in source.items() if k != 'merged_scopes'}]:
            if item and item not in source_scopes:
                source_scopes.append(item)
    if len(source_scopes) > 1:
        scope['merged_scopes'] = source_scopes
    merged['scope'] = scope
    if any(report.get('run_status') == 'running' for report in reports):
        merged['run_status'] = 'running'
    return merged


def report_html(report):
    # Escape '<' in JSON to prevent an evidence snippet closing the script tag.
    payload = json.dumps(report, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return HTML.replace("__DATA__", payload).replace('__USAGE_TYPES__', json.dumps(sorted(USAGE_TYPES)))


HTML = '''<!doctype html><html lang="ca"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Reutilització de Softcatalà</title>
<style>body{font:16px system-ui;background:#f6f8fc;color:#17283b;margin:30px}h1{font-size:28px}input,select,button{font:inherit;padding:8px;margin:4px;border:1px solid #abbacd;border-radius:6px}a{color:#185fa9}svg{background:white;border-radius:14px;max-width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;text-align:left;border-bottom:1px solid #dce3eb}pre{white-space:pre-wrap;max-width:650px}summary{cursor:pointer}.note{color:#506176}.warning{background:#fff2d2;padding:12px;border-radius:8px}#graph{overflow:auto}svg text{font-family:system-ui}section{margin-top:24px}</style>
<h1>Projectes que reutilitzen recursos de Softcatalà</h1>
<p class="note">Les connexions indiquen evidències al codi públic, no desplegaments en producció ni nombre d’usuaris. Cerca parcial, condicionada pels índexs i permisos de les plataformes.</p>
<input id="search" placeholder="Filtra per projecte o recurs" aria-label="Filtra">
<select id="platform"><option value="">Totes les plataformes</option><option>GitHub</option><option>GitLab</option><option>Altres</option></select>
<select id="status"><option value="confirmed">Ús o integració amb evidència</option></select>
<p><a href="graph-gource.svg">Obre el gràfic estàtic tipus Gource</a></p>
<button id="download">Descarrega el gràfic SVG</button><p id="counts"></p>
<div id="graph"></div><section><h2>Evidències</h2><table><thead><tr><th>Projecte</th><th>Recurs</th><th>Tipus / estat</th><th>Font</th></tr></thead><tbody id="rows"></tbody></table></section>
<section><h2>Abast i limitacions</h2><div id="warnings"></div></section>
<script id="data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('data').textContent), ns='http://www.w3.org/2000/svg';
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
function safeURL(url){try{const u=new URL(url);return ['https:','http:'].includes(u.protocol)?u.href:'#'}catch{return '#'}}
function link(url,label){const a=el('a',label);a.href=safeURL(url);a.target='_blank';a.rel='noopener noreferrer';return a}
function svgNode(tag,attrs,text){const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n}
function update(){const query=document.getElementById('search').value.toLowerCase(),platform=document.getElementById('platform').value,status=document.getElementById('status').value;
const usageTypes=__USAGE_TYPES__;
const rows=data.findings.filter(f=>!f.fork&&f.status==='confirmed'&&usageTypes.includes(f.type)&&(!platform||f.platform===platform)&&(!status||f.status===status)&&(f.project+' '+f.resource).toLowerCase().includes(query));
const projects=new Set(rows.map(f=>f.project_url)),groups=new Map();for(const f of rows){if(!groups.has(f.resource))groups.set(f.resource,new Map());groups.get(f.resource).set(f.project_url,f)}
document.getElementById('counts').textContent=`${projects.size} repositoris · ${groups.size} recursos · ${rows.length} fitxers amb evidències · ${data.generated_at}`+(data.run_status==='running'?` · Informe parcial (${data.progress.completed_steps} cerques/lectures completades)`:'');
const body=document.getElementById('rows');body.replaceChildren();for(const f of rows){const tr=el('tr'),p=el('td');const a=link(f.project_url,f.project_name||f.project.split('/').at(-1));a.title=f.project;p.append(a);tr.append(p,el('td',f.resource),el('td',f.type+' / '+f.status));const td=el('td');td.append(link(f.evidence_url,f.path));const d=el('details');d.append(el('summary','Mostra evidència'),el('pre',f.hits.map(h=>h.line+': '+h.text).join('\\n')));td.append(d);tr.append(td);body.append(tr)}
let y=85;const height=120+[...groups.values()].reduce((a,g)=>a+Math.max(1,g.size)*45+65,0),svg=svgNode('svg',{xmlns:ns,width:1400,height,viewBox:`0 0 1400 ${height}`,role:'img'});svg.append(svgNode('text',{x:35,y:42,'font-size':25,'font-weight':700},'Reutilització documentada de Softcatalà'));
let i=0;for(const [resource,items]of groups){const color=['#237a57','#295c9c','#90602e','#7154a1'][i++%4],start=y;svg.append(svgNode('rect',{x:35,y:y-20,width:310,height:42,rx:8,fill:color}),svgNode('text',{x:50,y:y+7,fill:'white','font-size':17},resource));for(const f of items.values()){svg.append(svgNode('path',{d:`M345 ${start} H390 V${y} H430`,fill:'none',stroke:color,'stroke-width':1.5}));const a=svgNode('a',{href:safeURL(f.evidence_url),target:'_blank'});a.append(svgNode('rect',{x:430,y:y-19,width:920,height:36,rx:7,fill:'#eef3fa',stroke:color}),svgNode('text',{x:445,y:y+5,'font-size':16},f.project+' · '+f.platform));svg.append(a);y+=45}y+=65}
document.getElementById('graph').replaceChildren(svg)}
for(const id of ['search','platform','status'])document.getElementById(id).addEventListener('input',update);
const warnings=document.getElementById('warnings');for(const w of data.warnings)warnings.append(el('p',w));if(data.warnings.length)warnings.className='warning';
document.getElementById('download').onclick=()=>{const svg=document.querySelector('#graph svg');const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}));const a=el('a');a.href=url;a.download='softcatala-reutilitzacio.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};update();
</script></html>'''


def report_svg(report):
    groups = {}
    for f in report["findings"]:
        if is_usage(f):
            groups.setdefault(f["resource"], {})[f["project_url"]] = f
    height = 120 + sum(len(v) * 45 + 65 for v in groups.values())
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{height}" viewBox="0 0 1400 {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<text x="35" y="42" font-family="sans-serif" font-size="25">Reutilització documentada de Softcatalà</text>']
    y = 85
    for name, projects in groups.items():
        start = y
        parts += [f'<rect x="35" y="{y-20}" width="310" height="42" rx="8" fill="#295c9c"/>',
                  f'<text x="50" y="{y+7}" fill="white" font-family="sans-serif" font-size="17">{html.escape(name)}</text>']
        for f in projects.values():
            parts += [f'<path d="M345 {start} H390 V{y} H430" fill="none" stroke="#295c9c"/>',
                      f'<a href="{html.escape(f["evidence_url"], quote=True)}" target="_blank">',
                      f'<rect x="430" y="{y-19}" width="920" height="36" rx="7" fill="#eef3fa"/>',
                      f'<text x="445" y="{y+5}" font-family="sans-serif" font-size="16">{html.escape(f.get("project_name") or f["project"])} · {html.escape(f["platform"])}</text></a>']
            y += 45
        y += 65
    return "\n".join(parts + ["</svg>"])


def reclassify_cached_report(report, cache):
    """Reapply current rules to cached GitHub evidence; never access the network."""
    gh = Client("https://api.github.com", "", cache / "github", offline=True)
    resources = {item["name"]: item for item in report.get("resources", [])}
    findings = []
    for original in report["findings"]:
        f = dict(original)
        if f["platform"] == "GitHub" and f["resource"] in resources and f.get("type") != "fork" and not f.get('manually_reviewed'):
            try:
                match = re.search(r"/blob/([^/]+)/", f["evidence_url"])
                params = {"ref": match.group(1)} if match else {}
                data = gh.get(f"/repos/{f['project']}/contents/" + quote(f["path"], safe="/"), params)
                content = decode_contents(data)
                f["status"], f["type"], f["hits"] = classify(f["path"], content, resources[f["resource"]])
            except (APIError, KeyError, ValueError):
                # Missing cached content must not be interpreted as verified use.
                f["status"] = "needs_review"
        findings.append(f)
    return {**report, "findings": deduplicate(findings)}


def write_report(report, output, *, products_file=None, product_kinds=DEFAULT_KINDS):
    report = {**report, "findings": deduplicate(report["findings"])}
    names = project_names(report)
    report["findings"] = [{**f, "project_name": names[f["project_url"]]} for f in report["findings"]]
    output.mkdir(parents=True, exist_ok=True)
    def atomic_text(name, content):
        atomic_write(output / name, content)
    write_json(output / "reuse.json", report)
    write_json(output / "github-coverage.json", report.get("github_searches", []))
    fields = ["platform", "project", "project_name", "resource", "status", "type", "path", "evidence_url", "project_url", "stars", "evidence"]
    rows = []
    for finding in report["findings"]:
        row = {key: finding.get(key, "") for key in fields}
        row["evidence"] = "\n".join(f"{hit['line']}: {hit['text']}" for hit in finding["hits"])
        rows.append(row)
    write_csv(output / "reuse.csv", rows, fields)
    atomic_text("index.html", report_html(report))
    atomic_text("graph.svg", report_svg(report))
    atomic_text("graph-gource.svg", gource_svg({**report, "findings": [f for f in report["findings"] if is_usage(f)]}))
    products_file = products_file or Path(__file__).resolve().with_name("products_catalog.json")
    catalog = read_json(products_file)
    products = product_report(report, catalog, product_kinds)
    write_json(output / "products.json", products)
    atomic_text("graph-products.svg", gource_svg(products))
    atomic_text("products.html", products_html(products))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    script_dir = Path(__file__).resolve().parent
    p.add_argument("--output", type=Path, default=script_dir / "softcatala-reuse-report")
    p.add_argument("--cache", type=Path, default=script_dir / ".cache")
    p.add_argument("--org", default="Softcatala")
    p.add_argument("--resource", action="append", help="Repository/package name; repeat to limit the search")
    p.add_argument("--resources-file", type=Path, help="JSON list of {name, terms, queries} for custom identifiers")
    p.add_argument("--products-file", type=Path, default=script_dir / "products_catalog.json", help="Reviewed product identities and their exact repository URLs")
    p.add_argument("--external-sources-file", type=Path, default=script_dir / "external_sources.json", help="Reviewed source probes outside GitHub/GitLab (Gitiles, Mozilla Add-ons)")
    p.add_argument("--no-external-sources", action="store_true", help="Skip external source probes")
    p.add_argument("--update-external-sources", action="store_true", help="With --from-report, update configured external evidence before rebuilding outputs")
    p.add_argument("--product-kind", action="append", choices=["application", "service", "distribution", "library", "developer-tool", "model"], help="Repeat to select product categories; default all reviewed software product categories")
    p.add_argument("--all-resources", action="store_true", help="Discover every public non-fork repository in the organization")
    p.add_argument("--gitlab-url", action="append", help="GitLab instance URL; repeat; default https://gitlab.com")
    p.add_argument("--gitlab-project", action="append", default=[], help="Explicit project URL or namespace/path; repeat")
    p.add_argument("--gitlab-projects-only", action="store_true", help="Scan only explicit GitLab projects; skip discovery/global search")
    p.add_argument("--gitlab-search", action="append", help="Extra/broader project discovery terms, e.g. whisper; repeat")
    p.add_argument("--no-github", action="store_true")
    p.add_argument('--github-repo', action='append', help='Limit code search to a consumer repository; repeat for multiple repositories')
    p.add_argument("--no-gitlab", action="store_true")
    p.add_argument("--max-pages", type=int, default=0, help="Pagination cap; 0 means all accessible pages")
    p.add_argument("--checkpoint-every", type=int, default=10, help="Save reports every N searches/repository scans; 0 disables periodic saves")
    p.add_argument("--max-gitlab-files", type=int, default=0, help="Files per GitLab project; 0 means no limit")
    p.add_argument("--max-file-bytes", type=int, default=INDEX_MAX_BYTES)
    p.add_argument("--max-wait", type=int, default=60, help="Maximum seconds for an API retry")
    p.add_argument("--search-delay", type=float, default=6.2, help="Seconds between GitHub code-search requests")
    p.add_argument("--refresh", action="store_true", help="Ignore cached successful responses")
    p.add_argument("--refresh-search", action="store_true", help="Refresh search responses while reusing cached file contents and metadata")
    p.add_argument("--offline", action="store_true", help="Use cached API responses only")
    p.add_argument("--from-report", type=Path, help="Regenerate outputs from reuse.json without network access")
    p.add_argument("--merge-report", type=Path, action='append', default=[], help="Merge saved reports into a scan or --from-report rebuild; repeat for multiple reports")
    p.add_argument("--reclassify-cached", action="store_true", help="With --from-report, apply current classification rules to cached GitHub file contents")
    p.add_argument("--evidence-file", type=Path, help="JSON list of manually reviewed findings to merge")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    for name in ("max_pages", "max_gitlab_files", "max_file_bytes", "max_wait", "search_delay", "checkpoint_every"):
        if getattr(args, name) < 0:
            parser().error(name + " must be nonnegative")
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    def external_scan(findings, warnings, checkpoint=None):
        client = Client("", "", args.cache / "external", offline=args.offline, refresh=args.refresh,
                        max_wait=args.max_wait, generic=True)
        probes = read_json(args.external_sources_file)
        scan_external_sources(client, probes, findings, warnings, checkpoint)
    if args.from_report:
        report = merge_reports(read_json(args.from_report), *(read_json(path) for path in args.merge_report))
        if args.resources_file:
            report['resources'] = list({r['name']: r for r in report.get('resources', []) + read_json(args.resources_file)}.values())
        if args.evidence_file:
            report['findings'] = deduplicate(report['findings'] + read_json(args.evidence_file))
        if args.reclassify_cached:
            report = reclassify_cached_report(report, args.cache)
        if args.update_external_sources and not args.no_external_sources:
            probe_ids = {p["id"] for p in read_json(args.external_sources_file)}
            report["findings"] = [f for f in report["findings"] if f.get("source_probe") not in probe_ids]
            external_scan(report["findings"], report["warnings"])
        write_report(report, args.output, products_file=args.products_file, product_kinds=args.product_kind or DEFAULT_KINDS)
        print(args.output / "products.html")
        return 0
    resources = [resource(name, args.org) for name in args.resource or DEFAULT_NAMES]
    previous = merge_reports(*(read_json(path) for path in args.merge_report))
    findings, warnings = list(previous.get("findings", [])), list(previous.get("warnings", []))
    args.github_searches = list(previous.get("github_searches", []))
    gh = Client("https://api.github.com", github_token(), args.cache / "github",
                offline=args.offline, refresh=args.refresh, max_wait=args.max_wait, search_delay=args.search_delay, refresh_search=args.refresh_search)
    if args.all_resources:
        try:
            resources = discover_github(gh, args.org, warnings)
        except APIError as exc:
            warnings.append(f"Organization discovery failed; using default resources: {exc}")
    if args.resources_file:
        resources = read_json(args.resources_file)
    report_resources = {item["name"]: item for item in previous.get("resources", [])}
    report_resources.update({item["name"]: item for item in resources})
    progress = {"completed_steps": 0, "last_step": "Starting"}
    def save_report(state):
        report = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                  "resources": list(report_resources.values()), "findings": deduplicate(findings), "warnings": sorted(set(warnings)),
                  "github_searches": args.github_searches,
                  "run_status": state, "progress": dict(progress),
                  "scope": {**previous.get('scope', {}), "github_default_branch_only": True, "github_max_results_per_query": 1000,
                            "github_size_partitioning": True,
                            'github_consumer_repositories': args.github_repo or [],
                            "gitlab_instances": [] if args.no_gitlab else args.gitlab_url or ["https://gitlab.com"],
                            "gitlab_projects_only": args.gitlab_projects_only,
                            "gitlab_explicit_projects": args.gitlab_project,
                            "gitlab_extra_search_terms": args.gitlab_search or [],
                            "max_pages": args.max_pages, "max_gitlab_files": args.max_gitlab_files,
                            "max_file_bytes": args.max_file_bytes, "include_forks": False,
                            "exhaustive": False}}
        write_report(report, args.output, products_file=args.products_file, product_kinds=args.product_kind or DEFAULT_KINDS)
    def checkpoint(label):
        progress["completed_steps"] += 1
        progress["last_step"] = label
        if args.checkpoint_every and progress["completed_steps"] % args.checkpoint_every == 0:
            save_report("running")
            LOG.info("Checkpoint saved: %s completed steps, %s evidence records", progress["completed_steps"], len(deduplicate(findings)))
    save_report("running")
    if not args.no_external_sources:
        external_scan(findings, warnings, checkpoint)
        save_report("running")
    if not args.no_github:
        if not gh.token and not args.offline:
            warnings.append("GitHub code search requires authentication: set GH_TOKEN/GITHUB_TOKEN or run gh auth login")
        else:
            scan_github(gh, resources, args, findings, warnings, checkpoint)
    save_report("running")
    if not args.no_gitlab:
        for url in args.gitlab_url or ["https://gitlab.com"]:
            url = url.rstrip("/")
            # Tokens are resolved per host; never send GitLab.com's token to a
            # different GitLab instance. Use GITLAB_TOKEN_GIT_UIBK_AC_AT etc.
            host = urlparse(url).hostname or ""
            env_name = "GITLAB_TOKEN_" + re.sub(r"[^A-Z0-9]", "_", host.upper())
            token = os.getenv(env_name, "") or (os.getenv("GITLAB_TOKEN", "") if host == "gitlab.com" else "")
            gl = Client(url + "/api/v4", token, args.cache / ("gitlab-" + re.sub(r"\W", "_", host)),
                        gitlab=True, offline=args.offline, refresh=args.refresh, max_wait=args.max_wait)
            scan_gitlab(gl, resources, args, findings, warnings, checkpoint)
            save_report("running")
    if args.evidence_file:
        findings.extend(read_json(args.evidence_file))
    findings = deduplicate(findings)
    save_report("completed")
    projects = {f["project_url"] for f in findings if is_usage(f)}
    print(f"{len(projects)} repositories with code evidence; {len(findings)} evidence records; {len(warnings)} limitations/errors")
    print(args.output / "products.html")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Interrupted. Successful API responses are cached; rerun to resume.", file=sys.stderr)
        sys.exit(130)
