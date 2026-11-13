# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The interactive file-transfer session for 'debops sftp'.

The destination follows the sftp grammar, '[user@]host[:path]', with
the host part resolved through the project's inventory: the session
inherits the connection parameters, the jump arguments and the
known_hosts store of 'debops ssh'.
"""

import logging
import os
import shlex

from .utils import (known_hosts_mode, known_hosts_store,
                    resolve_destination,
                    split_host_path, translate_ssh_args)

logger = logging.getLogger(__name__)


def build_sftp_command(project, destination, identity=None, accept=False,
                       sftp_args=None, sftp_head_args=None):
    """Build the sftp command line for 'debops sftp <destination>'.

    The destination follows the sftp grammar, '[user@]host[:path]';
    the host part resolves through the project's inventory and the
    path, when given, is the directory the session starts in. Raises
    ValueError when the host part is not defined in the inventory.
    """
    binary = project.config.raw['binaries']['sftp']
    host_part, start_path = split_host_path(destination)
    user = None
    if host_part is None:
        # A destination without a colon is the whole host; there is no
        # start path
        host = start_path
        start_path = None
    else:
        if '@' in host_part:
            user, _, host_part = host_part.partition('@')
        host = host_part.strip('[]')

    parameters = resolve_destination(project, host)
    effective_user = user or parameters.get('user')
    destination_token = (effective_user + '@' if effective_user else '') \
        + parameters.get('destination') \
        + (':' + start_path if start_path else '')

    command = [binary]
    port = parameters.get('port')
    if port:
        command.extend(['-P', str(port)])
    identity_file = identity or parameters.get('identity')
    if identity_file:
        command.extend(['-i', identity_file])

    ssh_options = []
    if known_hosts_mode(project) == 'project':
        store = known_hosts_store(project)
        if store:
            ssh_options.append('-o UserKnownHostsFile=' + store)
    translated, dropped = [], []
    for value in (parameters.get('common_args'),
                  parameters.get('extra_args')):
        if value:
            translated_side, dropped_side = translate_ssh_args(value)
            translated.extend(translated_side)
            dropped.extend(dropped_side)
    if dropped:
        logger.notice(
            'The ssh options which configure forwards or streams are '
            'not applicable to an sftp session and were dropped: '
            + ' '.join(dropped),
            extra={'allow': 'stderr'})
    ssh_options.extend(translated)
    if accept:
        ssh_options.append('-o StrictHostKeyChecking=accept-new')
    for option in dict.fromkeys(ssh_options):
        command.extend(shlex.split(option))

    command.extend(sftp_head_args or [])
    command.append(destination_token)
    command.extend(sftp_args or [])
    return command
