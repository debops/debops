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

The known_hosts store is selected by the 'ssh.known_hosts' option of
the view: the 'user' mode resolves to the user's default
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

from .dns import is_ip_address, key_fingerprint, lookup_sshfp, \
    ssh_fingerprint
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
    if known_hosts_mode(project) == 'project':
        store = known_hosts_store(project)
        if not store:
            raise ValueError(
                'The project known_hosts mode is active for the view, '
                'but the view does not declare a known_hosts store')
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
        configured_args = (parameters.get('ssh_args')
                           or project.ansible_cfg.get_option(
                               'ssh_args', section='ssh_connection'))
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


def scan_command(binaries, identifier, port=None, timeout=10):
    """Return the ssh-keyscan command line for a host identifier.

    The port of the host, when the resolution defines one, is passed
    to the scanner; ssh-keyscan writes the entries of the connections
    on non-default ports in the '[host]:port' form which the
    known_hosts matching requires.
    """
    command = [binaries['ssh-keyscan'], '-H', '-T', str(timeout)]
    if port:
        command.extend(['-p', str(port)])
    command.append(identifier)
    return command


def remove_command(binaries, identifier, store, port=None):
    """Return the ssh-keygen command line which removes the entries of
    a host identifier from a known_hosts store.

    The entries of a host on a non-default port carry the
    '[host]:port' form of the name, and only the qualified identifier
    matches them for the removal.
    """
    if port and str(port) != '22':
        identifier = '[' + identifier + ']:' + str(port)
    return [binaries['ssh-keygen'], '-R', identifier, '-f', store]


def rescan_actions(project, host, store, phases=('remove', 'scan'),
                   timeout=10):
    """Return the rescan actions of a host: '(actions, resolvable)'.

    'actions' is the list of '(phase, argv)' tuples -- the ssh-keygen
    removals and the ssh-keyscan scans of the host's identifiers, in
    the order the phases name them. 'resolvable' carries the
    identifiers the scan covers, which the classification uses for the
    SSHFP lookup. The connection port of the host comes from the same
    resolution the ssh command uses, so the scan hits the port the
    connections use.
    """
    try:
        parameters = resolve_host(project, host)
    except (ValueError, ChildProcessError):
        parameters = None
    port = (parameters or {}).get('port')
    identifiers = host_identifiers(project, host, parameters)
    binaries = project.config.raw['binaries']
    actions = []
    resolvable = []
    if 'remove' in phases:
        for identifier, _ in identifiers:
            actions.append(('remove', remove_command(
                binaries, identifier, store, port)))
    if 'scan' in phases:
        for identifier, can_scan in identifiers:
            if not can_scan:
                continue
            resolvable.append(identifier)
            actions.append(('scan', scan_command(
                binaries, identifier, port, timeout)))
    return actions, resolvable


def _confirmed_keys(host, fingerprints, confirm, details):
    """Return the keys to store after the confirmation callback.

    Without a callback the keys are stored as scanned; with one, the
    fingerprints are offered in the form ssh prints and the operator
    decides per host. The details list receives a note when the
    operator declined.
    """
    if confirm is None:
        return [key for algorithm, fingerprint, key in fingerprints]
    offered = []
    seen = set()
    for algorithm, digests, key in fingerprints:
        if digests[2] in seen:
            continue
        seen.add(digests[2])
        offered.append((ssh_fingerprint(digests[2]), key.split()[1]))
    if confirm(host, offered):
        return [key for algorithm, fingerprint, key in fingerprints]
    details.append('the scanned keys of the host were rejected by the '
                   'operator')
    return None


def _classify_scanned_keys(host, keys, resolvable, dns_mode, confirm,
                           details):
    """Decide which of the scanned keys of a host may be stored.

    With the 'dns' mode (the default), keys whose SSHFP fingerprints
    match the DNS records of the host are accepted automatically and
    keys which contradict the records refuse the whole host. Hosts
    without usable DNS records fall back to the 'confirm' callback,
    when one is given, or to the plain store operation. The
    'dns-verify' mode requires a DNSSEC-validating resolver to mark the
    answer as authenticated before a DNS match is trusted.

    Returns the list of keys to store, or None when the host must not
    be stored. The details list receives the report lines for the
    result.
    """
    fingerprints = []
    for key in keys:
        fields = key.split()
        if len(fields) < 3:
            continue
        algorithm, digests = key_fingerprint(fields[1], fields[2])
        if algorithm is not None:
            fingerprints.append((algorithm, digests, key))

    if dns_mode == 'no-dns':
        return keys, details
    if not fingerprints:
        # Keys of the types without SSHFP algorithm numbers -- the
        # FIDO key types among them, which OpenSSH does not map
        # either -- are refused, not stored without verification.
        details.append('the scanned keys could not be fingerprinted; '
                       'the host was not stored')
        return None, details

    candidates = [identifier for identifier in resolvable
                  if not is_ip_address(identifier)]
    records = None
    authenticated = False
    hostname = None
    for identifier in candidates:
        try:
            authenticated, records = lookup_sshfp(identifier)
        except Exception:
            continue
        if not records:
            continue
        if dns_mode == 'dns-verify' and not authenticated:
            continue
        hostname = identifier
        break
    if hostname is None:
        # No candidate produced usable SSHFP records.
        records = None

    if records is None:
        if dns_mode == 'dns-verify':
            details.append('the SSHFP records of the host could not be '
                           'verified through DNS; the host was not '
                           'stored')
            return None, details
        details.append('no SSHFP records found for the host')
        return _confirmed_keys(host, fingerprints, confirm, details), \
            details

    record_algorithms = {algorithm for algorithm, _, _ in records}

    def key_matches(algorithm, digests):
        """Whether any digest of the key appears in a record of the
        key's algorithm."""
        return any((algorithm, digest_type, digests[digest_type])
                   in records for digest_type in digests)

    matched = [key for algorithm, digests, key in fingerprints
               if key_matches(algorithm, digests)]
    contradicted = [key for algorithm, digests, key in fingerprints
                    if algorithm in record_algorithms
                    and not key_matches(algorithm, digests)]
    unverified = [key for algorithm, digests, key in fingerprints
                  if algorithm not in record_algorithms]
    if contradicted:
        details.append('the host keys do not match the SSHFP records of '
                       + hostname + '; the host was not stored')
        return None, details
    if not matched:
        details.append('none of the scanned keys matches the SSHFP '
                       'records of ' + hostname + '; the host was not '
                       'stored')
        return None, details
    if unverified:
        details.append(str(len(unverified)) + ' of the scanned keys have '
                       'no SSHFP records and were not stored')
    tier = 'DNSSEC-validated' if authenticated else 'DNS match'
    details.append('the host keys match the SSHFP records of '
                   + hostname + ' (' + tier + ')')
    return matched, details


def rescan_hosts(project, hosts, store=None, phases=('remove', 'scan'),
                 timeout=10, dns_mode='dns', confirm=None):
    """Cycle the known_hosts entries of the given hosts.

    For each host, its current host keys are scanned first and held in
    memory. With the 'dns' mode (the default), keys whose fingerprints
    match the SSHFP records of the host are accepted automatically,
    keys which contradict the published records are refused with a
    report, and hosts without usable DNS records fall back to the
    'confirm' callback, when one is given, or to the plain store
    operation. The 'dns-verify' mode additionally requires that a
    DNSSEC-validating resolver marked the DNS answer as authenticated.

    After the keys are accepted, the stale entries of all of the
    host's identifiers are removed from the store and the accepted
    keys are appended. The removal happens only when the scan produced
    keys to store: refused or contradictory keys keep the old trust
    intact, so a rescan never leaves a host without its known entries.
    The connections use the port of the host's resolution; the entries
    of the hosts on non-default ports carry the '[host]:port' form of
    the identifiers.

    A host which fails a phase is reported and the remaining
    hosts continue, so one host without a running sshd does not mask
    the results of the others.

    The 'confirm' callback, when given, is called with the host name
    and the list of '(fingerprint, key_type)' pairs of the keys which
    are about to be stored, and returns whether they should be stored.

    Returns a list of '(host, succeeded, message)' tuples, one per
    host; the message is empty when the host completed the requested
    phases. Raises ValueError when no store can be determined.
    """
    if store is None:
        store = known_hosts_store(project)
        # The user mode stores the keys in '~/.ssh/known_hosts', which
        # lies outside of the project by design; only the project mode
        # derives the store from configuration, so only that store is
        # contained.
        store_project = (project.path
                         if known_hosts_mode(project) == 'project'
                         else None)
    else:
        store_project = None
    if not store:
        raise ValueError(
            'Cannot rescan the hosts: the project known_hosts mode is '
            'active, but the view does not declare a known_hosts store')

    results = []
    for host in hosts:
        actions, resolvable = rescan_actions(project, host, store,
                                             phases, timeout)
        succeeded = True
        details = []
        store_keys = None
        scan_ok = None

        if 'scan' in phases:
            keys = []
            for phase, argv in actions:
                if phase != 'scan':
                    continue
                try:
                    process = subprocess.run(
                        argv, capture_output=True, text=True,
                        timeout=timeout + 5)
                except subprocess.TimeoutExpired:
                    succeeded = False
                    details.append('the key scan of ' + argv[-1]
                                   + ' timed out')
                    continue
                keys.extend(line for line in process.stdout.splitlines()
                            if line and not line.startswith('#')
                            and line not in keys)
            scan_ok = bool(keys)
            if keys:
                store_keys, scan_details = _classify_scanned_keys(
                    host, keys, resolvable, dns_mode, confirm, details)
                if store_keys is None:
                    succeeded = False
            elif resolvable:
                succeeded = False
                details.append('no host keys received from ' + host)
            else:
                succeeded = False
                details.append('no resolvable identifiers to scan for '
                               + host)

        # The stored entries of a host are only removed when the scan
        # produced keys to store, or when the removal was requested
        # explicitly without a scan phase. A failed scan and keys
        # which were refused keep the old trust intact: the removal
        # never leaves a host without its known entries.
        if scan_ok is None:
            remove_entries = 'remove' in phases
        else:
            remove_entries = bool(scan_ok and store_keys)
        if remove_entries and os.path.exists(store):
            for phase, argv in actions:
                if phase != 'remove':
                    continue
                process = subprocess.run(
                    argv, capture_output=True, text=True)
                if process.returncode != 0:
                    succeeded = False
                    detail = (process.stderr.strip().splitlines()
                              or [''])[-1]
                    details.append('cannot remove the entries of '
                                   + argv[2] + ': ' + detail)

        if store_keys:
            ensure_store_dir(store, store_project)
            with open(store, 'a') as handle:
                handle.write('\n'.join(store_keys) + '\n')
            os.chmod(store, 0o600)

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


def parse_config_stores(existing):
    """Return the project store paths listed in the managed block of
    an existing ssh configuration.

    The first path of the 'UserKnownHostsFile' line is the operator's
    own known_hosts file and is not part of the result: it stays the
    first entry of the line, because ssh appends newly accepted keys to
    the first file of the list.
    """
    if CONFIG_BLOCK_BEGIN not in existing or CONFIG_BLOCK_END not in existing:
        return []
    block = existing.split(CONFIG_BLOCK_BEGIN, 1)[1].split(
        CONFIG_BLOCK_END, 1)[0]
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith('UserKnownHostsFile'):
            stores = stripped.split()[1:]
            return stores[1:]
    return []


def render_config_snippet(project, project_stores=None):
    """Return the lines of the managed SSH client configuration block.

    In the 'project' mode the block adds the view's declared store as
    an additional known_hosts source next to the user's own, so that
    plain ssh outside of DebOps trusts the same hosts without writing
    into the project store. The 'project_stores' parameter carries the
    store paths of the other projects and views already present in the
    operator's configuration; the line lists them sorted, so the block
    stays identical no matter which project wrote it last. In the
    'user' mode there is nothing to configure and the block carries a
    note instead.
    """
    mode = known_hosts_mode(project)
    store = known_hosts_store(project)
    lines = [CONFIG_BLOCK_BEGIN]
    if mode == 'project' and store:
        if '\n' in store or '\r' in store:
            raise ValueError('The known_hosts store path contains newline '
                             'characters and cannot be written into an '
                             'SSH client configuration: ' + store)
        stores = sorted(set((project_stores or [])
                            + [unexpanduser(store)]))
        lines.append('Host *')
        lines.append('    UserKnownHostsFile '
                     + USER_KNOWN_HOSTS_STORE + ' '
                     + ' '.join(stores))
    else:
        lines.append('# The known_hosts mode of the view is set to "'
                     + mode + '"; there is nothing to configure.')
    lines.append(CONFIG_BLOCK_END)
    return lines


def write_config_snippet(project, path):
    """Write the managed block into an SSH client configuration file.

    The content between the managed markers is replaced; the content
    outside of the markers is preserved. A file without the markers
    gets the block appended. Store paths of other projects and views
    already listed in the block are kept, so projects do not overwrite
    each other's trust entries. The file is replaced atomically.
    Returns True when the file changed.
    """
    path = os.path.expanduser(path)
    existed = os.path.exists(path)
    existing = ''
    if existed:
        with open(path) as handle:
            existing = handle.read()
    existing_stores = parse_config_stores(existing)

    block = '\n'.join(render_config_snippet(project, existing_stores))
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
        mode = 0o600
        if existed:
            mode = os.stat(path).st_mode & 0o777
        temp_path = path + '.debops-new'
        with open(temp_path, 'w') as handle:
            handle.write(content)
        os.chmod(temp_path, mode)
        os.replace(temp_path, path)
    return changed
