# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys

# Detect the DebOps version from the Python module. If the version is not
# available, we are in a development environment in which case we use a stub
# version number to avoid errors.
try:
    from .__version__ import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0"


class Subcommands(object):

    def __init__(self, args=None):
        self.args = args

        self.global_parser = argparse.ArgumentParser(add_help=False)
        self.global_parser.add_argument('-v', '--verbose', action="count",
                                        help='increase output verbosity '
                                             '(e.g., -vv is more than -v)')
        self.global_parser.add_argument('--project-dir', type=str,
                                        nargs='?', default=os.getcwd(),
                                        help='path to the project directory')

        parser = argparse.ArgumentParser(
                description="DebOps CLI",
                usage='''debops <section> [<args>]

Sections:
    project  manage project directories
    exec     run Ansible commands directly against hosts
    run      run Ansible playbook(s) against hosts
    check    run Ansible playbook(s) in check mode
    env      run shell commands in project environment
    config   display DebOps configuration options''')

        parser.add_argument('section', help='Section to run')
        parser.add_argument('--version', action='version',
                            version='%(prog)s {version}'
                                    .format(version=__version__))

        self._section = parser.parse_args(self.args[1:2])
        self.section = self._section.section
        if not hasattr(self, 'do_' + self._section.section):
            print('Error: unrecognized section:', self._section.section)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_' + self._section.section)()

    def add_bool_argument(self, parser, name, default=False,
                          required=False, help=None, no_help=None):
        group = parser.add_mutually_exclusive_group(
                required=required)
        group.add_argument('--' + name, dest=name,
                           help=help, action='store_true')
        group.add_argument('--no-' + name, dest=name,
                           help=no_help, action='store_false')
        parser.set_defaults(**{name: default})

    def do_project(self):
        parser = argparse.ArgumentParser(
                description='manage project directory',
                usage='''debops project <command> [<args>]

Commands:
    init    initialize new project directory
    mkview  create a new infrastructure view
    commit  commit current changes in git repository
    refresh refresh existing project directory
    unlock  decrypt secrets in project directory
    lock    encrypt secrets in project directory''')
        parser.add_argument('command', help='project command to run')
        self._command = parser.parse_args(self.args[2:3])
        self.command = self._command.command
        if not hasattr(self, 'do_project_' + self._command.command):
            print('Error: unrecognized command:', self._command.command)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_project_' + self._command.command)()

    def do_project_init(self):
        parser = argparse.ArgumentParser(
                description='initialize new project directory',
                usage='debops project init [<args>] <project_dir>')
        parser.add_argument('-t', '--type', type=str, nargs='?',
                            choices=['legacy', 'modern'],
                            default='legacy',
                            help='select project type (default: %(default)s)')
        parser.add_argument('-V', '--default-view', type=str,
                            default='system',
                            help='name of the default infrastructure view '
                                 '(default: %(default)s)')
        self.add_bool_argument(parser, 'git',
                               help='enable git support (default)',
                               default='store_true',
                               no_help='disable git support')
        self.add_bool_argument(parser, 'requirements',
                               help='install Ansible Collections after '
                                    'initialization (default)',
                               default='store_true',
                               no_help="don't install Ansible Collections")
        parser.add_argument('--encrypt', type=str, nargs='?',
                            choices=['encfs', 'git-crypt'],
                            help='enable encrypted secrets')
        parser.add_argument('--keys', type=str,
                            help='list of GPG recipients with secret access, '
                                 'delimited by commas')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_refresh(self):
        parser = argparse.ArgumentParser(
                description='refresh existing project directory',
                usage='debops project refresh [<args>] <project_dir>')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_lock(self):
        parser = argparse.ArgumentParser(
                description='encrypt secrets inside project directory',
                usage='debops project lock [<args>] <project_dir>')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to lock')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_unlock(self):
        parser = argparse.ArgumentParser(
                description='decrypt secrets inside project directory',
                usage='debops project unlock [<args>] <project_dir>')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to unlock')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_mkview(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                description='create new infrastructure view',
                usage='debops project mkview [<args>] <new_view>')
        parser.add_argument('--encrypt', type=str, nargs='?',
                            choices=['encfs', 'git-crypt'],
                            help='enable encrypted secrets')
        parser.add_argument('--keys', type=str,
                            help='list of GPG recipients with secret access, '
                                 'delimited by commas')
        parser.add_argument('new_view', type=str, nargs='?',
                            help='name of the new infrastructure view')
        self.args = parser.parse_args(self.args[3:])

    def do_project_commit(self):
        parser = argparse.ArgumentParser(
                description='commit current changes in git repository',
                usage='debops project commit [<args>] <project_dir>')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_exec(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops exec [<args>] [--] <[ansible_args]>',
                description='run Ansible commands directly against hosts')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to use for the "ansible" command')
        parser.add_argument('-E', '--bell', default=False,
                            help='notify the user at the end '
                                 'of Ansible execution',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the Ansible command '
                                 'generated by DebOps',
                            action='store_true')
        parser.add_argument('ansible_args', type=str, nargs=argparse.REMAINDER,
                            help='arguments for the '
                                 '"ansible" command')
        self.args = parser.parse_args(self.args[2:])

    def do_run(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops run [<args>] [--] <[<namespace>.<collection>/]'
                      'playbook> [playbook] ... [ansible_args]',
                description='run Ansible playbook(s) against hosts')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to use for the "ansible-playbook" command')
        parser.add_argument('-E', '--bell', default=False,
                            help='notify the user at the end '
                                 'of Ansible execution',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the Ansible command '
                                 'generated by DebOps',
                            action='store_true')
        parser.add_argument('ansible_args', type=str, nargs=argparse.REMAINDER,
                            help='arguments for the '
                                 '"ansible-playbook" command')
        self.args = parser.parse_args(self.args[2:])

    def do_check(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops check [<args>] [--] <[<namespace>.<collection>/]'
                      'playbook> [playbook] ... [ansible_args]',
                description='run Ansible playbook(s) in check mode')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to use for the "ansible-playbook" command')
        parser.add_argument('-E', '--bell', default=False,
                            help='notify the user at the end '
                                 'of Ansible execution',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the Ansible command '
                                 'generated by DebOps',
                            action='store_true')
        parser.add_argument('ansible_args', type=str,
                            nargs=argparse.REMAINDER,
                            help='arguments for the '
                                 '"ansible-playbook" command')
        parser.add_argument(const='--diff',  dest='ansible_args',
                            help=argparse.SUPPRESS, action='append_const')
        parser.add_argument(const='--check', dest='ansible_args',
                            help=argparse.SUPPRESS, action='append_const')
        self.args = parser.parse_args(self.args[2:])

    def do_env(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops env [<args>] [command_args]',
                description='run shell commands in project environment')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to use for the command')
        parser.add_argument('--scope', type=str, nargs='?',
                            choices=['full', 'local'],
                            default='local',
                            help='specify which environment '
                                 'variables to show (default: %(default)s)')
        parser.add_argument('command_args', type=str, nargs=argparse.REMAINDER,
                            help='command and arguments to execute')
        self.args = parser.parse_args(self.args[2:])

    def do_config(self):
        parser = argparse.ArgumentParser(
                description='manage DebOps configuration state',
                usage='''debops config <command> [<args>]

Commands:
    get     return value of a specific configuration option
    list    list configuration files parsed by DebOps''')
        parser.add_argument('command', help='config command to run')
        self._command = parser.parse_args(self.args[2:3])
        self.command = self._command.command
        if not hasattr(self, 'do_config_' + self._command.command):
            print('Error: unrecognized command:', self._command.command)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_config_' + self._command.command)()

    def do_config_list(self):
        parser = argparse.ArgumentParser(
                usage='debops config list [<args>] <project_dir>',
                description='list configuration files parsed by DebOps')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_config_get(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops config get [<args>] [--] <key>',
                description='return value of specific DebOps option')
        parser.add_argument('--format', type=str, nargs='?',
                            choices=['json', 'toml', 'unix', 'yaml'],
                            default='unix',
                            help='output format (default: %(default)s)')
        parser.add_argument('-k', '--keys', default=False,
                            help='list configuration keys '
                                 'at the specified level',
                            action='store_true')
        parser.add_argument('key', type=str,
                            nargs=argparse.REMAINDER,
                            help='name of the '
                                 'configuration option')
        self.args = parser.parse_args(self.args[3:])
