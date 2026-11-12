# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Ansible-specific layer of the project runners.

The :class:`AnsibleProjectRunner` base class adds the Ansible argument
parsing and the Ansible environment construction on top of the
tool-agnostic :class:`debops.core.runner.Runner`, for the runners
which execute Ansible and user commands inside a project directory.
"""

from ..runner import Runner
import configparser
import logging
import os
import textwrap

logger = logging.getLogger(__name__)


class AnsibleProjectRunner(Runner):

    def __init__(self, project, bell=False):
        super().__init__(project, bell=bell, secrets_name='ansible')

        try:
            self._inventory_paths = (
                    project.ansible_cfg.get_option('inventory').split(','))
        except configparser.NoSectionError:
            path = project.ansible_cfg.path
            if (os.path.exists(path) and os.path.isfile(path)):
                logger.error('Cannot find [defaults] section in '
                             '{}'.format(path))
                raise ValueError("Cannot find [defaults] section in " + path)
            else:
                raise FileNotFoundError("Cannot find Ansible "
                                        "configuration file at " + path)
        except configparser.NoOptionError:
            errmsg = ('No inventory specified in the "ansible.cfg" '
                      'configuration file. You might want to run '
                      '"debops project refresh" command to ensure that it\'s '
                      'included in the generated file. If this is a legacy '
                      'project, check if the "inventory" option is present '
                      'in the ".debops.cfg" file. The default is:')
            raise ValueError(textwrap.fill(errmsg, 78) + '\n\n'
                             '    [ansible defaults]\n'
                             '    inventory = ansible/inventory')

    def _quote_spaces(self, string):
        if ' ' in string:
            return '"{}"'.format(string)
        else:
            return string

    def _add_global_vars(self):
        """Add the --extra-vars with 'global-vars.yml' files first so that
        they can be overridden by the user on the command line."""
        for inventory in self._inventory_paths:
            inventory_dir = os.path.abspath(
                    os.path.join(
                        os.path.expanduser(
                            self.project.path), inventory))
            if os.path.isdir(inventory_dir):
                extra_vars_file = os.path.normpath(
                        os.path.join(inventory_dir, '..', 'global-vars.yml'))
                if os.path.isfile(extra_vars_file):
                    self._ansible_command.extend(
                            ['--extra-vars',
                             '@' + os.path.relpath(extra_vars_file,
                                                   self.project.path)])

    def _expand_positional_argument(self, project, argument, index):
        """Handle a positional argument which is not an Ansible option.
        Runners which interpret positional arguments further can override
        this method."""
        self._ansible_command.append(argument)
        self._parsed_args.append(index)

    def _parse_ansible_args(self, ansible_args, project, flags):
        """Parse the arguments meant for Ansible, preserving their order.

        Options with separate arguments are kept together; the runners can
        customize what happens to the positional arguments.
        """
        self._parsed_args = []
        arg_length = len(ansible_args)
        for index, argument in enumerate(ansible_args):

            if argument == '--':
                continue
            elif index in self._parsed_args:
                continue
            elif (argument.startswith('-') or argument.startswith('--')):
                # This is an Ansible option which may have an argument, in
                # which case we need to add both of them in the preserved
                # order
                if (index + 1 < arg_length and
                        argument not in flags):
                    next_arg = ansible_args[index + 1]
                    if not next_arg.startswith('-'):
                        self._ansible_command.extend(
                                [argument, self._quote_spaces(next_arg)])
                        self._parsed_args.extend([index, index + 1])
                        continue

                # This is an Ansible option without an argument
                self._ansible_command.append(argument)
                self._parsed_args.append(index)

            else:
                self._expand_positional_argument(project, argument, index)

    def eval(self):
        """Return the shell commands which set up the project environment.

        The returned lines are meant to be passed to a shell 'eval', they
        export the Ansible environment variables and end with the Ansible
        command itself.
        """
        lines = ['export {}={}'.format(key, value)
                 for key, value in self._ansible_env.items()]
        lines.append(' '.join(self._ansible_command))
        return '\n'.join(lines)
