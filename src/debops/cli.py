# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .exceptions import NoDefaultViewException
from .config import Configuration
from .subcommands import Subcommands
from .projectdir import ProjectDir
from .ansiblerunner import AnsibleRunner
from .ansibleplaybookrunner import AnsiblePlaybookRunner
from .envrunner import EnvRunner
import sys


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
            elif self.parsed_args.command == 'lock':
                self.do_project_lock(self.parsed_args.args)
            elif self.parsed_args.command == 'unlock':
                self.do_project_unlock(self.parsed_args.args)
            elif self.parsed_args.command == 'mkview':
                self.do_project_mkview(self.parsed_args.args)
            elif self.parsed_args.command == 'commit':
                self.do_project_commit(self.parsed_args.args)

        elif self.parsed_args.section == 'exec':
            self.do_exec(self.parsed_args.args)

        elif self.parsed_args.section in ['run', 'check']:
            self.do_run(self.parsed_args.args)

        elif self.parsed_args.section == 'env':
            self.do_env(self.parsed_args.args)

        elif self.parsed_args.section == 'config':
            if self.parsed_args.command == 'list':
                self.do_config_list(self.parsed_args.args)
            elif self.parsed_args.command == 'get':
                self.do_config_get(self.parsed_args.args)

    def do_project_init(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 create=True, **vars(args))
            project.create()
        except (IsADirectoryError, NotADirectoryError,
                PermissionError, ValueError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

    def do_project_refresh(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
            project.refresh()
        except (IsADirectoryError, NotADirectoryError,
                PermissionError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

    def do_project_lock(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 view=args.view)
            try:
                project.lock()
            except (NoDefaultViewException) as errmsg:
                print('Error:', errmsg)
                sys.exit(1)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError, ChildProcessError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

    def do_project_unlock(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 view=args.view)
            try:
                project.unlock()
            except (NoDefaultViewException) as errmsg:
                print('Error:', errmsg)
                sys.exit(1)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError, ChildProcessError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

    def do_project_mkview(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 **vars(args))
            project.mkview(view=args.new_view)
        except (IsADirectoryError, NotADirectoryError, ValueError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

    def do_project_commit(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
            project.commit(interactive=True)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

    def do_exec(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 view=args.view)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

        try:
            runner = AnsibleRunner(project, **vars(args))
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

        if args.eval:
            runner.eval()
            sys.exit(0)
        else:
            sys.exit(runner.execute())

    def do_run(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 view=args.view)
        except (IsADirectoryError, NotADirectoryError, ChildProcessError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

        try:
            runner = AnsiblePlaybookRunner(project, **vars(args))
        except (NoDefaultViewException, ValueError,
                FileNotFoundError, ChildProcessError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

        if args.eval:
            runner.eval()
            sys.exit(0)
        else:
            try:
                sys.exit(runner.execute())
            except ChildProcessError as errmsg:
                print('Error:', errmsg)
                sys.exit(1)

    def do_env(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 view=args.view)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

        try:
            runner = EnvRunner(project, **vars(args))
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print('Error:', errmsg)
            sys.exit(1)

        if args.command_args:
            sys.exit(runner.execute())
        else:
            sys.exit(runner.show_env(scope=args.scope))

    def do_config_list(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass

        self.config.config_list()

    def do_config_get(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass

        if args.key:
            for option_name in args.key:
                self.config.config_get(option_name, format=args.format,
                                       keys=args.keys)
        else:
            self.config.config_get('.', format=args.format, keys=args.keys)
