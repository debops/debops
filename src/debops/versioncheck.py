# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import debops
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from xdg.BaseDirectory import xdg_cache_home

try:
    from .__version__ import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0"


class VersionCheck(object):

    def __init__(self, config, logger=None):
        self._logger = logger or logging.getLogger(__name__)
        self._settings = config.raw.get('version_check', {})
        self._version = __version__
        self._cache_dir = os.path.join(xdg_cache_home, 'debops')
        self._cache_file = os.path.join(self._cache_dir, 'version_check.json')
        self._pkg_dir = os.path.dirname(os.path.abspath(debops.__file__))
        self._repo = None
        self._method = None

    def check(self):
        if not self._settings.get('enabled', False):
            return

        try:
            self._do_check()
        except Exception:
            # Version check is best-effort; never crash the CLI
            self._logger.debug('Version check failed', exc_info=True)

    def _do_check(self):
        method = self._detect_install_method()
        self._method = method

        # Source or unknown installations are managed directly by the user,
        # so there's nothing to check against.
        if method not in ('git_master', 'git_stable', 'git_branch',
                          'pypi', 'pipx'):
            return

        self._logger.debug('Version check: install method %s', method)

        if self._cache_is_fresh():
            cached = self._load_cache()
            # Replay the cached result only if the installation method is
            # unchanged; otherwise fall through and re-check the live source.
            if cached and cached.get('source') == method:
                if cached.get('update_available'):
                    self._notify(cached.get('latest_version'),
                                 cached.get('source'))
                return

        result = None
        if method == 'git_master':
            result = self._check_git_master()
        elif method == 'git_stable':
            result = self._check_git_stable()
        elif method == 'git_branch':
            result = self._check_git_branch()
        elif method in ('pypi', 'pipx'):
            result = self._check_pypi()

        if result is not None:
            self._save_cache(result)
            if result.get('update_available'):
                self._notify(result['latest_version'],
                             result.get('source'))

    def _detect_install_method(self):
        try:
            import git
            repo = git.Repo(self._pkg_dir,
                            search_parent_directories=True)
        except Exception:
            repo = None

        if repo is not None:
            try:
                branch = repo.active_branch.name
            except Exception:
                self._logger.debug(
                    'Version check: detached checkout, nothing to check')
                return 'unknown'
            if branch == 'master':
                return 'git_master'
            if re.match(r'^stable-\d+\.\d+$', branch):
                return 'git_stable'
            # Any other branch with a remote-tracking ref is compared
            # against it; local commits ahead of the upstream keep the
            # check silent, so work in progress is never interrupted
            if self._has_upstream(branch):
                return 'git_branch'
            self._logger.debug(
                "Version check: no upstream for branch '%s', skipping",
                branch)
            return 'unknown'

        if self._is_editable():
            return 'editable'

        if ('site-packages' in self._pkg_dir or
                'dist-packages' in self._pkg_dir):
            if self._is_pipx():
                return 'pipx'
            return 'pypi'

        return 'unknown'

    def _is_editable(self):
        try:
            from importlib.metadata import distribution
        except ImportError:
            return False
        try:
            data = distribution('debops').read_text('direct_url.json')
        except Exception:
            return False
        if not data:
            return False
        try:
            return bool(json.loads(data).get(
                'dir_info', {}).get('editable', False))
        except ValueError:
            return False

    def _is_pipx(self):
        pipx_home = os.environ.get(
                'PIPX_HOME',
                os.path.join(os.path.expanduser('~'), '.local', 'pipx'))
        try:
            if os.path.commonpath([pipx_home,
                                   os.path.realpath(sys.argv[0])]) == pipx_home:
                return True
            if os.path.commonpath([pipx_home, self._pkg_dir]) == pipx_home:
                return True
        except ValueError:
            return False
        return False

    def _git_repo(self):
        if self._repo is None:
            import git
            self._repo = git.Repo(self._pkg_dir,
                                  search_parent_directories=True)
        return self._repo

    def _has_upstream(self, branch):
        """Does a remote-tracking ref exist for the branch?"""
        ref = self._settings.get('git_remote', 'origin') + '/' + branch
        try:
            self._git_repo().commit(ref)
            return True
        except Exception:
            return False

    def _git_fetch(self, with_tags=False):
        timeout = self._settings.get('timeout', 5)
        repo_url = self._settings.get('git_repo_url', '')
        remote = self._settings.get('git_remote', 'origin')

        command = ['git', '-C', self._pkg_dir, 'fetch']
        if with_tags:
            command.append('--tags')
        command.append(repo_url if repo_url else remote)
        command.append('--quiet')

        try:
            subprocess.run(command, timeout=timeout, capture_output=True,
                           check=True)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError,
                FileNotFoundError):
            self._logger.debug('Version check: fetch from %s failed',
                               command[-2], exc_info=True)
            return False

    def _compare_ref(self, ref_name):
        try:
            repo = self._git_repo()
            local = repo.commit('HEAD')
            try:
                remote = repo.commit(ref_name)
            except Exception:
                return None
            if local == remote:
                return {'update_available': False, 'source': self._method}
            ahead = list(repo.iter_commits('HEAD..' + ref_name))
            if ahead:
                return {
                    'update_available': True,
                    'latest_version': '{} ({} commits ahead)'
                                      .format(remote.hexsha[:8], len(ahead)),
                    'source': self._method
                }
            return {'update_available': False, 'source': self._method}
        except Exception:
            return None

    def _check_git_master(self):
        if not self._git_fetch():
            return None
        remote = self._settings.get('git_remote', 'origin')
        url = self._settings.get('git_repo_url', '')
        if url:
            # A fetch from a bare URL leaves refs in FETCH_HEAD; compare there
            return self._compare_ref('FETCH_HEAD')
        return self._compare_ref(remote + '/master')

    def _check_git_branch(self):
        branch = self._git_repo().active_branch.name
        if not self._git_fetch():
            return None
        return self._compare_ref(
            self._settings.get('git_remote', 'origin') + '/' + branch)

    def _check_git_stable(self):
        if not self._git_fetch(with_tags=True):
            return None
        try:
            repo = self._git_repo()
        except Exception:
            return None

        current = self._parse_version(self._version)
        if current is None:
            return None

        branch = repo.active_branch.name
        version_prefix = branch.replace('stable-', '')
        latest_version = None

        for tag in repo.tags:
            tag_str = tag.name.lstrip('v')
            if not tag_str.startswith(version_prefix + '.'):
                continue
            version = self._parse_version(tag_str)
            if (version is not None and
                    (latest_version is None or version > latest_version)):
                latest_version = version

        if latest_version is None:
            return None

        if latest_version > current:
            return {
                'update_available': True,
                'latest_version': str(latest_version),
                'source': self._method
            }
        return {'update_available': False, 'source': self._method}

    def _check_pypi(self):
        timeout = self._settings.get('timeout', 5)
        package = self._settings.get('pypi_package', 'debops')
        url_template = self._settings.get(
                'pypi_url', 'https://pypi.org/pypi/{package}/json')
        url = url_template.format(package=package)

        request = urllib.request.Request(
                url, headers={'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, urllib.error.HTTPError,
                OSError, ValueError, TimeoutError):
            return None

        latest_str = data.get('info', {}).get('version')
        if not latest_str:
            return None

        current = self._parse_version(self._version)
        latest = self._parse_version(latest_str)
        if current is None or latest is None:
            return None

        if latest > current:
            return {
                'update_available': True,
                'latest_version': str(latest),
                'source': self._method
            }
        return {'update_available': False, 'source': self._method}

    def _parse_version(self, version):
        try:
            from packaging.version import Version
            return Version(version)
        except Exception:
            return None

    def _cache_is_fresh(self):
        if not os.path.exists(self._cache_file):
            return False
        try:
            age_hours = (time.time() - os.path.getmtime(self._cache_file)) / 3600
            interval = self._settings.get('check_interval', 24)
            return age_hours < interval
        except OSError:
            return False

    def _load_cache(self):
        try:
            with open(self._cache_file, 'r') as fp:
                data = json.load(fp)
            if (isinstance(data, dict) and
                    'update_available' in data):
                return data
            return None
        except (OSError, ValueError):
            return None

    def _save_cache(self, result):
        try:
            os.makedirs(self._cache_dir, mode=0o755, exist_ok=True)
            result['timestamp'] = time.time()
            with open(self._cache_file, 'w') as fp:
                json.dump(result, fp, indent=2)
                fp.write('\n')
        except OSError:
            pass

    def _notify(self, latest_version, source):
        hint = ''
        if source == 'pipx':
            hint = ' (pipx upgrade debops)'
        elif source == 'pypi':
            if sys.prefix != sys.base_prefix:
                hint = ' (python -m pip install --upgrade debops)'
            else:
                hint = ' (pip install --upgrade debops)'
        elif source in ('git_master', 'git_branch'):
            hint = ' (git pull)'
        elif source == 'git_stable':
            hint = ' (git pull --tags)'

        self._logger.notice(
                'DebOps {} is available, you have {}{}'.format(
                    latest_version, self._version, hint),
                extra={'block': 'syslog'})
