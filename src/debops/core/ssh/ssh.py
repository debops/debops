# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The ssh command line and the 'debops ssh' subcommand machinery.

The connection parameters of an inventory host are resolved by
:mod:`debops.core.ssh.utils`, which also owns the known_hosts store
selection shared with 'debops scp'. This module builds the ssh command
line, cycles the known_hosts entries for 'debops ssh rescan', and
renders the SSH client configuration snippet for the
outside-of-DebOps path.

The known_hosts store is selected by the 'ssh.known_hosts'
configuration option: the 'user' mode resolves to the user's default
known_hosts file, the 'project' mode to the store declared in the
view's 'ansible.cfg' through the 'UserKnownHostsFile' option of the
'[ssh_connection] ssh_args' -- the value the 'view-<view>-ssh.toml'
configuration drop-in writes. A view which does not declare a store
stays on the user store while the 'project' mode is active.
"""

import configparser
import getpass
import logging
import os
import shlex
import socket
import subprocess

from .utils import (USER_KNOWN_HOSTS_STORE, ensure_store_dir,
                    known_hosts_mode, known_hosts_store, resolve_host,
                    ssh_executable)
from ..utils import unexpanduser

logger = logging.getLogger(__name__)


CONFIG_BLOCK_BEGIN = '# BEGIN debops ssh managed block'
CONFIG_BLOCK_END = '# END debops ssh managed block'


def split_destination(destination):
    """Split an ssh destination into the explicit user, host and port.

    The ssh destination grammar: '[user@]hostname' or the URI
    'ssh://[user@]hostname[:port]' -- the URI form requires brackets
    around an IPv6 hostname when a port follows. Forms ssh itself does
    not support, such as 'hostname:port' in the plain form, pass
    through verbatim and fail the same way ssh fails on them.

    Returns '(user, host, port)'; the user and the port are None when
    the destination does not carry them. The host is the part the
    inventory lookup uses.
    """
    if destination.startswith('ssh://'):
        remainder = destination[len('ssh://'):]
        user = None
        if '@' in remainder:
            user, _, remainder = remainder.partition('@')
        port = None
        if ':' in remainder:
            hostname, _, port = remainder.rpartition(':')
            if not port.isdigit():
                # Not a port; the whole remainder is the hostname
                hostname, port = remainder, None
        else:
            hostname = remainder
        return user, hostname.strip('[]'), port
    user = None
    host = destination
    if '@' in host:
        user, _, host = host.partition('@')
    return user, host, None


def build_ssh_command(project, host, parameters=None, user=None, port=None,
                      identity=None, accept=False, ssh_args=None,
                      options=None):
    """Build the ssh command line for 'debops ssh <host>'.

    The resolved inventory parameters fill the command, with the
    explicit options and the destination's own 'user@host' or URI parts
    taking precedence over the inventory values, the way ssh precedence
    works. The '[ssh_connection] ssh_args' of the
    view's ansible.cfg and the connection extras of the host are
    composed before the destination; the caller's 'ssh_args' follow
    the destination, exactly where ssh itself places them -- the
    remote command and its arguments.
    """
    if parameters is None:
        parameters = {}
    command = [ssh_executable(project)
               or project.config.raw['binaries']['ssh']]

    effective_user = user or parameters.get('user') or getpass.getuser()
    command.extend(['-l', effective_user])
    effective_port = port or parameters.get('port')
    if effective_port:
        command.extend(['-p', str(effective_port)])
    effective_identity = identity or parameters.get('identity')
    if effective_identity:
        command.extend(['-i', effective_identity])

    try:
        configured_args = project.ansible_cfg.get_option(
            'ssh_args', section='ssh_connection')
    except (configparser.NoOptionError, configparser.NoSectionError):
        configured_args = None
    if configured_args:
        command.extend(shlex.split(configured_args))
    for key in ('common_args', 'extra_args'):
        value = parameters.get(key)
        if value:
            command.extend(shlex.split(value))

    command.extend(options or [])
    if accept:
        command.extend(['-o', 'StrictHostKeyChecking=accept-new'])
    command.append(parameters.get('destination') or host)
    command.extend(ssh_args or [])
    return command


def host_identifiers(project, host, parameters=None):
    """Return the identifiers of a host's known_hosts entries.

    Returns a list of '(identifier, resolvable)' tuples: the given host
    name, the inventory hostname and the connection destination, plus
    every IPv4 and IPv6 address the names resolve to. An identifier
    which resolves can be scanned for host keys; a name which does not
    resolve contributes itself with 'resolvable' set to False -- its
    stale entries can still be removed, but there is nothing to scan.
    """
    if parameters is None:
        try:
            parameters = resolve_host(project, host)
        except (ValueError, ChildProcessError):
            parameters = None
    names = [host]
    destination = (parameters or {}).get('destination')
    if destination and destination not in names:
        names.append(destination)

    identifiers = []
    seen = set()

    def add(identifier, resolvable):
        if identifier not in seen:
            seen.add(identifier)
            identifiers.append((identifier, resolvable))

    for name in names:
        resolvable = False
        try:
            addresses = [info[4][0]
                         for info in socket.getaddrinfo(name, None)]
        except socket.gaierror:
            addresses = []
        for address in addresses:
            add(address, True)
            resolvable = True
        add(name, resolvable)
    return identifiers


def rescan_hosts(project, hosts, store=None, phases=('remove', 'scan'),
                 timeout=10):
    """Cycle the known_hosts entries of the given hosts.

    For each host, the stale entries of all of its identifiers are
    removed from the store and its current host keys are scanned and
    appended. A host which fails a phase is reported and the remaining
    hosts continue, so one host without a running sshd does not mask
    the results of the others.

    Returns a list of '(host, succeeded, message)' tuples, one per
    host; the message is empty when the host completed the requested
    phases. Raises ValueError when no store can be determined.
    """
    if store is None:
        store = known_hosts_store(project)
        store_project = project.path
    else:
        store_project = None
    if not store:
        raise ValueError(
            'Cannot rescan the hosts: the project known_hosts mode is '
            'active, but the view does not declare a known_hosts store')

    binaries = project.config.raw['binaries']
    results = []
    for host in hosts:
        identifiers = host_identifiers(project, host)
        names = [identifier for identifier, resolvable in identifiers]
        resolvable = [identifier for identifier, can_scan in identifiers
                      if can_scan]
        succeeded = True
        details = []

        if 'remove' in phases:
            if os.path.exists(store):
                for identifier in names:
                    process = subprocess.run(
                        [binaries['ssh-keygen'], '-R', identifier,
                         '-f', store],
                        capture_output=True, text=True)
                    if process.returncode != 0:
                        succeeded = False
                        detail = (process.stderr.strip().splitlines()
                                  or [''])[-1]
                        details.append('cannot remove the entries of '
                                       + identifier + ': ' + detail)
            # A store which does not exist yet has no stale entries to
            # remove; the scan phase creates it

        if 'scan' in phases:
            keys = []
            for identifier in resolvable:
                try:
                    process = subprocess.run(
                        [binaries['ssh-keyscan'], '-H', '-T', str(timeout),
                         identifier],
                        capture_output=True, text=True,
                        timeout=timeout + 5)
                except subprocess.TimeoutExpired:
                    succeeded = False
                    details.append('the key scan of ' + identifier
                                   + ' timed out')
                    continue
                keys.extend(line for line in process.stdout.splitlines()
                            if line and not line.startswith('#'))
            if keys:
                ensure_store_dir(store, store_project)
                with open(store, 'a') as handle:
                    handle.write('\n'.join(keys) + '\n')
                os.chmod(store, 0o600)
            elif resolvable:
                succeeded = False
                details.append('no host keys received from ' + host)
            else:
                succeeded = False
                details.append('no resolvable identifiers to scan for '
                               + host)

        message = '; '.join(details)
        results.append((host, succeeded, message))
        if succeeded:
            logger.notice(
                'Refreshed the known_hosts entries of the host '
                '"' + host + '" in ' + store,
                extra={'allow': ['stderr', 'syslog']})
        else:
            logger.error(
                'Cannot refresh the known_hosts entries of the host '
                '"' + host + '": ' + message,
                extra={'allow': 'syslog'})
    return results


def render_config_snippet(project):
    """Return the lines of the managed SSH client configuration block.

    In the 'project' mode the block adds the view's declared store as
    an additional known_hosts source next to the user's own, so that
    plain ssh outside of DebOps trusts the same hosts without writing
    into the project store. In the 'user' mode there is nothing to
    configure and the block carries a note instead.
    """
    mode = known_hosts_mode(project)
    store = known_hosts_store(project)
    lines = [CONFIG_BLOCK_BEGIN]
    if mode == 'project' and store:
        lines.append('Host *')
        lines.append('    UserKnownHostsFile '
                     + USER_KNOWN_HOSTS_STORE + ' '
                     + unexpanduser(store))
    else:
        lines.append('# The ssh.known_hosts option is set to "'
                     + mode + '"; there is nothing to configure.')
    lines.append(CONFIG_BLOCK_END)
    return lines


def write_config_snippet(project, path):
    """Write the managed block into an SSH client configuration file.

    The content between the managed markers is replaced; the content
    outside of the markers is preserved. A file without the markers
    gets the block appended. Returns True when the file changed.
    """
    path = os.path.expanduser(path)
    block = '\n'.join(render_config_snippet(project))
    existed = os.path.exists(path)
    existing = ''
    if existed:
        with open(path) as handle:
            existing = handle.read()

    if CONFIG_BLOCK_BEGIN in existing and CONFIG_BLOCK_END in existing:
        head = existing.split(CONFIG_BLOCK_BEGIN, 1)[0]
        tail = existing.split(CONFIG_BLOCK_END, 1)[1]
        content = head + block + '\n' + tail.lstrip('\n')
    elif existing.strip():
        content = existing.rstrip('\n') + '\n\n' + block + '\n'
    else:
        content = block + '\n'

    changed = content != existing
    if changed:
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent)
            os.chmod(parent, 0o700)
        with open(path, 'w') as handle:
            handle.write(content)
        if not existed:
            os.chmod(path, 0o600)
    return changed
