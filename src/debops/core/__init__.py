# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The DebOps library core.

Layer 0 of the DebOps tool: project directories, configuration,
inventories and runners, with explicit interfaces and no command line
concerns. The CLI in :mod:`debops.cli` is this package's first client;
the MCP daemon joins as :mod:`debops.mcp` on top of it.
"""
