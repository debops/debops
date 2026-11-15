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

from .utils import (compose_options, known_hosts_mode, known_hosts_store,
                    resolve_destination, split_operand,
                    translate_ssh_args)

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
    ssh_options = []
    dropped = []
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
                        + destination_host + ':' + path)
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
        for value in (parameters.get('common_args'),
                      parameters.get('extra_args')):
            if value:
                translated, dropped_side = translate_ssh_args(value)
                ssh_options.extend(translated)
                dropped.extend(dropped_side)

    if dropped:
        logger.notice(
            'The ssh options which configure forwards or streams are '
            'not applicable to a file transfer and were dropped: '
            + ' '.join(dropped),
            extra={'allow': 'stderr'})

    unique_ports = set(ports)
    if len(unique_ports) == 1:
        ssh_options.append(('-P', unique_ports.pop()))
    elif len(unique_ports) > 1:
        logger.notice(
            'The operands resolve to hosts with different ssh ports; '
            'scp applies one port to both connections and none was '
            'added', extra={'allow': 'stderr'})

    unique_executables = set(executables)
    if len(unique_executables) == 1:
        binary = unique_executables.pop()
    elif len(unique_executables) > 1:
        logger.notice(
            'The operands resolve to hosts with different scp '
            'executables; the configured scp binary is used',
            extra={'allow': 'stderr'})

    unique_identities = set(identities)
    if identity:
        ssh_options.append(('-i', identity))
    elif len(unique_identities) == 1:
        ssh_options.append(('-i', unique_identities.pop()))
    elif len(unique_identities) > 1:
        logger.notice(
            'The operands resolve to hosts with different private key '
            'files; scp applies one identity to both connections and '
            'none was added', extra={'allow': 'stderr'})

    if accept:
        ssh_options.append(('-o', 'StrictHostKeyChecking=accept-new'))
    if known_hosts_mode(project) == 'project':
        store = known_hosts_store(project)
        if not store:
            raise ValueError(
                'The project known_hosts mode is active for the view, '
                'but the view does not declare a known_hosts store')
        ssh_options.insert(0, ('-o', 'UserKnownHostsFile=' + store))

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
