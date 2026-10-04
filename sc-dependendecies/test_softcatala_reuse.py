"""Offline tests: python3 -m unittest discover -s reuse-softcatala -p 'test_softcatala_reuse.py'."""
import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import softcatala_reuse as reuse
import api_client
from product_catalog import product_report
from external_sources import scan_external_sources
from github_search import INDEX_MAX_BYTES, github_hits


class ReuseTests(unittest.TestCase):
    def setUp(self):
        self.resource = reuse.resource('whisper-ctranslate2', 'Softcatala')

    def test_classification_requires_more_than_a_mention(self):
        self.assertEqual(reuse.classify('README.md', 'Try whisper-ctranslate2', self.resource)[0], 'needs_review')
        self.assertEqual(reuse.classify('requirements.txt', 'whisper-ctranslate2>=0.4', self.resource)[:2], ('confirmed', 'dependency'))
        self.assertEqual(reuse.classify('worker.py', '# Try whisper-ctranslate2', self.resource)[0], 'needs_review')
        self.assertEqual(reuse.classify('worker.py', 'import whisper_ctranslate2', self.resource)[0], 'confirmed')
        self.assertEqual(reuse.classify('worker.py', 'name = "whisper-ctranslate2"', self.resource)[0], 'needs_review')
        self.assertEqual(reuse.classify('pyproject.toml', 'homepage = "https://github.com/Softcatala/whisper-ctranslate2"', self.resource)[0], 'needs_review')
        self.assertEqual(reuse.classify('.gitmodules', 'url = https://github.com/Softcatala/whisper-ctranslate2.git', self.resource)[:2], ('confirmed', 'third_party_integration'))
        self.assertEqual(reuse.classify('docs/dictation.md', 'whisper-ctranslate2\nCopyright someone', self.resource)[0], 'needs_review')
        self.assertEqual(reuse.classify('package.json', '{"description":"Install \'whisper-ctranslate2\'"}', self.resource)[0], 'needs_review')
        self.assertEqual(reuse.classify('engine.ts', 'const result = await run("whisper-ctranslate2", args);', self.resource)[:2], ('confirmed', 'code_usage'))
        self.assertEqual(reuse.classify('ci.yml', '  - pip install whisper-ctranslate2', self.resource)[:2], ('confirmed', 'installation'))
        self.assertEqual(reuse.classify('locale/ca.po', 'whisper-ctranslate2', self.resource)[0], 'excluded')

    def test_generic_identifier_does_not_match_unrelated_projects(self):
        item = reuse.resource('conjugador', 'Softcatala')
        self.assertEqual(reuse.classify('package.json', '{"name":"conjugador"}', item)[2], [])

    def test_vendored_metadata_does_not_prove_using_listed_projects(self):
        item = reuse.resource('open-dubbing', 'Softcatala')
        content = 'Name: faster-whisper\n\n* [Open-dubbing](https://github.com/softcatala/open-dubbing) uses this library.'
        self.assertEqual(reuse.classify('vendor/faster_whisper.dist-info/METADATA', content, item)[:2],
                         ('needs_review', 'package_metadata_reference'))

    def test_huggingface_loading_is_usage_but_a_model_name_alone_is_not(self):
        from huggingface_resources import resource
        item = resource('model', 'softcatala/whisper-medium-ca')
        self.assertEqual(reuse.classify('main.py', 'model = WhisperModel("softcatala/whisper-medium-ca")', item)[:2],
                         ('confirmed', 'code_usage'))
        self.assertEqual(reuse.classify('main.py', 'model_name = "softcatala/whisper-medium-ca"', item)[0], 'needs_review')

    def test_manual_review_survives_duplicate_automatic_findings(self):
        manual = dict(project='owner/project', project_url='https://github.com/owner/project',
                      resource='open-dubbing', path='vendor/METADATA', evidence_url='https://example.org/pinned',
                      status='excluded', type='reviewed_nonuse', manually_reviewed=True)
        automatic = {**manual, 'status': 'confirmed', 'type': 'third_party_integration', 'manually_reviewed': False}
        self.assertEqual(reuse.deduplicate([manual, automatic])[0]['status'], 'excluded')

    def test_declared_mirrors_are_also_excluded(self):
        self.assertTrue(reuse.is_derivative({'full_name': 'gentoo-mirror/gentoo', 'fork': False}))
        self.assertTrue(reuse.is_derivative({'description': 'Read-only mirror of upstream', 'fork': False}))
        self.assertFalse(reuse.is_derivative({'full_name': 'org/app', 'description': 'Uses a third party repository'}))

    def test_project_labels_keep_identity_and_fix_legacy_dictation_false_positive(self):
        finding = {'platform': 'GitHub', 'project': 'Chocobozzz/PeerTube', 'project_url': 'https://github.com/Chocobozzz/PeerTube',
                   'resource': 'whisper-ctranslate2', 'status': 'confirmed', 'type': 'dependency',
                   'path': 'requirements.txt', 'evidence_url': 'https://github.com/Chocobozzz/PeerTube/blob/abc/requirements.txt', 'hits': []}
        legacy = {**finding, 'type': 'bundled_dictionary', 'path': 'docs/dictation.md'}
        self.assertEqual(reuse.deduplicate([legacy])[0]['status'], 'needs_review')
        with tempfile.TemporaryDirectory() as directory:
            reuse.write_report({'findings': [finding], 'warnings': [], 'generated_at': 'test'}, Path(directory))
            result = json.loads((Path(directory) / 'reuse.json').read_text())['findings'][0]
            self.assertEqual(result['project_name'], 'PeerTube')
            self.assertEqual(result['project'], 'Chocobozzz/PeerTube')
            svg = ET.fromstring((Path(directory) / 'graph-gource.svg').read_text())
            labels = [e.text for e in svg.iter() if e.tag.endswith('text')]
            self.assertIn('PeerTube', labels)
            self.assertIn('(https://github.com/Chocobozzz/PeerTube)', [e.text for e in svg.iter() if e.tag.endswith('tspan')])
            self.assertNotIn('Chocobozzz/PeerTube', labels)

    def test_pagination_and_visible_truncation(self):
        with tempfile.TemporaryDirectory() as directory:
            client = reuse.Client('https://example.org', '', Path(directory), offline=True)
            warnings = []
            with patch.object(client, 'get', side_effect=[list(range(100)), [100]]) as get:
                self.assertEqual(len(list(client.pages('/projects', {}, warnings))), 101)
                self.assertEqual(get.call_args.args[1]['page'], 2)
            with patch.object(client, 'get', return_value=list(range(100))):
                self.assertEqual(len(list(client.pages('/projects', {}, warnings, max_pages=1))), 100)
            self.assertTrue(any('Pagination limited' in w for w in warnings))

    def test_offline_cache_never_requests_network(self):
        with tempfile.TemporaryDirectory() as directory:
            client = reuse.Client('https://example.org', '', Path(directory), offline=True)
            with patch.object(api_client, 'urlopen', side_effect=AssertionError('network request')):
                with self.assertRaises(reuse.APIError):
                    client.get('/missing')

    def test_github_reads_indexed_revision_and_reports_incomplete_search(self):
        class FakeClient:
            def get(self, endpoint, params=None):
                if endpoint == '/search/code':
                    return {'total_count': 1, 'incomplete_results': True, 'items': [{
                        'repository': {'full_name': 'consumer/app'}, 'path': 'requirements.txt',
                        'html_url': 'https://github.com/consumer/app/blob/abc123/requirements.txt'}]}
                if endpoint == '/repos/consumer/app':
                    return {'fork': False, 'html_url': 'https://github.com/consumer/app'}
                self.ref = params['ref']
                return {'encoding': 'base64', 'content': base64.b64encode(b'whisper-ctranslate2').decode()}
        client = FakeClient()
        findings, warnings = [], []
        reuse.scan_github(client, [self.resource], reuse.parser().parse_args(['--max-pages', '1']), findings, warnings)
        self.assertEqual(client.ref, 'abc123')
        self.assertEqual(findings[0]['status'], 'confirmed')
        self.assertTrue(any('incomplete search' in w for w in warnings))

    def test_github_partition_recovers_more_than_one_thousand_matches(self):
        class FakeClient:
            calls = []
            def get(self, endpoint, params):
                q, page = params['q'], params['page']
                self.calls.append((q, page))
                if 'size:' not in q:
                    first, total = 0, 1300
                elif f'size:0..{INDEX_MAX_BYTES//2}' in q:
                    first, total = 0, 1000
                else:
                    first, total = 1000, 300
                start = (page-1)*100
                return {'total_count': total, 'incomplete_results': False, 'items': [
                    {'repository': {'full_name': 'org/app'}, 'path': f'file-{first+i}.txt'}
                    for i in range(start, min(start+100,total))]}
        client = FakeClient(); warnings, stats = [], {}
        results = list(github_hits(client, 'package', warnings, stats=stats))
        self.assertEqual(len(results), 1300)
        self.assertEqual(stats['unique_matches'], 1300)
        self.assertTrue(stats['complete'])
        self.assertEqual(len(stats['partitions']), 2)
        self.assertEqual(warnings, [])
        self.assertLessEqual(max(page for _, page in client.calls), 10)

    def test_github_partition_reports_unresolvable_identical_sizes(self):
        import re
        class FakeClient:
            def get(self, endpoint, params):
                bounds = re.search(r'size:(\d+)\.\.(\d+)', params['q'])
                total = 1001 if not bounds or int(bounds[1]) <= 32 <= int(bounds[2]) else 0
                start = (params['page']-1)*100
                return {'total_count': total, 'incomplete_results': False, 'items': [
                    {'repository': {'full_name': 'org/app'}, 'path': f'file-{i}'}
                    for i in range(start, min(start+100, total))]}
        warnings, stats = [], {}
        results = list(github_hits(FakeClient(), 'package', warnings, stats=stats))
        self.assertEqual(len(results), 1000)
        self.assertFalse(stats['complete'])
        self.assertTrue(any('same byte size' in w for w in warnings))

    def test_github_partition_respects_user_page_limit(self):
        class FakeClient:
            def get(self, endpoint, params):
                return {'total_count': 150, 'items': [{'repository': {'full_name': 'org/app'}, 'path': str(i)} for i in range(100)]}
        warnings, stats = [], {}
        self.assertEqual(len(list(github_hits(FakeClient(), 'package', warnings, max_pages=1, stats=stats))), 100)
        self.assertFalse(stats['complete'])
        self.assertTrue(any('Pagination limited' in w for w in warnings))

    def test_gitlab_simple_metadata_cannot_hide_fork(self):
        project = {'id': 1, 'path_with_namespace': 'someone/mirror',
                   'web_url': 'https://gitlab.com/someone/mirror', 'default_branch': 'main',
                   'visibility': 'public', 'forked_from_project': {'id': 2}}
        class FakeClient:
            base = 'https://gitlab.com/api/v4'
            token = ''
            def pages(self, endpoint, params, warnings, **kwargs):
                if endpoint == '/projects':
                    return iter([{'id': 1}])
                return iter([{'path': 'requirements.txt', 'type': 'blob'}])
            def get(self, endpoint, params=None):
                if endpoint == '/projects/1':
                    return project
                return {'content': base64.b64encode(b'whisper-ctranslate2').decode(), 'commit_id': 'abc'}
        findings, warnings = [], []
        args = reuse.parser().parse_args([])
        reuse.scan_gitlab(FakeClient(), [self.resource], args, findings, warnings)
        self.assertEqual(findings, [])

    def test_reports_escape_snippets_and_regenerate_offline(self):
        findings = []
        reuse.add_finding(findings, platform='GitHub', project='a/<b>', project_url='https://github.com/a/b',
                          path='requirements.txt', evidence_url='https://github.com/a/b/blob/abc/requirements.txt',
                          content='whisper-ctranslate2 # </script><script>alert(1)</script>', item=self.resource)
        report = {'generated_at': 'test', 'warnings': [], 'resources': [self.resource], 'findings': findings}
        self.assertNotIn('</script><script>alert(1)', reuse.report_html(report))
        ET.fromstring(reuse.report_svg(report))
        self.assertEqual(len(reuse.deduplicate(findings + findings)), 1)
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source = directory / 'source.json'
            source.write_text(json.dumps(report))
            with patch.object(api_client, 'urlopen', side_effect=AssertionError('network request')):
                self.assertEqual(reuse.main(['--from-report', str(source), '--output', str(directory / 'out')]), 0)
            for name in ('index.html', 'graph.svg', 'graph-gource.svg', 'reuse.csv', 'reuse.json', 'products.html', 'products.json', 'graph-products.svg'):
                self.assertTrue((directory / 'out' / name).is_file())

    def test_periodic_checkpoint_at_ten_and_final_report(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            output = directory / 'out'
            def scan(client, resources, args, findings, warnings, checkpoint):
                for number in range(1, 12):
                    checkpoint(f'query {number}')
                    snapshot = json.loads((output / 'reuse.json').read_text())
                    self.assertEqual(snapshot['run_status'], 'running')
                    self.assertEqual(snapshot['progress']['completed_steps'], 0 if number < 10 else 10)
                for name in ('index.html', 'graph.svg', 'graph-gource.svg', 'reuse.csv', 'reuse.json', 'products.html', 'products.json', 'graph-products.svg'):
                    self.assertTrue((output / name).is_file())
                self.assertEqual(list(output.glob('*.tmp')), [])
            with patch.object(reuse, 'github_token', return_value='fixture-token'), patch.object(reuse, 'scan_github', side_effect=scan):
                reuse.main(['--no-gitlab', '--no-external-sources', '--output', str(output), '--cache', str(directory / 'cache')])
            final = json.loads((output / 'reuse.json').read_text())
            self.assertEqual(final['run_status'], 'completed')
            self.assertEqual(final['progress']['completed_steps'], 11)

    def test_static_tree_excludes_forks_and_unproven_code_mentions(self):
        base = {'platform': 'GitHub', 'project': 'real/consumer', 'project_url': 'https://github.com/real/consumer',
                'resource': 'whisper-ctranslate2', 'status': 'confirmed', 'type': 'dependency',
                'path': 'requirements.txt', 'evidence_url': 'https://github.com/real/consumer/blob/abc/requirements.txt', 'hits': []}
        findings = [base, {**base, 'project': 'fork/mirror', 'fork': True, 'project_url': 'https://github.com/fork/mirror'},
                    {**base, 'project': 'mention/only', 'type': 'code_reference', 'project_url': 'https://github.com/mention/only'}]
        with tempfile.TemporaryDirectory() as directory:
            reuse.write_report({'findings': findings, 'warnings': [], 'generated_at': 'test'}, Path(directory))
            svg = (Path(directory) / 'graph-gource.svg').read_text()
            ET.fromstring(svg)
            self.assertIn('real/consumer', svg)
            self.assertNotIn('fork/mirror', svg)
            self.assertNotIn('mention/only', svg)
            data = json.loads((Path(directory) / 'reuse.json').read_text())
            self.assertEqual(len(data['findings']), 2)
            self.assertEqual(next(f for f in data['findings'] if f['project'] == 'mention/only')['status'], 'needs_review')

    def test_client_retries_incomplete_http_response(self):
        class BrokenResponse:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): raise api_client.IncompleteRead(b'{', 20)
        class Response(BrokenResponse):
            def read(self): return b'{"ok":true}'
        with tempfile.TemporaryDirectory() as directory:
            client = reuse.Client('https://example.org', '', Path(directory))
            with patch.object(api_client, 'urlopen', side_effect=[BrokenResponse(), Response()]), patch.object(api_client.time, 'sleep'):
                self.assertEqual(client.get('/projects'), {'ok': True})

    def test_product_identity_collapses_repositories_without_inheriting_vendored_names(self):
        def finding(repo, path='requirements.txt', resource='whisper-ctranslate2', **extra):
            return {'project': repo, 'project_url': 'https://github.com/' + repo,
                    'resource': resource, 'status': 'confirmed', 'type': 'dependency',
                    'path': path, 'platform': 'GitHub', 'evidence_url': 'https://github.com/' + repo + '/blob/abc/' + path, **extra}
        identity = {'id': 'example', 'name': 'Example App', 'organization': 'Example', 'kind': 'application',
                    'reviewed': True, 'url': 'https://example.org',
                    'repositories': ['https://github.com/org/app', 'https://github.com/org/runner']}
        rows = [finding('org/app'), finding('org/runner'),
                finding('unknown/copy', path='vendor/ExampleApp/requirements.txt'),
                finding('org/app', path='tests.txt', fork=True)]
        result = product_report({'findings': rows, 'warnings': [], 'generated_at': 'test'}, [identity])
        self.assertEqual(len(result['products']), 1)
        self.assertEqual(len(result['findings']), 1)
        self.assertEqual(len(result['findings'][0]['evidence']), 2)
        self.assertEqual(len(result['products'][0]['matched_repositories']), 2)
        self.assertEqual(result['unassigned_repositories'][0]['project'], 'unknown/copy')
        svg = ET.fromstring(reuse.gource_svg(result))
        self.assertEqual(len(svg.findall('{http://www.w3.org/2000/svg}a')), 1)
        self.assertIn('Example App', [e.text for e in svg.iter() if e.tag.endswith('text')])
        self.assertIn('(https://example.org)', [e.text for e in svg.iter() if e.tag.endswith('tspan')])

    def test_product_categories_and_unreviewed_identities(self):
        finding = {'project': 'org/library', 'project_url': 'https://github.com/org/library',
                   'resource': 'whisper-ctranslate2', 'status': 'confirmed', 'type': 'dependency',
                   'path': 'requirements.txt', 'platform': 'GitHub', 'evidence_url': 'https://github.com/org/library/blob/abc/requirements.txt'}
        identity = {'id': 'lib', 'name': 'Library', 'organization': 'Org', 'kind': 'library',
                    'reviewed': True, 'url': 'https://example.org', 'repositories': [finding['project_url']]}
        report = {'findings': [finding]}
        self.assertEqual(len(product_report(report, [identity])['products']), 1)
        self.assertEqual(product_report(report, [identity], kinds=['application'])['products'], [])
        self.assertEqual(len(product_report(report, [identity], kinds=['library'])['products']), 1)
        identity['reviewed'] = False
        self.assertEqual(product_report(report, [identity], kinds=['library'])['products'], [])

    def test_product_catalog_rejects_conflicting_identity_assignments(self):
        identity = {'id': 'one', 'name': 'One', 'organization': 'Org', 'kind': 'application',
                    'reviewed': True, 'url': 'https://example.org', 'repositories': ['https://github.com/org/app']}
        with self.assertRaises(ValueError):
            product_report({'findings': []}, [identity, {**identity, 'id': 'two'}])

    def test_external_sources_validate_origin_and_optional_firefox_integration(self):
        probes = json.loads((Path(reuse.__file__).parent / 'external_sources.json').read_text())
        text = '\n'.join(probes[0]['expected_terms'])
        dependency = "'/chromium/deps/hunspell_dictionaries.git' + '@' + '" + 'a'*40 + "'"
        responses = [base64.b64encode(dependency.encode()).decode(), base64.b64encode(text.encode('latin-1')).decode(),
                     {'type': 'dictionary', 'authors': [{'name': 'Toniher (Softcatalà)'}],
                      'current_version': {'version': '3.0.8', 'compatibility': {'firefox': {'min': '61.0'}}}}]
        with patch.object(reuse.Client, 'get', side_effect=responses):
            with tempfile.TemporaryDirectory() as directory:
                client = reuse.Client('', '', Path(directory), generic=True)
                findings, warnings = [], []
                scan_external_sources(client, probes, findings, warnings)
        self.assertEqual(warnings, [])
        self.assertEqual(len(findings), 2)
        self.assertIn('/' + 'a'*40 + '/', findings[0]['evidence_url'])
        self.assertEqual(findings[1]['integration_context'], 'optional_dictionary_addon')
        catalog = json.loads((Path(reuse.__file__).parent / 'products_catalog.json').read_text())
        products = product_report({'findings': findings}, catalog)
        self.assertEqual({p['id'] for p in products['products']}, {'firefox', 'chromium'})

    def test_dictionary_discovery_includes_historical_package_names(self):
        item = reuse.resource('catalan-dict-tools', 'Softcatala')
        self.assertIn('softcatala-spell', item['queries'])
        self.assertIn('ispellcat', item['terms'])
        other = reuse.resource('catalan-dict-tools', 'OtherOrg')
        self.assertNotIn('softcatala-spell', other['terms'])

    def test_invalid_external_source_does_not_count_as_integration(self):
        probes = json.loads((Path(reuse.__file__).parent / 'external_sources.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            client = reuse.Client('', '', Path(directory), generic=True)
            with patch.object(client, 'get', return_value={'type': 'extension', 'authors': [], 'current_version': {}}):
                findings, warnings = [], []
                scan_external_sources(client, [probes[1]], findings, warnings)
        self.assertEqual(findings, [])
        self.assertEqual(len(warnings), 1)

    def test_dictionary_attribution_without_consumer_dependency_is_not_counted(self):
        probes = json.loads((Path(reuse.__file__).parent / 'external_sources.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            client = reuse.Client('', '', Path(directory), generic=True)
            with patch.object(client, 'get', return_value=base64.b64encode(b'No dictionary dependency here').decode()):
                findings, warnings = [], []
                scan_external_sources(client, [probes[0]], findings, warnings)
        self.assertEqual(findings, [])
        self.assertEqual(len(warnings), 1)


if __name__ == '__main__':
    unittest.main()
