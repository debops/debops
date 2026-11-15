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

# The ssh options which take a separate value argument, per the
# ssh(1) usage line. Used to walk argument lists where ssh options and
# operands mix.
SSH_OPTIONS_WITH_VALUE = set('BbcDEeFIiJLlMmOoQRSVWw')

# The sftp options which take a separate value argument, per the
# sftp(1) usage line.
SFTP_OPTIONS_WITH_VALUE = set('BbcDFiJlRoPRsS')


def split_options_operand(tokens, value_options, long_value_options=()):
    """Split an argument list into the options and the first operand.

    The walk follows the getopt permutation: an option which takes a
    value keeps the next token as its value, and the first token which
    is neither an option nor an option value is the operand. The
    tokens after the operand are returned as the tail, for the
    arguments which follow the operand on the command line. The '--'
    marker ends the options; the next token is the operand even when
    it looks like an option.

    The 'value_options' are the option letters which take a value and
    'long_value_options' the long option names; the set carries the
    options of the parser and the ones passed through to the command.
    """
    head = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == '--':
            index += 1
            break
        if not token.startswith('-') or token == '-':
            break
        head.append(token)
        letter = token[1] if len(token) > 1 else ''
        takes_value = ((letter in value_options and len(token) == 2)
                       or token in long_value_options)
        if takes_value and index + 1 < len(tokens):
            index += 1
            head.append(tokens[index])
        index += 1
    if index < len(tokens):
        return head, tokens[index], tokens[index + 1:]
    return head, None, []


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


def resolve_host(project, host):
    """Return the connection parameters of an inventory host.

    The parameters come from the Ansible inventory, resolved with
    'ansible-inventory --host' the same way the Ansible runners resolve
    it. Returns a dict with the keys 'destination', 'user', 'port',
    'identity', 'common_args' and 'extra_args'; parameters the
    inventory does not define are None.

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

    user = variables.get('ansible_user')
    if user is None:
        # Ansible semantics: the inventory connection variable wins over
        # the configuration, and the ANSIBLE_REMOTE_USER environment
        # overrides the 'remote_user' option of the configuration.
        try:
            remote_user = project.ansible_cfg.get_option(
                'remote_user', section='defaults')
        except (configparser.NoOptionError, configparser.NoSectionError):
            remote_user = None
        user = (os.environ.get('ANSIBLE_REMOTE_USER') or remote_user)
    destination = variables.get('ansible_host') or host
    if destination.startswith('-'):
        raise ValueError(
            'The ansible_host of the host "' + host + '" looks like an '
            'SSH option instead of a host name or address: ' + destination)
    return {
        'destination': destination,
        'user': user,
        'port': variables.get('ansible_port'),
        'identity': variables.get('ansible_ssh_private_key_file'),
        'common_args': variables.get('ansible_ssh_common_args'),
        'extra_args': variables.get('ansible_ssh_extra_args'),
    }


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
