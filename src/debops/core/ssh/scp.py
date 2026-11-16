# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The file-transfer composition for 'debops scp'.

The operands follow the scp grammar, '[[user@]host:]path', with the
host part resolved through the project's inventory: the connection
parameters, the jump arguments and the known_hosts store of
'debops ssh' apply to the file transfers alike.
"""

import logging
import shlex
import urllib.parse

from .store import known_hosts_option, require_store
from .utils import (JumpRewriter, bracket_ipv6, compose_options,
                    resolve_destination, split_operand, translate_ssh_args,
                    without_known_hosts_options)

logger = logging.getLogger(__name__)


def _uri_operand(user, host, port, path):
    """Return a remote operand in the 'scp://' URI form, which carries
    the port of its own connection.

    The plain grammar of scp applies one '-P' port to every connection
    of the command; the URI form carries one port per operand, which
    is how remote operands with different ports stay expressible in
    one command. The path is percent-encoded; in the URI grammar a
    single slash after the authority addresses a path relative to the
    remote home directory and a double slash an absolute path, which
    the composition produces from the shape of the operand path
    itself.
    """
    authority = (user + '@' if user else '') + bracket_ipv6(host)
    if port:
        authority += ':' + str(port)
    encoded = urllib.parse.quote(path, safe='/')
    if not encoded:
        return 'scp://' + authority
    return 'scp://' + authority + '/' + encoded


def build_scp_command(project, sources, destination_operand,
                      identity=None, accept=False, scp_args=None):
    """Build the scp command line for 'debops scp <source>...
    <destination>'.

    The operands follow the scp grammar, '[[user@]host:]path'; a host
    part resolves through the project's inventory, so the connection
    parameters, the jump arguments and the known_hosts store of
    'debops ssh' apply to the file transfers alike. Both sides may be
    remote; the composed ssh options then apply to both connections,
    which is the behavior of modern scp. Remote operands which resolve
    to different ssh ports compose in the 'scp://' URI form, which
    carries a port per connection -- the plain grammar applies one
    port to all of them. Raises ValueError when a host part is not
    defined in the inventory.
    """
    binary = None
    operand_specs = []
    translated = []
    dropped = []
    store, inject = require_store(project)
    identities = []
    executables = []
    transfer_args = []

    for operand in (*sources, destination_operand):
        user, host, path = split_operand(operand)
        if host is None:
            operand_specs.append(('local', operand))
            continue
        parameters = resolve_destination(project, host)
        side_user = user or parameters.get('user')
        destination_host = parameters.get('destination')
        port = parameters.get('port')
        operand_specs.append(('remote', (side_user, destination_host,
                                         port, path)))
        side_identity = parameters.get('identity')
        if side_identity:
            identities.append(side_identity)
        executable = parameters.get('scp_executable')
        if executable:
            executables.append(executable)
        extra = parameters.get('scp_extra_args')
        if extra:
            transfer_args.extend(shlex.split(extra))
        for value in (parameters.get('ssh_args'),
                      parameters.get('common_args'),
                      parameters.get('extra_args')):
            if value:
                tokens = shlex.split(value)
                if inject:
                    # The store of the view is injected; a declaration
                    # in the resolved arguments would be dead weight.
                    # In the user mode the declaration of the operator
                    # passes through
                    tokens = without_known_hosts_options(tokens)
                translated_side, dropped_side = translate_ssh_args(tokens)
                # scp re-emits its own port as '-o Port=' after the
                # options it forwards, so a 'Port=' in the resolved
                # arguments would win over the '-P' of the inventory
                # regardless of the composed order
                translated_side = [pair for pair in translated_side
                                   if not (isinstance(pair, tuple)
                                           and pair[1].startswith('Port='))]
                translated.extend(translated_side)
                dropped.extend(dropped_side)

    if dropped:
        logger.notice(
            'The ssh options which configure forwards or streams are '
            'not applicable to a file transfer and were dropped: '
            + ' '.join(dropped),
            extra={'allow': 'stderr'})

    remote_ports = [value[2] for kind, value in operand_specs
                    if kind == 'remote']
    # The effective port of an operand without an inventory port is
    # the ssh default; the conflict decision compares the effective
    # ports, or a mix of a default-port host and an explicit-port host
    # would look like one unique port
    effective_ports = {str(port) if port else '22'
                       for port in remote_ports}

    # The operands compose in the order they were given. When the
    # effective ports differ, each remote operand carries its own port
    # in the 'scp://' URI form -- the plain grammar applies one port
    # to every connection of the command, the URI form one per
    # operand, and an operand without a port stays on the port its ssh
    # client configuration names; the local operands are local paths
    # in both cases
    operands = []
    for kind, value in operand_specs:
        if kind == 'local':
            operands.append(value)
            continue
        side_user, destination_host, port, path = value
        if len(effective_ports) > 1:
            operands.append(_uri_operand(side_user, destination_host,
                                         port, path))
        else:
            operands.append((side_user + '@' if side_user else '')
                            + bracket_ipv6(destination_host) + ':' + path)

    unique_executables = set(executables)
    if len(unique_executables) == 1:
        binary = unique_executables.pop()
    elif len(unique_executables) > 1:
        logger.notice(
            'The operands resolve to hosts with different scp '
            'executables; the configured scp binary is used',
            extra={'allow': 'stderr'})

    unique_identities = set(identities)

    # The options DebOps derives lead the command: ssh applies the
    # first obtained value of an option, and the derived values -- the
    # store of the view, the accept-new instruction, the port and the
    # identity -- must not be defeated by a value in the resolved
    # arguments of the hosts
    ssh_options = []
    if inject:
        ssh_options.append(('-o', known_hosts_option(store)))
    if accept:
        ssh_options.append(('-o', 'StrictHostKeyChecking=accept-new'))
    if len(effective_ports) == 1 and remote_ports and all(remote_ports) \
            and not (scp_args and '-P' in scp_args):
        # An explicit '-P' of the operator wins over the inventory
        # ports; scp applies the last obtained value. The port is
        # composed only when every remote operand carries the same
        # explicit port: a '-P 22' for hosts without an inventory port
        # would override the Port entries of the operator's own ssh
        # client configuration
        ssh_options.append(('-P', effective_ports.pop()))
    elif len(effective_ports) > 1:
        logger.notice(
            'The operands resolve to hosts with different ssh ports; '
            'each remote operand carries its own port in the scp:// '
            'URI form', extra={'allow': 'stderr'})
    if identity:
        ssh_options.append(('-i', identity))
    elif len(unique_identities) == 1:
        ssh_options.append(('-i', unique_identities.pop()))
    elif len(unique_identities) > 1:
        logger.notice(
            'The operands resolve to hosts with different private key '
            'files; scp applies one identity to both connections and '
            'none was added', extra={'allow': 'stderr'})

    ssh_options.extend(translated)

    # The options the jump process runs with are the ones of the
    # transfer: the store of the view and the host key checking mode;
    # the structured jumps are rewritten into explicit ProxyCommand
    # options which carry them into the jump process
    child_pairs = []
    if inject:
        child_pairs.append(('-o', known_hosts_option(store)))
    if accept:
        child_pairs.append(('-o', 'StrictHostKeyChecking=accept-new'))
    rewriter = JumpRewriter(child_pairs)
    ssh_options = rewriter.rewrite_pairs(ssh_options)
    rewriter.check()

    command = [binary or project.config.raw['binaries']['scp']]
    command.extend(compose_options(ssh_options))
    command.extend(scp_args or [])
    command.extend(transfer_args)
    if any(operand.startswith('-') for operand in operands):
        # An operand which starts with '-' would be parsed as an
        # option; the marker ends the option parsing of scp
        command.append('--')
    command.extend(operands)
    return command
