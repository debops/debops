# Copyright (C) 2020-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys
import textwrap

# Detect the DebOps version from the Python module. If the version is not
# available, we are in a development environment in which case we use a stub
# version number to avoid errors.
try:
    from ..__version__ import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0"

from . import print_error
from ..core.ssh import (SCP_OPTIONS_WITH_VALUE, SFTP_OPTIONS_WITH_VALUE,
                        SSH_OPTIONS_WITH_VALUE, split_options_operands,
                        value_options_of)
import shutil


# argparse wraps the help at the terminal width minus two; the full
# width of a modern terminal is a strain to read, so cap it at the
# width an 80-column terminal would get. A narrower terminal still
# wins
HELP_WIDTH = 78


def help_width():
    """The width the help output wraps at: the terminal width minus
    two, capped at :data:`HELP_WIDTH`."""
    return min(shutil.get_terminal_size().columns - 2, HELP_WIDTH)


class HelpFormatter(argparse.HelpFormatter):
    """The help formatter of the subcommands: the capped wrap width
    and no mid-word breaks."""

    def __init__(self, prog, indent_increment=2, max_help_position=24,
                 width=None):
        if width is None:
            width = help_width()
        super().__init__(prog, indent_increment=indent_increment,
                         max_help_position=max_help_position,
                         width=width)

    def _fill_text(self, text, width, indent):
        # Wrap without breaking the option names at the hyphens; a
        # '--skip-tags' split in the middle would confuse an
        # unfamiliar user
        wrapped = []
        for line in text.split('\n'):
            wrapped.append(textwrap.fill(
                    line, width=width,
                    initial_indent=indent, subsequent_indent=indent,
                    break_long_words=False, break_on_hyphens=False))
        return '\n'.join(wrapped)

    def _split_lines(self, text, width):
        text = self._whitespace_matcher.sub(' ', text).strip()
        return textwrap.wrap(text, width=width,
                             break_long_words=False,
                             break_on_hyphens=False)


def _argument_parser(**kwargs):
    """The subcommand parsers share the comfortable help width."""
    return argparse.ArgumentParser(formatter_class=HelpFormatter,
                                   **kwargs)


class Subcommands(object):

    def __init__(self, args=None):
        self.args = args

        self.global_parser = _argument_parser(add_help=False)
        self.global_parser.add_argument('-v', '--verbose', action="count",
                                        help='increase output verbosity '
                                             '(e.g., -vv is more than -v)')
        self.global_parser.add_argument('--project-dir', type=str,
                                        nargs='?', default=os.getcwd(),
                                        help='path to the project directory')

        parser = _argument_parser(
                description="DebOps CLI",
                usage='''debops <section> [<args>]

Sections:
    project  manage project directories
    exec     run Ansible commands directly against hosts
    run      run Ansible playbook(s) against hosts
    check    run Ansible playbook(s) in check mode
    env      run shell commands in project environment
    config   manage DebOps configuration options
    tofu     manage OpenTofu views, state and inventory

SSH connections:
    ssh      connect to hosts over ssh and manage known_hosts
    scp      copy files to and from hosts over ssh
    sftp     transfer files interactively over ssh

Misc operations:
    checklist  manage operational checklists''')

        parser.add_argument('section', help='Section to run')
        parser.add_argument('--version', action='version',
                            version='%(prog)s {version}'
                                    .format(version=__version__))

        self._section = parser.parse_args(self.args[1:2])
        self.section = self._section.section
        if not hasattr(self, 'do_' + self._section.section):
            print_error('unrecognized section: ' + self._section.section)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_' + self._section.section)()

    def add_bool_argument(self, parser, name, default=False,
                          required=False, help=None, no_help=None):
        group = parser.add_mutually_exclusive_group(
                required=required)
        option = name.replace('_', '-')
        group.add_argument('--' + option, dest=name,
                           help=help, action='store_true')
        group.add_argument('--no-' + option, dest=name,
                           help=no_help, action='store_false')
        parser.set_defaults(**{name: default})

    # The ansible options the 'run', 'check' and 'exec' subcommands
    # recognize as first-class options, in the order they are injected
    # into the ansible arguments. Each entry: (dest, short option, long
    # option, metavar, group, one-line description used by the
    # '--help-ansible' output). The options are hidden from the regular
    # '--help' output to keep it readable; '--help-ansible' lists them.
    PLAYBOOK_ANSIBLE_OPTIONS = (
        ('check', '-C', '--check', None, 'mode',
         "don't make any changes; predict what would change"),
        ('diff', '-D', '--diff', None, 'mode',
         'show the differences of files and templates when changing'),
        ('syntax_check', None, '--syntax-check', None, 'mode',
         'parse the playbooks and exit; nothing runs'),
        ('step', None, '--step', None, 'mode',
         'one-step-at-a-time; confirm each task before running'),
        ('list_hosts', None, '--list-hosts', None, 'mode',
         'list the affected hosts and exit; nothing runs'),
        ('list_tasks', None, '--list-tasks', None, 'mode',
         'list the tasks and exit; nothing runs'),
        ('list_tags', None, '--list-tags', None, 'mode',
         'list all available tags and exit; nothing runs'),
        ('limit', '-l', '--limit', 'SUBSET', 'shaping',
         'only run plays and tasks whose hosts match the pattern'),
        ('tags', '-t', '--tags', 'TAGS', 'shaping',
         'only run plays and tasks with these tags'),
        ('skip_tags', None, '--skip-tags', 'TAGS', 'shaping',
         'skip plays and tasks with these tags'),
        ('forks', '-f', '--forks', 'N', 'shaping',
         'run this many parallel host processes'),
        ('start_at_task', None, '--start-at-task', 'NAME', 'shaping',
         'start at the task with this name'),
        ('force_handlers', None, '--force-handlers', None, 'shaping',
         'run the notified handlers even if a task fails'),
        ('flush_cache', None, '--flush-cache', None, 'shaping',
         'clear the fact cache for every host'),
        ('user', '-u', '--user', 'NAME', 'connection',
         'connection user'),
        ('become', '-b', '--become', None, 'connection',
         'run operations with become'),
        ('become_user', None, '--become-user', 'NAME', 'connection',
         'user to become (default: root)'),
        ('ask_become_pass', '-K', '--ask-become-pass', None, 'connection',
         'ask for the privilege escalation password'),
        ('ask_pass', '-k', '--ask-pass', None, 'connection',
         'ask for the connection password'),
        ('connection', '-c', '--connection', 'NAME', 'connection',
         'connection type to use'),
        ('timeout', '-T', '--timeout', 'T', 'connection',
         'connection timeout in seconds'),
    )

    # The 'exec' subcommand runs the ad-hoc 'ansible' command, which
    # accepts only the subset below; in particular '-t' is '--tree'
    # there, not '--tags'
    ADHOC_ANSIBLE_OPTIONS = frozenset((
        'limit', 'forks', 'user', 'become', 'become_user',
        'ask_become_pass', 'ask_pass', 'connection', 'timeout'))

    def add_ansible_options(self, parser, adhoc=False):
        """Add the hidden first-class ansible options to a subcommand
        parser, along with the visible '--help-ansible' option."""
        for dest, short, long_option, metavar, group, option_help in \
                self.PLAYBOOK_ANSIBLE_OPTIONS:
            if adhoc and dest not in self.ADHOC_ANSIBLE_OPTIONS:
                continue
            names = [long_option] + ([short] if short else [])
            if metavar is None:
                parser.add_argument(*names, dest=dest,
                                    help=argparse.SUPPRESS,
                                    action='store_true')
            else:
                parser.add_argument(*names, dest=dest, metavar=metavar,
                                    help=argparse.SUPPRESS,
                                    action='store')
        parser.add_argument('--help-ansible', action='store_true',
                            help='show the recognized ansible options '
                                 'and exit')

    def ansible_options_to_args(self, options, adhoc=False):
        """The recognized ansible options given on the command line,
        as ansible arguments to prepend to the pass-through arguments."""
        result = []
        for dest, _short, long_option, metavar, _group, _option_help in \
                self.PLAYBOOK_ANSIBLE_OPTIONS:
            if adhoc and dest not in self.ADHOC_ANSIBLE_OPTIONS:
                continue
            value = options.get(dest)
            if not value:
                continue
            if metavar is None:
                result.append(long_option)
            else:
                result.extend([long_option, value])
        return result

    def print_ansible_help(self, command, adhoc=False):
        """Print the recognized ansible options; the '--help-ansible'
        output."""
        binary = 'ansible' if adhoc else 'ansible-playbook'
        width = help_width()
        print('debops {} recognizes these ansible options directly:'
              .format(command))
        print()
        for group, title in (('mode', 'execution mode:'),
                             ('shaping', 'run shaping:'),
                             ('connection', 'connection:')):
            spellings = []
            for dest, short, long_option, metavar, option_group, _help in \
                    self.PLAYBOOK_ANSIBLE_OPTIONS:
                if option_group != group:
                    continue
                if adhoc and dest not in self.ADHOC_ANSIBLE_OPTIONS:
                    continue
                spelling = short + ', ' + long_option if short else long_option
                if metavar:
                    spelling += ' ' + metavar
                spellings.append(spelling)
            if not spellings:
                continue
            print('  ' + title)
            print(textwrap.fill(', '.join(spellings), width=width,
                                initial_indent='    ',
                                subsequent_indent='    ',
                                break_long_words=False,
                                break_on_hyphens=False) + '\n')
        print(textwrap.fill(
            'Everything after the playbook name(s) is passed to '
            + binary + ' unchanged; see \'' + binary
            + ' --help\' for its full option set.', width=width,
            break_long_words=False, break_on_hyphens=False))

    def do_project(self):
        parser = _argument_parser(
                description='manage project directory',
                usage='''debops project <command> [<args>]

Commands:
    init    initialize new project directory
    mkview  create a new infrastructure view
    commit  commit current changes in git repository
    refresh refresh existing project directory
    unlock  decrypt secrets in project directory
    lock    encrypt secrets in project directory
    venv    manage Python virtual environment''')
        parser.add_argument('command', help='project command to run')
        self._command = parser.parse_args(self.args[2:3])
        self.command = self._command.command
        if not hasattr(self, 'do_project_' + self._command.command):
            print_error('unrecognized command: ' + self._command.command)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_project_' + self._command.command)()

    def add_spec_arguments(self, parser):
        """Add the options which read and apply an inventory file
        specification. Shared by the 'project' subcommands which can create
        or refresh an Ansible inventory."""
        parser.add_argument('--template', type=str, dest='spec_sources',
                            action='append', metavar='SPEC',
                            help='apply an inventory spec from '
                                 'template, file or stdin (multiple)')
        parser.add_argument('-n', '--dry-run', action='store_true',
                            help='only simulate changes from inventory '
                                 'spec')
        parser.add_argument('--force', action='store_true',
                            help='overwrite, clear or remove paths which '
                                 'already exist')
        parser.add_argument('--allow-io', action='store_true',
                            help='allow commands or file includes in '
                                 'inventory spec')
        inspect = parser.add_mutually_exclusive_group()
        inspect.add_argument('--graph', action='store_true',
                             help='display the Ansible inventory graph')
        inspect.add_argument('--list', action='store_true',
                             help='display the Ansible inventory as JSON')
        inspect.add_argument('--host', type=str, metavar='HOST',
                             help='display selected host variables as JSON')

    def do_project_init(self):
        parser = _argument_parser(
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
                               default=True,
                               no_help='disable git support')
        self.add_bool_argument(parser, 'requirements',
                               help='install Ansible Collections after '
                                    'initialization (default)',
                               default=True,
                               no_help="don't install Ansible Collections")
        self.add_bool_argument(parser, 'venv',
                               help='enable Python virtual environment '
                                    '(modern projects only)',
                               default=False,
                               no_help="don't enable Python virtual "
                                       "environment")
        self.add_bool_argument(parser, 'ssh',
                               help='configure the SSH known_hosts store '
                                    'of the default view (modern '
                                    'projects only)',
                               default=False,
                               no_help="don't configure the SSH "
                                       "known_hosts store")
        parser.add_argument('--encrypt', type=str, nargs='?',
                            choices=['encfs', 'git-crypt', 'plain'],
                            help='enable encrypted secrets; plain commits '
                                 'the passphrase unencrypted')
        self.add_bool_argument(parser, 'tofu',
                               help='create the OpenTofu view of the '
                                    'default view after the initialization',
                               no_help="don't create the OpenTofu view")
        self.add_bool_argument(parser, 'pre_commit',
                               help='install the pre-commit hook after '
                                    'the initialization',
                               no_help="don't install the pre-commit hook")
        parser.add_argument('--keys', type=str,
                            help='list of GPG recipients with secret access, '
                                 'delimited by commas')
        self.add_spec_arguments(parser)
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_refresh(self):
        parser = _argument_parser(
                description='refresh existing project directory',
                usage='debops project refresh [<args>] <project_dir>')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to refresh')
        self.add_spec_arguments(parser)
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_lock(self):
        parser = _argument_parser(
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
        parser = _argument_parser(
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
        parser = _argument_parser(
                parents=[self.global_parser],
                description='create new infrastructure view',
                usage='debops project mkview [<args>] <new_view>')
        parser.add_argument('--encrypt', type=str, nargs='?',
                            choices=['encfs', 'git-crypt'],
                            help='enable encrypted secrets')
        parser.add_argument('--keys', type=str,
                            help='list of GPG recipients with secret access, '
                                 'delimited by commas')
        self.add_bool_argument(parser, 'ssh',
                               help='configure the SSH known_hosts store '
                                    'of the new view',
                               default=False,
                               no_help="don't configure the SSH "
                                       "known_hosts store")
        self.add_spec_arguments(parser)
        parser.add_argument('new_view', type=str, nargs='?',
                            help='name of the new infrastructure view')
        self.args = parser.parse_args(self.args[3:])

    def do_project_commit(self):
        parser = _argument_parser(
                description='commit current changes in git repository',
                usage='debops project commit [<args>] <project_dir>')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_project_venv(self):
        parser = _argument_parser(
                description='manage Python virtual environment in project '
                            'directory',
                usage='''debops project venv <action> [<args>] [<project_dir>]

Actions:
    enable    activate the environment in an existing project
    install   create the environment and install requirements
    upgrade   upgrade the seed Python packages and Ansible Collections
    recreate  destroy the environment and install it from scratch
    freeze    write the installed package versions to the requirements file''')
        parser.add_argument('action', type=str,
                            choices=['enable', 'install', 'upgrade',
                                     'recreate', 'freeze'],
                            help='action to perform on the environment')
        scope = parser.add_mutually_exclusive_group()
        scope.add_argument('--python', dest='scope', action='store_const',
                           const='python',
                           help='manage only the Python packages')
        scope.add_argument('--collections', dest='scope',
                           action='store_const', const='collections',
                           help='manage only the Ansible Collections')
        scope.add_argument('--all', dest='scope', action='store_const',
                           const='all',
                           help='manage everything (default)')
        parser.set_defaults(scope='all')
        parser.add_argument('-v', '--verbose', action="count",
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        # The 'action' and 'project_dir' positionals need to be matched
        # around the options, which parse_args() cannot do on its own
        self.args = parser.parse_intermixed_args(self.args[3:])

    def do_exec(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops exec [<args>] [--] <[ansible_args]>',
                description='run Ansible commands directly against hosts',
                epilog='A subset of the ansible options is recognized '
                       'directly; run \'debops exec --help-ansible\' for '
                       'the list. Any other options must be specified '
                       'after the command arguments.')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to use for the "ansible" command')
        parser.add_argument('-E', '--bell', default=False,
                            help='notify the user at the end '
                                 'of Ansible execution',
                            action='store_true')
        parser.add_argument('--accept', default=False,
                            help='accept unseen ssh host keys on first '
                                 'contact for this invocation',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the Ansible command '
                                 'generated by DebOps',
                            action='store_true')
        self.add_ansible_options(parser, adhoc=True)
        parser.add_argument('ansible_args', type=str, nargs=argparse.REMAINDER,
                            help='arguments for the '
                                 '"ansible" command')
        self.args = parser.parse_args(self.args[2:])

        if self.args.help_ansible:
            self.print_ansible_help('exec', adhoc=True)
            sys.exit(0)

        self.args.ansible_args = (self.ansible_options_to_args(
                                      vars(self.args), adhoc=True)
                                  + self.args.ansible_args)

    def do_run(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops run [<args>] [--] <[<namespace>.<collection>/]'
                      'playbook> [playbook] ... [ansible_args]',
                description='run Ansible playbook(s) against hosts',
                epilog='A subset of the ansible-playbook options is '
                       'recognized directly; run \'debops run '
                       '--help-ansible\' for the list. Any other options '
                       'must be specified after the playbook name(s).')
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
        parser.add_argument('--debug', default=False,
                            help='run with debugging output: -vv, '
                                 'ANSIBLE_DEBUG, the remote module '
                                 'files kept on the hosts',
                            action='store_true')
        parser.add_argument('--accept', default=False,
                            help='accept unseen ssh host keys on first '
                                 'contact for this invocation',
                            action='store_true')
        self.add_ansible_options(parser)
        parser.add_argument('ansible_args', type=str, nargs=argparse.REMAINDER,
                            help='arguments for the '
                                 '"ansible-playbook" command')
        self.args = parser.parse_args(self.args[2:])

        if self.args.help_ansible:
            self.print_ansible_help('run')
            sys.exit(0)

        self.args.ansible_args = (self.ansible_options_to_args(
                                      vars(self.args))
                                  + self.args.ansible_args)

    def do_check(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops check [<args>] [--] <[<namespace>.<collection>/]'
                      'playbook> [playbook] ... [ansible_args]',
                description='run Ansible playbook(s) in check mode',
                epilog='Check mode with diff output is enabled '
                       'automatically. A subset of the ansible-playbook '
                       'options is recognized directly; run \'debops check '
                       '--help-ansible\' for the list. Any other options '
                       'must be specified after the playbook name(s).')
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
        parser.add_argument('--debug', default=False,
                            help='run with debugging output: -vv, '
                                 'ANSIBLE_DEBUG, the remote module '
                                 'files kept on the hosts',
                            action='store_true')
        parser.add_argument('--accept', default=False,
                            help='accept unseen ssh host keys on first '
                                 'contact for this invocation',
                            action='store_true')
        self.add_ansible_options(parser)
        parser.add_argument('ansible_args', type=str,
                            nargs=argparse.REMAINDER,
                            help='arguments for the '
                                 '"ansible-playbook" command')
        self.args = parser.parse_args(self.args[2:])

        if self.args.help_ansible:
            self.print_ansible_help('check')
            sys.exit(0)

        # Run in check mode with diff output; the flags are added only
        # if the user did not already choose them, as first-class
        # options on either side of the playbook name(s), or as
        # pass-through options after them
        ansible_args = (self.ansible_options_to_args(vars(self.args))
                        + self.args.ansible_args)
        if '--diff' not in ansible_args and '-D' not in ansible_args:
            ansible_args.append('--diff')
        if '--check' not in ansible_args and '-C' not in ansible_args:
            ansible_args.append('--check')
        self.args.ansible_args = ansible_args

    def do_env(self):
        parser = _argument_parser(
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

    def do_tofu(self):
        parser = _argument_parser(
                parents=[self.global_parser], add_help=False,
                usage='''debops tofu [<args>] [--] <operation> [<operation args>]

DebOps-level operations (not passed to the 'tofu' command):
  mkview     create a new view with its store and the environment file
  update     reconcile the files DebOps owns in the view and run
             'tofu init' through the wrapper
  install    install the OpenTofu binaries which the views pin
  inventory  render the inventory outputs of the view into the
             Ansible view's inventory
  plans      list the plan files the wrapper saves for the view and
             show, apply or delete one of them by its id
  rekey      rotate the state passphrase of the view through the
             fallback key provider of the OpenTofu encryption
  cache      list and clean the OpenTofu cache of the project''',
                epilog="The operation and its arguments are passed to "
                       "the 'tofu' command; the DebOps options come "
                       'before the operation, the options of the '
                       'operation after it.')
        # The options of the section and the ones inherited from the
        # global parser share the 'DebOps options' section of the
        # composed help screen
        parser._optionals.title = 'DebOps options'
        parser.add_argument(
                '-h', '--help', action='store_true',
                help='show the OpenTofu help followed by the options '
                     'of the wrapper')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view '
                                 'to use for the "tofu" command')
        parser.add_argument('-E', '--bell', default=False,
                            help='notify the user at the end '
                                 'of the OpenTofu operation',
                            action='store_true')
        parser.add_argument('--no-color', default=False,
                            help='strip the ANSI color codes '
                                 'from the operation output',
                            action='store_true')
        parser.add_argument('-w', '--workspace', type=str,
                            help='run the operation against the '
                                 'named workspace of the view, '
                                 'overriding the workspace '
                                 'configured for the view')
        parser.add_argument('-M', '--allow-missing-state',
                            default=False, action='store_true',
                            help='proceed with the state-touching '
                                 'operations on a view whose state '
                                 'file is missing: for the '
                                 'deliberate wipe-and-rebuild')
        parser.add_argument('--eval', default=False,
                            help='print the OpenTofu command '
                                 'and exit',
                            action='store_true')
        parser.add_argument('tofu_args', type=str, nargs=argparse.REMAINDER,
                            help=argparse.SUPPRESS)
        self.args = parser.parse_args(self.args[2:])
        self._parse_tofu_operation()
        if self.args.help:
            self.args.help_body = self._tofu_help_body(parser)

    def _tofu_help_body(self, parser):
        """The help of the wrapper without the usage synopsis: the
        composed help screen prints the OpenTofu help first, whose
        rewritten usage line stands in for ours."""
        return parser.format_help().split('\n', 1)[1]

    def _parse_tofu_operation(self):
        """Parse the options of the DebOps-level tofu operations: the
        operations which the wrapper does not pass to the 'tofu'
        command carry their own options and their own help screens."""
        if self.args.tofu_args and self.args.tofu_args[0] == '--':
            # The '--' separator the usage line promises between the
            # wrapper options and the operation: a leading one must
            # not turn the DebOps-level operations into raw
            # passthrough
            self.args.tofu_args.pop(0)
        if (not self.args.tofu_args
                or self.args.tofu_args[0] not in ('mkview', 'update',
                                                  'install', 'inventory',
                                                  'plans', 'rekey',
                                                  'cache')):
            return
        if self.args.tofu_args[0] == 'mkview':
            parser = _argument_parser(
                    usage='debops tofu mkview [<options>] <new_view>',
                    description='create a new OpenTofu view with its '
                                'encrypted store and the environment '
                                'key file of the view')
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            parser.add_argument('-e', '--encrypt', type=str, nargs='?',
                                choices=['encfs', 'git-crypt', 'plain'],
                                help="the encryption of the view's "
                                     'secret store: the mechanism '
                                     'detected in the project is the '
                                     "default -- 'git-crypt' for the "
                                     'repository-wide setup, '
                                     "'encfs' where the Ansible views "
                                     'carry EncFS volumes; required '
                                     'when the project carries no '
                                     "store yet, and 'plain' commits "
                                     'the passphrase unencrypted')
            parser.add_argument('--keys', type=str,
                                help='list of GPG recipients with '
                                     'secret access, delimited by '
                                     'commas; required for EncFS')
            mkview_options = parser.add_argument_group(
                    "the 'debops tofu mkview' options")
            mkview_options.add_argument('-p', '--provider', type=str,
                                        action='append', default=None,
                                        help='require the OpenTofu provider '
                                             'in the created view, as a '
                                             'registry source address; '
                                             'repeatable')
            mkview_options.add_argument('-m', '--module', type=str,
                                        action='append', default=None,
                                        help='instantiate the OpenTofu module '
                                             'in the created view, as a '
                                             'registry source address; '
                                             'repeatable')
            parser.add_argument('new_view', type=str,
                                help='name of the view to create')
            self.args = parser.parse_args(self.args.tofu_args[1:],
                                          namespace=self.args)
            return
        if self.args.tofu_args[0] == 'inventory':
            parser = _argument_parser(
                    usage='debops tofu inventory [<options>]',
                    description="render the inventory outputs of the "
                                "view into the Ansible view's "
                                'inventory: the hosts file in the '
                                'configured format, the variables '
                                'files of the hosts and groups, and '
                                'the sensitive values into the '
                                "view's secret store")
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            parser.add_argument('-f', '--force', action='store_true',
                                help='refresh the state of the view '
                                     'before the render: in-place '
                                     'changes and late DHCP leases '
                                     'land in the inventory')
            parser.add_argument('-n', '--dry-run', action='store_true',
                                help='only simulate the render: '
                                     'report the changes without '
                                     'applying them')
            parser.add_argument('-t', '--to-view', type=str,
                                help="render into the named Ansible "
                                     "view's inventory and store "
                                     'instead of the mirror view of '
                                     'the same name')
            parser.add_argument('--diff', action='store_true',
                                help='print the unified diffs of the '
                                     'changes instead of the paths')
            self.args = parser.parse_args(self.args.tofu_args[1:],
                                          namespace=self.args)
            return
        if self.args.tofu_args[0] == 'plans':
            parser = _argument_parser(
                    usage='debops tofu plans [<verb> [<id>]]',
                    description="list the plan files the wrapper "
                                "saves for the view -- the sequence "
                                'id, the stamp, the size and the '
                                'age -- and show, apply or delete '
                                'one of them by its id. The ids are '
                                'stable while the retention prunes '
                                'the oldest files; the plan files '
                                'are OpenTofu-encrypted')
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            parser.add_argument('--json', action='store_true',
                                help='render the plan as JSON')
            parser.add_argument('verb', nargs='?',
                                choices=['show', 'apply', 'delete'],
                                help='the operation on one saved '
                                     'plan; the bare operation '
                                     'lists them')
            parser.add_argument('plan_id', nargs='?',
                                help='the sequence id of the saved '
                                     'plan, or the unique prefix of '
                                     'its file name')
            self.args = parser.parse_args(self.args.tofu_args[1:],
                                          namespace=self.args)
            if self.args.json and self.args.verb != 'show':
                parser.error("'--json' renders a plan: it needs the "
                             "'show' verb")
            if self.args.verb and not self.args.plan_id:
                parser.error("The '{}' verb needs the id of the "
                             'saved plan'.format(self.args.verb))
            return
        if self.args.tofu_args[0] == 'rekey':
            parser = _argument_parser(
                    usage='debops tofu rekey',
                    description="rotate the state passphrase of the "
                                "view: the new passphrase is "
                                'generated, the state is '
                                're-encrypted through the fallback '
                                'key provider of the OpenTofu '
                                'encryption, the saved plan files '
                                'encrypted under the retired key '
                                'are removed. An interrupted '
                                'rotation resumes on a re-run')
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            self.args = parser.parse_args(self.args.tofu_args[1:],
                                          namespace=self.args)
            return
        if self.args.tofu_args[0] == 'cache':
            parser = _argument_parser(
                    usage='debops tofu cache [<options>]',
                    description="list and clean the OpenTofu cache of "
                                'the project: the data directories of '
                                'its views, the in-tree '
                                "'.terraform/ leftovers of the views "
                                'which predate the data dir relocation, '
                                'and the shared plugin cache. The '
                                'cleaned data is re-derivable: the '
                                'state is tracked in the view tree, '
                                'the next init rebuilds the rest')
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            parser.add_argument('--clean', action='store_true',
                                help='remove the cache entries of the '
                                     'selected scope: the resolved '
                                     "view's data dir by default")
            parser.add_argument('--project', action='store_true',
                                help="scope the clean to the data "
                                     'dirs of all the views of the '
                                     'project')
            parser.add_argument('--plugins', action='store_true',
                                help='scope the clean to the shared '
                                     'plugin cache of all views and '
                                     'projects')
            parser.add_argument('--reset', action='store_true',
                                help='clean the whole cache root: '
                                     'the data dirs of all projects, '
                                     'the shared plugin cache and the '
                                     'stale entries of the projects '
                                     'which moved away')
            parser.epilog = (
                'The scopes rank from the narrow to the whole: '
                "'--clean' cleans the resolved view, '--project' the "
                'views of the project, \'--plugins\' the shared '
                'provider cache, and \'--reset\' the entire cache '
                'root. Provider binaries live in the shared cache and '
                're-download on the next init; the module state lives '
                'in the data dirs.')
            self.args = parser.parse_args(self.args.tofu_args[1:],
                                          namespace=self.args)
            if self.args.reset and (self.args.project
                                    or self.args.plugins):
                parser.error("'--reset' cleans the whole cache root: "
                             "it does not combine with '--project' "
                             "or '--plugins'")
            if self.args.project and self.args.plugins:
                parser.error("'--project' and '--plugins' are separate "
                             'scopes: choose one')
            if ((self.args.project or self.args.plugins or self.args.reset)
                    and not self.args.clean):
                parser.error("'--project', '--plugins' and '--reset' are "
                             "scopes of '--clean': give both options")
            return
        if self.args.tofu_args[0] == 'update':
            parser = _argument_parser(
                    usage='debops tofu update [<options>]',
                    description="reconcile the files DebOps owns in the "
                                "view: the generated 'providers.tf' and "
                                "'modules.tf' files follow the "
                                'dependency sets recorded in the view '
                                "configuration drop-in, and 'tofu init' "
                                'runs through the wrapper to apply the '
                                'changed requirement files')
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            parser.add_argument('-n', '--dry-run', action='store_true',
                                help='only simulate the reconcile: '
                                     'report the changes without '
                                     'applying them')
            parser.add_argument('--diff', action='store_true',
                                help='print the unified diffs of the '
                                     'changes instead of the paths')
            parser.add_argument('--force', action='store_true',
                                help='overwrite, clear or remove paths '
                                     'which already exist')
        else:
            parser = _argument_parser(
                    usage='debops tofu install [<options>]',
                    description='install the OpenTofu binaries which '
                                'the views of the project pin, '
                                'version-keyed in the DebOps data '
                                'directory; the release archives are '
                                'verified against the release '
                                'checksums, whose signature the '
                                'DebOps-managed keyring authenticates')
            parser.add_argument('-v', '--verbose', action='count',
                                help='increase output verbosity '
                                     '(e.g., -vv is more than -v)')
            parser.add_argument('--force', action='store_true',
                                help='reinstall the binaries which are '
                                     'installed already: the download, '
                                     'the verification and the install '
                                     'run again')
        self.args = parser.parse_args(self.args.tofu_args[1:],
                                      namespace=self.args)

    def do_config(self):
        parser = _argument_parser(
                description='manage DebOps configuration state',
                usage='''debops config <command> [<args>]

Commands:
    check   check the configuration for errors
    get     return value of a specific configuration option
    list    list configuration files parsed by DebOps
    set     set or remove a configuration option''')
        parser.add_argument('command', help='config command to run')
        self._command = parser.parse_args(self.args[2:3])
        self.command = self._command.command
        if not hasattr(self, 'do_config_' + self._command.command):
            print_error('unrecognized command: ' + self._command.command)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_config_' + self._command.command)()

    def do_config_list(self):
        parser = _argument_parser(
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
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops config get [<args>] [--] <key>',
                description='return value of specific DebOps option')
        parser.add_argument('-f', '--format', type=str, nargs='?',
                            choices=['json', 'toml', 'unix', 'yaml'],
                            default=None,
                            help="output format (default: from the "
                                 "'config.default_output' option, 'yaml')")
        parser.add_argument('-k', '--keys', default=False,
                            help='list configuration keys '
                                 'at the specified level',
                            action='store_true')
        parser.add_argument('-r', '--root', default=False,
                            help='print the option nested under its '
                                 'full path in the configuration tree',
                            action='store_true')
        parser.add_argument('--show-origin', default=False,
                            help='show the source which last set each '
                                 'option',
                            action='store_true')
        parser.add_argument('--show-scope', default=False,
                            help='show the configuration layer which '
                                 'last set each option',
                            action='store_true')
        parser.add_argument('key', type=str,
                            nargs='*',
                            help='name of the '
                                 'configuration option')
        self.args = parser.parse_args(self.args[3:])

    def do_config_set(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops config set [<args>] [--] <key> '
                      '[<values>...]',
                description='set or remove a DebOps configuration '
                            'option in the configuration files')
        parser.add_argument('-u', '--user', default=False,
                            help='set the option in the user '
                                 'configuration instead of the project '
                                 'configuration',
                            action='store_true')
        parser.add_argument('-d', '--delete', default=False,
                            help='remove the option from the '
                                 'configuration file; with values, '
                                 'remove the values from a list option',
                            action='store_true')
        parser.add_argument('-t', '--type', default=None,
                            choices=['bool', 'list', 'str', 'int',
                                     'dict'],
                            help='the type of the option: with no '
                                 'values, the option is created with '
                                 "the empty value of the type "
                                 "('bool' options need a value)")
        parser.add_argument('key', type=str,
                            help='path of the configuration option')
        parser.add_argument('values', type=str, nargs='*',
                            help='the values of the option: multiple '
                                 'values are appended to a list '
                                 'option')
        self.args = parser.parse_args(self.args[3:])

    def do_config_check(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops config check [<args>]',
                description='check the DebOps configuration for errors')
        parser.add_argument('--strict', default=False,
                            help='report unknown configuration options '
                                 'as errors',
                            action='store_true')
        self.args = parser.parse_args(self.args[3:])

    def do_checklist(self):
        parser = _argument_parser(
                description='manage operational checklists',
                usage='''debops checklist <command> [<args>]

Commands:
    list    list the discovered checklists and the open copies
    open    open a checklist as a working copy
    edit    edit an open checklist copy in an editor
    commit  record a checkpoint of an open copy in the project vault
    close   discard an open copy''')
        parser.add_argument('command', help='checklist command to run')
        self._command = parser.parse_args(self.args[2:3])
        self.command = self._command.command
        if not hasattr(self, 'do_checklist_' + self._command.command):
            print_error('unrecognized command: ' + self._command.command)
            parser.print_help()
            sys.exit(1)
        getattr(self, 'do_checklist_' + self._command.command)()

    def do_checklist_list(self):
        parser = _argument_parser(
                usage='debops checklist list [<args>] [<project_dir>]')
        parser.add_argument('-a', '--active', action='store_true',
                            help='list the open copies instead of the '
                                 'discovered checklists')
        parser.add_argument('-f', '--format', type=str,
                            choices=['text', 'json'], default='text',
                            help='output format (default: text)')
        parser.add_argument('-v', '--verbose', action='count', default=0,
                            help='increase output verbosity '
                                 '(e.g., -vv is more than -v)')
        parser.add_argument('project_dir', type=str, nargs='?',
                            default=os.getcwd(),
                            help='path to the project directory')
        self.args = parser.parse_args(self.args[3:])

    def do_checklist_open(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops checklist open [<args>] [<id>] <checklist>')
        parser.add_argument('checklist', nargs='+',
                            help='checklist path, optionally preceded by '
                                 'a copy id; a lone open copy id with '
                                 '--reset re-opens the copy from its '
                                 'recorded checklist')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-r', '--reset', dest='reset', default=False,
                           help='discard the current state of the '
                                'copy id and re-copy the checklist',
                           action='store_true')
        group.add_argument('--no-reset', dest='reset',
                           help='keep the current state of the '
                                'copy id',
                           action='store_false')
        parser.add_argument('-d', '--dry-run', dest='dry_run',
                            default=False,
                            help='show what would be opened without '
                                 'opening anything',
                            action='store_true')
        self.args = parser.parse_args(self.args[3:])
        if not 1 <= len(self.args.checklist) <= 2:
            parser.error('open takes a checklist path, optionally '
                         'preceded by a copy id')

    def do_checklist_edit(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops checklist edit [<args>] [<copy>]')
        parser.add_argument('copy', nargs='?', default=None,
                            help='copy id or checklist path; defaults '
                                 'to the only open copy')
        self.args = parser.parse_args(self.args[3:])

    def do_checklist_commit(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops checklist commit [<args>] [<copy>]')
        parser.add_argument('copy', nargs='?', default=None,
                            help='copy id or checklist path; defaults '
                                 'to the only open copy')
        parser.add_argument('-c', '--close', action='store_true',
                            help='deactivate the copy after the commit')
        parser.add_argument('-e', '--edit', action='store_true',
                            help='compose the commit message in an '
                                 'editor')
        self.args = parser.parse_args(self.args[3:])

    def do_checklist_close(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops checklist close [<args>] [<copy>]')
        parser.add_argument('copy', nargs='?', default=None,
                            help='copy id or checklist path; defaults '
                                 'to the only open copy')
        parser.add_argument('-f', '--force', action='store_true',
                            help='discard the copy even when items are '
                                 'still open')
        parser.add_argument('-A', '--all', action='store_true',
                            help='close every open copy: the completed '
                                 'ones normally, the incomplete ones '
                                 'only together with --force')
        self.args = parser.parse_args(self.args[3:])
        if self.args.all and self.args.copy:
            parser.error('close takes a copy or --all, not both')

    def do_ssh(self):
        # The first token selects the subcommand; anything else -- an
        # option or a host name -- belongs to the connect invocation,
        # whose parser reports its own errors
        token = self.args[2] if len(self.args) > 2 else ''
        if token in ('rescan', 'config'):
            self.command = token
            getattr(self, 'do_ssh_' + token)()
        elif token in ('-h', '--help') or not token:
            # The help of the section: the commands and the full option
            # list of the connect invocation, rendered from the connect
            # parser itself
            print("""debops ssh <command|host> [<args>]

Commands:
    rescan  refresh the known_hosts entries of hosts
    config  print or write the SSH client configuration

Connection of a host:""")
            self._ssh_connect_parser().print_help()
            sys.exit(0 if token else 2)
        else:
            self.command = 'connect'
            self.do_ssh_connect()

    def _ssh_connect_parser(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops ssh [<args>] <host> [-- <ssh_args>]',
                description='connect to a host over ssh, using the '
                            'connection parameters of the Ansible '
                            'inventory')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view')
        parser.add_argument('-u', '--user', type=str, metavar='NAME',
                            help='connect as this user instead of the '
                                 'inventory value')
        parser.add_argument('-p', '--port', type=str, metavar='PORT',
                            help='connect to this port instead of the '
                                 'inventory value')
        parser.add_argument('-i', '--identity', type=str, metavar='KEY',
                            help='use this private key instead of the '
                                 'inventory value')
        parser.add_argument('--accept', default=False,
                            help='accept unseen ssh host keys on first '
                                 'contact for this session',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the ssh command and exit',
                            action='store_true')
        # The destination and the remote command are split out of the
        # argument list by the getopt-style walk in 'do_ssh_connect'
        return parser

    def do_ssh_connect(self):
        parser = self._ssh_connect_parser()
        tokens = self.args[2:]
        marker = tokens.index('--') if '--' in tokens else len(tokens)
        handoff = tokens[marker + 1:] if marker < len(tokens) else None
        value_options, long_value_options = value_options_of(
            parser, passthrough=SSH_OPTIONS_WITH_VALUE)
        try:
            options, operands, tail = split_options_operands(
                tokens[:marker], value_options, long_value_options)
        except ValueError as error:
            parser.error(str(error))
        destination = operands[0] if operands else None
        self.args, extras = parser.parse_known_args(options)
        if destination is None and handoff is None:
            parser.error('the following arguments are required: '
                         'destination')
        self.args.handoff = handoff if destination is None else None
        self.args.host = destination
        self.args.ssh_args = tail + (handoff or [])
        self.args.ssh_extra_args = extras

    def do_ssh_rescan(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops ssh rescan [<args>] <pattern> [<pattern>...]',
                description='refresh the known_hosts entries of the '
                            'hosts matching the Ansible inventory '
                            'patterns: remove the stale entries and '
                            'scan the current host keys')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view')
        parser.add_argument('--remove', default=False,
                            help='only remove the stale entries',
                            action='store_true')
        parser.add_argument('--scan', default=False,
                            help='only scan and add the current host '
                                 'keys',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the actions and exit',
                            action='store_true')
        parser.add_argument('-f', '--known-hosts-file', type=str,
                            metavar='FILE',
                            help='known_hosts file to operate on '
                                 '(default: the store of the active '
                                 'mode)')
        parser.add_argument('-T', '--timeout', type=int, default=10,
                            metavar='SECONDS',
                            help='timeout of each key scan (default: '
                                 '10)')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--dns', dest='dns_mode', action='store_const',
                           const='dns', default=None,
                           help='verify the scanned host keys against '
                                'the SSHFP records of the DNS; '
                                'DNSSEC-validated records are stored '
                                'automatically, unsigned matches follow '
                                'the ssh.rescan.'
                                'trust_unsigned_records option')
        group.add_argument('--no-dns', dest='dns_mode',
                           action='store_const', const='no-dns',
                           help='do not check the SSH host keys against '
                                'DNS')
        group.add_argument('--dns-verify', dest='dns_mode',
                           action='store_const', const='dns-verify',
                           help='store keys automatically only when a '
                                'DNSSEC-validating resolver '
                                'authenticated the SSHFP records')
        # Without one of the options the mode comes from the
        # 'ssh.rescan.resolver_mode' option of the configuration
        confirm_group = parser.add_mutually_exclusive_group()
        confirm_group.add_argument('-c', '--confirm', dest='confirm',
                                   default=None, action='store_true',
                                   help='show the scanned fingerprints '
                                        'and ask for each host before '
                                        'storing them; without the '
                                        'option the prompting follows '
                                        'the ssh.rescan.confirm option '
                                        'of the configuration')
        confirm_group.add_argument('--no-confirm', dest='confirm',
                                   default=None, action='store_false',
                                   help='do not ask for the scanned '
                                        'fingerprints before storing '
                                        'them')
        parser.add_argument('hosts', nargs='+', metavar='pattern',
                            help='hosts, groups or the other Ansible '
                                 'inventory patterns to refresh the '
                                 'known_hosts entries of')
        self.args = parser.parse_args(self.args[3:])

    def do_ssh_config(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops ssh config [<args>]',
                description='print or write the SSH client configuration '
                            'of the active known_hosts mode')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view')
        parser.add_argument('--write', default=False,
                            help='write the managed block into the '
                                 '~/.ssh/config file',
                            action='store_true')
        self.args = parser.parse_args(self.args[3:])

    def do_scp(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops scp [<args>] [<scp options>] <source> '
                      '<destination>',
                description='copy files to and from hosts over ssh, '
                            'using the connection parameters of the '
                            'Ansible inventory',
                epilog='Note: the composed ssh options apply to both '
                       'connections. Operands whose inventory entries '
                       'define different jump hosts or other connection '
                       'options will not both work; use the '
                       '\'~/.ssh/config\' file for them.')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view')
        parser.add_argument('-i', '--identity', type=str, metavar='KEY',
                            help='use this private key for both sides')
        parser.add_argument('--accept', default=False,
                            help='accept unseen ssh host keys on first '
                                 'contact for this invocation',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the scp command and exit',
                            action='store_true')
        # The source and the destination operands are split out of the
        # argument list by the getopt-style walk in 'do_scp'; the
        # tokens after the '--' marker are the operands as well, the
        # way scp ends its option parsing there
        # The scp options which DebOps does not interpret are gathered
        # as unrecognized arguments and passed to scp unchanged
        tokens = self.args[2:]
        marker = tokens.index('--') if '--' in tokens else len(tokens)
        value_options, long_value_options = value_options_of(
            parser, passthrough=SCP_OPTIONS_WITH_VALUE)
        try:
            options, operands, _ = split_options_operands(
                tokens[:marker], value_options, long_value_options,
                stop_at_operand=False)
        except ValueError as error:
            parser.error(str(error))
        operands.extend(tokens[marker + 1:])
        self.args, extras = parser.parse_known_args(options)
        if len(operands) < 2:
            parser.error('at least two operands are required: one or '
                         'more sources and a destination')
        self.args.sources = operands[:-1]
        self.args.destination = operands[-1]
        self.args.scp_extra_args = extras

    def do_sftp(self):
        parser = _argument_parser(
                parents=[self.global_parser],
                usage='debops sftp [<args>] [<sftp options>] '
                      '<[user@]host[:path]>',
                description='run an interactive file transfer session '
                            'over ssh, using the connection parameters '
                            'of the Ansible inventory')
        parser.add_argument('-V', '--view', type=str,
                            help='select the infrastructure view')
        parser.add_argument('-i', '--identity', type=str, metavar='KEY',
                            help='use this private key for the session')
        parser.add_argument('--accept', default=False,
                            help='accept unseen ssh host keys on first '
                                 'contact for this session',
                            action='store_true')
        parser.add_argument('--eval', default=False,
                            help='print the sftp command and exit',
                            action='store_true')
        # The destination is split out of the argument list by the
        # getopt-style walk in 'do_sftp'
        # The sftp options which DebOps does not interpret are split
        # into the ones before the destination and the ones after it,
        # and passed to sftp in their places
        tokens = self.args[2:]
        marker = tokens.index('--') if '--' in tokens else len(tokens)
        handoff = tokens[marker + 1:] if marker < len(tokens) else None
        value_options, long_value_options = value_options_of(
            parser, passthrough=SFTP_OPTIONS_WITH_VALUE)
        try:
            options, operands, tail = split_options_operands(
                tokens[:marker], value_options, long_value_options)
        except ValueError as error:
            parser.error(str(error))
        destination = operands[0] if operands else None
        self.args, extras = parser.parse_known_args(options)
        if destination is None and handoff is None:
            parser.error('the following arguments are required: '
                         'destination')
        self.args.handoff = handoff if destination is None else None
        self.args.destination = destination
        self.args.sftp_head_args = extras
        self.args.sftp_tail_args = tail + (handoff or [])
