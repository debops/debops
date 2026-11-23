.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops tofu`` [-h|--help] [--project-dir <project_dir>] [-V|--view <view>] [-v|--verbose] [--eval] [--no-color] [-E|--bell] [-w|--workspace <workspace>] [-M|--allow-missing-state] [<DebOps-level operation> [<options>]]

``debops tofu`` [-h|--help] [--project-dir <project_dir>] [-V|--view <view>] [-v|--verbose] [--eval] [--no-color] [-E|--bell] [-w|--workspace <workspace>] [-M|--allow-missing-state] [--] <tofu operation> [<operation args>]

DebOps-level operations: ``mkview``, ``update``, ``install``, ``inventory``, ``plans``, ``rekey``, ``cache``. Every other token runs the :program:`tofu` command. Run :command:`debops tofu --help` for the full list.
