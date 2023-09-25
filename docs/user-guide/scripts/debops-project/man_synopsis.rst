.. Copyright (C) 2021-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops project`` [-h|--help] [<command>] [<args>]

``debops project init`` [-h|--help] [-t|--type legacy|modern] [-V|--default-view <view>] [--git|--no-git] [--encrypt encfs|git-crypt --keys <recipient>,[<recipient>]] [-v|--verbose] <project_dir>

``debops project mkview`` [-h|--help] [--project-dir <project_dir>] [--encrypt encfs|git-crypt --keys <recipient>,[<recipient>]] [-v|--verbose] <new_view>

``debops project refresh`` [-h|--help] [-v|--verbose] [<project_dir>]

``debops project unlock`` [-h|--help] [-V|--view <view>] [-v|--verbose] [<project_dir>]

``debops project lock`` [-h|--help] [-V|--view <view>] [-v|--verbose] [<project_dir>]
