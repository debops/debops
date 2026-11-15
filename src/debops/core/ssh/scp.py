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
import os
import shlex

from .store import known_hosts_option, require_store
from .utils import (bracket_ipv6, compose_options, resolve_destination,
                    split_operand, translate_ssh_args, without_known_hosts_options)

logger = logging.getLogger(__name__)


def build_scp_command(project, sources, destination_operand,
                      identity=None, accept=False, scp_args=None):
    """Build the scp command line for 'debops scp <source>...
    <destination>'.

    The operands follow the scp grammar, '[[user@]host:]path'; a host
    part resolves through the project's inventory, so the connection
    parameters, the jump arguments and the known_hosts store of
    'debops ssh' apply to the file transfers alike. Both sides may be
    remote; the composed ssh options then apply to both connections,
    which is the behavior of modern scp. Raises ValueError when a host
    part is not defined in the inventory.
    """
    binary = None
    operands = []
    translated = []
    dropped = []
    store, inject = require_store(project)
    ports = []
    identities = []
    executables = []
    transfer_args = []

    for operand in (*sources, destination_operand):
        user, host, path = split_operand(operand)
        if host is None:
            operands.append(operand)
            continue
        parameters = resolve_destination(project, host)
        side_user = user or parameters.get('user')
        destination_host = parameters.get('destination')
        operands.append((side_user + '@' if side_user else '')
                        + bracket_ipv6(destination_host) + ':' + path)
        port = parameters.get('port')
        if port:
            ports.append(str(port))
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
                translated.extend(translated_side)
                dropped.extend(dropped_side)

    if dropped:
        logger.notice(
            'The ssh options which configure forwards or streams are '
            'not applicable to a file transfer and were dropped: '
            + ' '.join(dropped),
            extra={'allow': 'stderr'})

    unique_ports = set(ports)

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
    if len(unique_ports) == 1 and not (scp_args and '-P' in scp_args):
        # An explicit '-P' of the operator wins over the inventory
        # ports; scp applies the last obtained value
        ssh_options.append(('-P', unique_ports.pop()))
    elif len(unique_ports) > 1:
        logger.notice(
            'The operands resolve to hosts with different ssh ports; '
            'scp applies one port to both connections and none was '
            'added', extra={'allow': 'stderr'})
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
