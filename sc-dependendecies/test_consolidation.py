"""Regression tests for shared storage, merged coverage and Debian evidence loss."""
import csv
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from pathlib import Path
import tempfile
import io
import unittest
from unittest.mock import patch

from debian_integrations import reviewed_integrations
from softcatala_reuse import deduplicate, merge_reports
from storage import atomic_write, read_json, write_csv, write_json
import huggingface_resources


class ConsolidationTests(unittest.TestCase):
    def test_huggingface_offline_fallback_filters_the_requested_organization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fallback = root / 'fallback.json'
            output = root / 'resources.json'
            write_json(fallback, [huggingface_resources.resource('model', 'softcatala/example'),
                                  huggingface_resources.resource('model', 'other/example')])
            arguments = ['huggingface_resources.py', '--offline', '--cache', str(root / 'cache'),
                         '--fallback-file', str(fallback), '--output', str(output)]
            with patch('sys.argv', arguments), patch.object(huggingface_resources, 'urlopen') as request:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    huggingface_resources.main()
            request.assert_not_called()
            self.assertEqual([r['identifier'] for r in read_json(output)], ['softcatala/example'])

    def test_failed_atomic_replace_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            write_json(path, {'name': 'Softcatalà'})
            with patch.object(Path, 'replace', side_effect=OSError('disk unavailable')):
                with self.assertRaises(OSError):
                    atomic_write(path, 'incomplete')
            self.assertEqual(read_json(path), {'name': 'Softcatalà'})
            self.assertEqual(list(Path(directory).glob('*.tmp')), [])

    def test_csv_preserves_unicode_and_multiline_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.csv'
            rows = [{'name': 'Català', 'evidence': 'first\nsecond, quoted'}]
            write_csv(path, rows, ['name', 'evidence'])
            with path.open(encoding='utf-8', newline='') as stream:
                self.assertEqual(list(csv.DictReader(stream)), rows)

    def test_report_merging_is_idempotent_and_keeps_scopes(self):
        evidence = dict(project='org/app', project_url='https://github.com/org/app',
                        resource='CTranslate2', status='confirmed', type='dependency',
                        path='requirements.txt', evidence_url='https://example.org/pinned')
        first = dict(findings=[evidence], resources=[{'name': 'CTranslate2'}],
                     github_searches=[{'query': 'first'}], scope={'github_consumer_repositories': []})
        second = dict(findings=[evidence], resources=[{'name': 'HF model'}],
                      github_searches=[{'query': 'second'}], scope={'github_consumer_repositories': ['org/app']})
        original = deepcopy(first)
        merged = merge_reports(first, second)
        self.assertEqual(len(merged['findings']), 1)
        self.assertEqual(len(merged['resources']), 2)
        self.assertEqual(len(merged['github_searches']), 2)
        self.assertEqual(len(merged['scope']['merged_scopes']), 2)
        self.assertEqual(merge_reports(merged, second), merged)
        self.assertEqual(first, original)

    def test_debian_same_field_keeps_all_distinct_dependency_groups(self):
        report = dict(suite='stable', index_url='https://example.org/Packages.xz', index_sha256='abc', seeds=[],
                      relations=[dict(binary_package='task-catalan', source_package='tasksel', version='1',
                                      target_package=target, field='Recommends', relation_kind='recommended', expression=target)
                                 for target in ('aspell-ca', 'icatalan', 'wcatalan')])
        identity = dict(id='debian', name='Debian', organization='Debian', kind='distribution',
                        url='https://www.debian.org/', reviewed=True, packages=['task-catalan'],
                        allowed_targets=['aspell-ca', 'icatalan', 'wcatalan'])
        findings, catalog = reviewed_integrations(report, [identity], [])
        self.assertEqual(len(deduplicate(findings)), 1)
        self.assertEqual(len(findings[0]['hits']), 3)
        self.assertEqual(len(catalog[0]['repositories']), 1)
        self.assertEqual(reviewed_integrations(report, [identity], catalog), (findings, catalog))


if __name__ == '__main__':
    unittest.main()
