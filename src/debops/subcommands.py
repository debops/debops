# -*- coding: utf-8 -*-

# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
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
        self.global_parser.add_argument('--project-dir', type=str,
                                        nargs='?', default=os.getcwd(),
                                        help='path to the project directory')

        parser = argparse.ArgumentParser(
                description="DebOps CLI",
                usage='''debops <section> [<args>]

Sections:
    project  manage project directories
    run      run Ansible playbook(s) against hosts
    check    run Ansible playbook(s) in check mode
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
    refresh refresh existing project directory
    unlock  decrypt secrets in project directory
    lock    encrypt secrets in project directory
    status  display project information''')
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
        self.add_bool_argument(parser, 'git',
                               help='enable git support (default)',
                               no_help='disable git support')
        parser.add_argument('--encrypt', type=str, nargs='?',
                            choices=['encfs', 'git-crypt'],
                            help='enable encrypted secrets')
        parser.add_argument('--keys', type=str,
                            help='list of GPG recipients with secret access, '
                                 'delimited by commas')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_refresh(self):
        parser = argparse.ArgumentParser(
                description='refresh existing project directory',
                usage='debops project refresh [<args>] <project_dir>')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_lock(self):
        parser = argparse.ArgumentParser(
                description='encrypt secrets inside project directory',
                usage='debops project lock [<args>] <project_dir>')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_unlock(self):
        parser = argparse.ArgumentParser(
                description='decrypt secrets inside project directory',
                usage='debops project unlock [<args>] <project_dir>')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_status(self):
        parser = argparse.ArgumentParser(
                usage='debops project status [<args>] <project_dir>',
                description='display project information')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_run(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops run [<args>] [--] <[<namespace>.<collection>/]'
                      'playbook> [playbook] ... [ansible_args]',
                description='run Ansible playbook(s) against hosts')
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

    def do_config(self):
        parser = argparse.ArgumentParser(
                parents=[self.global_parser],
                usage='debops config [<args>]',
                description='display DebOps configuration options')
        parser.add_argument('--env', default=False,
                            help='show environment inside DebOps '
                                 'execution context',
                            action='store_true')
        parser.add_argument('--format', type=str, nargs='?',
                            choices=['json', 'toml'],
                            default='toml',
                            help='output format (default: %(default)s)')
        self.args = parser.parse_args(self.args[2:])
