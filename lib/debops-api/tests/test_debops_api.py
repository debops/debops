from nose.tools import assert_equals

from debops.api import DebOpsAPI


def test__get_maintainer_from_changelog():
    debops_api = DebOpsAPI()
    expected = {
        'The current role maintainer_ is drybjed_.': ['drybjed'],
        'The current role maintainers_ are drybjed_ and ypid_.': (
            ['drybjed', 'ypid']),
        'The current role maintainers_ are drybjed_, foo_ and ypid_.': (
            ['drybjed', 'foo', 'ypid']),
        'The current role maintainer is drybjed_.': ['drybjed'],
        'The current role maintainer is drybjed.': ['drybjed'],
        'The current role maintainer is drybjed': ['drybjed'],
        'The current maintainer is drybjed': ['drybjed'],
        'The maintainer is drybjed': ['drybjed'],
        '.. include:: includes/all.rst': None,
    }
    for line, expected_result in expected.items():
        assert_equals(
            expected_result,
            debops_api._get_maintainers_from_line(line)
        )
