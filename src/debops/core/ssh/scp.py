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

from .utils import (known_hosts_mode, known_hosts_store,
                    resolve_destination,
                    split_host_path, translate_ssh_args)

logger = logging.getLogger(__name__)


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


def build_scp_command(project, source_operand, destination_operand,
                      identity=None, accept=False, scp_args=None):
    """Build the scp command line for 'debops scp <source>
    <destination>'.

    The operands follow the scp grammar, '[[user@]host:]path'; a host
    part resolves through the project's inventory, so the connection
    parameters, the jump arguments and the known_hosts store of
    'debops ssh' apply to the file transfers alike. Both sides may be
    remote; the composed ssh options then apply to both connections,
    which is the behavior of modern scp. Raises ValueError when a host
    part is not defined in the inventory.
    """
    binary = project.config.raw['binaries']['scp']
    operands = []
    ssh_options = []
    dropped = []
    ports = []
    identities = []

    for operand in (source_operand, destination_operand):
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
        ssh_options.append('-P ' + unique_ports.pop())
    elif len(unique_ports) > 1:
        logger.notice(
            'The operands resolve to hosts with different ssh ports; '
            'scp applies one port to both connections and none was '
            'added', extra={'allow': 'stderr'})

    unique_identities = set(identities)
    if identity:
        ssh_options.append('-i ' + identity)
    elif len(unique_identities) == 1:
        ssh_options.append('-i ' + unique_identities.pop())
    elif len(unique_identities) > 1:
        logger.notice(
            'The operands resolve to hosts with different private key '
            'files; scp applies one identity to both connections and '
            'none was added', extra={'allow': 'stderr'})

    if accept:
        ssh_options.append('-o StrictHostKeyChecking=accept-new')
    if known_hosts_mode(project) == 'project':
        store = known_hosts_store(project)
        if store:
            ssh_options.insert(0, '-o UserKnownHostsFile=' + store)

    command = [binary]
    for option in dict.fromkeys(ssh_options):
        command.extend(shlex.split(option))
    command.extend(scp_args or [])
    command.extend(operands)
    return command
