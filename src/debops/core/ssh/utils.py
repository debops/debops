# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The machinery shared by the ssh-family commands.

The known_hosts store selection, the store layout of a project view,
the resolution of the connection parameters of an inventory host and
the splitting of ssh-style argument lists are shared by the
'debops ssh', 'debops scp' and 'debops sftp' subcommands; the
command-specific builders live in the sibling modules.
"""

import configparser
import json
import logging
import os
import pkgutil
import shlex
import subprocess

import jinja2

from ..utils import path_inside_project

logger = logging.getLogger(__name__)

USER_KNOWN_HOSTS_STORE = '~/.ssh/known_hosts'

# The ssh options which take a separate value argument, per the usage
# line of the OpenSSH 9.2 ssh(1). Used to walk argument lists where
# ssh options and operands mix. A newer OpenSSH which adds value
# options needs the set revisited; the walk cannot infer the values
# of the options it does not know.
SSH_OPTIONS_WITH_VALUE = set('BbcDEeFIiJLlmOopQRSWw')

# The scp options which take a separate value argument, per the usage
# line of the OpenSSH 9.2 scp(1). The scp grammar differs from the
# ssh one: '-P' is the port and '-B', '-O', '-R' are flags.
SCP_OPTIONS_WITH_VALUE = set('cDFiJlPSX')

# The sftp options which take a separate value argument, per the
# usage line of the OpenSSH 9.2 sftp(1).
SFTP_OPTIONS_WITH_VALUE = set('BbcDFiJlPRsSX')

# The ssh options whose value is optional: they consume the next
# token when one follows, and stand alone at the end of the argument
# list ('ssh -Q' lists the query types).
SSH_OPTIONS_WITH_OPTIONAL_VALUE = {'Q'}


def value_options_of(parser, passthrough=()):
    """Return the options of a parser which take a value.

    The getopt-style walk needs to know which options carry a value so
    that the token after such an option is not mistaken for an operand.
    The parser's own registered actions are inspected: actions that
    take no value (flags, counters, help) are skipped, everything else
    contributes its short option letters and long option names. The
    'passthrough' letters are the options of the underlying command,
    which the parser does not register but the walk must still honor.

    Returns '(shorts, longs)': the set of the short option letters and
    the list of the long option names which take a value.
    """
    shorts = set(passthrough)
    longs = []
    for action in parser._actions:
        if action.nargs == 0:
            continue
        for option_string in action.option_strings:
            if option_string.startswith('--'):
                longs.append(option_string)
            else:
                shorts.add(option_string.lstrip('-'))
    return shorts, longs


def _option_consumes_next(token, value_options, long_value_options):
    """Whether the option token consumes the following token as its
    value.

    A long option with the value attached ('--option=value') does
    not; a short option consumes the next token when its last letter
    takes a value and the token carries no attached value ('-o value',
    '-qL value'), while the attached form ('-oValue') does not.
    """
    if token.startswith('--'):
        if '=' in token:
            return False
        return token in long_value_options
    if len(token) == 2:
        return token[1] in value_options
    # A cluster of short options; the first letter which takes a
    # value ends the option part of the token
    for position, letter in enumerate(token[1:]):
        if letter in value_options:
            return position + 2 == len(token)
    return False


def split_options_operands(tokens, value_options, long_value_options=(),
                           stop_at_operand=True):
    """Split an argument list into the options and the operands.

    The walk follows the getopt permutation: an option which takes a
    value keeps the next token as its value, and the tokens which are
    neither options nor option values are the operands, in the order
    they appear. With 'stop_at_operand' the walk ends at the first
    operand and the tokens after it are returned as the 'tail', in
    their places -- the arguments which follow the operand on the
    command line, such as the remote command of ssh, must not be
    permuted. Without it the walk covers the whole list, the way the
    multi-operand commands permute.

    The 'value_options' are the option letters which take a value and
    'long_value_options' the long option names; the set carries the
    options of the parser and the ones passed through to the command.
    The '--' marker ends the options; the next token is an operand
    even when it looks like an option.

    An option which requires a value and finds none raises ValueError;
    left valueless, the command would consume an operand as the value
    instead. The options with an optional value stand alone.
    """
    options = []
    operands = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == '--':
            index += 1
            # The tokens after the marker are the operands, even when
            # they look like options
            if stop_at_operand:
                if index < len(tokens):
                    operands.append(tokens[index])
                    index += 1
            else:
                operands.extend(tokens[index:])
                index = len(tokens)
            break
        if not token.startswith('-') or token == '-':
            operands.append(token)
            index += 1
            if stop_at_operand:
                break
            continue
        options.append(token)
        if _option_consumes_next(token, value_options,
                                 long_value_options):
            if index + 1 < len(tokens):
                index += 1
                options.append(tokens[index])
            elif token[-1] not in SSH_OPTIONS_WITH_OPTIONAL_VALUE:
                raise ValueError('the option ' + token
                                 + ' requires a value')
        index += 1
    tail = tokens[index:] if stop_at_operand else []
    return options, operands, tail


def split_host_path(operand):
    """Split an scp/sftp operand into the host part and the path.

    The operand grammar: '[[user@]host:]path'; the colon which
    separates the host from the path is the first colon, or the first
    colon after the closing bracket of a bracketed address. Returns
    '(None, operand)' when the operand carries no colon.
    """
    bracket_end = operand.find(']')
    if bracket_end != -1:
        candidate = operand.find(':', bracket_end)
    else:
        candidate = operand.find(':')
    if candidate == -1:
        return None, operand
    return operand[:candidate], operand[candidate + 1:]


def split_operand(operand):
    """Split an scp operand into the user, the host and the path.

    The scp operand grammar: '[[user@]host:]path'; the host part may
    carry a 'user@' prefix and a bracketed IPv6 address. Returns
    '(None, None, operand)' when the operand is a local path.
    """
    host_part, path = split_host_path(operand)
    if host_part is None:
        return None, None, operand
    user = None
    if '@' in host_part:
        user, _, host_part = host_part.partition('@')
    host = host_part.strip('[]')
    return user, host, path


def compose_options(pairs):
    """Return the argv list for ssh option pairs, without duplicates.

    The pairs are '(option, value)' tuples. The first occurrence of a
    pair wins, matching the way ssh treats its configuration; the
    result is the flat argv list the options compose into.
    """
    argv = []
    for pair in dict.fromkeys(pairs):
        argv.extend(pair)
    return argv


def translate_ssh_args(ssh_args):
    """Translate ssh arguments into the '-o' option pairs which the
    file-transfer commands accept for their ssh connections.

    '-J destination' becomes the ('-o', 'ProxyJump=destination') pair,
    '-o value' pairs pass through unchanged, and the options which
    configure port and packet forwards -- meaningless for a file
    transfer -- are dropped and reported. Returns the list of
    '(option, value)' pairs to add to the command, and the list of the
    dropped arguments as display strings.
    """
    tokens = (shlex.split(ssh_args)
              if isinstance(ssh_args, str) else list(ssh_args))
    translated = []
    dropped = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        letter = token[1] if len(token) > 1 else ''
        attached = len(token) > 2

        if token == '-J' or (letter == 'J' and attached):
            value = token[2:] if attached else (
                tokens[index + 1] if index + 1 < len(tokens) else None)
            if value is None:
                dropped.append(token)
                index += 1
                continue
            translated.append(('-o', 'ProxyJump=' + value))
            index += 1 if attached else 2
        elif token == '-o' or (letter == 'o' and attached):
            if attached:
                translated.append(('-o', token[2:]))
                index += 1
            elif index + 1 < len(tokens):
                translated.append(('-o', tokens[index + 1]))
                index += 2
            else:
                dropped.append(token)
                index += 1
        elif letter in SSH_OPTIONS_WITH_VALUE and attached:
            dropped.append(token)
            index += 1
        elif letter in SSH_OPTIONS_WITH_VALUE:
            dropped.append(token + ' ' + tokens[index + 1])
            index += 2
        else:
            dropped.append(token)
            index += 1
    return translated, dropped


def ssh_store_dir(project_path, view):
    """Return the directory of the view's isolated known_hosts store."""
    return os.path.join(project_path, '.debops', 'ssh', 'views', view)


def ssh_store_file(project_path, view):
    """Return the known_hosts file of the view's isolated store."""
    return os.path.join(ssh_store_dir(project_path, view), 'known_hosts')


def ensure_store_dir(store_file, project=None):
    """Create the directory chain of a view's known_hosts store.

    The directories from the '.debops/ssh' root of the project down
    to the store directory are created with the 0700 mode of the
    real '~/.ssh'; existing directories which are open to the group
    or the others are tightened to the same mode. A store outside of
    the project layout gets only its own directory ensured, without
    permission changes. When the project directory is given, the store
    path is refused when it resolves outside of it. Returns the store
    directory.
    """
    store_file = os.path.expanduser(store_file)
    if project is not None and not path_inside_project(store_file, project):
        raise ValueError('Refusing to create a known_hosts store outside '
                         'of the project directory: ' + store_file)
    store_dir = os.path.dirname(os.path.abspath(store_file))
    views_dir = os.path.dirname(store_dir)
    ssh_dir = os.path.dirname(views_dir)
    in_project = False
    if (os.path.basename(views_dir) == 'views'
            and os.path.basename(ssh_dir) == 'ssh'
            and os.path.basename(os.path.dirname(ssh_dir)) == '.debops'):
        # The '.debops' directory keeps the default permissions; only
        # the 'ssh' tree becomes private
        os.makedirs(os.path.dirname(ssh_dir), exist_ok=True)
        chain = [ssh_dir, views_dir, store_dir]
        in_project = True
    else:
        chain = [store_dir]
    for directory in chain:
        existed = os.path.isdir(directory)
        os.makedirs(directory, mode=0o700, exist_ok=True)
        if existed and in_project:
            mode = os.stat(directory).st_mode & 0o777
            if mode & 0o077:
                os.chmod(directory, 0o700)
    return store_dir


def render_ssh_drop_in(view):
    """Return the content of the view's SSH known_hosts drop-in.

    The drop-in is a TOML document which declares the project
    known_hosts mode and the view's isolated store through the Ansible
    configuration; the project directory merges it into the
    configuration tree, and the generated 'ansible.cfg' carries the
    store. The '${DEBOPS_PROJECT_PATH}' reference expands when the
    configuration is loaded and when the 'ansible.cfg' is parsed.
    """
    template = jinja2.Template(
            pkgutil.get_data(
                'debops',
                os.path.join('_data', 'templates', 'projectdir', 'modern',
                             'view', 'ssh.toml.j2')).decode('utf-8'),
            trim_blocks=True)
    return template.render(view_name=view,
                           store_path='.debops/ssh/views/' + view
                           + '/known_hosts')


def known_hosts_mode(project):
    """Return the known_hosts mode of the project's active view:
    'user' or 'project'."""
    views = project.config.raw.get('views', {})
    view_config = views.get(project.view, {})
    return view_config.get('ssh', {}).get('known_hosts', 'user')


def declared_known_hosts_store(project):
    """Return the known_hosts store declared in the view's ansible.cfg.

    The store is the value of the 'UserKnownHostsFile' option in the
    '[ssh_connection] ssh_args' of the generated configuration, written
    by the 'view-<view>-ssh.toml' configuration drop-in. The function
    returns None when the view does not declare a store; such a view
    stays on the user store while the 'project' mode is active.
    """
    try:
        ssh_args = project.ansible_cfg.get_option(
            'ssh_args', section='ssh_connection')
    except (configparser.NoOptionError, configparser.NoSectionError):
        return None
    for token in shlex.split(ssh_args):
        if token.startswith('UserKnownHostsFile='):
            return os.path.expanduser(token.split('=', 1)[1])
    return None


def known_hosts_store(project):
    """Return the known_hosts store of the active mode.

    The 'user' mode resolves to the user's default known_hosts file.
    The 'project' mode resolves to the store declared in the view's
    configuration and returns None when the view does not declare one.
    """
    mode = known_hosts_mode(project)
    if mode == 'project':
        return declared_known_hosts_store(project)
    return os.path.expanduser(USER_KNOWN_HOSTS_STORE)


# The connection options of the ssh connection plugin, each in the
# resolution order the plugin applies: the inventory variables over
# the environment over the option of the 'ansible.cfg'. The table
# carries the variable names, the environment variable and the
# configuration option of each connection parameter; the 'debops ssh'
# commands resolve them the same way the plugin does, so a connection
# composed by DebOps reaches the host the same way an Ansible
# connection does.
CONNECTION_OPTIONS = (
    # (key, variable names, environment name, ini section, ini key)
    ('destination', ('ansible_host', 'ansible_ssh_host'),
     None, None, None),
    ('user', ('ansible_user', 'ansible_ssh_user'),
     'ANSIBLE_REMOTE_USER', 'defaults', 'remote_user'),
    ('port', ('ansible_port', 'ansible_ssh_port'),
     'ANSIBLE_REMOTE_PORT', 'defaults', 'remote_port'),
    ('identity', ('ansible_private_key_file',
                  'ansible_ssh_private_key_file'),
     'ANSIBLE_PRIVATE_KEY_FILE', 'defaults', 'private_key_file'),
    ('ssh_args', ('ansible_ssh_args',),
     'ANSIBLE_SSH_ARGS', 'ssh_connection', 'ssh_args'),
    ('common_args', ('ansible_ssh_common_args',),
     'ANSIBLE_SSH_COMMON_ARGS', 'ssh_connection', 'ssh_common_args'),
    ('extra_args', ('ansible_ssh_extra_args',),
     'ANSIBLE_SSH_EXTRA_ARGS', 'ssh_connection', 'ssh_extra_args'),
    ('ssh_executable', ('ansible_ssh_executable',),
     'ANSIBLE_SSH_EXECUTABLE', 'ssh_connection', 'ssh_executable'),
    ('scp_executable', ('ansible_scp_executable',),
     'ANSIBLE_SCP_EXECUTABLE', 'ssh_connection', 'scp_executable'),
    ('scp_extra_args', ('ansible_scp_extra_args',),
     'ANSIBLE_SCP_EXTRA_ARGS', 'ssh_connection', 'scp_extra_args'),
    ('sftp_executable', ('ansible_sftp_executable',),
     'ANSIBLE_SFTP_EXECUTABLE', 'ssh_connection', 'sftp_executable'),
    ('sftp_extra_args', ('ansible_sftp_extra_args',),
     'ANSIBLE_SFTP_EXTRA_ARGS', 'ssh_connection', 'sftp_extra_args'),
    ('timeout', (), 'ANSIBLE_TIMEOUT', 'defaults', 'timeout'),
)


def resolve_host(project, host):
    """Return the connection parameters of an inventory host.

    The parameters come from the Ansible inventory, resolved with
    'ansible-inventory --host' the same way the Ansible runners resolve
    it, and follow the option resolution of the ssh connection plugin
    (:data:`CONNECTION_OPTIONS`): the inventory variables over the
    environment over the options of the 'ansible.cfg'. Returns a dict
    with the keys of :data:`CONNECTION_OPTIONS`; parameters which
    nothing defines are None.

    Raises ValueError when the host is not defined in the inventory of
    the project's view, ChildProcessError when the resolution cannot
    run.
    """
    binary = project.config.raw['binaries']['ansible-inventory']
    try:
        process = subprocess.run(
            [binary, '--host', host], cwd=project.path,
            env=project.environment(), capture_output=True, text=True)
    except OSError as error:
        raise ChildProcessError(
            'Cannot run the inventory resolution: ' + str(error))
    if process.returncode != 0:
        detail = (process.stderr.strip().splitlines() or [''])[-1]
        raise ValueError('Cannot resolve the host "' + host + '": '
                         + detail)
    try:
        variables = json.loads(process.stdout)
    except ValueError:
        raise ValueError('Cannot resolve the host "' + host + '": the '
                         'inventory returned no usable host variables')

    parameters = {}
    for key, var_names, env_name, section, ini_key in CONNECTION_OPTIONS:
        value = next((variables[name] for name in var_names
                      if variables.get(name)), None)
        if not value and env_name:
            value = os.environ.get(env_name)
        if not value and ini_key:
            try:
                value = project.ansible_cfg.get_option(ini_key,
                                                       section=section)
            except (configparser.NoOptionError,
                    configparser.NoSectionError):
                value = None
        parameters[key] = value
    destination = parameters['destination'] or host
    if destination.startswith('-'):
        raise ValueError(
            'The ansible_host of the host "' + host + '" looks like an '
            'SSH option instead of a host name or address: ' + destination)
    parameters['destination'] = destination
    return parameters


def resolve_patterns(project, patterns):
    """Expand Ansible inventory patterns into inventory host names.

    The patterns are expanded by the 'ansible' binary with
    '--list-hosts', the same pattern engine the runners use, so
    'all', the group names, the wildcards and the unions work. Returns
    '(hosts, unmatched)': the deduplicated host names in the order of
    the patterns, and the patterns which matched no host. Raises
    ValueError when the expansion fails, ChildProcessError when it
    cannot run.
    """
    binary = project.config.raw['binaries']['ansible']
    hosts = []
    unmatched = []
    for pattern in patterns:
        try:
            process = subprocess.run(
                [binary, pattern, '--list-hosts'], cwd=project.path,
                env=project.environment(), capture_output=True, text=True)
        except OSError as error:
            raise ChildProcessError(
                'Cannot run the pattern expansion: ' + str(error))
        if process.returncode != 0:
            detail = (process.stderr.strip().splitlines() or [''])[-1]
            raise ValueError('Cannot expand the pattern "' + pattern
                             + '": ' + detail)
        matched = []
        in_list = False
        for line in process.stdout.splitlines():
            if line.startswith('['):
                continue
            if not in_list:
                if line.lstrip().startswith('hosts ('):
                    in_list = True
                continue
            if not line.strip():
                continue
            if line.startswith((' ', '\t')):
                matched.append(line.strip())
            else:
                break
        for host in matched:
            if host not in hosts:
                hosts.append(host)
        if not matched:
            unmatched.append(pattern)
    return hosts, unmatched


def resolve_destination(project, name):
    """Resolve the destination of a single-host ssh suite command.

    The destination must be a literal inventory host name: the name is
    expanded the way the Ansible patterns are, and only a name which
    matches itself resolves -- 'all' and the other patterns are the
    domain of 'debops ssh rescan', even when they would match a single
    host. Raises ValueError when the name is not defined in the
    inventory or when it matches several hosts, ChildProcessError when
    the expansion cannot run.
    """
    hosts, _ = resolve_patterns(project, [name])
    if not hosts:
        raise ValueError('Cannot resolve the host "' + name + '": it is '
                         'not defined in the inventory of the view')
    if hosts == [name]:
        return resolve_host(project, name)
    if len(hosts) == 1:
        raise ValueError('The destination "' + name + '" is an '
                         'inventory pattern; a single host destination '
                         'is required')
    raise ValueError('The destination "' + name + '" matches '
                     + str(len(hosts)) + ' inventory hosts; a single '
                     'host destination is required')


def ssh_executable(project):
    """Return the ssh binary which the connections use.

    The 'ssh_executable' option of the view's 'ansible.cfg' overrides
    the configured default.
    """
    try:
        return project.ansible_cfg.get_option(
            'ssh_executable', section='ssh_connection')
    except (configparser.NoOptionError, configparser.NoSectionError):
        return None


def build_handoff_command(project, command, arguments, identity=None,
                          accept=False):
    """Build the command line of the '--' handoff invocation.

    The arguments which follow the '--' marker go to the command
    unchanged: the inventory is not consulted and the known_hosts
    store is not injected, so the command behaves like the plain
    binary. Only the options which DebOps itself interprets apply:
    the identity and the accept-new option.
    """
    binary = ssh_executable(project) if command == 'ssh' else None
    options = []
    if identity:
        options.extend(['-i', identity])
    if accept:
        options.extend(['-o', 'StrictHostKeyChecking=accept-new'])
    return [binary or project.config.raw['binaries'][command]] \
        + options + list(arguments)
