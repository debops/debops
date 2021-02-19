# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .config import Configuration
from .subcommands import Subcommands
from .projectdir import ProjectDir
from .ansibleplaybookrunner import AnsiblePlaybookRunner


class Interpreter(object):

    def __init__(self, args=None):
        self.args = args
        self.config = Configuration()
        self.parsed_args = Subcommands(self.args)

        if self.parsed_args.section == 'project':
            if self.parsed_args.command == 'init':
                self.do_project_init(self.parsed_args.args)
            elif self.parsed_args.command == 'refresh':
                self.do_project_refresh(self.parsed_args.args)
            elif self.parsed_args.command == 'status':
                self.do_project_status(self.parsed_args.args)

        elif self.parsed_args.section in ['run', 'check']:
            self.do_run(self.parsed_args.args)

        elif self.parsed_args.section == 'config':
            self.do_config(self.parsed_args.args)

    def do_project_init(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 create=True)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError) as errmsg:
            print('Error:', errmsg)
            exit(1)

    def do_project_refresh(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 create=False, refresh=True)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError) as errmsg:
            print('Error:', errmsg)
            exit(1)

    def do_project_status(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            print('Error:', errmsg)
            exit(1)

        project.status()

    def do_run(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            print('Error:', errmsg)
            exit(1)

        runner = AnsiblePlaybookRunner(project, **vars(args))
        if args.eval:
            runner.eval()
            exit()
        else:
            runner.execute()

    def do_config(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass

        if args.env:
            self.config.show_env()
        else:
            self.config.show(format=args.format)
