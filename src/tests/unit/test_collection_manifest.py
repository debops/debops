# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the tracked Ansible Collection manifest.

The 'galaxy.yml' manifest of the bundled Collection is tracked in git
and used by 'ansible-galaxy' when installing the Collection directly
from a git repository. The tests validate the keys that ansible-galaxy
requires and the consistency of the version with the changelog.
"""

import os
import re
import unittest

try:
    import yaml
except ImportError:
    raise SystemExit('The PyYAML Python library is required '
                     '(Debian package: python3-yaml)')

REPO_ROOT = os.path.realpath(os.path.join(
        os.path.dirname(__file__), '..', '..', '..'))
MANIFEST = os.path.join('ansible', 'collections', 'ansible_collections',
                        'debops', 'debops', 'galaxy.yml')

MANDATORY_KEYS = ('namespace', 'name', 'version', 'readme', 'authors')


def changelog_release():
    """The version of the latest release, from the changelog."""
    with open(os.path.join(REPO_ROOT, 'CHANGELOG.rst')) as fp:
        for line in fp:
            if re.match(r'^`debops v', line):
                return line.split()[1].rstrip('`_').lstrip('v')
    return None


class CollectionManifestTestCase(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(REPO_ROOT, MANIFEST)) as fp:
            self.manifest = yaml.safe_load(fp)

    def test_mandatory_keys_are_present(self):
        for key in MANDATORY_KEYS:
            self.assertIn(key, self.manifest)

    def test_readme_file_exists(self):
        manifest_dir = os.path.dirname(os.path.join(REPO_ROOT, MANIFEST))
        self.assertTrue(os.path.exists(
            os.path.join(manifest_dir, self.manifest['readme'])))

    def test_version_matches_the_changelog(self):
        self.assertEqual(self.manifest['version'], changelog_release())

    def test_all_shipped_licenses_are_listed(self):
        licenses_dir = os.path.join(REPO_ROOT, 'LICENSES')
        for license_file in os.listdir(licenses_dir):
            license_name = os.path.splitext(license_file)[0]
            self.assertIn(license_name, self.manifest['license'])


if __name__ == '__main__':
    unittest.main()
