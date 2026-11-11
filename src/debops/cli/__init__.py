# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The DebOps command line interface.

The reference client of the :mod:`debops.core` library: the interpreter
which dispatches the subcommands and the argument parsers which describe
them. The library reports failures by raising exceptions; this package
owns the translation into exit codes and terminal output.
"""

import logging
import sys


def print_error(errmsg):
    """Print a failure message to standard error.

    Machine-readable output written to stdout, for example the inventory or
    the configuration in JSON, must stay parseable, so the failure reports
    never appear there. The failure is also recorded in the journal; the
    record is skipped when the logging subsystem is not wired up (the test
    runs), since the logging fallback would print the message a second
    time.
    """
    debops_log = logging.getLogger('debops')
    if debops_log.handlers:
        debops_log.error(str(errmsg), extra={'allow': 'syslog'})
    print('Error:', errmsg, file=sys.stderr)
