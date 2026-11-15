.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops ssh`` [-h|--help] [--project-dir <project_dir>] [-V|--view <view>] [-u|--user <name>] [-p|--port <port>] [-i|--identity <key>] [--accept] [--eval] [-v|--verbose] <[user@]destination> [<remote_command> ...]

``debops ssh`` [<options>] ``--`` <ssh_arguments>

``debops ssh rescan`` [-h|--help] [--project-dir <project_dir>] [-V|--view <view>] [--remove] [--scan] [--eval] [-f|--known-hosts-file <file>] [-T|--timeout <seconds>] [-v|--verbose] <pattern> [<pattern> ...]

``debops ssh config`` [-h|--help] [--project-dir <project_dir>] [-V|--view <view>] [--write] [-v|--verbose]
