# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from . import print_error, print_notice
from ..core.exceptions import (NoDefaultViewException, InventorySpecError,
                               OptionNotFoundError, OptionRefused,
                               ViewNotFoundError)
from ..core.config import Configuration, shadowing_file
from .subcommands import Subcommands
from ..core.projectdir import ProjectDir
from ..core.projectvenv import ProjectVenv
from ..core.ansible.ansiblerunner import AnsibleRunner, parse_list_hosts
from ..core.ansible.ansibleplaybookrunner import AnsiblePlaybookRunner
from ..core.envrunner import EnvRunner
from ..core.tofu.inventory import render_view_inventory
from ..core.tofu import plans as plans_module
from ..core.tofu.plans import plan_rows, resolve_plan_file
from ..core.tofu import cache
from ..core.tofu.rekey import rekey_view
from ..core.tofu.runner import TofuOperationFailed, TofuRunner
from ..core.tofu.providers import resolve_providers
from ..core.tofu.modules import resolve_modules
from ..core.tofu.binary import reconcile_binaries
from ..core.tofu.registry import view_drop_in_path, view_tofu_root
from ..core.tofu.view import create_view, reconcile_view
from ..core import checklists, ssh
from ..core.utils import (path_inside_project, remove_file,
                          unexpanduser, write_file)
from git import GitCommandError
from xdg.BaseDirectory import xdg_config_home
import json
import logging
import getpass
import re
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
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


def _tree_glyphs(encoding):
    """The tree connectors for the terminal encoding.

    Unicode box-drawing when the output is UTF-8; the ASCII fallback
    keeps the tree readable over legacy ssh locales.
    """
    if 'utf' in encoding.lower():
        return {'branch': '├── ', 'leaf': '└── ', 'column': '│',
                'pass': '│   ', 'indent': '    '}
    return {'branch': '|-- ', 'leaf': '`-- ', 'column': '|',
            'pass': '|   ', 'indent': '    '}


def _shorten_path(path, start=8, end=8):
    """The head and tail of a long path with the middle elided.

    Paths longer than the eight-character head, the ellipsis and the
    eight-character tail collapse to exactly that form; shorter paths
    pass through unchanged. For the compact roster, where the full
    path remains discoverable through `list -v`.
    """
    if len(path) <= start + 3 + end:
        return path
    return path[:start] + '...' + path[-end:]


def _columns(rows):
    """Pad every cell of a table to its column's widest entry.

    Returns the rows as lists of padded cells; the caller joins them
    with the separator of its choosing and strips the trailing
    padding from the last column.
    """
    widths = [max(len(row[column]) for row in rows)
              for column in range(len(rows[0]))]
    return [[cell.ljust(widths[column])
             for column, cell in enumerate(row)] for row in rows]


def _copy_tree_lines(copies, progress, glyphs, checklist=None):
    """Render open copies as a component tree, one line per node.

    Copy ids are paths: `web1/alpha` nests as `web1` over `alpha`, so
    a fleet of copies groups by host. A node whose id is itself a
    copy carries its progress above its children.

    Copy ids that nest under the checklist name display relative to
    it: for the checklist `flow`, the copy `flow/alpha` shows as
    `alpha` directly under the root. The strip is skipped when
    another copy already occupies the stripped id -- two copies on
    one display node would silently lose a progress value.
    """
    ids = {copy.copy_id for copy in copies}
    prefix = checklist + '/' if checklist else ''
    display = []
    for copy in copies:
        copy_id = copy.copy_id
        if prefix and copy_id.startswith(prefix):
            stripped = copy_id[len(prefix):]
            if stripped and stripped not in ids:
                copy_id = stripped
        display.append((copy_id, copy))
    root = {}
    for copy_id, copy in display:
        node = root
        for part in (part for part in copy_id.split('/') if part):
            node = node.setdefault(part, {})
        node[''] = copy
    lines = []

    def walk(node, prefix):
        keys = sorted(key for key in node if key != '')
        for index, key in enumerate(keys):
            last = index == len(keys) - 1
            connector = glyphs['leaf'] if last else glyphs['branch']
            line = prefix + connector + key
            sub = node[key]
            if '' in sub:
                line += ' ({})'.format(progress[sub[''].copy_id])
            lines.append(line)
            walk(sub, prefix + (glyphs['indent'] if last
                                else glyphs['pass']))

    walk(root, '')
    return lines


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

        elif self.parsed_args.section == 'checklist':
            if self.parsed_args.command == 'list':
                self.do_checklist_list(self.parsed_args.args)
            elif self.parsed_args.command == 'open':
                self.do_checklist_open(self.parsed_args.args)
            elif self.parsed_args.command == 'edit':
                self.do_checklist_edit(self.parsed_args.args)
            elif self.parsed_args.command == 'commit':
                self.do_checklist_commit(self.parsed_args.args)
            elif self.parsed_args.command == 'close':
                self.do_checklist_close(self.parsed_args.args)

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
        if args.tofu:
            self._init_tofu_view(args)
        if args.pre_commit:
            self._install_pre_commit(args)

    def _init_tofu_view(self, args):
        """Create the OpenTofu view of the default view after the
        project initialization.

        The '--encrypt' decision of the initialization carries over:
        'git-crypt' joins the repository-wide store, 'encfs' mounts
        the view's own volume keyed by the '--keys' recipients, and
        without the option the view's store stays plain -- the choice
        belongs to the operator at init; the refusals belong to the
        existing projects and 'debops tofu mkview'."""
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd, view=args.default_view)
            create_view(project, args.default_view,
                        providers=resolve_providers(project),
                        modules=resolve_modules(project),
                        encrypt=args.encrypt or 'plain',
                        keys=args.keys)
        except (NoDefaultViewException, ValueError, ChildProcessError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _install_pre_commit(self, args):
        """Install the pre-commit hook of the fresh project.

        The configuration file ships with the project; the hook
        engages after 'pre-commit install'. The tool is optional at
        initialization: a missing binary, a missing git repository
        and a failed install notice and skip -- the initialization
        does not fail over the optional development tool."""
        if not args.git:
            logger.notice(
                "The '--no-git' option left the project without a git "
                'repository: run \'pre-commit install\' after '
                "'git init'.",
                extra={'allow': ['stderr', 'syslog']})
            return
        try:
            result = subprocess.run(['pre-commit', 'install'],
                                    cwd=args.project_dir,
                                    capture_output=True, text=True)
        except FileNotFoundError:
            logger.notice(
                "The 'pre-commit' tool is not on the PATH: install it "
                "and run 'pre-commit install' in the project to engage "
                'the hook.',
                extra={'allow': ['stderr', 'syslog']})
            return
        if result.returncode != 0:
            logger.notice(
                'The pre-commit hook install failed: {}'.format(
                    (result.stderr or result.stdout).strip()),
                extra={'allow': ['stderr', 'syslog']})
            return
        if result.stdout.strip():
            print(result.stdout.strip())
        logger.notice(
            'The pre-commit hook is installed.',
            extra={'allow': ['stderr', 'syslog']})

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

    def _project(self, args):
        """The project directory of a checklist command, or exit.

        The checklist commands that work on copies require a DebOps
        project directory: the vault records and the git commits land
        in it, and the state directory is namespaced by its path.
        """
        try:
            return ProjectDir(path=args.project_dir, config=self.config,
                              cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError,
                ViewNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def do_checklist_list(self, args):
        try:
            selection = checklists.compile_selection(args.glob)
        except checklists.ChecklistError as errmsg:
            print_error(errmsg)
            sys.exit(1)

        project = None
        try:
            project = ProjectDir(path=args.project_dir, config=self.config,
                                 cwd=self.cwd)
        except (IsADirectoryError, NotADirectoryError):
            # The list works outside a project directory; the project
            # layer of the discovery is simply omitted then
            pass
        except ViewNotFoundError as errmsg:
            print_error(errmsg)
            sys.exit(1)

        # The state key follows the resolved project root, so a
        # subdirectory invocation sees the same copies.
        state_dir = checklists.checklist_state_dir(
            project.path if project is not None else args.project_dir)
        open_copies = checklists.find_open_copies(state_dir)
        glyphs = _tree_glyphs(sys.stdout.encoding or '')
        layers = checklists.checklist_layers(
            project.path if project is not None else None)
        filters = self._checklist_filters()
        stale_ids = {copy.copy_id for copy in checklists.find_stale_copies(
            open_copies, layers, filters=filters)}

        if args.active:
            rows = []
            records = []
            for copy in open_copies:
                if not checklists.name_selected(
                        copy.checklist, selection):
                    continue
                try:
                    parsed = checklists.parse_checklist(
                        self._read_copy_text(copy))
                except checklists.ChecklistError:
                    parsed = None
                implicit = copy.implicit
                if args.format == 'json':
                    records.append({
                        'copy_id': copy.copy_id, 'implicit': implicit,
                        'checklist': copy.checklist,
                        'path': str(copy.path), 'origin': copy.origin,
                        'opened': copy.opened.astimezone().isoformat(),
                        'counts': parsed.counts if parsed else None})
                    continue
                row = [copy.checklist if implicit else copy.copy_id,
                       '' if implicit else _shorten_path(copy.checklist),
                       '({})'.format(copy.opened.date().isoformat()),
                       parsed.progress if parsed else 'unreadable']
                if args.verbose >= 2:
                    row.append('[{}]'.format(copy.origin))
                rows.append(row)
            if args.format == 'json':
                print(json.dumps(records, indent=2))
                return
            if rows:
                for row in _columns(rows):
                    print('    '.join(row).rstrip())
            return

        layers = checklists.checklist_layers(
            project.path if project is not None else None)
        try:
            entries = checklists.list_checklists(layers, filters=filters)
        except checklists.ChecklistError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        entries = [entry for entry in entries
                   if checklists.name_selected(entry[0], selection)]

        if args.format == 'json':
            records = []
            for name, path, origin in entries:
                try:
                    parsed = checklists.parse_checklist(
                        path.read_text(encoding='utf-8'))
                except (OSError, UnicodeDecodeError):
                    continue
                copies_json = []
                for copy in open_copies:
                    if copy.checklist != name:
                        continue
                    try:
                        copy_parsed = checklists.parse_checklist(
                            self._read_copy_text(copy))
                        counts = copy_parsed.counts
                    except checklists.ChecklistError:
                        counts = None
                    copies_json.append({
                        'copy_id': copy.copy_id,
                        'implicit': copy.implicit,
                        'opened': copy.opened.astimezone().isoformat(),
                        'counts': counts,
                        'stale': copy.copy_id in stale_ids})
                records.append({
                    'checklist': name, 'path': str(path),
                    'origin': origin, 'title': parsed.title,
                    'copies': copies_json})
            print(json.dumps(records, indent=2))
            return

        if args.verbose >= 1:
            rows = []
            blocks = []
            for name, path, origin in entries:
                try:
                    parsed = checklists.parse_checklist(
                        path.read_text(encoding='utf-8'))
                except (OSError, UnicodeDecodeError):
                    # An unreadable or undecodable document is skipped;
                    # a broken file must not take the listing down
                    continue
                copies = [copy for copy in open_copies
                          if copy.checklist == name]
                progress = {}
                for copy in copies:
                    progress[copy.copy_id] = '{}{}'.format(
                        self._copy_progress(copy),
                        ' [stale]' if copy.copy_id in stale_ids else '')
                path_cell = name
                implicit = [copy for copy in copies if copy.implicit]
                if implicit:
                    path_cell += ' ({})'.format(progress[name])
                origin_cell = '[{}]'.format(origin) \
                    if args.verbose >= 2 else ''
                rows.append([path_cell, parsed.title or name,
                             origin_cell])
                named = [copy for copy in copies
                         if copy.copy_id != name]
                blocks.append(
                    _copy_tree_lines(named, progress, glyphs, name))
            if not rows:
                return
            for (path_cell, title, origin_cell), tree_lines in zip(
                    _columns(rows), blocks):
                tail = '{} {}'.format(title, origin_cell).rstrip()
                print('{} {} {}'.format(path_cell, glyphs['column'],
                                        tail))
                for tree_line in tree_lines:
                    print(tree_line)
            return

        for name, path, origin in entries:
            copies = [copy for copy in open_copies
                      if copy.checklist == name]
            progress = {}
            for copy in copies:
                progress[copy.copy_id] = '{}{}'.format(
                    self._copy_progress(copy),
                    ' [stale]' if copy.copy_id in stale_ids else '')
            path_cell = name
            implicit = [copy for copy in copies if copy.implicit]
            if implicit:
                path_cell += ' ({})'.format(progress[name])
            print(path_cell)
            named = [copy for copy in copies if copy.copy_id != name]
            for tree_line in _copy_tree_lines(named, progress, glyphs,
                                              name):
                print(tree_line)

    def do_checklist_open(self, args):
        project = self._project(args)
        if len(args.checklist) == 2:
            copy_id, name = args.checklist
        else:
            name = args.checklist[0]
            copy_id = checklists.strip_md(name)

        layers = checklists.checklist_layers(project.path)
        state_dir = checklists.checklist_state_dir(project.path)
        filters = self._checklist_filters()
        try:
            try:
                path, origin = checklists.find_checklist(
                    name, layers, filters=filters)
            except checklists.ChecklistNotFoundError:
                if len(args.checklist) != 1:
                    raise
                # A lone argument that is not a checklist name can
                # still be an open copy id; with --reset the copy
                # re-opens from the checklist its sidecar records
                copy_id, name, path, origin = checklists.resolve_heal(
                    name, state_dir, layers, filters, reset=args.reset,
                    dry_run=args.dry_run)
            parsed = checklists.parse_checklist(
                path.read_text(encoding='utf-8'))
            checklists.require_task_items(parsed, name)
            # An inventory pattern in the copy id expands to one copy
            # per matching host; the whole batch validates before the
            # first copy opens
            expanded = '[' in copy_id and ']' in copy_id
            copy_ids = self._expand_copy_id(project, copy_id)
            checklists.check_occupancy(state_dir, copy_ids, name,
                                       reset=args.reset, expanded=expanded)
            if args.dry_run:
                self._print_dry_run(copy_ids, name, origin, state_dir)
                return
            failures = []
            for expanded_id in copy_ids:
                try:
                    checklists.open_copy(path, name, origin, expanded_id,
                                         state_dir, reset=args.reset)
                except OSError as errmsg:
                    # The batch promise covers occupancy; an I/O
                    # failure mid-batch is reported with the ids that
                    # landed
                    failures.append((expanded_id, errmsg))
                    continue
                if expanded_id == checklists.strip_md(name):
                    print('Opened {} [{}]'.format(
                        checklists.strip_md(name), origin))
                else:
                    print('Opened {} as copy {} [{}]'.format(
                        checklists.strip_md(name), expanded_id, origin))
            for failed_id, errmsg in failures:
                print_error('The copy {} could not be opened: '
                            '{}'.format(failed_id, errmsg))
            if failures:
                sys.exit(1)
        except checklists.ChecklistError as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _expand_copy_id(self, project, copy_id):
        """The copy ids of one operand.

        The grammar lives in the library; this wrapper runs the
        ansible query the expansion needs -- the pattern through the
        project environment, the output parsed against its declared
        host count.
        """
        parsed_pattern = checklists.parse_copy_pattern(copy_id)
        if parsed_pattern is None:
            return [copy_id]
        pattern = parsed_pattern[1]
        runner = AnsibleRunner(project, ansible_args=[
            shlex.quote(pattern), '--list-hosts'])
        returncode, output = runner.capture()
        if returncode != 0:
            raise checklists.ChecklistError(
                'The inventory pattern [{}] could not be '
                'expanded'.format(pattern))
        try:
            hosts = parse_list_hosts(output)
        except ValueError as errmsg:
            raise checklists.ChecklistError(str(errmsg)) from None
        if not hosts:
            raise checklists.ChecklistError(
                'The inventory pattern [{}] matches no '
                'hosts'.format(pattern))
        return checklists.expand_copy_ids(copy_id, hosts)

    def _print_dry_run(self, copy_ids, name, origin, state_dir):
        """Print what ``open`` would do, without opening anything."""
        open_ids = {copy.copy_id for copy in
                    checklists.find_open_copies(state_dir)}
        print('Would open {} of {} [{}]:'.format(
            len(copy_ids), name, origin))
        for copy_id in copy_ids:
            marker = ' (already open)' if copy_id in open_ids else ''
            print('  {}{}'.format(copy_id, marker))

    def _copy_progress(self, copy):
        """The progress line of one working copy.

        An unreadable copy lists as unreadable: the copy stays
        visible, because the listing is how the user finds the copy
        that needs recovery.
        """
        try:
            return checklists.parse_checklist(
                self._read_copy_text(copy)).progress
        except checklists.ChecklistError:
            return 'unreadable'

    def _read_copy_text(self, copy):
        """The working copy text, with the unreadable case explained.

        A copy corrupted by a locale mismatch or a broken editor save
        must not crash the commands that are supposed to recover it.
        """
        try:
            return copy.path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as errmsg:
            raise checklists.ChecklistError(
                'The working copy {} cannot be read: {}; re-open it '
                'with --reset'.format(copy.copy_id, errmsg)) from None

    def do_checklist_edit(self, args):
        project = self._project(args)
        state_dir = checklists.checklist_state_dir(project.path)
        try:
            copy = checklists.resolve_single(args.copy, state_dir)
        except checklists.ChecklistError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        try:
            subprocess.run(self._editor_argv() + [str(copy.path)],
                           check=False)
        except OSError as errmsg:
            print_error('The editor could not be run: {}'.format(errmsg))
            sys.exit(1)
        parsed = checklists.parse_checklist(self._read_copy_text(copy))
        print('{}: {}'.format(copy.copy_id, parsed.progress))

    def _editor_argv(self):
        """The editor argv, with a notice when the environment lies.

        A ``$VISUAL``/``$EDITOR`` value that does not split into a
        command falls back to the Debian ``sensible-editor``
        indirection, announced on the notice channel.
        """
        try:
            return checklists.editor_argv()
        except checklists.ChecklistError as errmsg:
            print_notice('{}, using sensible-editor'.format(errmsg))
            return ['sensible-editor']

    def _checklist_filters(self):
        """The ``checklist.filters`` rule list, validated.

        The rules govern the discovery -- the listing, the open
        resolution and the heal. The state commands are untouched:
        the filter is a discovery policy, not a state destructor.
        """
        filters = self.config.get(['checklist', 'filters'])
        if filters == {}:
            return []
        if not isinstance(filters, list) or not all(
                isinstance(pattern, str) and pattern
                for pattern in filters):
            print_error('The checklist.filters value must be a list '
                        'of glob patterns')
            sys.exit(1)
        return filters

    def do_checklist_commit(self, args):
        if args.all and args.edit:
            print_error('The --edit option commits one copy at a time')
            sys.exit(1)
        project = self._project(args)
        state_dir = checklists.checklist_state_dir(project.path)
        vault_dir = self._checklist_vault_dir(project)
        if args.all:
            self._commit_all_copies(project, state_dir, vault_dir, args)
            return
        try:
            copy = checklists.resolve_single(args.copy, state_dir)
            self._commit_copy(project, state_dir, vault_dir, copy, args)
        except checklists.ChecklistError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        except GitCommandError as errmsg:
            print_error('The git commit of the vault record failed: '
                        '{}'.format(errmsg))
            sys.exit(1)

    def _checklist_vault_dir(self, project):
        """The resolved vault directory, refused when unconfigured."""
        vault_base = self.config.get(['checklist', 'commit_path'])
        if not isinstance(vault_base, str) or not vault_base:
            print_error('The checklist vault directory is not configured')
            sys.exit(1)
        vault_dir = Path(project.path) / vault_base
        if not path_inside_project(vault_dir, project.path):
            print_error('The vault directory resolves outside of the '
                        'project: ' + vault_base)
            sys.exit(1)
        return vault_dir

    def _commit_all_copies(self, project, state_dir, vault_dir, args):
        """Commit every open copy, optionally one checklist's copies.

        Per-copy independence: an invalid copy is skipped with its
        reason, a failed git commit is reported, the rest of the
        batch proceeds, and the exit code reports the partial
        failure. With ``--close``, each copy deactivates after its
        commit; the vault record exists, so the working copy's loss
        is recoverable and no --force is demanded.
        """
        copies = checklists.find_open_copies(state_dir)
        if args.copy:
            scope = checklists.strip_md(args.copy)
            copies = [copy for copy in copies
                      if copy.checklist == scope]
            if not copies:
                print_error('The checklist {} has no open '
                            'copies'.format(scope))
                sys.exit(1)
        elif not copies:
            print_error('No open copies')
            sys.exit(1)
        if not os.path.exists(os.path.join(project.path, '.git')):
            print_notice('The project directory is not a git repository, '
                         'the vault records are not committed')
        failed = []
        for copy in copies:
            try:
                self._commit_copy(project, state_dir, vault_dir, copy,
                                  args)
            except checklists.ChecklistError as errmsg:
                print_error(errmsg)
                failed.append(copy.copy_id)
            except GitCommandError as errmsg:
                print_error('The git commit of the vault record failed: '
                            '{}'.format(errmsg))
                failed.append(copy.copy_id)
        if failed:
            sys.exit(1)

    def _commit_copy(self, project, state_dir, vault_dir, copy, args,
                     git_notice=True):
        """One copy's commit flow; raises the typed errors."""
        parsed = checklists.parse_checklist(
            self._read_copy_text(copy))
        checklists.require_task_items(parsed, copy.checklist)
        if not copy.checklist:
            raise checklists.ChecklistError(
                'The copy {} does not record its checklist; '
                're-open it with --reset'.format(copy.copy_id))

        vault_path = checklists.vault_record_path(
            vault_dir, copy.checklist, copy.copy_id, copy.opened)
        copy_text = self._read_copy_text(copy)
        try:
            unchanged = vault_path.exists() and \
                vault_path.read_text(encoding='utf-8') == copy_text
        except (OSError, UnicodeDecodeError):
            # A hand-tampered record reads as changed; the re-commit
            # restores the copy's content
            unchanged = False
        if unchanged:
            print('No changes since the last commit')
        else:
            try:
                write_file(str(vault_path), copy_text,
                           overwrite=True, project=str(project.path),
                           mode=0o600)
            except ValueError as errmsg:
                # The vault confinement refused the write; the copy's
                # record path never resolves outside of the project
                raise checklists.ChecklistError(str(errmsg)) from None

        message = 'checklist: {}{} ({})'.format(
            '{} '.format(copy.copy_id)
            if not copy.implicit else '',
            copy.checklist, parsed.progress)
        if args.edit:
            message = self._edit_text(message) or message

        if git_notice and not os.path.exists(
                os.path.join(project.path, '.git')):
            print_notice('The project directory is not a git repository, '
                         'the vault record is not committed')
        project.commit(interactive=False, message=message,
                       paths=[str(vault_path)])
        if args.close:
            checklists.close_copy(copy.state_dir, copy.copy_id)
        if not unchanged:
            print('Committed {} to {}'.format(
                copy.checklist, os.path.relpath(vault_path, project.path)))

    def _edit_text(self, text):
        """Hand *text* to the editor and return the edited result."""
        descriptor, path = tempfile.mkstemp(suffix='.msg')
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            handle.write(text + '\n')
        try:
            subprocess.run(self._editor_argv() + [path], check=False)
            with open(path, encoding='utf-8') as handle:
                return handle.read().strip()
        finally:
            os.unlink(path)

    def do_checklist_close(self, args):
        project = self._project(args)
        state_dir = checklists.checklist_state_dir(project.path)
        if args.all:
            copies = checklists.find_open_copies(state_dir)
        else:
            try:
                copies = [checklists.resolve_single(args.copy, state_dir)]
            except checklists.ChecklistError as errmsg:
                print_error(errmsg)
                sys.exit(1)
        skipped_incomplete = []
        skipped_empty = []
        skipped_unreadable = []
        for copy in copies:
            try:
                parsed = checklists.parse_checklist(
                    self._read_copy_text(copy))
            except checklists.ChecklistError:
                parsed = None
            if parsed is None:
                if not args.force:
                    skipped_unreadable.append(copy)
                    continue
            elif not parsed.items:
                if not args.force:
                    skipped_empty.append(copy)
                    continue
            elif parsed.has_open_items and not args.force:
                skipped_incomplete.append(copy)
                continue
            checklists.close_copy(state_dir, copy.copy_id)
            print('Closed {}'.format(copy.copy_id))
        if skipped_unreadable:
            print_notice('Still open (unreadable): {}'.format(
                ', '.join(copy.copy_id for copy in skipped_unreadable)))
        if skipped_incomplete or skipped_empty:
            if args.all:
                if skipped_incomplete:
                    print_notice('Still open (incomplete): {}'.format(
                        ', '.join(copy.copy_id
                                  for copy in skipped_incomplete)))
                if skipped_empty:
                    print_notice('Still open (no task items): {}'.format(
                        ', '.join(copy.copy_id
                                  for copy in skipped_empty)))
            else:
                if skipped_unreadable:
                    print_error('The working copy {} cannot be read; '
                                'use --force to close it anyway'.format(
                                    skipped_unreadable[0].copy_id))
                elif skipped_incomplete:
                    print_error('The checklist {} is incomplete; use '
                                '--force to close it anyway'.format(
                                    skipped_incomplete[0].copy_id))
                else:
                    print_error('The checklist {} does not contain any '
                                'task items; use --force to close it '
                                'anyway'.format(
                                    skipped_empty[0].copy_id))
                sys.exit(1)

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

        self._run_wrapped_operation(args, project, args.tofu_args,
                                    eval_first=args.eval)

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

        self._run_wrapped_operation(args, project, ['init'],
                                    eval_first=args.eval)

    def _do_tofu_install(self, args, project):
        """Run the 'debops tofu install' operation: reconcile the
        OpenTofu binaries which the project's views pin with the
        installed ones. The '--eval' option reports the install
        instead of running it."""
        try:
            installed = reconcile_binaries(project, force=args.force,
                                           dry_run=args.eval)
        except ValueError as errmsg:
            print_error(errmsg)
            sys.exit(1)
        if args.eval:
            if installed:
                for version in installed:
                    print("Would install the pinned OpenTofu binary "
                          "'{}'".format(version))
            else:
                print("The pinned binaries of the views of the project "
                      "{!r} are installed".format(project.name))
            return
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
                bell=args.bell, to_view=args.to_view)
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

    def _run_wrapped_operation(self, args, project, tofu_args,
                               eval_first=False):
        """Construct the runner, run the operation, map the failures
        to the exit codes -- the boilerplate the tofu operations
        share. With 'eval_first' the printed command replaces the
        execution: the '--eval' dry-run of the update."""
        try:
            runner = TofuRunner(project, tofu_args, bell=args.bell,
                                no_color=args.no_color,
                                workspace=args.workspace,
                                allow_missing_state=(
                                    args.allow_missing_state))
        except (NoDefaultViewException, ValueError,
                FileNotFoundError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

        if eval_first:
            self._note_pending_view_creation(project)
            print(runner.eval())
            sys.exit(0)

        try:
            sys.exit(runner.execute())
        except (ChildProcessError, ValueError) as errmsg:
            print_error(errmsg)
            sys.exit(1)

    def _do_tofu_rekey(self, args, project):
        """Run the 'debops tofu rekey' operation: rotate the state
        passphrase of the view through the fallback key provider of
        the OpenTofu encryption, printing the change records the
        rotation applies."""
        try:
            changes = rekey_view(project, project.view,
                                 workspace=args.workspace)
        except (NoDefaultViewException, ValueError, FileNotFoundError,
                ChildProcessError) as errmsg:
            print_error(errmsg)
            sys.exit(1)
        self._render_tofu_changes(changes)

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
                    print('{:>4}  {}  {:>7}  {}'.format(
                        sequence, plans_module.plan_stamp(name),
                        cache.human_size(size), human_age(mtime)))
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
        self._run_wrapped_operation(
            args, project,
            [args.verb] + (['-json'] if args.json else []) + [plan_file])

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
                    # object and a non-zero exit code; the other
                    # formats name the option -- a silent exit would
                    # hide a mistyped key or an option consumed as one
                    if args.format == 'json':
                        print('{}')
                    else:
                        print_error(
                            "The option '{}' is not defined in the "
                            'configuration'.format(option_name))
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

        shadow = shadowing_file(option_file, args.key)
        if shadow:
            shadow_path, shadow_value = shadow
            logger.warning(
                "The value of '%s' set in '%s' is shadowed by '%s', "
                'which loads after it: its value %r wins', args.key,
                unexpanduser(option_file), unexpanduser(shadow_path),
                shadow_value,
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
