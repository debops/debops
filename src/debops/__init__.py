# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

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

from .cli import Interpreter  # noqa: E402
