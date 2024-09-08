# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import debops
import sys
import os
import logging
from logging.handlers import SysLogHandler


def main():

    # Check command line arguments early to detect log verbosity
    args = sys.argv
    parsed_args = debops.subcommands.Subcommands(args)
    log_verbosity = parsed_args.args.verbose

    # Check DebOps configuration to get logging options
    config = debops.config.Configuration()

    # The NOTICE log level is missing in the Python's logging module,
    # let's add it back (sysadmin's perspective)
    LOGGING_NOTICE_NUM = (logging.INFO + 5)
    logging.addLevelName(LOGGING_NOTICE_NUM, "NOTICE")
    logging.NOTICE = LOGGING_NOTICE_NUM

    def notice(self, message, *args, **kws):
        if self.isEnabledFor(LOGGING_NOTICE_NUM):
            # Yes, logger takes its '*args' as 'args'.
            self._log(LOGGING_NOTICE_NUM, message, args, **kws)
    logging.Logger.notice = notice

    def build_handler_filters(handler: str):
        """Add a way to block output of a specific log handler
        Usage: logger.level('Message', extra={'block': 'handler'})"""

        def handler_filter(record: logging.LogRecord):
            if hasattr(record, 'block'):
                if record.block == handler:
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

    # Configure logging early so that it's available as soon as possible
    logger = logging.getLogger('debops')

    if log_verbosity:
        if log_verbosity >= 3:
            logger.setLevel(logging.DEBUG)
        elif log_verbosity == 2:
            logger.setLevel(logging.INFO)
        elif log_verbosity == 1:
            logger.setLevel(logging.NOTICE)
    else:
        logger.setLevel(syslog_levels.get(config.raw['syslog']['level'],
                                          logging.WARNING))

    stderr_handler = logging.StreamHandler()
    stderr_handler.addFilter(build_handler_filters('stderr'))
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
    if log_verbosity:
        if log_verbosity >= 2:
            syslog_handler.setLevel(logging.DEBUG)
    else:
        syslog_handler.setLevel(syslog_levels.get(config.raw['syslog']['level'],
                                                  logging.WARNING))
    syslog_fmt = logging.Formatter('[%(levelname)s] %(message)s')
    syslog_handler.setFormatter(syslog_fmt)
    logger.addHandler(syslog_handler)
    if isinstance(syslog_address, str):
        logger.debug('Logging to {} enabled'.format(syslog_address))
    else:
        logger.debug('Logging to {}:{} enabled'.format(syslog_address[0],
                                                       syslog_address[1]))
    logger.debug('Logging subsystem initialized')

    interpreter = debops.Interpreter(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.notice('User interrupted execution',
                      extra={'block': 'stderr'})
        raise SystemExit('... aborted by user')
