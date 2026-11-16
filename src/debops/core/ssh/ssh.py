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

import logging
import os
import shlex
import socket
import subprocess
import tempfile

from .dns import (blob_fingerprint, is_ip_address, is_link_local,
                  key_fingerprint, lookup_sshfp, ssh_fingerprint)
from .store import (USER_KNOWN_HOSTS_STORE, entry_key_material,
                    ensure_store_dir, known_hosts_mode, known_hosts_option,
                    known_hosts_store, quote_store_path, require_store)
from .utils import (JumpRewriter, resolve_host, ssh_executable,
                    transfer_executable, translate_ssh_args,
                    without_known_hosts_options)
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
            # ssh splits the user at the last '@' of the destination
            user, _, remainder = remainder.rpartition('@')
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
        user, _, host = host.rpartition('@')
    return user, host, None


def build_ssh_command(project, host, parameters, user=None, port=None,
                      identity=None, accept=False, ssh_args=None,
                      options=None):
    """Build the ssh command line for 'debops ssh <host>'.

    The resolved inventory parameters fill the command. The explicit
    options and the destination's own 'user@host' or URI parts take
    precedence over the inventory values, the way ssh precedence
    works. The resolved 'ssh_args' and the connection extras of the
    host are composed before the destination. The caller's 'ssh_args'
    follow the destination, exactly where ssh itself places them --
    the remote command and its arguments. The flags DebOps composes
    come before the resolved arguments, so an explicit '-p' beats a
    port inside 'ssh_args' -- the opposite order of the ssh connection
    plugin, which places its '-o' options after 'ssh_args'.

    In the project known_hosts mode the store of the view is injected
    as the first ssh option: ssh applies the first obtained value of
    an option, so no resolved argument can bypass the store of the
    view. The 'UserKnownHostsFile' options of the resolved arguments
    are dropped, so the command carries the store declaration once.

    The structured jump options of the connection are rewritten into
    explicit 'ProxyCommand' options which carry the store, the host
    key checking mode and the connection timeout into the jump
    process, which OpenSSH builds without inheriting the options of
    the parent. A comma-separated jump chain is left to ssh
    unchanged.

    Without a user from the options or the inventory, no '-l' is
    composed: ssh picks the user from the operator's SSH client
    configuration, the way plain ssh does. The connection timeout of
    the resolution applies like it does for the Ansible connections.
    An earlier '-o ConnectTimeout' of the composed command wins.
    """
    command = [(parameters.get('ssh_executable') or ssh_executable(project)
                or project.config.raw['binaries']['ssh'])]
    store, inject = require_store(project)
    if inject:
        command.extend(['-o', known_hosts_option(store)])
    if accept:
        # Before the resolved arguments: ssh applies the first
        # obtained value of an option, and an explicit '--accept' must
        # not be defeated by a StrictHostKeyChecking in the resolved
        # arguments
        command.extend(['-o', 'StrictHostKeyChecking=accept-new'])

    # The options the jump process runs with: the same trust and mode
    # options the destination leg carries, and the connection timeout
    # of the resolution, which bounds the connect of the jump leg
    child_pairs = []
    if inject:
        child_pairs.append(('-o', known_hosts_option(store)))
    if accept:
        child_pairs.append(('-o', 'StrictHostKeyChecking=accept-new'))
    child_pairs.append(
        ('-o', 'ConnectTimeout=' + str(parameters.get('timeout') or 10)))
    rewriter = JumpRewriter(child_pairs)

    option_tokens = list(options or [])
    configured_args = parameters.get('ssh_args')
    configured_tokens = shlex.split(configured_args) \
        if configured_args else []
    if inject:
        configured_tokens = without_known_hosts_options(configured_tokens)
    common_tokens = shlex.split(parameters.get('common_args') or '')
    extra_tokens = shlex.split(parameters.get('extra_args') or '')
    # The scan of every argument group runs before the rewriting: the
    # config file and the verbosity flags of the parent command line
    # must be known when the first ProxyCommand value is built, no
    # matter which group carries them
    for group in (option_tokens, configured_tokens, common_tokens,
                  extra_tokens):
        rewriter.scan(group)

    if option_tokens:
        # The options the operator typed directly precede everything
        # DebOps derives: ssh applies the first obtained value of an
        # option, and an '-l' or '-o' the operator typed must not be
        # defeated by the inventory or the view
        command.extend(rewriter.rewrite_tokens(option_tokens))
    effective_user = user or parameters.get('user')
    if effective_user:
        command.extend(['-l', effective_user])
    effective_port = port or parameters.get('port')
    if effective_port:
        command.extend(['-p', str(effective_port)])
    effective_identity = identity or parameters.get('identity')
    if effective_identity:
        command.extend(['-i', effective_identity])
    command.extend(rewriter.rewrite_tokens(configured_tokens))
    command.extend(rewriter.rewrite_tokens(common_tokens))
    command.extend(rewriter.rewrite_tokens(extra_tokens))

    timeout = parameters.get('timeout')
    if timeout is None:
        timeout = 10
    if not any(token.startswith('ConnectTimeout=')
               or token.startswith('-oConnectTimeout=')
               for token in command):
        command.extend(['-o', 'ConnectTimeout=' + str(timeout)])
    rewriter.check()
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
    Link-local addresses without the interface scope are not scannable
    and contribute removal-only identifiers as well.
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
            if is_link_local(address):
                # A link-local address without the interface scope
                # cannot be scanned; its stale entries can still be
                # removed
                add(address, False)
                continue
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


def connection_jump_names(parameters):
    """Return the jump hosts of a host's resolved connection options,
    in the order the connections traverse them.

    The hops of the '-J' and 'ProxyJump=' options of 'ssh_args' and
    the connection extras. A bastion hidden inside a 'ProxyCommand'
    cannot be discovered: the command is an arbitrary shell pipeline.
    """
    names = []
    for value in (parameters.get('ssh_args'),
                  parameters.get('common_args'),
                  parameters.get('extra_args')):
        if not value:
            continue
        translated, dropped = translate_ssh_args(value)
        for pair in translated:
            if isinstance(pair, tuple) and pair[0] == '-o' \
                    and pair[1].startswith('ProxyJump='):
                for hop in pair[1][len('ProxyJump='):].split(','):
                    if hop and hop not in names:
                        names.append(hop)
    return names


def _hop_endpoint(hop):
    """Split a ProxyJump hop into the host, the port and the
    known_hosts identifier the connections verify the hop under."""
    name = hop
    if '@' in name:
        name = name.rpartition('@')[2]
    port = None
    if name.startswith('[') and ']' in name:
        host, _, remainder = name[1:].partition(']')
        name = host
        if remainder.startswith(':') and remainder[1:].isdigit():
            port = remainder[1:]
    elif ':' in name:
        name, _, candidate = name.rpartition(':')
        if candidate.isdigit():
            port = candidate
        else:
            name = hop
    identifier = name
    if port and port != '22':
        identifier = '[' + name + ']:' + port
    return name, port, identifier


def _collect_through_connection(project, parameters, store, timeout,
                                details):
    """Collect the host keys of a host whose connection traverses a
    jump host, by running the connection itself with a throwaway
    known_hosts file.

    The connection authenticates the first jump host against the
    entries the store already holds for it, and the key of the
    negotiated exchange with the destination is collected into the
    throwaway whether or not the authentication succeeds -- the
    connection runs with BatchMode and a remote command which does
    nothing. Returns the collected key lines which do not belong to
    the jump, or None when the jump's key is not known to the store
    or the connection could not be established.
    """
    parameters = parameters or {}
    jumps = connection_jump_names(parameters)
    if not jumps:
        return None
    _, _, identifier = _hop_endpoint(jumps[0])
    binaries = project.config.raw['binaries']
    probe = subprocess.run(
        [binaries['ssh-keygen'], '-F', identifier, '-f', store],
        capture_output=True, text=True)
    jump_entries = [line for line in probe.stdout.splitlines() if line]
    if not jump_entries:
        details.append('the key of the jump host ' + identifier
                       + ' is not known to the store; scan the jump '
                         'host first')
        return None
    store_dir = os.path.dirname(store) or '.'
    descriptor, throwaway = tempfile.mkstemp(
        dir=store_dir, prefix='known_hosts.scan.')
    with os.fdopen(descriptor, 'w') as handle:
        handle.write('\n'.join(jump_entries) + '\n')
    os.chmod(throwaway, 0o600)
    try:
        # The options the jump process runs with are the ones of the
        # parent command: the throwaway known_hosts file with the
        # pre-seeded entries of the jump, the BatchMode which keeps the
        # scan from stopping at a prompt, and the connection timeout
        # which bounds the connect of the jump leg
        rewriter = JumpRewriter([
            ('-o', 'UserKnownHostsFile=' + quote_store_path(throwaway)),
            ('-o', 'BatchMode=yes'),
            ('-o', 'StrictHostKeyChecking=accept-new'),
            ('-o', 'ConnectTimeout=' + str(timeout)),
        ])
        command = [(parameters.get('ssh_executable')
                    or ssh_executable(project)
                    or binaries['ssh']),
                   '-o', 'BatchMode=yes',
                   '-o', 'UserKnownHostsFile=' + throwaway,
                   '-o', 'StrictHostKeyChecking=accept-new']
        port = parameters.get('port')
        if port:
            command.extend(['-p', str(port)])
        groups = [shlex.split(value)
                  for value in (parameters.get('ssh_args'),
                                parameters.get('common_args'),
                                parameters.get('extra_args'))
                  if value]
        for group in groups:
            rewriter.scan(group)
        for group in groups:
            command.extend(rewriter.rewrite_tokens(group))
        try:
            rewriter.check()
        except ValueError as error:
            details.append(str(error))
            return None
        command.append(parameters.get('destination') or '')
        command.append('true')
        try:
            subprocess.run(command, capture_output=True, text=True,
                           timeout=timeout + 5)
        except subprocess.TimeoutExpired:
            details.append('the connection to the host timed out')
            return None
        lines = [line for line in open(throwaway).read().splitlines()
                 if line and line not in jump_entries]
        return lines or None
    finally:
        if os.path.exists(throwaway):
            os.unlink(throwaway)


def rescan_actions(project, host, store, phases=('remove', 'scan'),
                   timeout=10, parameters=None):
    """Return the rescan actions of a host: '(actions, resolvable)'.

    'actions' is the list of '(phase, argv)' tuples -- the ssh-keygen
    removals and the ssh-keyscan scans of the host's identifiers, the
    removals first: the scanned keys are appended after the removals,
    by the rescan itself from memory and by an external consumer of
    the actions from the scan output -- in the opposite order the
    removal would take down the freshly appended entries too, since
    it removes every entry of the identifier. 'resolvable' carries
    the identifiers the scan covers, for the SSHFP lookup of the
    classification. The connection port of the host comes from the
    same resolution the ssh command uses, so the scan hits the port
    the connections use. The resolved parameters can be handed in
    when the caller has already resolved them.
    """
    if parameters is None:
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


def _offered_fingerprints(keys):
    """Return the '(fingerprint, key_type)' pairs of the scanned keys
    for a confirmation offer.

    Every key whose blob decodes is offered, the types without SSHFP
    algorithm numbers among them: their fingerprints exist the same
    way, only the DNS comparison does not apply to them. The first
    key of each digest wins, so a scan which reports the same key
    under several identifiers offers it once.
    """
    offered = []
    seen = set()
    for key in keys:
        fields = key.split()
        if len(fields) < 3:
            continue
        digest = blob_fingerprint(fields[2])
        if digest is None or digest in seen:
            continue
        seen.add(digest)
        offered.append((ssh_fingerprint(digest), fields[1]))
    return offered


def _confirmed_keys(host, fingerprints, confirm, details):
    """Return the keys to store after the confirmation callback.

    Without a callback the keys are stored as scanned; with one, the
    fingerprints are offered in the form ssh prints and the operator
    decides per host. The details list receives a note when the
    operator declined.
    """
    if confirm is None:
        return [key for algorithm, fingerprint, key in fingerprints]
    offered = _offered_fingerprints(
        [key for algorithm, digest, key in fingerprints])
    if confirm(host, offered):
        return [key for algorithm, fingerprint, key in fingerprints]
    details.append('the scanned keys of the host were rejected by the '
                   'operator')
    return None


def _classify_scanned_keys(host, keys, resolvable, dns_mode, confirm,
                           details, trust_unsigned=True):
    """Decide which of the scanned keys of a host may be stored.

    With the 'dns' mode (the default), keys whose SSHFP fingerprints
    match DNSSEC-validated records of the host are accepted
    automatically and keys which contradict the records refuse the
    whole host. A match against records which the resolver did not
    authenticate grants no trust: with 'trust_unsigned' the keys fall
    back to the 'confirm' callback, when one is given, or to the plain
    store operation, and without it the host is not stored. The
    'dns-verify' mode requires a DNSSEC-validating resolver to mark the
    answer as authenticated before a DNS match is trusted; an
    unauthenticated match and a host without records are refused
    unless the 'confirm' callback accepts them. The 'no-dns' mode
    stores the keys as scanned; with the 'confirm' callback every
    store is gated on the operator's decision.

    The confirmation callback never overrides the refusal of the keys
    which contradict the published records of the host.

    A lookup failure of the resolver other than the absence of records
    refuses the host: a SERVFAIL of a validating resolver, a timeout
    or a broken installation must not read as 'no records'.

    Returns the list of keys to store, or None when the host must not
    be stored, with the DNS verdict of the classification: 'validated'
    for the DNSSEC-authenticated match, 'unsigned' for a match the
    resolver did not authenticate, 'no-records' for a host without
    records and 'not-checked' for the 'no-dns' mode; None accompanies
    a refused host. The details list receives the report lines for
    the result.
    """
    fingerprints = []
    unparsable = set()
    for key in keys:
        fields = key.split()
        if len(fields) < 3:
            unparsable.add(fields[1] if len(fields) > 1 else 'malformed')
            continue
        algorithm, digests = key_fingerprint(fields[1], fields[2])
        if algorithm is not None:
            fingerprints.append((algorithm, digests, key))
        else:
            unparsable.add(fields[1])

    if dns_mode == 'no-dns':
        if confirm is None:
            return keys, details, 'not-checked'
        # The raw store contract of the mode stays: the confirmation
        # gates the store, and a confirmation stores the keys as
        # scanned, the fingerprints of the offer being the operator's
        # thing to check
        if confirm(host, _offered_fingerprints(keys)):
            return keys, details, 'not-checked'
        details.append('the scanned keys of the host were rejected by '
                       'the operator')
        return None, details, None
    if not fingerprints:
        # Keys of the types without SSHFP algorithm numbers -- the
        # FIDO key types among them, which OpenSSH does not map
        # either -- are refused, not stored without verification.
        details.append('the scanned keys could not be fingerprinted; '
                       'the host was not stored')
        return None, details, None
    if unparsable:
        # A scan which offers unverifiable keys alongside verifiable
        # ones cannot be trusted for the unverifiable part: the key
        # offer of a connection carries public keys their holder does
        # not need to own. The host is refused; its stored entries
        # stay.
        details.append('the scan produced keys of the types without '
                       'SSHFP algorithm numbers ('
                       + ', '.join(sorted(unparsable))
                       + '); the host was not stored')
        return None, details, None

    candidates = [identifier for identifier in resolvable
                  if not is_ip_address(identifier)]
    verified = None
    unsigned = None
    for identifier in candidates:
        try:
            authenticated, found = lookup_sshfp(identifier)
        except Exception as error:
            # Only the absence of records falls back to the operator's
            # decision; a resolver which cannot answer the question --
            # SERVFAIL of a validating resolver, a timeout, a broken
            # installation -- must not read as 'no records', or the
            # keys of a signed zone would be stored on the failure
            details.append('the SSHFP lookup of ' + identifier
                           + ' failed: ' + str(error)
                           + '; the host was not stored')
            return None, details, None
        if not found:
            continue
        if authenticated:
            # An authenticated answer is the strongest evidence the
            # resolver can offer; a later candidate cannot improve on
            # it
            verified = (identifier, found)
            break
        if unsigned is None:
            unsigned = (identifier, found)
    if verified is not None:
        hostname, records = verified
        authenticated = True
    elif unsigned is not None:
        hostname, records = unsigned
        authenticated = False
    else:
        # No candidate produced usable SSHFP records.
        hostname, records, authenticated = None, None, False

    if records is None:
        if dns_mode == 'dns-verify':
            if confirm is None:
                details.append('the SSHFP records of the host could not '
                               'be verified through DNS; the host was '
                               'not stored')
                return None, details, None
            stored = _confirmed_keys(host, fingerprints, confirm, details)
            if stored is not None:
                details.append('no DNSSEC-validated SSHFP records were '
                               'found; the keys are stored by the '
                               'operator\'s decision')
            return stored, details, 'no-records'
        details.append('no SSHFP records found for the host')
        return _confirmed_keys(host, fingerprints, confirm, details), \
            details, 'no-records'

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
        return None, details, None
    if not matched:
        details.append('none of the scanned keys matches the SSHFP '
                       'records of ' + hostname + '; the host was not '
                       'stored')
        return None, details, None
    strict = dns_mode == 'dns-verify' or not trust_unsigned
    if not authenticated and strict:
        # The policy refuses the unsigned match; the confirmation
        # callback is the operator's explicit override of it
        if confirm is None:
            if unverified:
                details.append(str(len(unverified)) + ' of the scanned '
                               'keys have no SSHFP records and were '
                               'not stored')
            details.append('the SSHFP records of ' + hostname + ' are '
                           'not DNSSEC-validated; the host was not '
                           'stored (rerun with \'--confirm\' to accept '
                           'the keys after checking the fingerprints)')
            return None, details, None
        stored = _confirmed_keys(host, fingerprints, confirm, details)
        if stored is None:
            if unverified:
                details.append(str(len(unverified)) + ' of the scanned '
                               'keys have no SSHFP records and were '
                               'not stored')
            return None, details, None
        details.append('the SSHFP records of ' + hostname + ' are not '
                       'DNSSEC-validated; the keys are stored as '
                       'scanned by the operator\'s decision')
        return stored, details, 'unsigned'
    if authenticated:
        if confirm is None:
            if unverified:
                details.append(str(len(unverified)) + ' of the scanned '
                               'keys have no SSHFP records and were '
                               'not stored')
            details.append('the host keys match the SSHFP records of '
                           + hostname + ' (DNSSEC-validated)')
            return matched, details, 'validated'
        # The operator asked to decide every store: the offer carries
        # every scanned key, and the acceptance stores them as
        # scanned, the same contract the other paths give
        stored = _confirmed_keys(host, fingerprints, confirm, details)
        if stored is not None:
            details.append('the host keys match the SSHFP records of '
                           + hostname + ' (DNSSEC-validated); the keys '
                           'are stored as scanned by the operator\'s '
                           'decision')
        return stored, details, 'validated'
    # The unsigned match grants no trust of its own: the keys are
    # handled like the keys of a host without SSHFP records
    details.append('the SSHFP match of ' + hostname + ' is not '
                   'DNSSEC-validated; the keys are stored as scanned')
    return _confirmed_keys(host, fingerprints, confirm, details), \
        details, 'unsigned'


def rescan_hosts(project, hosts, store=None, phases=('remove', 'scan'),
                 timeout=10, dns_mode='dns', confirm=None, variables=None):
    """Cycle the known_hosts entries of the given hosts.

    For each host, the current host keys are scanned and classified.
    The stored entries of the identifiers which answered the scan are
    then replaced: the store is copied to a temporary file, the stale
    entries of those identifiers are removed from the copy, and the
    accepted keys are appended. The copy swaps in atomically, so a
    crash in the middle leaves the operator's store as it was. The
    entries of the identifiers which did not answer, and of a host
    whose keys were refused, stay as they are. The connections use the
    port of the host's resolution; the entries of the hosts on
    non-default ports carry the '[host]:port' form of the identifiers.
    A host which fails a phase is reported and the remaining hosts
    continue, so one host without a running sshd does not mask the
    results of the others.

    The scanned keys are compared with the entries the store holds,
    key by key, and only the entries of the identifiers whose key
    material changed are rewritten: a rescan of an unchanged host
    leaves the store file alone. The hashed host names of the
    entries carry a fresh salt on every scan, so the comparison runs
    on the key material and not on the text of the lines.

    The hosts whose connections traverse a jump host scan after the
    jump: the keys of the jump must be in the store before a
    connection through it can be verified. When the direct scan of
    such a host produces no keys and the resolved connection options
    carry a 'ProxyJump' whose key the store knows, the keys are
    collected through the connection itself: the connection runs
    with a throwaway known_hosts file, so only the keys which pass
    the verification of this run enter the store. A bastion hidden
    inside a 'ProxyCommand' cannot be discovered. The ordering covers
    the hosts which depend on another host of the run: a chain
    scanned in one run keeps the order it was given, and the
    connection-scan of the outermost host fails when an intermediate
    hop's key is not in the store yet. The failure is reported and a
    second run collects the host.

    The classification of the scanned keys against the SSHFP records
    of the DNS follows the contract documented in
    `_classify_scanned_keys`: the modes select which keys are stored
    automatically, the trust policy handles the matches the resolver
    did not authenticate, and the 'confirm' callback, when given,
    gates every store of the run on the operator's decision. The keys
    which contradict the published records of a host are refused with
    or without the callback.

    The 'variables' parameter carries the host variables a pattern
    expansion already fetched, keyed by host name -- the hosts it
    covers resolve without a second invocation of the inventory.
    Returns a list of '(host, succeeded, message)' tuples, one per
    host; the message is empty when the host completed the requested
    phases. Raises ValueError when no store can be determined.
    """
    store_project = None
    if store:
        store = os.path.expanduser(store)
    if store is None:
        store, inject = require_store(project)
        # The user mode stores the keys in '~/.ssh/known_hosts', which
        # lies outside of the project by design; only the project mode
        # derives the store from configuration, so only that store is
        # contained.
        if inject:
            store_project = project.path

    # The connection parameters of the hosts are resolved up front:
    # the hosts whose connections traverse another host of the run
    # scan after that host, because the connection-scan of a host
    # behind a jump needs the key of the jump in the store. The
    # variables a pattern expansion already fetched resolve the hosts
    # without a second invocation
    variables = variables or {}
    parameters_of = {}
    for host in hosts:
        try:
            parameters_of[host] = resolve_host(
                project, host, variables=variables.get(host))
        except (ValueError, ChildProcessError):
            parameters_of[host] = None
    known_names = set()
    for host in hosts:
        known_names.add(host)
        parameters = parameters_of[host]
        if parameters and parameters.get('destination'):
            known_names.add(parameters['destination'])

    def traverses_run_host(item):
        for hop in connection_jump_names(parameters_of[item] or {}):
            name, _, _ = _hop_endpoint(hop)
            if name in known_names:
                return True
        return False

    ordered_hosts = [host for host in hosts
                     if not traverses_run_host(host)]
    ordered_hosts += [host for host in hosts if traverses_run_host(host)]

    results = []
    for host in ordered_hosts:
        parameters = parameters_of[host]
        actions, resolvable = rescan_actions(
            project, host, store, phases, timeout, parameters=parameters)
        succeeded = True
        details = []
        store_keys = None
        scan_ok = None
        verdict = None
        keys_by_identifier = {}

        if 'scan' in phases:
            keys = []
            scanned = set()
            keys_by_identifier = {}
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
                fresh = [line for line in process.stdout.splitlines()
                         if line and not line.startswith('#')]
                if fresh:
                    scanned.add(argv[-1])
                    merged = keys_by_identifier.get(argv[-1], [])
                    keys_by_identifier[argv[-1]] = merged + [
                        line for line in fresh if line not in merged]
                keys.extend(line for line in fresh
                            if line not in keys)
            scan_ok = bool(keys)
            if not keys and connection_jump_names(parameters or {}):
                # The host did not answer the direct scan; when its
                # connection traverses a jump host whose key the
                # store knows, the keys are collected through the
                # connection itself
                details.append('the direct scan produced no keys; '
                               'the keys are collected through the '
                               'connection')
                keys = _collect_through_connection(
                    project, parameters, store, timeout, details) or []
                destination = (parameters or {}).get('destination')
                if keys and destination:
                    scanned.add(destination)
                    keys_by_identifier[destination] = list(keys)
                scan_ok = bool(keys)
            if keys:
                trust_unsigned = project.config.raw.get('ssh', {}).get(
                    'rescan', {}).get('trust_unsigned_records', True)
                store_keys, scan_details, verdict = \
                    _classify_scanned_keys(
                        host, keys, resolvable, dns_mode, confirm, details,
                        trust_unsigned)
                if store_keys is None:
                    succeeded = False
            elif resolvable:
                succeeded = False
                details.append('no host keys received from ' + host)
            else:
                succeeded = False
                details.append('no resolvable identifiers to scan for '
                               + host)

        # The entries the store already holds, per the identifier the
        # scan covers; 'ssh-keygen -F' resolves the hashed entries
        # whatever salt they were hashed with
        store_existed = os.path.exists(store)
        stored_material = {}
        changed = set()
        line_identifier = {}
        if 'scan' in phases and store_keys:
            if store_existed:
                binaries = project.config.raw['binaries']
                port = (parameters or {}).get('port')
                for identifier in scanned:
                    qualified = identifier
                    if port and str(port) != '22':
                        qualified = '[' + identifier + ']:' + str(port)
                    probe = subprocess.run(
                        [binaries['ssh-keygen'], '-F', qualified,
                         '-f', store],
                        capture_output=True, text=True)
                    stored_material[identifier] = entry_key_material(
                        probe.stdout.splitlines())
            for identifier, lines in keys_by_identifier.items():
                for line in lines:
                    line_identifier.setdefault(line, identifier)
            for identifier in scanned:
                accepted = entry_key_material(
                    [line for line in store_keys
                     if line_identifier.get(line) == identifier])
                if accepted != stored_material.get(identifier, set()):
                    changed.add(identifier)
            if store_existed and not changed:
                # Every scanned key matches the entry the store
                # already holds, key material for key material: the
                # file stays as it is, and a tracked store gains no
                # commit for an unchanged host
                details.append('the scanned keys match the entries the '
                               'store already holds')
        append_keys = [line for line in (store_keys or [])
                       if line_identifier.get(line) in changed]

        # The stored entries of a host are only removed when the scan
        # produced keys to store, or when the removal was requested
        # explicitly without a scan phase. A failed scan and keys
        # which were refused keep the old trust intact: the removal
        # never leaves a host without its known entries. The entries
        # of the identifiers whose keys did not change stay untouched,
        # their hashed host names and all.
        if scan_ok is None:
            remove_entries = 'remove' in phases
        else:
            remove_entries = bool(scan_ok and changed)
        # The cycle of removals and appends works on a copy of the
        # store which replaces it atomically: a crash between the
        # removals and the append leaves the operator's store as it
        # was, and the append cannot merge into a last line which
        # lacks its newline
        if os.path.islink(store):
            # The cycle is written through the symlink, the way the
            # client configuration is: the target the operator's
            # dotfiles manage keeps receiving the entries
            store = os.path.realpath(store)
        work_store = store
        temp_path = None
        backup = None
        try:
            if (store_existed and remove_entries) or append_keys:
                ensure_store_dir(store, store_project)
                # The store is created with the private mode from the
                # start, without the world-readable window between the
                # creation and the chmod
                descriptor, temp_path = tempfile.mkstemp(
                    dir=os.path.dirname(store) or '.',
                    prefix='known_hosts.')
                backup = temp_path + '.old'
                # The copy and the append run in binary mode: the
                # store content is not text in any locale, and an
                # operator comment in an unusual encoding must not
                # abort the rescan
                with os.fdopen(descriptor, 'wb') as handle:
                    if store_existed:
                        with open(store, 'rb') as source:
                            content = source.read()
                    else:
                        content = b''
                    if content and not content.endswith(b'\n'):
                        content += b'\n'
                    handle.write(content)
                os.chmod(temp_path, 0o600)
                work_store = temp_path
            if store_existed and remove_entries:
                for phase, argv in actions:
                    if phase != 'remove':
                        continue
                    if 'scan' in phases:
                        bare = argv[2]
                        if bare.startswith('[') and ']' in bare:
                            bare = bare[1:bare.index(']')]
                        if bare not in changed:
                            continue
                    process = subprocess.run(
                        argv[:-1] + [work_store],
                        capture_output=True, text=True)
                    if process.returncode != 0:
                        succeeded = False
                        detail = (process.stderr.strip().splitlines()
                                  or [''])[-1]
                        details.append('cannot remove the entries of '
                                       + argv[2] + ': ' + detail)
            if append_keys:
                with open(work_store, 'ab') as handle:
                    handle.write(('\n'.join(append_keys) + '\n').encode())
            if work_store is not store:
                # The private mode is the store's mode, established or
                # created
                os.chmod(work_store, 0o600)
                os.replace(work_store, store)
                temp_path = None
        finally:
            # The working copy and the backup which 'ssh-keygen -R'
            # leaves next to it go with it
            for leftover in (temp_path, backup):
                if leftover and os.path.exists(leftover):
                    os.unlink(leftover)

        message = '; '.join(details)
        results.append((host, succeeded, message))
        if succeeded:
            # The notice names what happened to the store, so the
            # lines stay greppable: the entries were added on the
            # first contact, refreshed when the keys changed, kept
            # when they did not, and removed by a removal-only run
            if 'scan' not in phases:
                notice = ('Removed the known_hosts entries of the host '
                          '"' + host + '" from ' + store)
            elif not changed:
                notice = ('Kept the known_hosts entries of the host '
                          '"' + host + '" in ' + store)
            elif any(stored_material.get(identifier)
                     for identifier in scanned):
                notice = ('Refreshed the known_hosts entries of the '
                          'host "' + host + '" in ' + store)
            else:
                notice = ('Added the known_hosts entries of the host '
                          '"' + host + '" in ' + store)
            # The verdict rides the line only when it says something:
            # a host without SSHFP records is the ordinary case, and
            # the '--no-dns' mode made no lookup to report on
            suffix = {
                'validated': '(SSHFP validated)',
                'unsigned': '(SSHFP unsigned)',
            }.get(verdict)
            if suffix:
                notice += ' ' + suffix
            logger.notice(notice, extra={'allow': ['stderr', 'syslog']})
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
            # The store paths which carry whitespace are double-quoted
            # in the line; the shell grammar reads them back as single
            # tokens
            stores = shlex.split(stripped)[1:]
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
        stores = sorted(set((project_stores or [])
                            + [unexpanduser(store)]))
        # The store paths which carry whitespace are quoted; unquoted,
        # the option parsing of ssh would split them into fragment
        # paths
        tokens = [USER_KNOWN_HOSTS_STORE] + [
            quote_store_path(store) for store in stores]
        lines.append('Host *')
        lines.append('    UserKnownHostsFile ' + ' '.join(tokens))
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
    each other's trust entries. The file is replaced atomically, from
    a uniquely named temporary file. A 'UserKnownHostsFile' directive
    outside of the managed block is reported: ssh applies the first
    obtained value of an option, so such a directive shadows the
    block. Returns True when the file changed.
    """
    path = os.path.expanduser(path)
    if os.path.islink(path):
        # The block is written through the symlink, so the target the
        # operator's dotfiles manage keeps receiving it
        path = os.path.realpath(path)
    existed = os.path.exists(path)
    existing = ''
    if existed:
        with open(path) as handle:
            existing = handle.read()
    if CONFIG_BLOCK_BEGIN in existing \
            and CONFIG_BLOCK_END not in existing:
        # A block without its end marker would leave its content in
        # place, where it would win over the fresh block, and the
        # next write would treat the span as its own
        raise ValueError(
            'The SSH client configuration carries a managed block '
            'without its end marker; complete or remove the markers '
            'of ' + path + ' manually before writing it again')
    existing_stores = parse_config_stores(existing)

    outside = existing
    if CONFIG_BLOCK_BEGIN in existing and CONFIG_BLOCK_END in existing:
        outside = existing.split(CONFIG_BLOCK_BEGIN, 1)[0] \
            + existing.split(CONFIG_BLOCK_END, 1)[1]
    for line in outside.splitlines():
        if line.strip().startswith('UserKnownHostsFile'):
            logger.notice(
                'The SSH client configuration declares its own '
                'UserKnownHostsFile outside of the managed block; '
                'ssh applies the first obtained value of an option, '
                'and the managed block may not apply',
                extra={'allow': 'stderr'})
            break

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
        # A unique temporary name: two projects writing the block at
        # the same time must not truncate each other's content
        descriptor, temp_path = tempfile.mkstemp(
            dir=parent or '.', prefix=os.path.basename(path) + '.')
        try:
            with os.fdopen(descriptor, 'w') as handle:
                handle.write(content)
            os.chmod(temp_path, mode)
            os.replace(temp_path, path)
        except OSError:
            os.unlink(temp_path)
            raise
    return changed


def build_handoff_command(project, command, arguments, identity=None,
                          accept=False, passthrough=(), user=None,
                          port=None):
    """Build the command line of the '--' handoff invocation.

    The arguments which follow the '--' marker go to the command
    unchanged: the inventory is not consulted, so the command behaves
    like the plain binary. The options which DebOps itself interprets
    apply: the identity, the user and the port, and the accept-new
    option. The 'passthrough' options are the ones the argument walk
    collected before the marker -- options of the command which DebOps
    does not interpret; they keep their places in front of the
    arguments, so nothing the operator wrote before the marker is
    lost.

    The '--accept' option makes the command store unseen host keys; in
    the project known_hosts mode the store of the view is injected
    with it, so the accepted keys land in the store of the view and
    not in the operator's own file. Without '--accept' no store is
    applied.
    """
    binary = (ssh_executable(project) if command == 'ssh'
              else transfer_executable(project, command))
    options = []
    if accept:
        store, inject = require_store(project)
        if inject:
            options.extend(['-o', known_hosts_option(store)])
        options.extend(['-o', 'StrictHostKeyChecking=accept-new'])
    if identity:
        options.extend(['-i', identity])
    if user and command == 'ssh':
        # The login user and the port are flags of ssh; sftp carries
        # them in its destination and has no preserve flag to collide
        # with
        options.extend(['-l', user])
    if port and command == 'ssh':
        options.extend(['-p', str(port)])
    return [binary or project.config.raw['binaries'][command]] \
        + options + list(passthrough) + list(arguments)
