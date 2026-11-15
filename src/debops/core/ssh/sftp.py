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

from .store import known_hosts_option, require_store
from .utils import (bracket_ipv6, compose_options, resolve_destination,
                    split_host_path, translate_ssh_args, without_known_hosts_options)

logger = logging.getLogger(__name__)


def build_sftp_command(project, destination, identity=None, accept=False,
                       sftp_args=None, sftp_head_args=None):
    """Build the sftp command line for 'debops sftp <destination>'.

    The destination follows the sftp grammar, '[user@]host[:path]';
    the host part resolves through the project's inventory and the
    path, when given, is the directory the session starts in. Raises
    ValueError when the host part is not defined in the inventory.
    """
    host_part, start_path = split_host_path(destination)
    user = None
    if host_part is None:
        # A destination without a colon is the whole host; there is no
        # start path
        host = start_path
        start_path = None
    else:
        if '@' in host_part:
            # ssh splits the user at the last '@' of the destination
            user, _, host_part = host_part.rpartition('@')
        host = host_part.strip('[]')

    parameters = resolve_destination(project, host)
    binary = (parameters.get('sftp_executable')
              or project.config.raw['binaries']['sftp'])
    effective_user = user or parameters.get('user')
    destination_token = (effective_user + '@' if effective_user else '') \
        + bracket_ipv6(parameters.get('destination')) \
        + (':' + start_path if start_path else '')
    if destination_token.startswith('-'):
        # A user which carries an option would be parsed as one by
        # sftp, and its value executed through the user's shell by ssh
        raise ValueError(
            'The sftp destination of the host "' + host + '" looks '
            'like an SSH option instead of a destination: '
            + destination_token)

    command = [binary]
    sftp_args = (sftp_args or []) + shlex.split(
        parameters.get('sftp_extra_args') or '')
    port = parameters.get('port')
    if port:
        command.extend(['-P', str(port)])
    identity_file = identity or parameters.get('identity')
    if identity_file:
        command.extend(['-i', identity_file])

    ssh_options = []
    store, inject = require_store(project)
    if inject:
        ssh_options.append(('-o', known_hosts_option(store)))
    if accept:
        # Before the translated arguments: ssh applies the first
        # obtained value of an option, and an explicit '--accept' must
        # not be defeated by a StrictHostKeyChecking in the resolved
        # arguments
        ssh_options.append(('-o', 'StrictHostKeyChecking=accept-new'))
    translated, dropped = [], []
    for value in (parameters.get('ssh_args'),
                  parameters.get('common_args'),
                  parameters.get('extra_args')):
        if value:
            tokens = without_known_hosts_options(shlex.split(value))
            translated_side, dropped_side = translate_ssh_args(tokens)
            translated.extend(translated_side)
            dropped.extend(dropped_side)
    if dropped:
        logger.notice(
            'The ssh options which configure forwards or streams are '
            'not applicable to an sftp session and were dropped: '
            + ' '.join(dropped),
            extra={'allow': 'stderr'})
    ssh_options.extend(translated)
    command.extend(compose_options(ssh_options))

    command.extend(sftp_head_args or [])
    command.append(destination_token)
    command.extend(sftp_args or [])
    return command
