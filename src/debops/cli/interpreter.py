# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from . import print_error
from ..core.exceptions import (NoDefaultViewException, InventorySpecError,
                               OptionNotFoundError, OptionRefused,
                               ViewNotFoundError)
from ..core.config import Configuration
from .subcommands import Subcommands
from ..core.projectdir import ProjectDir
from ..core.projectvenv import ProjectVenv
from ..core.ansible.ansiblerunner import AnsibleRunner
from ..core.ansible.ansibleplaybookrunner import AnsiblePlaybookRunner
from ..core.envrunner import EnvRunner
from ..core.tofu.inventory import render_view_inventory
from ..core.tofu.runner import TofuOperationFailed, TofuRunner
from ..core.tofu.plans import (PLAN_FILE_PREFIX, plan_rows,
                               resolve_plan_file)
from ..core.tofu import cache
from ..core.tofu.view import create_view, rekey_view
from ..core.tofu.providers import resolve_providers
from ..core.tofu.modules import resolve_modules
from ..core.tofu.binary import reconcile_binaries
from ..core.tofu.registry import view_drop_in_path, view_tofu_root
from ..core.tofu.view import reconcile_view
from ..core import ssh
from ..core.utils import remove_file, unexpanduser
from xdg.BaseDirectory import xdg_config_home
import logging
import getpass
import shlex
import sys
import time
import os

logger = logging.getLogger(__name__)


def human_age(then):
    """The age of a modification time, human-sized: the seconds,
    the minutes, the hours or the days."""
    seconds = max(int(time.time()) - int(then), 0)
    if seconds < 60:
        return '{} second{} ago'.format(
            seconds, 's' if seconds != 1 else '')
    for span, unit in ((86400, 'day'), (3600, 'hour'),
                       (60, 'minute')):
        if seconds >= span:
            count = seconds // span
            return '{} {}{} ago'.format(
                count, unit, 's' if count != 1 else '')
    return '0 seconds ago'


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

        elif self.parsed_args.section == 'tofu':
            self.do_tofu(self.parsed_args.args)

        elif self.parsed_args.section == 'ssh':
            if self.parsed_args.command == 'rescan':
                self.do_ssh_rescan(self.parsed_args.args)
            elif self.parsed_args.command == 'config':
                self.do_ssh_config(self.parsed_args.args)
            else:
                self.do_ssh_connect(self.parsed_args.args)

        elif self.parsed_args.section == 'scp':
            self.do_scp(self.parsed_args.args)

        elif self.parsed_args.section == 'sftp':
            self.do_sftp(self.parsed_args.args)

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
                inspect_host=args.host, ssh=args.ssh)
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
            project.mkview(view=args.new_view, ssh=args.ssh)
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
                PermissionError, ViewNotFoundError) as errmsg:
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
                ChildProcessError, ValueError,
                ViewNotFoundError) as errmsg:
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
                                   bell=args.bell, accept=args.accept)
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
                debug=args.debug, accept=args.accept)
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

    def do_tofu(self, args):
        if not args.tofu_args and not args.help:
            print_error('At least one operand is required: the OpenTofu '
                        'operation to run; see \'debops tofu --help\'')
            sys.exit(2)

        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        # The '--help' option composes the help screen: the OpenTofu
        # help -- its usage lines name the wrapper -- followed by the
        # options of the wrapper
        if args.help:
            runner = TofuRunner(project, ['help'], no_color=args.no_color,
                                workspace=args.workspace)
            runner.execute()
            sys.stdout.write(args.help_body)
            sys.exit(0)

        # The 'mkview' operation is a DebOps-level command: it creates
        # the view tree, its encrypted store and the environment key
        # file, with the store cycled around the key material
        if args.tofu_args[0] == 'mkview':
            self._do_tofu_mkview(args, project)
            return

        # The 'update' operation is a DebOps-level command: it
        # reconciles the files DebOps owns in the view and runs 'tofu
        # init' through the wrapper
        if args.tofu_args[0] == 'update':
            self._do_tofu_update(args, project)
            return

        # The 'install' operation is a DebOps-level command: it
        # reconciles the OpenTofu binaries which the project's views
        # pin with the installed ones
        if args.tofu_args[0] == 'install':
            self._do_tofu_install(args, project)
            return

        # The 'cache' operation is a DebOps-level command: it lists
        # and cleans the OpenTofu cache of the project. It runs no
        # 'tofu' command, so no hooks fire around it.
        if args.tofu_args[0] == 'cache':
            self._do_tofu_cache(args, project)
            return

        # The 'inventory' operation is a DebOps-level command: it
        # collects the inventory outputs of the view through the
        # wrapper and renders them into the Ansible view's inventory
        if args.tofu_args[0] == 'inventory':
            self._do_tofu_inventory(args, project)
            return

        # The 'plans' operation is a DebOps-level command: it lists
        # the plan files the wrapper saves for the view and shows,
        # applies or deletes one of them by its id
        if args.tofu_args[0] == 'plans':
            self._do_tofu_plans(args, project)
            return

        # The 'rekey' operation is a DebOps-level command: it
        # rotates the state passphrase of the view through the
        # fallback key provider of the OpenTofu encryption
        if args.tofu_args[0] == 'rekey':
            self._do_tofu_rekey(args, project)
            return

        try:
            runner = TofuRunner(project, args.tofu_args, bell=args.bell,
                                no_color=args.no_color,
                                workspace=args.workspace,
                                allow_missing_state=(
                                    args.allow_missing_state))
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        try:
            if args.eval:
                self._note_pending_view_creation(project)
                print(runner.eval())
                sys.exit(0)

            sys.exit(runner.execute())
        except (ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _note_pending_view_creation(self, project):
        """Note on stderr when '--eval' would run before the view tree
        is created: the printed command is the one which runs after the
        template application."""
        if os.path.exists(os.path.join(view_tofu_root(project,
                                                      project.view),
                                       'main.tf')):
            return
        logger.warning(
            "The view tree of the view '{}' does not exist yet; the "
            'printed command runs after the template is applied to '
            'it.'.format(project.view),
            extra={'allow': ['stderr', 'syslog']})

    def _do_tofu_mkview(self, args, project):
        """Run the 'debops tofu mkview' operation: create the view
        tree, its encrypted store and the environment key file, with
        the store cycled around the key material."""
        try:
            create_view(project, args.new_view,
                        providers=resolve_providers(project,
                                                    args.provider),
                        modules=resolve_modules(project,
                                                args.module),
                        encrypt=args.encrypt, keys=args.keys)
        except (NoDefaultViewException, ValueError,
                ChildProcessError, FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _do_tofu_update(self, args, project):
        """Run the 'debops tofu update' operation: reconcile the files
        DebOps owns in the view, then run 'tofu init' through the
        wrapper."""
        # The '--eval' option implies the dry-run behavior: the
        # reconcile shows its changes and the printed command is the
        # one which runs after them
        try:
            changes = reconcile_view(project, project.view,
                                     force=args.force,
                                     dry_run=(args.dry_run or args.eval))
        except ValueError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        self._render_tofu_changes(changes, diff=args.diff,
                                  dry_run=(args.dry_run or args.eval),
                                  color=(sys.stdout.isatty()
                                         and not args.no_color))
        if args.dry_run:
            return

        try:
            runner = TofuRunner(project, ['init'], bell=args.bell,
                                no_color=args.no_color,
                                workspace=args.workspace)
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.eval:
            self._note_pending_view_creation(project)
            print(runner.eval())
            sys.exit(0)

        try:
            sys.exit(runner.execute())
        except (ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _do_tofu_install(self, args, project):
        """Run the 'debops tofu install' operation: reconcile the
        OpenTofu binaries which the project's views pin with the
        installed ones."""
        try:
            installed = reconcile_binaries(project, force=args.force)
        except ValueError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        if not installed:
            logger.notice(
                'The pinned binaries of the views of the project {!r} '
                'are installed'.format(project.name),
                extra={'allow': ['stderr', 'syslog']})

    def _do_tofu_cache(self, args, project):
        """Run the 'debops tofu cache' operation: list the cache
        entries of the project, or remove the ones of the selected
        scope and print the removed paths."""
        if args.reset:
            removed = [cache.reset_cache()]
        elif args.clean:
            if args.project:
                removed = cache.clean_project(project)
            elif args.plugins:
                removed = [cache.clean_plugins()]
            else:
                removed = [cache.clean_data_dir(project)]
        else:
            removed = None
        if removed is not None:
            for path in removed:
                if path:
                    print(path)
            return
        rows = [(unexpanduser(path), size, note)
                for path, size, note in cache.cache_rows(project)]
        width = max(len(path) for path, _, _ in rows) if rows else 0
        for path, size, note in rows:
            print('{}  {:>7}  {}'.format(path.ljust(width),
                                         cache.human_size(size),
                                         note))

    def _do_tofu_inventory(self, args, project):
        """Run the 'debops tofu inventory' operation through the
        core machinery and print the changes it applies."""
        try:
            changes = render_view_inventory(
                project, project.view, force=args.force,
                dry_run=args.dry_run,
                allow_missing_state=args.allow_missing_state,
                bell=args.bell)
        except TofuOperationFailed as errmsg:
            print_error(errmsg)
            sys.exit(errmsg.return_code)
        except (NoDefaultViewException, ValueError, FileNotFoundError,
                ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        self._render_tofu_changes(
            changes, diff=args.diff, dry_run=args.dry_run,
            color=(sys.stdout.isatty() and not args.no_color))

    def _do_tofu_rekey(self, args, project):
        """Run the 'debops tofu rekey' operation: rotate the state
        passphrase of the view through the fallback key provider of
        the OpenTofu encryption."""
        try:
            rekey_view(project, project.view,
                       workspace=args.workspace)
        except (NoDefaultViewException, ValueError, FileNotFoundError,
                ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _do_tofu_plans(self, args, project):
        """Run the 'debops tofu plans' operation: list the plan files
        the wrapper saves for the view, or show, apply or delete one
        of them by its id.

        The listing reads the view's plans directory -- the names
        and the metadata are plaintext-side, no store cycle. The
        show and the apply run through the runner machinery: the
        plan files are OpenTofu-encrypted and the passphrase comes
        from the store's environment file, which the cycle unlocks.
        The delete is a file removal with the id resolved; it
        reports the removed path, the reconcile convention."""
        view_root = view_tofu_root(project, project.view)
        try:
            if args.verb is None:
                rows = plan_rows(view_root)
                for sequence, name, size, mtime in rows:
                    stamp = name[len(PLAN_FILE_PREFIX):-len('.tfplan')]
                    stamp = stamp.partition('-')[2]
                    print('{:>4}  {}  {:>7}  {}'.format(
                        sequence, stamp, cache.human_size(size),
                        human_age(mtime)))
                return
            plan_file = resolve_plan_file(view_root, args.plan_id)
        except ValueError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        if args.verb == 'delete':
            remove_file(os.path.join(view_root, plan_file),
                        project=view_root)
            print(plan_file)
            return
        try:
            runner = TofuRunner(
                project,
                [args.verb] + (['-json'] if args.json else [])
                + [plan_file],
                bell=args.bell, no_color=args.no_color,
                workspace=args.workspace,
                allow_missing_state=args.allow_missing_state)
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)
        try:
            sys.exit(runner.execute())
        except (ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _render_tofu_changes(self, changes, diff=False, dry_run=False,
                             color=False):
        """Print the changes which the operation applies: the paths
        and the actions, or the unified diffs with '--diff'. A change
        without a diff -- the sensitive files of the inventory render
        -- prints its action line in both modes: the values must not
        reach the terminal."""
        for change in changes:
            if diff and change.get('diff') is not None:
                self._print_colored_diff(change['diff'], color=color)
                continue
            action = change['action']
            if dry_run:
                action = 'Would ' + action
            else:
                action = action.capitalize()
            print('{} {}'.format(action, change['path']))

    @staticmethod
    def _print_colored_diff(diff_text, color=False):
        """Print a unified diff, coloring the '+' and '-' lines when
        the output is a terminal."""
        if not color:
            print(diff_text, end='')
            return
        for line in diff_text.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                print('\033[32m' + line + '\033[0m')
            elif line.startswith('-') and not line.startswith('---'):
                print('\033[31m' + line + '\033[0m')
            else:
                print(line)

    def do_scp(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if not args.sources or args.destination is None:
            print_error('At least two operands are required: one or '
                        'more sources and a destination; see '
                        '\'debops scp --help\'')
            sys.exit(2)

        try:
            command = ssh.build_scp_command(
                project, args.sources, args.destination,
                identity=args.identity, accept=args.accept,
                scp_args=args.scp_extra_args)
        except (ValueError, ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.eval:
            print(shlex.join(command))
            sys.exit(0)

        logger.debug('Copying "' + '", "'.join(args.sources) + '" to "'
                     + args.destination + '"',
                     extra={'allow': 'stderr'})
        try:
            os.execvp(command[0], command)
        except (FileNotFoundError, PermissionError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_sftp(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.handoff is not None:
            try:
                command = ssh.build_handoff_command(
                    project, 'sftp', args.handoff,
                    identity=args.identity, accept=args.accept,
                    passthrough=args.sftp_head_args)
            except (ValueError, ChildProcessError) as errmsg:
                print_error(errmsg)
                sys.exit(1)
        else:
            try:
                command = ssh.build_sftp_command(
                    project, args.destination,
                    identity=args.identity, accept=args.accept,
                    sftp_args=args.sftp_tail_args,
                    sftp_head_args=args.sftp_head_args)
            except (ValueError, ChildProcessError) as errmsg:
                print_error(errmsg)
                sys.exit(1)

        if args.eval:
            print(shlex.join(command))
            sys.exit(0)

        if args.handoff is None:
            logger.debug('Starting the sftp session with "'
                         + args.destination + '"',
                         extra={'allow': 'stderr'})
        try:
            os.execvp(command[0], command)
        except (FileNotFoundError, PermissionError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_ssh_connect(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.handoff is not None:
            try:
                command = ssh.build_handoff_command(
                    project, 'ssh', args.handoff,
                    identity=args.identity, accept=args.accept,
                    passthrough=args.ssh_extra_args,
                    user=args.user, port=args.port)
            except (ValueError, ChildProcessError) as errmsg:
                print_error(errmsg)
                sys.exit(1)
        else:
            user, host, port = ssh.split_destination(args.host)
            user = user or args.user
            port = port or args.port

            try:
                parameters = ssh.resolve_destination(project, host)
            except (ValueError, ChildProcessError) as errmsg:
                print_error(errmsg)
                sys.exit(1)

            try:
                command = ssh.build_ssh_command(
                    project, host, parameters,
                    user=user, port=port, identity=args.identity,
                    accept=args.accept, ssh_args=args.ssh_args,
                    options=args.ssh_extra_args)
            except ValueError as errmsg:
                print_error(errmsg)
                sys.exit(1)

        if args.eval:
            print(shlex.join(command))
            sys.exit(0)

        if args.handoff is None:
            logger.debug('Connecting to the host "' + host + '"',
                         extra={'allow': 'stderr'})
        try:
            os.execvp(command[0], command)
        except (FileNotFoundError, PermissionError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_ssh_rescan(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        # The defaults of the DNS mode and the confirmation come from
        # the configuration; the options of the command line override
        # them
        rescan_config = project.config.raw.get('ssh', {}).get(
            'rescan', {})
        dns_mode = args.dns_mode or rescan_config.get('resolver_mode',
                                                      'dns')
        if dns_mode not in ('dns', 'no-dns', 'dns-verify'):
            print_error('The ssh.rescan.resolver_mode option of the '
                        'configuration carries an unknown DNS '
                        'verification mode: ' + str(dns_mode))
            sys.exit(1)
        confirm = args.confirm
        if confirm is None:
            confirm = rescan_config.get('confirm', False)

        phases = ('remove', 'scan')
        if args.remove and not args.scan:
            phases = ('remove',)
        elif args.scan and not args.remove:
            phases = ('scan',)

        try:
            hosts, unmatched, variables = ssh.resolve_patterns(
                project, args.hosts)
        except (ValueError, ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)
        for pattern in unmatched:
            logger.notice('The pattern "' + pattern + '" matched no '
                          'hosts', extra={'allow': 'stderr'})
        if not hosts:
            print_error('No hosts matched the given patterns: '
                        + ' '.join(args.hosts))
            sys.exit(1)

        # A scan of a few hosts is fast enough for interactive
        # operation; the estimate is only shown when the worst case
        # takes three minutes or longer.
        # A reachable host scans in about two seconds including the
        # startup of the command; hosts which do not respond wait for
        # the full key scan timeout, so the real time can be longer.
        estimate = len(hosts) * 2
        if estimate >= 180:
            if estimate >= 3600:
                estimate_text = '{:.1f} hours'.format(estimate / 3600.0)
            else:
                estimate_text = '{} minutes'.format(estimate // 60)
            print('Scanning {} hosts, estimated time: {} (hosts which '
                  'do not respond take longer).'.format(len(hosts),
                                                        estimate_text))

        if args.eval:
            if args.known_hosts_file:
                store = args.known_hosts_file
            else:
                try:
                    store, _ = ssh.require_store(project)
                except ValueError as errmsg:
                    print_error(errmsg)
                    sys.exit(1)
            for host in hosts:
                # The variables of the pattern expansion resolve the
                # host without a second invocation; a host whose
                # resolution fails is reported like a failed scan and
                # the remaining hosts continue
                try:
                    parameters = None if host not in variables else \
                        ssh.resolve_host(project, host,
                                         variables=variables[host])
                except (ValueError, ChildProcessError) as errmsg:
                    print_error('Cannot refresh the known_hosts entries '
                                'of the host "' + host + '": '
                                + str(errmsg))
                    continue
                actions, _ = ssh.rescan_actions(
                    project, host, store, phases, args.timeout,
                    parameters=parameters)
                for phase, argv in actions:
                    print(shlex.join(argv))
            sys.exit(0)

        def confirm_host(host, offered):
            """Show the scanned fingerprints and ask for the host."""
            print('The SSH host keys of "' + host + '" were scanned:')
            for fingerprint, key_type in offered:
                print('  ' + fingerprint + '  ' + key_type)
            try:
                answer = input('  Accept these keys and store them? '
                               '[y=yes, Enter=no, Ctrl-C=abort] ')
            except EOFError:
                # The input ended; without an answer the keys are not
                # stored
                print('  The input ended; the keys were not stored')
                return False
            # Only an explicit affirmative answer stores the keys: a
            # bare Enter, a typo or an unknown word declines, the way
            # a trust prompt should behave -- the keys of a host are
            # worth their two characters
            return answer.strip().lower() in ('y', 'yes')

        try:
            results = ssh.rescan_hosts(
                project, hosts, store=args.known_hosts_file,
                phases=phases, timeout=args.timeout,
                dns_mode=dns_mode, variables=variables,
                confirm=confirm_host if confirm else None)
        except (ValueError, OSError) as errmsg:
            print_error(errmsg)
            sys.exit(1)
        except KeyboardInterrupt:
            print('Rescan aborted; the hosts processed so far keep '
                  'their state')
            sys.exit(130)

        failed = [(host, message) for host, ok, message in results
                  if not ok]
        for host, message in failed:
            print_error('Cannot refresh the known_hosts entries of the '
                        'host "' + host + '": ' + message)
        sys.exit(1 if failed else 0)

    def do_ssh_config(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.view)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if args.write:
            config_path = os.path.expanduser('~/.ssh/config')
            try:
                changed = ssh.write_config_snippet(project, config_path)
            except (OSError, ValueError) as errmsg:
                print_error(errmsg)
                sys.exit(1)
            if changed:
                logger.notice('Wrote the managed debops ssh block into '
                              + config_path,
                              extra={'allow': ['stderr', 'syslog']})
            else:
                logger.notice('The managed debops ssh block in '
                              + config_path + ' is up to date',
                              extra={'allow': ['stderr', 'syslog']})
            sys.exit(0)

        try:
            for line in ssh.render_config_snippet(project):
                print(line)
        except ValueError as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_config_list(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass
        except ViewNotFoundError as errmsg:
            print_error(errmsg)
            sys.exit(1)

        for line in self.config.config_list():
            print(line)

    def do_config_get(self, args):
        try:
            project = ProjectDir(path=args.project_dir, config=self.config, cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError) as errmsg:
            # This is not a project directory, so no project-dependent
            # configuration is included
            pass
        except ViewNotFoundError as errmsg:
            print_error(errmsg)
            sys.exit(1)

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
            except ViewNotFoundError as errmsg:
                print_error(errmsg)
                sys.exit(1)
        if directory is None:
            directory = os.path.join(xdg_config_home, 'debops', 'conf.d')

        try:
            option_file = self.config.option_file(directory)
            action = self.config.write_option(
                option_file, args.key, values=args.values,
                delete=args.delete, option_type=args.type)
        except OptionRefused:
            # The refusal is reported through the log
            sys.exit(1)
        except (ValueError, OSError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if action == 'set':
            logger.info("Set '%s' to '%s' in %s", args.key,
                        ' '.join(args.values), option_file,
                        extra={'allow': ['stderr', 'syslog']})
        elif action == 'create':
            logger.info("Created the '%s' option in %s", args.key,
                        option_file,
                        extra={'allow': ['stderr', 'syslog']})
        elif action == 'append':
            logger.info("Added the values to the '%s' list in %s",
                        args.key, option_file,
                        extra={'allow': ['stderr', 'syslog']})

    def do_config_check(self, args):
        try:
            ProjectDir(path=args.project_dir, config=self.config,
                       cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError):
            # The configuration is checked without the project's files
            # when there is no project directory to work on
            pass
        except ViewNotFoundError as errmsg:
            print_error(errmsg)
            sys.exit(1)

        failures = [violation for violation in self.config._violations
                    if violation['dropped']]
        if args.strict:
            failures += [violation for violation in self.config._violations
                         if not violation['dropped']]
        if failures:
            sys.exit(1)
        logger.notice('The DebOps configuration is valid',
                      extra={'allow': ['stderr', 'syslog']})
