# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from . import print_error
from ..core.exceptions import (NoDefaultViewException, InventorySpecError,
                               OptionNotFoundError, ViewNotFoundError)
from ..core.config import Configuration
from .subcommands import Subcommands
from ..core.projectdir import ProjectDir
from ..core.projectvenv import ProjectVenv
from ..core.ansible.ansiblerunner import AnsibleRunner
from ..core.ansible.ansibleplaybookrunner import AnsiblePlaybookRunner
from ..core.envrunner import EnvRunner
from xdg.BaseDirectory import xdg_config_home
import logging
import getpass
import sys
import os

logger = logging.getLogger(__name__)


def _inspect_mode(args):
    """The inventory inspection mode selected on the command line.

    The '--graph', '--list' and '--host' options are mutually exclusive;
    this collapses them into the mode string the library methods take.
    """
    if args.graph:
        return 'graph'
    if args.list:
        return 'list'
    if args.host:
        return 'host'
    return None


class Interpreter(object):

    def __init__(self, args=None, config=None):
        # The shell's working directory, captured before anything runs:
        # the view resolution is anchored here
        self.cwd = os.getcwd()
        self.args = args
        # The configuration arrives from main(), which has already built
        # one for the logging setup; building a second one here would
        # load and validate every configuration file twice
        self.config = config if config is not None else Configuration()
        self.parsed_args = Subcommands(self.args)
        logger.debug('Command line interpreter initialized')
        logger.debug('Control user=' + getpass.getuser())

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
            elif self.parsed_args.command == 'venv':
                self.do_project_venv(self.parsed_args.args)

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
            elif self.parsed_args.command == 'set':
                self.do_config_set(self.parsed_args.args)
            elif self.parsed_args.command == 'check':
                self.do_config_check(self.parsed_args.args)

    def do_project_init(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 project_type=args.type, create=True,
                                 encrypt=args.encrypt, keys=args.keys)
            output = project.create(
                git_repo=args.git, venv=args.venv,
                requirements=args.requirements,
                default_view=args.default_view,
                spec_sources=args.spec_sources,
                allow_io=args.allow_io, dry_run=args.dry_run,
                force=args.force, inspect_mode=_inspect_mode(args),
                inspect_host=args.host)
            if args.venv and args.requirements:
                venv = ProjectVenv(project)
                venv.install()
        except (IsADirectoryError, NotADirectoryError,
                PermissionError, InventorySpecError, FileNotFoundError,
                ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)
        if output:
            print(output)

    def do_project_refresh(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 view=args.view)
            output = project.refresh(
                spec_sources=args.spec_sources,
                allow_io=args.allow_io, dry_run=args.dry_run,
                force=args.force, inspect_mode=_inspect_mode(args),
                inspect_host=args.host)
        except (IsADirectoryError, NotADirectoryError, ViewNotFoundError,
                PermissionError, InventorySpecError,
                ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)
        if output:
            print(output)

    def do_project_lock(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 view=args.view)
            try:
                project.lock()
            except (NoDefaultViewException) as errmsg:
                print_error(errmsg)
                sys.exit(1)
        except (IsADirectoryError, NotADirectoryError, ViewNotFoundError,
                PermissionError, ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_project_unlock(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 view=args.view)
            try:
                project.unlock()
            except (NoDefaultViewException) as errmsg:
                print_error(errmsg)
                sys.exit(1)
        except (IsADirectoryError, NotADirectoryError, ViewNotFoundError,
                PermissionError, ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_project_mkview(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, encrypt=args.encrypt,
                                 keys=args.keys)
            project.mkview(view=args.new_view)
        except (IsADirectoryError, NotADirectoryError,
                InventorySpecError, ChildProcessError,
                ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_project_commit(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd)
            project.commit(interactive=True)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_project_venv(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd)
            if args.action == 'enable':
                project.enable_venv(scope=args.scope)
                return
            venv = ProjectVenv(project)
            if args.action == 'install':
                venv.install(scope=args.scope)
            elif args.action == 'upgrade':
                venv.upgrade(scope=args.scope)
            elif args.action == 'recreate':
                venv.recreate(scope=args.scope)
            elif args.action == 'freeze':
                venv.freeze(scope=args.scope)
        except (IsADirectoryError, NotADirectoryError,
                PermissionError, FileNotFoundError,
                ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_exec(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        try:
            runner = AnsibleRunner(project, ansible_args=args.ansible_args,
                                   bell=args.bell)
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.eval:
            print(runner.eval())
            sys.exit(0)
        else:
            try:
                sys.exit(runner.execute())
            except ChildProcessError as errmsg:
                print_error(errmsg)
                sys.exit(1)

    def do_run(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 view=args.view)
        except (IsADirectoryError, NotADirectoryError, ViewNotFoundError,
                ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        try:
            runner = AnsiblePlaybookRunner(
                project, ansible_args=args.ansible_args, bell=args.bell,
                debug=args.debug)
        except (NoDefaultViewException, ValueError,
                FileNotFoundError, ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.eval:
            print(runner.eval())
            sys.exit(0)
        else:
            try:
                sys.exit(runner.execute())
            except (ChildProcessError, ValueError) as errmsg:
                print_error(errmsg)
                sys.exit(1)

    def do_env(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd,
                                 view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        try:
            runner = EnvRunner(project, command_args=args.command_args)
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.command_args:
            try:
                sys.exit(runner.execute())
            except ChildProcessError as errmsg:
                print_error(errmsg)
                sys.exit(1)
        else:
            for line in runner.show_env(scope=args.scope):
                print(line)
            sys.exit(0)

    def do_config_list(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass

        for line in self.config.config_list():
            print(line)

    def do_config_get(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass

        if args.key:
            for option_name in args.key:
                try:
                    output = self.config.config_get(
                        option_name, format=args.format, keys=args.keys,
                        root=args.root, show_origin=args.show_origin,
                        show_scope=args.show_scope)
                except OptionNotFoundError:
                    # An undefined option is reported as an empty JSON
                    # object and a non-zero exit code
                    if args.format == 'json':
                        print('{}')
                    sys.exit(1)
                except ValueError as errmsg:
                    print_error(errmsg)
                    sys.exit(1)
                if output is not None:
                    print(output)
        else:
            try:
                output = self.config.config_get(
                    '.', format=args.format, keys=args.keys,
                    root=args.root, show_origin=args.show_origin,
                    show_scope=args.show_scope)
            except ValueError as errmsg:
                print_error(errmsg)
                sys.exit(1)
            if output is not None:
                print(output)

    def do_config_set(self, args):
        directory = None
        if not args.user:
            try:
                project = ProjectDir(path=args.project_dir,
                                     config=self.config, cwd=self.cwd)
                directory = os.path.join(project.path, '.debops',
                                         'conf.d')
            except (IsADirectoryError, NotADirectoryError):
                # Outside of a project directory, the options are set
                # in the user configuration
                directory = None
        if directory is None:
            directory = os.path.join(xdg_config_home, 'debops', 'conf.d')

        try:
            option_file = self.config.option_file(directory)
            self.config.write_option(option_file, args.key,
                                     value=args.value,
                                     delete=args.delete)
        except (ValueError, OSError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.delete:
            logger.notice("Removed '%s' from %s", args.key, option_file,
                          extra={'allow': ['stderr', 'syslog']})
        else:
            logger.notice("Set '%s' to '%s' in %s", args.key, args.value,
                          option_file,
                          extra={'allow': ['stderr', 'syslog']})

    def do_config_check(self, args):
        try:
            ProjectDir(path=args.project_dir, config=self.config,
                       cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError):
            # The configuration is checked without the project's files
            # when there is no project directory to work on
            pass

        failures = [violation for violation in self.config._violations
                    if violation['dropped']]
        if args.strict:
            failures += [violation for violation in self.config._violations
                         if not violation['dropped']]
        if failures:
            sys.exit(1)
        logger.notice('The DebOps configuration is valid',
                      extra={'allow': ['stderr', 'syslog']})
