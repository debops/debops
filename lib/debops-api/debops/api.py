#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2016 Robin Schneider <ypid@riseup.net>
# Copyright (C) 2016 DebOps Project http://debops.org/
#
# debops-api is part of DebOps.
#
# debops-api is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3 of the
# License.
#
# debops-api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import json
import re
import logging
import pprint
from distutils.version import StrictVersion
import shutil

import yaml
import git
from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator

__license__ = 'AGPL-3.0-only'
__author__ = 'Robin Schneider <ypid@riseup.net>'
__version__ = '0.1.0'

"""
debops-api - Machine readable metadata about the DebOps Project.
"""


class NoHeaderHTMLTranslator(HTMLTranslator):
    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []


def reSTify(string):
    _w = Writer()
    _w.translator_class = NoHeaderHTMLTranslator
    return core.publish_string(string, writer=_w)


class DebOpsAPI:

    def __init__(
        self,
        strict=True,
        docs_url_pattern=None,
        changelog_url_pattern=None,
        role_owner=None,
        test_mode=False,
    ):

        self._strict = strict
        self._docs_url_pattern = docs_url_pattern
        self._changelog_url_pattern = changelog_url_pattern
        self._role_owner = role_owner
        self._test_mode = test_mode

        self._metadata = {}
        self._roles = {}

    def _get_role_full_name(self, role_owner, role_name):
        """
        Return the Ansible role name according to Ansible Galaxy naming
        convention.
        """

        return '{}.{}'.format(role_owner, role_name)

    def _get_repo_url(self, role_owner, role_name):
        """
        Return repository URL for the given Ansible role.
        """

        github_base_url = 'https://github.com'
        return '/'.join([
            github_base_url,
            role_owner,
            'ansible-' + self._get_normalized_role_name(role_name),
        ])

    def _read_github_repos_api_response(
        self,
        api_res_encoded_json,
        role_owner=None
    ):
        """
        Read GitHub API response for a /users/:username/repos or
        /orgs/:org/repos query handed over as encoded JSON string.
        Unfinished because relying on GitHub API is discouraged for the DebOps
        Project in case there are other ways to do it.
        """

        api_response = json.load(api_res_encoded_json)
        for repo in api_response:
            _re = re.match(r'ansible-(?P<role_name>[a-z0-9_-]+)+$',
                           repo['name'])
            if not _re:
                continue

            role_name = _re.group('role_name')
            role_full_name = self._get_role_full_name(role_owner, role_name)
            role_owner = self._get_owner_from_vcs_url(repo['html_url'])

            metadata_from_api = {
                'role_owner': role_owner,
                'role_name': role_name,
                'vcs_url': repo['html_url'],
                'role_format_version': '0.1.0',
            }
            self._metadata.setdefault(role_full_name, {})
            self._metadata[role_full_name].update(metadata_from_api)

    def read_github_repos_api_file(self, file_path, role_owner=None):
        """
        Read GitHub API response file for a /users/:username/repos or
        /orgs/:org/repos query passed as file path.
        """

        with open(args.github_api_response_file) as gh_rsp_fh:
            self._read_github_repos_api_response(
                gh_rsp_fh,
                role_owner=role_owner,
            )

    def _interpret_role_dir_name(self, role_dir_name):
        """
        Extract and return information from the role directory name.
        """

        version_by_pattern_map = {
            '0.1.0': re.compile(
                r'^(?P<role_owner>[^.]+)\.(?P<role_name>[a-z0-9_-]+)\.rst$'),
            '0.2.0': re.compile(
                r'^ansible-(?P<role_name>[a-z0-9_-]+)$'),
        }

        for role_format_version, pattern in version_by_pattern_map.items():
            _re = pattern.search(role_dir_name)
            if _re:
                role_owner = None
                if 'role_owner' in _re.groups():
                    role_owner = _re.group('role_owner')
                role_name = _re.group('role_name')
                logger.debug('Detected docs format version {} '
                             'for owner: {}, name: {} from {}'.format(
                                    role_format_version,
                                    role_owner,
                                    role_name,
                                    role_dir_name,
                                ))
                return {
                    'role_format_version': role_format_version,
                    'role_owner': role_owner,
                    'role_name': role_name,
                }

        return None

    def _get_decoded_yaml(self, yaml_file_path):
        """
        Get decoded YAML file.
        """

        try:
            with open(yaml_file_path) as ansigenome_fh:
                return yaml.safe_load(ansigenome_fh)
        except OSError:
            return {}

    def _get_owner_from_vcs_url(self, vcs_url):
        """
        Return owner name from VCS URL.
        Return `ypid` for `https://github.com/ypid/ansible-packages/`.
        """

        _re = re.match('[^:]+://[^/]+/(?P<owner_name>[^/]+)/', vcs_url)
        if _re:
            owner_name = _re.group('owner_name')
            logger.debug("Detected owner '{}' for URL: {}".format(
                owner_name,
                vcs_url,
            ))
            return owner_name
        else:
            return None

    def _get_vcs_info(self, dir_path):
        """
        Read VCS metadata for the given directory path.
        """

        g = git.Git(dir_path)

        # %cd: committer date
        last_committer_date = g.log('-1', '--format=%cd', '--date=iso8601')
        #  logger.debug('Got last committer date {} for: {}'.format(
        #      last_committer_date,
        #      dir_path,
        #  ))

        #  describe_version = g.describe()
        #  logger.debug(describe_version)

        try:
            version = g.describe('--abbrev=0', '--tags')
        except Exception:
            # Did not work on Travis test.
            # except git.exc.GitCommandError:
            version = '0.0.0'

        if self._test_mode:
            # Fake committer date in test mode
            last_committer_date = '1970-01-01 00:00:00 +0000'

        metadata = {
            'vcs_last_committer_date': last_committer_date,
            'version': re.sub(r'^v', '', version),
        }

        if not self._test_mode and version != '0.0.0':
            try:
                commits_since_last_release = len(
                    g.log('{}...HEAD'.format(version), '--oneline').split('\n')
                )
            except Exception:
                commits_since_last_release = None

            if commits_since_last_release is not None:
                metadata.update({
                    'vcs_commits_since_last_release': (
                        commits_since_last_release),
                })

        return metadata

    def _get_maintainers_from_line(self, line):
        # Modeled with the natural language processing from AIML in mind.
        # TODO: Remove redundancy. Duplicated into ansigenome source code.
        # Origin: debops-api
        _re = re.match(
            r'^[^.]*?maintainers?[\W_]+(:?is|are)[\W_]+`?(?P<nicks>.+?)\.?$',
            line,
            re.IGNORECASE
        )
        if _re:
            return [x.rstrip('_') for x in re.split(r'[\s,]+',
                    _re.group('nicks')) if x not in ['and', ',']]
        else:
            return None

    def _get_maintainers_from_changelog(self, changes_file):
        # TODO: Remove redundancy. Duplicated into ansigenome source code.
        # Origin: debops-api
        """
        Extract the maintainer from CHANGES.rst file and return the nickname of
        the maintainer.
        """

        try:
            with open(changes_file, 'r') as changes_fh:
                for line in changes_fh:
                    nick = self._get_maintainers_from_line(line)
                    if nick is not None:
                        return nick
        except FileNotFoundError:
            return None
        return None

    def _get_role_metadata(self, role_path):
        """
        Read metadata for the given role.
        """

        role_metadata = {}

        role_metadata['ansigenome'] = self._get_decoded_yaml(
            os.path.join(role_path, 'meta', 'ansigenome.yml')
        )['ansigenome_info']

        role_metadata['meta'] = self._get_decoded_yaml(
            os.path.join(role_path, 'meta', 'main.yml')
        )

        maintainer_nicks = self._get_maintainers_from_changelog(
            os.path.join(role_path, 'CHANGES.rst')
        )
        if maintainer_nicks is not None:
            role_metadata['maintainer_nicks'] = maintainer_nicks
            role_metadata['role_format_version'] = '0.2.1'

        return role_metadata

    def _get_normalized_meta_ansigenome(self, meta_ansigenome):
        """
        Returns normalized meta/ansigenome.yml data intended for inclusion in
        self._metadata.
        """

        metadata = {}

        if 'authors' in meta_ansigenome:
            metadata.setdefault('authors', [])

            for author_item in meta_ansigenome['authors']:
                metadata['authors'].append({
                    'name': author_item['name'],
                    'nick': author_item['github'],
                    'maintainer': False,
                })

        return metadata

    def _get_normalized_role_name(self, role_name):
        """
        Returns normalized role name as used in URLs
        Example role name: `ansible`, returns: `role-ansible`.
        """

        if role_name == 'ansible':
            role_name = 'role-' + role_name
        return role_name

    def _get_normalized_meta_main(self, meta_main):
        """
        Returns normalized meta/main.yml data intended for inclusion in
        self._metadata.
        """

        metadata = {}
        if 'galaxy_info' not in meta_main:
            return metadata

        license_map = {
            'GNU General Public License v3': 'GPL-3.0-only',
        }
        skip_keys = [
            'company',
            'author',
        ]
        rename_keys = {
            'galaxy_tags': 'tags',
        }

        for k, v in meta_main['galaxy_info'].items():
            if k == 'license':
                if v in license_map:
                    v = license_map[v]
            if k in skip_keys:
                continue
            k = rename_keys.get(k, k)

            metadata[k] = v

        return metadata

    def gen_role_metadata(self):
        """
        Generate metadata based on already present metadata.
        """

        for role_full_name, metadata in self._metadata.items():

            role_owner = metadata['role_owner']
            role_name = metadata['role_name']

            additonal_metadata = {
                'normalized_role_name': (
                    self._get_normalized_role_name(role_name)),
                'ci_badge_url': (
                    'https://api.travis-ci.org/{}/ansible-{}.png'.format(
                        role_owner,
                        self._get_normalized_role_name(role_name),
                    )
                ),
                'ci_url': 'https://travis-ci.org/{}/ansible-{}'.format(
                    role_owner,
                    self._get_normalized_role_name(role_name),
                ),
                'test_suite_url': (
                    'https://github.com/debops/test-suite/'
                    'tree/master/ansible-{}'.format(
                        self._get_normalized_role_name(role_name),
                    )
                ),
                'galaxy_url': 'https://galaxy.ansible.com/{}/{}'.format(
                    role_owner,
                    role_name,
                ),
            }

            if 'vcs_url' in metadata:
                additonal_metadata.update({
                    'clone_url': metadata['vcs_url'] + '.git',
                    'issue_url': metadata['vcs_url'] + '/issues',
                    'pr_url': metadata['vcs_url'] + '/pulls',
                })

            if StrictVersion('0.2.0') <= \
                    StrictVersion(metadata['role_format_version']):

                if self._docs_url_pattern:
                    additonal_metadata['docs_url'] = (
                            self._docs_url_pattern.format(
                                role_owner=role_owner,
                                role_name=role_name,
                                normalized_role_name=(
                                    self._get_normalized_role_name(role_name)),
                            )
                        )

                if self._changelog_url_pattern:
                    additonal_metadata['changelog_url'] = (
                            self._changelog_url_pattern.format(
                                role_owner=role_owner,
                                role_name=role_name,
                                normalized_role_name=(
                                    self._get_normalized_role_name(role_name)),
                            )
                        )

            self._metadata[role_full_name].update(additonal_metadata)

    def read_role_metadata(self, role_path):
        """
        Read metadata from each role available in role_path.
        """

        for role_dir_name in os.listdir(role_path):
            role_dir_info = self._interpret_role_dir_name(role_dir_name)

            # Ignore roles with old docs format for now since it would be
            # required to get the meta data from external servers (and to
            # encourage conversion to the new docs format).
            if role_dir_info:
                if StrictVersion('0.2.0') <= StrictVersion(
                        role_dir_info['role_format_version']):
                    role_name = role_dir_info['role_name']
                    role_metadata = self._get_role_metadata(
                            os.path.join(role_path, role_dir_name))
                    role_vcs_url = role_metadata['ansigenome']['github_url']
                    role_owner = self._get_owner_from_vcs_url(role_vcs_url)
                    role_full_name = self._get_role_full_name(
                            role_owner, role_name)

                    metadata = {
                        'vcs_url': role_vcs_url,
                        'role_format_version':
                            role_metadata['role_format_version']
                            if 'role_format_version' in role_metadata
                            else role_dir_info['role_format_version'],
                        'role_owner': role_owner,
                        'role_name': role_name,
                    }

                    metadata.update(
                        self._get_vcs_info(os.path.join(
                            role_path, role_dir_name))
                    )

                    if 'meta' in role_metadata:
                        metadata.update(
                            self._get_normalized_meta_main(
                                role_metadata['meta'])
                        )
                    if 'ansigenome' in role_metadata:
                        metadata.update(
                            self._get_normalized_meta_ansigenome(
                                role_metadata['ansigenome'])
                        )
                    if 'maintainer_nicks' in role_metadata:
                        nicks = role_metadata['maintainer_nicks']
                        metadata.setdefault('authors', [])

                        author_present = set([])
                        for author_item in metadata['authors']:
                            if author_item['nick'] in nicks:
                                author_present.add(author_item['nick'])
                                author_item['maintainer'] = True
                        if not author_present:
                            if self._strict:
                                raise Exception(
                                    "Nick(s) {nicks} are maintainers but"
                                    " no other meta information for them"
                                    " could be found in the repository."
                                    " Affected role: {role_full_name}".format(
                                        role_full_name=role_full_name,
                                        nicks=set(nicks).difference(
                                            author_present),
                                    )
                                )

                else:
                    # Legacy stuff.
                    role_name = role_dir_info['role_name']
                    role_owner = (role_dir_info['role_owner']
                                  if role_dir_info['role_owner']
                                  else self._role_owner)
                    if not role_owner:
                        raise Exception("Default role owner"
                                        " not given but required.")

                    role_vcs_url = self._get_repo_url(
                        role_owner,
                        role_name,
                    )
                    role_full_name = self._get_role_full_name(
                        role_owner,
                        role_name,
                    )

                    metadata = {
                        'vcs_url': role_vcs_url,
                        'role_format_version': '0.1.0',
                        'role_owner': role_owner,
                        'role_name': role_name,
                    }

                self._metadata.setdefault(role_full_name, {})
                self._metadata[role_full_name].update(metadata)

    def get_metadata(self, metadata=None):
        """
        Return public metadata.
        """

        if not metadata:
            metadata = self._metadata

        return metadata

        if not isinstance(metadata, dict):
            return metadata

        public_metadata = {}

        for k, v in metadata.items():
            if not k.startswith('_'):
                public_metadata[k] = self.get_metadata(v)

        return public_metadata

    def write_api_dir(self, api_dir):
        """
        Write metadata to API directory.
        The write is done to a temp directory which is later renamed to archive
        a atomic operation and to ensure that the API returns consistent data.
        """

        api_work_root_dir = api_dir
        api_dir = os.path.join(api_dir, 'v0')
        api_work_dir = api_dir + '_new'

        try:
            shutil.rmtree(api_work_dir)
        except OSError:
            pass

        os.makedirs(os.path.join(api_work_dir, 'role'))
        os.makedirs(os.path.join(api_work_dir, 'roles'))

        # API: /
        with open(os.path.join(api_work_dir, 'version'), 'w') as outfile:
            outfile.write('{}\n'.format(__version__))

        debops_api_base_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '..')
        with open(os.path.join(api_work_dir, 'license'), 'w') as outfile:
            with open(os.path.join(debops_api_base_dir,
                                   'COPYRIGHT'), 'r') as copyright:
                outfile.write(copyright.read())
            outfile.write('\n\n\n')
            with open(os.path.join(debops_api_base_dir,
                                   'LICENSE'), 'r') as license:
                outfile.write(license.read())

        with open(os.path.join(debops_api_base_dir,
                               'README.rst'), 'r') as license:
            readme_html_string = reSTify(
                    license.read()).decode('utf-8', 'strict')
            with open(os.path.join(api_work_root_dir,
                                   'README.html'), 'w') as outfile:
                outfile.write(readme_html_string)
            with open(os.path.join(api_work_dir,
                                   'README.html'), 'w') as outfile:
                outfile.write(readme_html_string)

        # API: /role/
        for role_full_name, metadata in self.get_metadata().items():
            role_api_file = os.path.join(
                api_work_dir,
                'role',
                role_full_name + '.json'
            )
            with open(role_api_file, 'w') as outfile:
                json.dump(metadata, outfile, sort_keys=True)
                outfile.write('\n')

        # API: /roles/
        with open(os.path.join(api_work_dir,
                               'roles', 'count'), 'w') as outfile:
            outfile.write('{}\n'.format(len(self.get_metadata().keys())))

        metadata_per_owner = {}
        for role_full_name, metadata in self.get_metadata().items():
            role_owner = metadata['role_owner']
            metadata_per_owner.setdefault(role_owner, {})
            metadata_per_owner[role_owner][role_full_name] = metadata

        for role_owner, metadata in metadata_per_owner.items():
            with open(os.path.join(api_work_dir, 'roles',
                                   role_owner + '.list'),
                      'w') as outfile:
                role_list = self.get_metadata(metadata).keys()
                outfile.write('\n'.join(sorted(role_list)) + '\n')
            with open(os.path.join(api_work_dir,
                                   'roles', role_owner + '.json'),
                      'w') as outfile:
                json.dump(self.get_metadata(metadata), outfile, sort_keys=True)
                outfile.write('\n')
            with open(os.path.join(api_work_dir,
                                   'roles', 'count:' + role_owner),
                      'w') as outfile:
                outfile.write('{}\n'.format(
                    len(self.get_metadata(metadata).keys())))

        try:
            shutil.rmtree(api_dir)
        except OSError:
            pass

        os.rename(api_work_dir, api_dir)


if __name__ == '__main__':
    from argparse import ArgumentParser

    args_parser = ArgumentParser(
        description=__doc__,
    )
    args_parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    args_parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements.",
        action='store_const',
        dest='loglevel',
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    args_parser.add_argument(
        '-v', '--verbose',
        help="Be verbose.",
        action='store_const',
        dest='loglevel',
        const=logging.INFO,
    )
    args_parser.add_argument(
        '-n', '--no-strict',
        help="Do not exit immediately when there is a inconsistency.",
        dest='strict',
        action='store_false',
        default=True,
    )
    args_parser.add_argument(
        '-i', '--github-api-response-file',
        help="Responds file from a /users/:username/repos"
        " or /orgs/:org/repos API query.",
    )
    args_parser.add_argument(
        '-r', '--role-path',
        help="Base directory where all roles are available.",
    )
    args_parser.add_argument(
        '-o', '--role-owner',
        help="Default role owner if not available from Ansible role metadata.",
        default='debops',
    )
    args_parser.add_argument(
        '-a', '--api-dir',
        help="Write the static parts of api.debops.org"
        " to the given directory."
        " Note that all files in this directory are going to be"
        " overwritten or deleted.",
    )
    args_parser.add_argument(
        '-D', '--docs-url-pattern',
        help="Documentation URL for each role.",
        default='https://docs.debops.org/en/latest/'
        'ansible/roles/ansible-{role_name}/docs/index.html',
    )
    args_parser.add_argument(
        '-C', '--changelog-url-pattern',
        help="Changelog URL for each role.",
        default='https://docs.debops.org/en/latest/'
        'ansible/roles/ansible-{role_name}/docs/changelog.html',
    )
    args_parser.add_argument(
        '-t', '--test-mode',
        help="Make the output reproducible by normalizing changing peaces like"
        "timestamps.",
        action='store_true',
        default=False,
    )
    args = args_parser.parse_args()
    if not args.github_api_response_file and not args.role_path:
        args_parser.print_help()
        sys.exit(1)

    logger = logging.getLogger(__file__)
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=args.loglevel,
    )

    debops_metadata = DebOpsAPI(
        strict=args.strict,
        docs_url_pattern=args.docs_url_pattern,
        changelog_url_pattern=args.changelog_url_pattern,
        role_owner=args.role_owner,
        test_mode=args.test_mode,
    )

    if args.github_api_response_file:
        debops_metadata.read_github_repos_api_file(
            args.github_api_response_file,
        )

    if args.role_path:
        debops_metadata.read_role_metadata(args.role_path)

    debops_metadata.gen_role_metadata()

    if args.api_dir:
        debops_metadata.write_api_dir(args.api_dir)

    logging.info("Metadata:\n{}".format(
        pprint.pformat(debops_metadata.get_metadata()),
    ))
