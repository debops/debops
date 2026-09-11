# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the opt-in version update check (src/debops/versioncheck.py).

Written with 'unittest' so that the suite runs under pytest without extra
dependencies. The tests run offline: git subprocess calls are performed
against fixture repositories in temporary directories and the network
access is mocked.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock

from debops.versioncheck import VersionCheck

GIT_ENV = dict(os.environ,
               GIT_AUTHOR_NAME='DebOps Tests',
               GIT_AUTHOR_EMAIL='debops-tests@example.org',
               GIT_COMMITTER_NAME='DebOps Tests',
               GIT_COMMITTER_EMAIL='debops-tests@example.org',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')


class FakeConfig(object):
    """Minimal configuration stand-in with '[version_check]' options."""

    def __init__(self, settings):
        self.raw = {'version_check': settings}


def make_check(settings=None):
    """A VersionCheck instance with its cache in a temporary directory."""
    return VersionCheck(FakeConfig(settings or {}))


def git_fixture(path, branch, commits=1, tags=()):
    """Create a repository with a branch, commits and annotated tags."""
    subprocess.run(['git', 'init', '-q', '-b', branch, path],
                   check=True, capture_output=True, env=GIT_ENV)
    for index in range(commits):
        subprocess.run(['git', '-C', path, 'commit', '-q', '--allow-empty',
                        '-m', 'commit {}'.format(index)],
                       check=True, capture_output=True, env=GIT_ENV)
    for tag in tags:
        subprocess.run(['git', '-C', path, 'tag', '-a', '-m', tag,
                        tag.lstrip('v')], check=True, capture_output=True,
                       env=GIT_ENV)


class VersionCheckTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='debops-versioncheck-')
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)
        cache_patcher = unittest.mock.patch(
            'debops.versioncheck.xdg_cache_home',
            os.path.join(self.tmpdir, 'cache'))
        cache_patcher.start()
        self.addCleanup(cache_patcher.stop)

    def cache_file(self):
        return os.path.join(self.tmpdir, 'cache', 'debops',
                            'version_check.json')


class DetectionTestCase(VersionCheckTestCase):
    """Installation method detection."""

    def detect(self, _pkg_dir):
        check = make_check({'enabled': True})
        check._pkg_dir = _pkg_dir
        return check._detect_install_method()

    def repo_with_pkg(self, name, branch):
        repo_dir = os.path.join(self.tmpdir, name)
        git_fixture(repo_dir, branch)
        pkg_dir = os.path.join(repo_dir, 'src', 'debops')
        os.makedirs(pkg_dir)
        return pkg_dir

    def test_disabled_by_default_makes_no_network_calls(self):
        check = make_check()  # no 'enabled' setting present
        check._pkg_dir = os.path.join(self.tmpdir, 'nowhere')
        with unittest.mock.patch.object(check, '_do_check') as do_check:
            check.check()
        do_check.assert_not_called()

    def test_unknown_without_git_repo(self):
        plain_dir = os.path.join(self.tmpdir, 'plain')
        os.makedirs(plain_dir)
        self.assertEqual(self.detect(plain_dir), 'unknown')

    def test_git_master_branch(self):
        self.assertEqual(
            self.detect(self.repo_with_pkg('repo-master', 'master')),
            'git_master')

    def test_git_stable_branch(self):
        self.assertEqual(
            self.detect(self.repo_with_pkg('repo-stable', 'stable-3.3')),
            'git_stable')

    def test_feature_branch_is_unknown(self):
        self.assertEqual(
            self.detect(self.repo_with_pkg('repo-feature',
                                           'feature/something')),
            'unknown')

    def test_pipx_location_detected(self):
        pipx_home = os.path.join(self.tmpdir, 'pipx')
        pkg_dir = os.path.join(pipx_home, 'venvs', 'ansible-core', 'lib',
                               'python3.11', 'site-packages', 'debops')
        os.makedirs(pkg_dir)
        argv0 = os.path.join(pipx_home, 'bin', 'debops')
        with unittest.mock.patch('sys.argv', [argv0]), \
                unittest.mock.patch.dict(os.environ, {'PIPX_HOME': pipx_home}):
            self.assertEqual(self.detect(pkg_dir), 'pipx')


class VersionComparisonTestCase(VersionCheckTestCase):
    """Version parsing and comparison behaviour."""

    def test_parse_version(self):
        check = make_check()
        self.assertEqual(str(check._parse_version('3.3.0')), '3.3.0')
        self.assertEqual(str(check._parse_version('3.3.0.dev10+gfeedface')),
                         '3.3.0.dev10+gfeedface')
        self.assertIsNone(check._parse_version('nonsense~'))

    def test_remote_ref_is_not_an_update_when_equal(self):
        repo_dir = os.path.join(self.tmpdir, 'repo-equal')
        git_fixture(repo_dir, 'master')
        check = make_check()
        check._pkg_dir = repo_dir
        self.assertEqual(check._compare_ref('HEAD'),
                         {'update_available': False, 'source': None})

    def test_remote_ref_ahead_of_head_is_an_update(self):
        # Git rev 'HEAD..ref' counts commits reachable from the ref that
        # are not reachable from HEAD, so the compared ref is the state of
        # the remote which is positioned after the local history
        repo_dir = os.path.join(self.tmpdir, 'repo-behind')
        git_fixture(repo_dir, 'master')
        subprocess.run(['git', '-C', repo_dir, 'commit', '-q',
                        '--allow-empty', '-m', 'remote-only change'],
                       check=True, capture_output=True, env=GIT_ENV)
        subprocess.run(['git', '-C', repo_dir, 'branch', 'remotehead',
                        'HEAD'], check=True, capture_output=True, env=GIT_ENV)
        subprocess.run(['git', '-C', repo_dir, 'reset', '-q', '--hard',
                        'HEAD~1'], check=True, capture_output=True,
                       env=GIT_ENV)
        check = make_check()
        check._pkg_dir = repo_dir
        result = check._compare_ref('remotehead')
        self.assertTrue(result['update_available'])
        self.assertIn('1 commits ahead', result['latest_version'])


class StableBranchTestCase(VersionCheckTestCase):
    """Tag based comparison for 'stable-X.Y' checkouts."""

    def setUp(self):
        super().setUp()
        self.repo_dir = os.path.join(self.tmpdir, 'repo-stable-tags')
        self.check = make_check()
        self.check._pkg_dir = os.path.join(self.repo_dir, 'src', 'debops')
        self.check._pkg_dir and os.makedirs(self.check._pkg_dir)

    def test_latest_tag_newer_than_current(self):
        git_fixture(self.repo_dir, 'stable-3.3', commits=2,
                    tags=['v3.3.0', 'v3.3.1'])
        self.check._version = '3.3.0'
        with unittest.mock.patch.object(self.check, '_git_fetch',
                                        return_value=True):
            result = self.check._check_git_stable()
        self.assertTrue(result['update_available'])
        self.assertEqual(result['latest_version'], '3.3.1')

    def test_no_newer_tag_is_not_an_update(self):
        git_fixture(self.repo_dir, 'stable-3.3', commits=1, tags=['v3.3.1'])
        self.check._version = '3.3.1'
        with unittest.mock.patch.object(self.check, '_git_fetch',
                                        return_value=True):
            result = self.check._check_git_stable()
        self.assertFalse(result['update_available'])


class PyPICheckTestCase(VersionCheckTestCase):
    """The PyPI JSON API check with a mocked response."""

    def setUp(self):
        super().setUp()
        self.check = make_check({'enabled': True})
        self.check._version = '3.3.0'
        self.check._pkg_dir = os.path.join(self.tmpdir, 'plain')

    def pypi_response(self, version):
        """Patch the PyPI JSON response and run the check."""
        payload = json.dumps({'info': {'version': version}})
        response = unittest.mock.mock_open(read_data=payload.encode('utf-8'))
        with unittest.mock.patch('urllib.request.urlopen', response):
            return self.check._check_pypi()

    def test_newer_version_available(self):
        result = self.pypi_response('3.4.0')
        self.assertTrue(result['update_available'])
        self.assertEqual(result['latest_version'], '3.4.0')

    def test_same_version_is_no_update(self):
        self.assertFalse(self.pypi_response('3.3.0')['update_available'])


class NotifyHintTestCase(VersionCheckTestCase):
    """Upgrade hint selected per installation source."""

    def hints(self, source, version='1.0.0'):
        check = make_check()
        check._logger = unittest.mock.Mock()
        check._pkg_dir = self.tmpdir
        check._notify(version, source)
        return check._logger.notice.call_args[0][0]

    def test_pipx_hint(self):
        self.assertIn('(pipx upgrade debops)', self.hints('pipx'))

    def test_pypi_hint(self):
        self.assertIn('(pip install --upgrade debops)',
                      self.hints('pypi'))

    def test_git_master_hint(self):
        self.assertIn('(git pull)', self.hints('git_master'))

    def test_git_stable_hint(self):
        self.assertIn('(git pull --tags)', self.hints('git_stable'))


class CacheTestCase(VersionCheckTestCase):
    """The cached result is replayed without contacting the source."""

    def cache_result(self, source, update_available):
        return {'update_available': update_available,
                'latest_version': '1.2.3', 'source': source}

    def save_fresh_cache(self, result):
        check = make_check({'enabled': True})
        check._save_cache(result)
        return check

    def master_repo_with_pkg(self):
        # A checkable 'git_master' fixture with a stub network response
        repo_dir = os.path.join(self.tmpdir, 'repo-cache')
        git_fixture(repo_dir, 'master')
        pkg_dir = os.path.join(repo_dir, 'src', 'debops')
        os.makedirs(pkg_dir)
        return pkg_dir

    def test_replayed_cached_notice_avoids_network(self):
        check = self.save_fresh_cache(
            self.cache_result('git_master', update_available=True))
        check._logger = unittest.mock.Mock()
        check._pkg_dir = self.master_repo_with_pkg()
        with unittest.mock.patch.object(check, '_git_fetch',
                                        return_value=True) as fetch:
            check.check()
        self.assertFalse(os.path.exists(
            os.path.join(self.tmpdir, 'fetch-marker')))
        self.assertNotIn(True, [fetch.call_count > 1])
        self.assertIn('1.2.3', check._logger.notice.call_args[0][0])

    def test_mismatched_source_is_rechecked_from_the_live_source(self):
        # Cache remembers 'git_stable', but the live tree is on 'master':
        # the live 'master' check runs and finds no remote reference
        check = self.save_fresh_cache(
            self.cache_result('git_stable', update_available=False))
        check._logger = unittest.mock.Mock()
        check._pkg_dir = self.master_repo_with_pkg()
        with unittest.mock.patch.object(check, '_git_fetch',
                                        return_value=True):
            check.check()
        check._logger.notice.assert_not_called()

    def test_stale_cache_is_rechecked(self):
        result = self.cache_result('git_master', update_available=False)
        check = self.save_fresh_cache(result)
        os.utime(self.cache_file(), times=(0, 0))  # mtime in 1970: stale
        check._logger = unittest.mock.Mock()
        check._pkg_dir = self.master_repo_with_pkg()
        with unittest.mock.patch.object(check, '_check_git_master',
                                        return_value=None) as master_check:
            check.check()
        master_check.assert_called_once()
        check._logger.notice.assert_not_called()


if __name__ == '__main__':
    unittest.main()
