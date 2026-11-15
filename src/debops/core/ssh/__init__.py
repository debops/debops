# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""SSH-family access to inventory hosts and the project trust store.

The package hosts the machinery of the 'debops ssh' and 'debops scp'
subcommands: the resolution of the connection parameters of inventory
hosts, the known_hosts store selection and layout, the ssh command
builder and the rescan cycle in :mod:`debops.core.ssh.ssh`, the
file-transfer composition in :mod:`debops.core.ssh.scp`, and the
shared machinery in :mod:`debops.core.ssh.utils`.
"""

from .utils import (SFTP_OPTIONS_WITH_VALUE, SSH_OPTIONS_WITH_VALUE,
                    USER_KNOWN_HOSTS_STORE, build_handoff_command,
                    declared_known_hosts_store, ensure_store_dir,
                    known_hosts_mode, known_hosts_store,
                    resolve_destination, resolve_host, resolve_patterns,
                    render_ssh_drop_in, split_options_operand,
                    ssh_executable, ssh_store_dir, ssh_store_file,
                    translate_ssh_args, value_options_of)
from .ssh import (build_ssh_command, host_identifiers, rescan_hosts,
                  split_destination, write_config_snippet,
                  render_config_snippet)
from .scp import build_scp_command
from .sftp import build_sftp_command
