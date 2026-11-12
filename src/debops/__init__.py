# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import contextvars
import logging

# The NOTICE log level is missing in the Python's logging module, let's add
# it back (sysadmin's perspective). Register it at package import time so
# that it is available to any module that uses 'logger.notice()', not only
# when the command line interface is executed.
LOGGING_NOTICE_NUM = (logging.INFO + 5)
logging.addLevelName(LOGGING_NOTICE_NUM, "NOTICE")
logging.NOTICE = LOGGING_NOTICE_NUM


def notice(self, message, *args, **kws):
    if self.isEnabledFor(LOGGING_NOTICE_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(LOGGING_NOTICE_NUM, message, args, **kws)


logging.Logger.notice = notice

# The project context of the running operation: which project and view
# the process currently works with. Set when a project directory is
# opened; the journal formatter renders it as a '[project:view]' prefix
# so that journal entries can be correlated with the project they
# belong to. A ContextVar keeps the mechanism safe for the daemon,
# which may serve requests from multiple threads.
_project_context = contextvars.ContextVar(
    'debops-project-context', default=None)


def set_project_context(project, view):
    """Record the project and view the process currently works with.

    Passing None for both clears the context, for instance when the
    project directory is being torn down.
    """
    if project is None:
        _project_context.set(None)
    else:
        _project_context.set('{}:{}'.format(project, view))


def get_project_context():
    """Return the current 'project:view' tag, or None outside of a
    project context."""
    return _project_context.get()


class ProjectContextFilter(logging.Filter):
    """Stamp every record with the current project context."""

    def filter(self, record):
        record.project_view = _project_context.get() or ''
        return True


class ProjectFormatter(logging.Formatter):
    """Render journal records with a '[project:view]' prefix.

    Records emitted outside of a project context are formatted
    unchanged. The prefix is folded into the message on a copy of the
    record, so that other handlers attached to the same logger are not
    affected by the formatting of one of them.
    """

    def format(self, record):
        prefix = getattr(record, 'project_view', '')
        if prefix:
            record = logging.makeLogRecord({
                **record.__dict__,
                'msg': '[{}] {}'.format(prefix, record.getMessage()),
                'args': None})
        return super().format(record)
