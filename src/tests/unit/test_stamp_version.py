# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the version stamping script (lib/ansible-galaxy/stamp-version).

Written with 'unittest' so that the suite runs under pytest without extra
dependencies. The script runs against a fixture repository in a temporary
directory, with a fake but real git history.
"""

import os
import shutil
import subprocess
import tempfile
import unittest

REPO_ROOT = os.path.realpath(os.path.join(
        os.path.dirname(__file__), '..', '..', '..'))
SCRIPT = os.path.join('lib', 'ansible-galaxy', 'stamp-version')

GIT_ENV = dict(os.environ,
               GIT_AUTHOR_NAME='DebOps Tests',
               GIT_AUTHOR_EMAIL='debops-tests@example.org',
               GIT_COMMITTER_NAME='DebOps Tests',
               GIT_COMMITTER_EMAIL='debops-tests@example.org',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')


class StampVersionTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='debops-stamp-')
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

        # The script locates its tree from its own path, so the fixture
        # mirrors the repository layout
        script_dir = os.path.join(self.tmpdir, 'lib', 'ansible-galaxy')
        os.makedirs(script_dir)
        shutil.copy2(os.path.join(REPO_ROOT, SCRIPT), script_dir)
        os.makedirs(os.path.join(self.tmpdir, 'src', 'debops'))

    def run_script(self):
        return subprocess.run(
                [os.path.join(self.tmpdir, SCRIPT)],
                check=True, capture_output=True, text=True, env=GIT_ENV)

    def git(self, *args):
        subprocess.run(['git'] + list(args), cwd=self.tmpdir,
                       check=True, capture_output=True, env=GIT_ENV)

    def stamped_version_py(self):
        with open(os.path.join(self.tmpdir, 'src', 'debops',
                               '__version__.py')) as fp:
            return fp.read()

    def stamped_version_file(self):
        with open(os.path.join(self.tmpdir, 'VERSION')) as fp:
            return fp.read()

    def test_stamp_from_git_describe(self):
        self.git('init', '-q')
        self.git('commit', '-q', '--allow-empty', '-m', 'initial')
        self.git('tag', '-a', '-m', 'release', 'v3.3.0')
        self.git('commit', '-q', '--allow-empty', '-m', 'one')
        self.git('commit', '-q', '--allow-empty', '-m', 'two')

        result = self.run_script()
        describe = subprocess.run(
                ['git', 'describe'], cwd=self.tmpdir, check=True,
                capture_output=True, text=True, env=GIT_ENV
                ).stdout.strip().lstrip('v')
        # 'v3.3.0-2-g<hash>' → semver as-is, PEP 440 for Python
        count, ghash = describe.split('-')[1:3]
        self.assertIn('__version__ = "3.3.0.dev{}+{}"'
                      .format(count, ghash), self.stamped_version_py())
        self.assertIn('3.3.0.dev{}+{}\n'.format(count, ghash),
                      self.stamped_version_file())
        self.assertIn('Stamped', result.stdout)

    def test_stamp_on_a_release_tag(self):
        self.git('init', '-q')
        self.git('commit', '-q', '--allow-empty', '-m', 'initial')
        self.git('tag', '-a', '-m', 'release', 'v3.3.0')
        self.run_script()
        self.assertIn('__version__ = "3.3.0"', self.stamped_version_py())
        self.assertIn('3.3.0\n', self.stamped_version_file())

    def test_second_run_is_a_noop(self):
        self.git('init', '-q')
        self.git('commit', '-q', '--allow-empty', '-m', 'initial')
        self.git('tag', '-a', '-m', 'release', 'v3.3.0')
        self.run_script()
        result = self.run_script()
        self.assertNotIn('Stamped', result.stdout)

    def test_version_file_fallback_without_git(self):
        with open(os.path.join(self.tmpdir, 'VERSION'), 'w') as fp:
            fp.write('3.2.1\n')
        result = self.run_script()
        self.assertIn('__version__ = "3.2.1"', self.stamped_version_py())
        self.assertIn('3.2.1\n', self.stamped_version_file())
        self.assertIn('Stamped', result.stdout)


if __name__ == '__main__':
    unittest.main()
