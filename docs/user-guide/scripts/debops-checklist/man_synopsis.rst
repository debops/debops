.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops checklist list``    [-h|--help] [-a|--active] [-f|--format text|json] [-v|--verbose] [<project_dir>]

``debops checklist open``    [-h|--help] [--project-dir <project_dir>] [-v|--verbose] [<copy-id>] <checklist> [-r|--reset] [--no-reset] [-d|--dry-run]

``debops checklist edit``    [-h|--help] [--project-dir <project_dir>] [-v|--verbose] [<copy>]

``debops checklist commit``  [-h|--help] [--project-dir <project_dir>] [-v|--verbose] [<copy>] [-e|--edit] [-c|--close] [-A|--all]

``debops checklist close``   [-h|--help] [--project-dir <project_dir>] [-v|--verbose] [<copy>] [-f|--force] [-A|--all]

An omitted ``<copy>`` operand resolves to the only open copy. With
several copies open, the command needs an operand that names one of
them. The ``<checklist>`` name is relative to a checklist layer root
and accepts an optional ``.md`` suffix. A lone ``<copy-id>`` operand
on :command:`debops checklist open` together with the ``--reset``
option re-opens the copy from the checklist its sidecar records.
