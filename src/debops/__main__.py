# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import debops
import sys


def main():
    args = sys.argv

    interpreter = debops.Interpreter(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit('... aborted by user')
