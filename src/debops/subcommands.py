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
    from .__version__ import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0"

from .utils import print_error
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
    config   display DebOps configuration options''')

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
        group.add_argument('--' + name, dest=name,
                           help=help, action='store_true')
        group.add_argument('--no-' + name, dest=name,
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
        parser.add_argument('--encrypt', type=str, nargs='?',
                            choices=['encfs', 'git-crypt'],
                            help='enable encrypted secrets')
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

    def do_config(self):
        parser = _argument_parser(
                description='manage DebOps configuration state',
                usage='''debops config <command> [<args>]

Commands:
    get     return value of a specific configuration option
    list    list configuration files parsed by DebOps''')
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
