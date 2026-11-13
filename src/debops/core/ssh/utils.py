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

logger = logging.getLogger(__name__)

USER_KNOWN_HOSTS_STORE = '~/.ssh/known_hosts'

# The ssh options which take a separate value argument, per the
# ssh(1) usage line. Used to walk argument lists where ssh options and
# operands mix.
SSH_OPTIONS_WITH_VALUE = set('BbcDEeFIiJLlMmOoQRSVWw')


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


def translate_ssh_args(ssh_args):
    """Translate ssh arguments into the '-o' options which the
    file-transfer commands accept for their ssh connections.

    '-J destination' becomes '-o ProxyJump=destination', '-o value'
    pairs pass through unchanged, and the options which configure port
    and packet forwards -- meaningless for a file transfer -- are
    dropped and reported. Returns '(translated, dropped)'.
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
            translated.append('-o ProxyJump=' + value)
            index += 1 if attached else 2
        elif token == '-o' or (letter == 'o' and attached):
            if attached:
                translated.append(token)
                index += 1
            elif index + 1 < len(tokens):
                translated.append('-o ' + tokens[index + 1])
                index += 2
            else:
                dropped.append(token)
                index += 1
        elif letter in SSH_OPTIONS_WITH_VALUE and attached:
            dropped.append(token)
            index += 1
        elif letter in SSH_OPTIONS_WITH_VALUE:
            dropped.extend(tokens[index:index + 2])
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


def ensure_store_dir(store_file):
    """Create the directory chain of a view's known_hosts store.

    The directories from the '.debops/ssh' root of the project down
    to the store directory are created with the 0700 mode of the
    real '~/.ssh'; existing directories which are open to the group
    or the others are tightened to the same mode. A store outside of
    the project layout gets only its own directory ensured. Returns
    the store directory.
    """
    store_file = os.path.expanduser(store_file)
    store_dir = os.path.dirname(os.path.abspath(store_file))
    views_dir = os.path.dirname(store_dir)
    ssh_dir = os.path.dirname(views_dir)
    if (os.path.basename(views_dir) == 'views'
            and os.path.basename(ssh_dir) == 'ssh'
            and os.path.basename(os.path.dirname(ssh_dir)) == '.debops'):
        # The '.debops' directory keeps the default permissions; only
        # the 'ssh' tree becomes private
        os.makedirs(os.path.dirname(ssh_dir), exist_ok=True)
        chain = [ssh_dir, views_dir, store_dir]
    else:
        chain = [store_dir]
    for directory in chain:
        os.makedirs(directory, mode=0o700, exist_ok=True)
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
    """Return the configured known_hosts mode: 'user' or 'project'."""
    return project.config.raw.get('ssh', {}).get('known_hosts', 'user')


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
    return {
        'destination': variables.get('ansible_host') or host,
        'user': variables.get('ansible_user'),
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
