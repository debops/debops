# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import os
import logging
from logging.handlers import SysLogHandler

from .cli import Interpreter
from .core.config import Configuration
from .subcommands import Subcommands

# Configure logging early so that it's available as soon as possible
logger = logging.getLogger('debops')


def main():

    # Check command line arguments early to detect log verbosity
    args = sys.argv
    parsed_args = Subcommands(args)
    log_verbosity = parsed_args.args.verbose

    # Check DebOps configuration to get logging options
    config = Configuration()

    def build_handler_filters(handler: str, quiet_level=None):
        """Route records between the handlers and keep the terminal
        quiet.

        Usage: logger.notice('Message', extra={'allow': 'syslog'})
        sends the record to the syslog handler only; a list of handler
        names sends it to each of them. Records without the marker go
        to every handler whose gate admits them. The terminal also
        holds back the records below its quiet level, unless a record
        is explicitly allowed on it -- that is how an opt-in notice
        like the version check stays visible while the routine
        notices wait in the journal."""

        def handler_filter(record: logging.LogRecord):
            allow = getattr(record, 'allow', None)
            allowed = (allow == handler
                       or (isinstance(allow, (list, tuple))
                           and handler in allow))
            if allow is not None and not allowed:
                return False
            if (handler == 'stderr' and quiet_level is not None
                    and record.levelno < quiet_level and not allowed):
                return False
            return True

        return handler_filter

    syslog_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'NOTICE': logging.NOTICE,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    syslog_facilities = {
        'kern': SysLogHandler.LOG_KERN,
        'user': SysLogHandler.LOG_USER,
        'mail': SysLogHandler.LOG_MAIL,
        'daemon': SysLogHandler.LOG_DAEMON,
        'auth': SysLogHandler.LOG_AUTH,
        'syslog': SysLogHandler.LOG_SYSLOG,
        'lpr': SysLogHandler.LOG_LPR,
        'news': SysLogHandler.LOG_NEWS,
        'uucp': SysLogHandler.LOG_UUCP,
        'authpriv': SysLogHandler.LOG_AUTHPRIV,
        'ftp': SysLogHandler.LOG_FTP,
        'cron': SysLogHandler.LOG_CRON,
        'local0': SysLogHandler.LOG_LOCAL0,
        'local1': SysLogHandler.LOG_LOCAL1,
        'local2': SysLogHandler.LOG_LOCAL2,
        'local3': SysLogHandler.LOG_LOCAL3,
        'local4': SysLogHandler.LOG_LOCAL4,
        'local5': SysLogHandler.LOG_LOCAL5,
        'local6': SysLogHandler.LOG_LOCAL6,
        'local7': SysLogHandler.LOG_LOCAL7
    }

    levels = [logging.DEBUG, logging.INFO, logging.NOTICE,
              logging.WARNING, logging.ERROR, logging.CRITICAL]

    # The journal follows the configured '[syslog] level'; the terminal
    # stays quiet and is raised a step at a time with '-v'. The journal
    # is kept one step more verbose than the terminal, so the durable
    # record carries the operator-relevant notices even when the
    # terminal shows nothing.
    syslog_level = syslog_levels.get(config.raw['syslog']['level'],
                                     logging.NOTICE)
    stderr_level = logging.WARNING
    if log_verbosity:
        stderr_index = max(3 - min(log_verbosity, 3), 0)
        stderr_level = levels[stderr_index]
        syslog_level = levels[max(min(levels.index(syslog_level),
                                      stderr_index - 1), 0)]

    logger.setLevel(syslog_level)

    stderr_handler = logging.StreamHandler()
    stderr_handler.addFilter(build_handler_filters('stderr', stderr_level))
    stderr_format = logging.Formatter('%(message)s')
    stderr_handler.setFormatter(stderr_format)
    logger.addHandler(stderr_handler)
    logger.debug('Logging to stderr enabled')

    if config.raw['syslog']['address']:
        if config.raw['syslog']['address'].startswith('/'):
            syslog_address = config.raw['syslog']['address']
        else:
            syslog_address = (config.raw['syslog']['address'],
                              config.raw['syslog']['port'])
    else:
        syslog_address = '/dev/log'

    # Make sure that a syslog UNIX socket path is sane
    if isinstance(syslog_address, str):
        if not os.path.exists(syslog_address):
            if syslog_address not in ('/dev/log', '/var/run/syslog'):
                logger.warning('Syslog path {} does not exist, '
                               'checking known ones'.format(syslog_address))
            for path in ('/dev/log', '/var/run/syslog'):
                if os.path.exists(path):
                    syslog_address = path
                    break

    syslog_handler = SysLogHandler(address=syslog_address,
                                   facility=syslog_facilities.get(
                                       config.raw['syslog']['facility'],
                                       SysLogHandler.LOG_USER))
    syslog_handler.addFilter(build_handler_filters('syslog'))
    syslog_fmt = logging.Formatter('[%(levelname)s] %(message)s')
    syslog_handler.setFormatter(syslog_fmt)
    logger.addHandler(syslog_handler)
    if isinstance(syslog_address, str):
        logger.debug('Logging to {} enabled'.format(syslog_address))
    else:
        logger.debug('Logging to {}:{} enabled'.format(syslog_address[0],
                                                       syslog_address[1]))
    logger.debug('Logging subsystem initialized')

    # Check for DebOps updates (opt-in, best-effort). Runs after config and
    # logging are ready but before the interpreter, so the notice appears
    # first. Lazy import keeps the module out of the common execution path.
    try:
        from .core.versioncheck import VersionCheck
        VersionCheck(config).check()
    except Exception:
        logger.debug('Version check initialization failed', exc_info=True)

    interpreter = Interpreter(args)


def run():
    try:
        main()
    except KeyboardInterrupt:
        logger.notice('User interrupted execution',
                      extra={'allow': 'syslog'})
        raise SystemExit('... aborted by user')


if __name__ == '__main__':
    run()
