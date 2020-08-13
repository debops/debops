# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os

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
        parser = argparse.ArgumentParser(
                description="DebOps CLI",
                usage='''debops <command> [<args>]

Commands:
    init     initialize new project directory
    status   display project information
    run      run Ansible playbook(s) against hosts
    check    run Ansible playbook(s) in check mode''')

        parser.add_argument('command', help='Subcommand to run')
        parser.add_argument('--version', action='version',
                            version='%(prog)s {version}'
                                    .format(version=__version__))

        self.subcommand = parser.parse_args(self.args[1:2])
        self.command = self.subcommand.command
        if not hasattr(self, 'do_' + self.subcommand.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, 'do_' + self.subcommand.command)()

    def add_bool_argument(self, parser, name, default=False,
                          required=False, help=None, no_help=None):
        group = parser.add_mutually_exclusive_group(
                required=required)
        group.add_argument('--' + name, dest=name,
                           help=help, action='store_true')
        group.add_argument('--no-' + name, dest=name,
                           help=no_help, action='store_false')
        parser.set_defaults(**{name: default})

    def do_init(self):
        parser = argparse.ArgumentParser(
                description='initialize new project directory',
                usage='debops init [<args>] [dir]')
        self.add_bool_argument(parser, 'git',
                               help='enable git support (default)',
                               no_help='disable git support')
        parser.add_argument('dir', type=str, nargs='?', default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[2:])

    def do_status(self):
        parser = argparse.ArgumentParser(
                description='display project information')
        self.args = parser.parse_args(self.args[2:])

    def do_run(self):
        parser = argparse.ArgumentParser(
                description='run Ansible playbook(s) against hosts')
        parser.add_argument('playbook', type=str, nargs='?',
                            default='site.yml',
                            help='names of Ansible playbooks')
        self.args = parser.parse_args(self.args[2:])

    def do_check(self):
        parser = argparse.ArgumentParser(
                description='run Ansible playbook(s) in check mode')
        parser.add_argument('playbook', type=str, nargs='?',
                            default='site.yml',
                            help='names of Ansible playbooks')
        self.args = parser.parse_args(self.args[2:])
