# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the ``debops`` entry point in ``debops.__main__``.

``main()`` wires up the logging subsystem and hands the command line to the
interpreter. The tests replace the three collaborators (``Subcommands``,
``Configuration``, ``Interpreter``) and check the resulting logging state,
which the ``clean_logging`` fixture restores afterwards.
"""

import logging
from logging.handlers import SysLogHandler
import os
import subprocess
import sys
from types import SimpleNamespace
from unittest import mock

import pytest

import debops
import debops.__main__ as main_module
import debops.config
import debops.subcommands


@pytest.fixture
def clean_logging():
    """Restore the logging state that ``main()`` changes."""
    logger = logging.getLogger("debops")
    old_handlers = list(logger.handlers)
    old_level = logger.level
    yield
    logger.handlers = old_handlers
    logger.setLevel(old_level)


def stub_main_collaborators(monkeypatch, verbose=None,
                            syslog_level="WARNING", syslog_address="",
                            syslog_facility="user", syslog_port=514):
    """Replace what ``main()`` builds, return the Interpreter class mock."""
    parsed = SimpleNamespace(args=SimpleNamespace(verbose=verbose))
    monkeypatch.setattr(debops.subcommands, "Subcommands",
                        mock.Mock(return_value=parsed))
    config = mock.Mock()
    config.raw = {"syslog": {"level": syslog_level,
                             "address": syslog_address,
                             "facility": syslog_facility,
                             "port": syslog_port}}
    monkeypatch.setattr(debops.config, "Configuration",
                        mock.Mock(return_value=config))
    interpreter_class = mock.Mock()
    monkeypatch.setattr(debops, "Interpreter", interpreter_class)
    return interpreter_class


def syslog_handler():
    return [handler for handler in logging.getLogger("debops").handlers
            if isinstance(handler, SysLogHandler)][0]


def stream_handler():
    return [handler for handler in logging.getLogger("debops").handlers
            if isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, SysLogHandler)][0]


def test_main_runs_the_interpreter_with_the_command_line(clean_logging,
                                                         monkeypatch):
    interpreter_class = stub_main_collaborators(monkeypatch)

    main_module.main()

    interpreter_class.assert_called_once_with(list(os.sys.argv))


def test_importing_the_package_installs_the_notice_level():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [os.path.dirname(os.path.dirname(debops.__file__)),
         env.get("PYTHONPATH", "")])
    result = subprocess.run(
        [sys.executable, "-c",
         "import logging\n"
         "import debops\n"
         "assert logging.getLevelName(logging.NOTICE) == 'NOTICE'\n"
         "logging.getLogger('debops').notice('test message')\n"],
        capture_output=True, env=env)

    assert result.returncode == 0, result.stderr.decode()


def test_main_adds_the_stderr_and_syslog_handlers(clean_logging, monkeypatch):
    stub_main_collaborators(monkeypatch)

    main_module.main()

    assert isinstance(stream_handler(), logging.StreamHandler)
    assert isinstance(syslog_handler(), SysLogHandler)


@pytest.mark.parametrize(("verbosity", "level"), [
    (3, logging.DEBUG),
    (2, logging.INFO),
    (1, logging.INFO + 5),
])
def test_main_verbosity_overrides_the_configured_level(clean_logging,
                                                       monkeypatch,
                                                       verbosity, level):
    stub_main_collaborators(monkeypatch, verbose=verbosity,
                            syslog_level="ERROR")

    main_module.main()

    assert logging.getLogger("debops").level == level


def test_main_uses_the_configured_level_without_verbosity(clean_logging,
                                                          monkeypatch):
    stub_main_collaborators(monkeypatch, verbose=None, syslog_level="DEBUG")

    main_module.main()

    assert logging.getLogger("debops").level == logging.DEBUG


def test_main_defaults_the_syslog_address_to_the_local_socket(clean_logging,
                                                              monkeypatch):
    stub_main_collaborators(monkeypatch, syslog_address="")

    main_module.main()

    assert syslog_handler().address == "/dev/log"


def test_main_uses_a_remote_syslog_address(clean_logging, monkeypatch):
    stub_main_collaborators(monkeypatch, syslog_address="192.0.2.1",
                            syslog_port=514)

    main_module.main()

    assert syslog_handler().address == ("192.0.2.1", 514)


def test_main_falls_back_to_a_known_syslog_socket(clean_logging, monkeypatch):
    if not (os.path.exists("/dev/log") or os.path.exists("/var/run/syslog")):
        pytest.skip("no syslog socket available on this machine")
    stub_main_collaborators(monkeypatch,
                            syslog_address="/nonexistent/debops-test")

    main_module.main()

    assert syslog_handler().address in ("/dev/log", "/var/run/syslog")


def test_main_maps_the_syslog_facility(clean_logging, monkeypatch):
    stub_main_collaborators(monkeypatch, syslog_facility="local0")

    main_module.main()

    assert syslog_handler().facility == SysLogHandler.LOG_LOCAL0


def test_main_filters_can_block_a_handler(clean_logging, monkeypatch):
    stub_main_collaborators(monkeypatch)

    main_module.main()

    record = logging.LogRecord("debops", logging.INFO, __file__, 1,
                               "message", (), None)
    record.block = "stderr"
    assert stream_handler().filters[0](record) is False
    assert syslog_handler().filters[0](record) is True
    record.block = "syslog"
    assert stream_handler().filters[0](record) is True
    assert syslog_handler().filters[0](record) is False
    del record.block
    assert stream_handler().filters[0](record) is True


def test_run_reports_a_keyboard_interrupt(clean_logging, monkeypatch):
    monkeypatch.setattr(main_module, "main",
                        mock.Mock(side_effect=KeyboardInterrupt))
    monkeypatch.setattr(main_module.logger, "notice", mock.Mock(),
                        raising=False)

    with pytest.raises(SystemExit):
        main_module.run()

    main_module.logger.notice.assert_called_once()


def test_notice_is_a_noop_when_disabled():
    logger = logging.getLogger("debops.test")
    logger.setLevel(logging.WARNING)

    with mock.patch.object(logger, "_log") as log:
        logger.notice("message")

    log.assert_not_called()
