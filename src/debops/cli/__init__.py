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
import re
import sys

from ..core.utils import wrap_message

# Control characters printed to the terminal let a hostile file name
# or frontmatter value steer the display; the reports strip them.
# Newlines and tabs survive: multi-line reports keep their shape.
_CONTROLS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def _without_controls(text):
    """The text without control characters."""
    return _CONTROLS_RE.sub("", str(text))


def print_error(errmsg):
    """Print a failure message to standard error.

    Machine-readable output written to stdout, for example the inventory or
    the configuration in JSON, must stay parseable, so the failure reports
    never appear there. The failure is also recorded in the journal; the
    record is skipped when the logging subsystem is not wired up (the test
    runs), since the logging fallback would print the message a second
    time. The terminal output is wrapped to the terminal width; the
    journal record keeps its single-line form.
    """
    debops_log = logging.getLogger('debops')
    message = _without_controls(errmsg)
    if debops_log.handlers:
        # The journal record keeps its single-line form
        debops_log.error(' '.join(message.splitlines()),
                         extra={'allow': 'syslog'})
    print(wrap_message('Error: ' + message), file=sys.stderr)


def print_notice(message):
    """Print a notice line to standard error.

    The non-failure sibling of ``print_error``: reports that deserve
    the attention channel without claiming error severity -- the
    batch-close report of copies left open, for example. The terminal
    output is wrapped to the terminal width; the journal record keeps
    its single-line form and is skipped when the logging subsystem is
    not wired up.
    """
    debops_log = logging.getLogger('debops')
    message = _without_controls(message)
    if debops_log.handlers:
        debops_log.info(message, extra={'allow': 'syslog'})
    print(wrap_message(message), file=sys.stderr)
