# Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .utils import unexpanduser
from .ansibleconfig import AnsibleConfig
from .ansible.inventory import AnsibleInventory
import subprocess
import configparser
import textwrap
import os
import sys


class AnsibleRunner(object):

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

        self._ansible_env = {'ANSIBLE_CONFIG': project.ansible_cfg.path}
        self._ansible_command = [
                project.config.raw['binaries']['ansible']
        ]

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

        # List of ansible options which don't expect arguments
        ansible_flags = ['--ask-vault-password', '--ask-vault-pass',
                         '--list-hosts', '--syntax-check',
                         '--version', '-C', '--check',
                         '-D', '--diff', '-K', '--ask-become-pass',
                         '-h', '--help', '-k', '--ask-pass',
                         '-o', '--one-line', '-v', '-vv', '-vvv',
                         '-vvvv', '-vvvvv', '-vvvvvv', '--verbose',
                         '-b', '--become']

        self._parsed_args = []
        arg_length = len(self.kwargs['ansible_args'])
        for index, argument in enumerate(self.kwargs['ansible_args']):

            if argument == '--':
                continue
            elif index in self._parsed_args:
                continue
            elif (argument.startswith('-') or argument.startswith('--')):
                # This is an 'ansible' option which may have an argument, in
                # which case we need to add both of them in the preserved order
                if (index + 1 < arg_length and
                        argument not in ansible_flags):
                    next_arg = self.kwargs['ansible_args'][index + 1]
                    if (not next_arg.startswith('-') or
                            not next_arg.startswith('--')):
                        self._ansible_command.extend(
                                [argument, self._quote_spaces(next_arg)])
                        self._parsed_args.extend([index, index + 1])
                        continue
                else:
                    self._ansible_command.append(argument)
                    self._parsed_args.append(index)

            else:
                # This is an 'ansible' option without an argument
                self._ansible_command.append(argument)
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

    def eval(self):
        for key, value in self._ansible_env.items():
            print('export', key + '=' + value)
        print(' '.join(self._ansible_command))

    def execute(self):
        unlocked = False

        for key, value in self._ansible_env.items():
            os.environ[key] = value
        try:
            unlocked = self.inventory.unlock()

            executor = subprocess.Popen(' '.join(self._ansible_command),
                                        shell=True)
            std_out, std_err = executor.communicate()
            self._ring_bell()
            return executor.returncode

        except KeyboardInterrupt:
            if unlocked:
                self.inventory.lock()
            raise SystemExit('... aborted by user')

        else:
            self._ring_bell()

        finally:
            if unlocked:
                self.inventory.lock()
