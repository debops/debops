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
import shlex
import textwrap

from ..ssh.store import (USER_KNOWN_HOSTS_STORE, declared_known_hosts_store,
                         ensure_store_dir, quote_store_path)

logger = logging.getLogger(__name__)


class AnsibleProjectRunner(Runner):

    def __init__(self, project, bell=False):
        super().__init__(project, bell=bell, secrets_name='ansible')
        self._accept_armed = False

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

        self._ensure_known_hosts_store()

    def _ensure_known_hosts_store(self):
        """Create the known_hosts store directory which the view
        declares in its 'ansible.cfg'.

        The ssh client cannot create the missing parent directories
        when it accepts a host key into the store, so the directory
        chain is ensured before the connections run.
        """
        store = declared_known_hosts_store(self.project)
        if store:
            try:
                ensure_store_dir(store, self.project.path)
            except OSError as error:
                logger.notice('Cannot ensure the known_hosts store of '
                              'the view: ' + str(error),
                              extra={'allow': 'stderr'})

    def _enable_accept_new(self, env):
        """Compose the 'ANSIBLE_SSH_ARGS' environment variable which
        makes the ssh connections accept unseen host keys on first
        contact.

        The environment variable masks the 'ssh_args' of the
        'ansible.cfg', so the composed value carries the configured
        arguments forward and adds the accept-new option; an
        'ANSIBLE_SSH_ARGS' variable of the operator's environment takes
        precedence over the configured one. The known_hosts store of
        the view is carried as well when the composed value does not
        declare one: without it, an operator's environment variable
        would store the accepted keys outside of the project store.

        The acceptance itself happens inside the ssh connections of
        the run; the runner announces it up front, and reports what
        the store gained after the run finished.
        """
        try:
            ssh_args = self.project.ansible_cfg.get_option(
                'ssh_args', section='ssh_connection')
        except (configparser.NoOptionError, configparser.NoSectionError):
            ssh_args = None
        base = os.environ.get('ANSIBLE_SSH_ARGS') or ssh_args
        if not base:
            # Neither the environment nor the configuration carries the
            # ssh_args: the connection plugin applies its own default,
            # which the composed variable would replace -- restate it,
            # the way the ssh configuration drop-in of the project mode
            # does. The default of the plugin is restated here by
            # value; a change of the plugin default must be mirrored
            base = '-C -o ControlMaster=auto -o ControlPersist=60s'
        # The accept-new option leads the composed value: ssh applies
        # the first obtained value of an option, and an explicit
        # '--accept' must not be defeated by a StrictHostKeyChecking
        # in the base arguments
        composed = '-o StrictHostKeyChecking=accept-new'
        if base:
            composed += ' ' + base
        store = declared_known_hosts_store(self.project)
        try:
            tokens = shlex.split(composed)
        except ValueError:
            # An environment value whose quotes do not balance cannot
            # be inspected; the store is carried, as it was before the
            # inspection existed
            tokens = []
        if store and not any('UserKnownHostsFile' in token
                             for token in tokens):
            # The single-quoted form survives the argument splitting
            # of the ssh connection plugin, which would consume the
            # double quotes of the store path directly
            composed += (' -o \'UserKnownHostsFile='
                         + quote_store_path(store) + '\'')
        env['ANSIBLE_SSH_ARGS'] = composed
        self._accept_armed = True
        logger.notice('Ansible will auto-accept new SSH host keys',
                      extra={'allow': ['stderr', 'syslog']})

    def _accept_store(self):
        """Return the known_hosts file the connections accept new keys
        into: the store the view declares, or the operator's own
        known_hosts file in the user mode."""
        return (declared_known_hosts_store(self.project)
                or os.path.expanduser(USER_KNOWN_HOSTS_STORE))

    def _snapshot_accepted_keys(self):
        """Return the known_hosts entries the store holds before the
        run, as a set of lines, or None when the acceptance is not
        armed.

        The entries are compared as lines, not as key material: the
        acceptance of Ansible's connections appends lines and never
        rewrites the existing ones, so a new line is a new entry even
        when its key is already trusted under another name of the
        host -- and that is exactly the event worth reporting.
        """
        if not self._accept_armed:
            return None
        try:
            with open(self._accept_store(), 'rb') as handle:
                content = handle.read().decode('utf-8', 'replace')
        except OSError:
            return set()
        return {line for line in content.splitlines() if line}

    def _report_accepted_keys(self, snapshot):
        """Report the host keys Ansible accepted during the run.

        The report names Ansible as the acceptor, because the
        acceptance happens inside its ssh connections; it is skipped
        when the store gained no entries, and the singular form is
        used for one entry.
        """
        if snapshot is None:
            return
        try:
            with open(self._accept_store(), 'rb') as handle:
                content = handle.read().decode('utf-8', 'replace')
        except OSError:
            return
        added = ({line for line in content.splitlines() if line}
                 - snapshot)
        if not added:
            return
        count = len(added)
        logger.notice(
            'Ansible auto-accepted {} {} during the run'.format(
                count, 'SSH host key' if count == 1
                else 'SSH host keys'),
            extra={'allow': ['stderr', 'syslog']})

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
