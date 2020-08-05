# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .subcommands import Subcommands


class Interpreter(object):

    def __init__(self, args=None):
        self.args = args
        self.parsed_args = Subcommands(self.args)

        if self.parsed_args.command == 'init':
            self.do_init(self.parsed_args.args)

        elif self.parsed_args.command == 'run':
            self.do_run(self.parsed_args.args)

        elif self.parsed_args.command == 'check':
            self.do_check(self.parsed_args.args)

        elif self.parsed_args.command == 'status':
            self.do_status(self.parsed_args.args)

    def do_init(self, args):
        print('Creating the project directory')

    def do_run(self, args):
        print('Running the Ansible playbooks')

    def do_check(self, args):
        print('Running the playbooks in check mode')

    def do_status(self, args):
        print('Showing project status')
