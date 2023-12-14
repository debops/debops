# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .utils import unexpanduser
from .ansibleconfig import AnsibleConfig
from .ansible.inventory import AnsibleInventory
import subprocess
import configparser
import textwrap
import os
import sys


class AnsiblePlaybookRunner(object):

    def __init__(self, project, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.inventory = AnsibleInventory(project, name=project.view)

        try:
            self._inventory_paths = (
                    project.ansible_cfg.get_option('inventory').split(','))
        except configparser.NoSectionError:
            path = project.ansible_cfg.path
            if (os.path.exists(path) and os.path.isfile(path)):
                raise ValueError("Cannot find [defaults] section in " + path)
            else:
                raise FileNotFoundError("Cannot find Ansible "
                                        "configuration file at " + path)
        except configparser.NoOptionError:
            errmsg = ('Error: No inventory specified in the "ansible.cfg" '
                      'configuration file. You might want to run '
                      '"debops project refresh" command to ensure that it\'s '
                      'included in the generated file. If this is a legacy '
                      'project, check if the "inventory" option is present '
                      'in the ".debops.cfg" file. The default is:')
            print(textwrap.fill(errmsg, 78))
            print('\n    [ansible defaults]\n    inventory = ansible/inventory')
            sys.exit(1)

        self._playbook_dirs = self._expand_playbook_paths(project)
        self._known_collections = self._find_collections(project)

        self._ansible_env = {'ANSIBLE_CONFIG': project.ansible_cfg.path}
        self._ansible_command = [
                project.config.raw['binaries']['ansible-playbook']
        ]
        self._found_playbooks = []

        # Add the --extra-vars with 'global-vars.yml' files first so that they
        # can overridden by the user on the command line
        for inventory in self._inventory_paths:
            inventory_dir = os.path.abspath(
                    os.path.join(
                        os.path.expanduser(
                            project.path), inventory))
            if os.path.isdir(inventory_dir):
                extra_vars_file = os.path.normpath(
                        os.path.join(inventory_dir, '..', 'global-vars.yml'))
                if os.path.isfile(extra_vars_file):
                    self._ansible_command.extend(
                            ['--extra-vars',
                             '@' + os.path.relpath(extra_vars_file)])

        # List of ansible-playbook options which don't expect arguments
        ansible_playbook_flags = ['--ask-vault-password', '--ask-vault-pass',
                                  '--flush-cache', '--force-handlers',
                                  '--list-hosts', '--list-tags',
                                  '--list-tasks', '--step', '--syntax-check',
                                  '--version', '-C', '--check',
                                  '-D', '--diff', '-K', '--ask-become-pass',
                                  '-h', '--help', '-k', '--ask-pass',
                                  '-v', '-vv', '-vvv', '-vvvv', '-vvvvv',
                                  '-vvvvvv', '--verbose',
                                  '-b', '--become']

        self._parsed_args = []
        arg_length = len(self.kwargs['ansible_args'])
        for index, argument in enumerate(self.kwargs['ansible_args']):

            if argument == '--':
                continue
            elif index in self._parsed_args:
                continue
            elif (argument.startswith('-') or argument.startswith('--')):
                # This is an 'ansible-playbook' option which may have an
                # argument, in which case we need to add both of them in the
                # preserved order
                if (index + 1 < arg_length and
                        argument not in ansible_playbook_flags):
                    next_arg = self.kwargs['ansible_args'][index + 1]
                    if (not next_arg.startswith('-') or
                            not next_arg.startswith('--')):
                        self._ansible_command.extend(
                                [argument, self._quote_spaces(next_arg)])
                        self._parsed_args.extend([index, index + 1])
                        continue

                # This is an 'ansible-playbook' option without an argument
                self._ansible_command.append(argument)
                self._parsed_args.append(index)
            else:
                # Most likely a name of a playbook which we can expand
                self._ansible_command.append(self._quote_spaces(
                    self._expand_playbook(project, argument)))
                self._found_playbooks.append(self._quote_spaces(
                    self._expand_playbook(project, argument)))
                self._parsed_args.append(index)

    def _quote_spaces(self, string):
        if ' ' in string:
            return '"{}"'.format(string)
        else:
            return string

    def _ring_bell(self):
        # Notify user at end of execution
        if self.kwargs.get('bell', False):
            print('\a', end='')

    def _expand_playbook_paths(self, project):
        playbook_dirs = []

        playbooks_paths = [
            os.path.join(project.path, 'ansible', 'views',
                         project.view, 'playbooks'),
            os.path.join(project.path, 'ansible', 'playbooks'),
            os.path.join(project.path, 'playbooks')
        ]

        for path in playbooks_paths:
            if os.path.exists(path) and os.path.isdir(path):
                playbook_dirs.append(path)

        return playbook_dirs

    def _walklevel(self, some_dir, level=1):
        '''A custom os.walk function which can limit recursion to a specific level
           under a given subdirectory'''
        some_dir = some_dir.rstrip(os.path.sep)
        num_sep = some_dir.count(os.path.sep)
        for root, dirs, files in os.walk(some_dir, followlinks=True):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs[:]

    def _find_collections(self, project):
        known_collections = {}
        playbook_paths = []

        try:
            collection_paths = project.ansible_cfg.get_option(
                    'collections_paths')
        except configparser.NoOptionError:
            collection_paths = project.ansible_cfg.get_option(
                    'collections_path')

        for directory in collection_paths.split(':'):
            directory = os.path.expanduser(directory)

            # If we are running outside of the project directory, relative
            # paths need to be fixed to absolute paths, otherwise the correct
            # directories won't be found
            if not os.path.isdir(directory):

                # Path might be relative to the 'ansible.cfg' file in an
                # infrastructure view
                if os.path.isdir(os.path.join(project.path, 'ansible',
                                              'views', project.view,
                                              directory)):
                    directory = os.path.join(project.path, 'ansible',
                                             'views', project.view,
                                             directory)

                # Path might be relative to the 'ansible.cfg' file in the root
                # of the project directory
                elif os.path.isdir(os.path.join(project.path, directory)):
                    directory = os.path.join(project.path, directory)

                # Normalize path after resolution
                directory = os.path.realpath(directory)

            # We are looking for the 'playbooks/' subdirectory in Ansible
            # Collections, which have specific directory structure. We want to
            # avoid catching subdirectories further down the path, for example
            # in '<namespace>/<collection>/tests/integration/playbooks/' since
            # they are not a part of the actual collection Ansible cares about.
            #
            # The 'playbooks/' directory we want to find will be 4 levels deep:
            # ansible_collections/<namespace>/<collection>/playbooks/
            for root, dirs, files in list(
                    self._walklevel(os.path.expanduser(directory), 4)):
                if 'playbooks' in dirs:
                    playbook_paths.append(os.path.join(root, 'playbooks'))

        for path in playbook_paths:
            if (os.path.join('ansible', 'collections', 'ansible_collections/')
                    in path):
                collection_name = path.split(
                        os.path.join('ansible',
                                     'collections',
                                     'ansible_collections/'),
                        )[1]
                if collection_name.endswith('/playbooks'):
                    collection_name = collection_name[:-10]
                if not known_collections.get(
                        collection_name.replace('/', '.')):
                    known_collections.update({
                        collection_name.replace('/', '.'): path})

        return known_collections

    def _find_playbook_in_collection(self, playbook):
        playbook_path = None
        playbook_name = playbook

        for collection, path in self._known_collections.items():
            if playbook_name.startswith(collection + '/'):
                playbook_name = '/'.join(playbook_name.split('/')[1:])
                playbook_name = os.path.expanduser(
                        os.path.join(path, playbook_name))
                if os.path.isfile(playbook_name):
                    playbook_path = playbook_name
                    break
        return playbook_path

    def _expand_playbook(self, project, playbook):
        playbook_path = None
        playbook_name = playbook

        # Normalize playbook name, which most likely ends with '.yml' extension
        if not playbook_name.endswith('.yml'):
            playbook_name = playbook_name + '.yml'

        # Check if playbook can be found directly
        if os.path.isfile(playbook_name):
            playbook_path = playbook_name

        if not playbook_path:
            # Check if playbook is present in the project directories
            for playbook_dir in self._playbook_dirs:
                if os.path.isfile(os.path.join(playbook_dir, playbook_name)):
                    playbook_path = os.path.relpath(
                            os.path.join(playbook_dir, playbook_name))
                    break

        if not playbook_path:
            # Find playbook which might be included in an Ansible Collection
            playbook_path = self._find_playbook_in_collection(playbook_name)

        if not playbook_path:
            try:

                # Find playbook in Ansible Collections specific to the current
                # infrastructure view
                collection_names = (
                        (project.config.raw['views'][project.view]
                                           ['playbook_collections']))
                for collection in collection_names:
                    playbook_path = self._find_playbook_in_collection(
                            collection + '/' + playbook_name)
                    if playbook_path:
                        break

            except KeyError:

                # Find playbook in the default Ansible Collection
                playbook_path = self._find_playbook_in_collection(
                        'debops.debops/' + playbook_name)

        if playbook_path:
            return playbook_path
        else:
            return playbook

    def eval(self):
        for key, value in self._ansible_env.items():
            print('export', key + '=' + value)
        print(' '.join(self._ansible_command))

    def execute(self):
        unlocked = False
        if not self._found_playbooks:
            print('No playbooks specified, aborting')
            sys.exit(1)

        for key, value in self._ansible_env.items():
            os.environ[key] = value
        try:
            unlocked = self.inventory.unlock()

            print('Executing Ansible playbooks:')
            for playbook in self._found_playbooks:
                print(unexpanduser(playbook))
            executor = subprocess.Popen(' '.join(self._ansible_command),
                                        shell=True)
            std_out, std_err = executor.communicate()
            self._ring_bell()
            return executor.returncode

        except ChildProcessError:
            raise ChildProcessError('Cannot unlock project secrets, '
                                    'git working directory not clean')

        except KeyboardInterrupt:
            if unlocked:
                self.inventory.lock()
            raise SystemExit('... aborted by user')
        else:
            self._ring_bell()

        finally:
            if unlocked:
                self.inventory.lock()
