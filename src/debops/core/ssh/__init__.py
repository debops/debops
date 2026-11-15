# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""SSH-family access to inventory hosts and the project trust store.

The package hosts the machinery of the 'debops ssh' and 'debops scp'
subcommands: the known_hosts store layout, mode and policy in
:mod:`debops.core.ssh.store` -- the module the project machinery
imports, which pulls nothing else of the suite in --, the resolution
of the connection parameters and the argument walk in
:mod:`debops.core.ssh.utils`, the ssh command builder and the rescan
cycle in :mod:`debops.core.ssh.ssh`, and the file-transfer
composition in :mod:`debops.core.ssh.scp`.
"""

from .store import (USER_KNOWN_HOSTS_STORE, declared_known_hosts_store,
                    ensure_store_dir, known_hosts_mode, known_hosts_option,
                    known_hosts_store, quote_store_path, render_ssh_drop_in,
                    require_store, ssh_store_dir, ssh_store_file,
                    ssh_store_path)
from .utils import (CONNECTION_OPTIONS, SCP_OPTIONS_WITH_VALUE,
                    SFTP_OPTIONS_WITH_VALUE, SSH_OPTIONS_WITH_VALUE,
                    SSH_OPTIONS_WITH_OPTIONAL_VALUE,
                    bracket_ipv6, build_handoff_command,
                    resolve_destination,
                    resolve_host, resolve_patterns,
                    split_operand, split_options_operands, ssh_executable,
                    translate_ssh_args, value_options_of)
from .ssh import (build_ssh_command, host_identifiers, parse_config_stores,
                  remove_command, render_config_snippet, rescan_actions,
                  rescan_hosts, scan_command, split_destination,
                  write_config_snippet, without_known_hosts_options)
from .scp import build_scp_command
from .sftp import build_sftp_command
