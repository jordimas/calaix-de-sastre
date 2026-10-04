import unittest

from debian_reverse_dependencies import dependencies, records


class DebianDependenciesTests(unittest.TestCase):
    def test_multiline_and_alternatives(self):
        packages = list(records('Package: app\nSource: app-src (1)\n'
                                'Depends: hunspell, hunspell-ca:any (>= 1) | myspell-ca\n'
                                'Suggests: hyphen-ca,\n mythes-ca\n\n'))
        rows = dependencies(packages)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]['source_package'], 'app-src')
        self.assertEqual(rows[0]['relation_kind'], 'alternative')
        self.assertEqual(rows[0]['field'], 'Depends')
        self.assertEqual(rows[-1]['relation_kind'], 'suggested')

    def test_generic_engine_is_not_catalan_evidence(self):
        self.assertEqual(dependencies([{'Package': 'browser',
                                       'Depends': 'hunspell, hunspell-dictionary'}]), [])

    def test_internal_resource_dependency_is_excluded(self):
        self.assertEqual(dependencies([{'Package': 'icatalan', 'Suggests': 'wcatalan'}]), [])

    def test_required_and_recommended_are_distinct(self):
        rows = dependencies([{'Package': 'keyboard', 'Depends': 'hunspell-ca'},
                             {'Package': 'browser', 'Recommends': 'hunspell-ca'}])
        self.assertEqual([r['relation_kind'] for r in rows], ['mandatory', 'recommended'])


if __name__ == '__main__':
    unittest.main()
