# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The ssh suite handlers of the interpreter, driven in-process.

The integration tests run the command line as a subprocess, which the
coverage measurement does not see; these tests call the handlers
directly with a stubbed project, so the error paths, the '--eval'
compositions and the '--' handoffs are covered at the Python level.
"""

import os
import shlex
import socket
from types import SimpleNamespace
from unittest import mock

import pytest

import debops.cli.interpreter as cli_module
from debops.cli.interpreter import Interpreter
from debops.cli.subcommands import Subcommands


def make_interpreter():
    interpreter = Interpreter.__new__(Interpreter)
    interpreter.config = mock.Mock()
    interpreter.cwd = "/shell/cwd"
    return interpreter


def stub_the_project(monkeypatch, project):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))


def stub_the_execution(monkeypatch):
    """Replace 'os.execvp' with a recorder; the real call would
    replace the test process."""
    executed = []
    monkeypatch.setattr(os, "execvp",
                        lambda *arguments: executed.append(arguments))
    return executed


def ssh_args(**kwargs):
    defaults = dict(project_dir=None, view="system", host="web", user=None,
                    port=None, identity=None, accept=False, eval=True,
                    handoff=None, ssh_args=[], ssh_extra_args=[])
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def scp_args(**kwargs):
    defaults = dict(project_dir=None, view="system",
                    sources=["web:/src"], destination="web:/dst",
                    identity=None, accept=False, eval=True, handoff=None,
                    scp_extra_args=[])
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def sftp_args(**kwargs):
    defaults = dict(project_dir=None, view="system", destination="web",
                    identity=None, accept=False, eval=True, handoff=None,
                    sftp_head_args=[], sftp_tail_args=[])
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def rescan_args(**kwargs):
    defaults = dict(project_dir=None, view="system", remove=False,
                    scan=False, eval=True, known_hosts_file=None,
                    timeout=10, hosts=["web"], dns_mode="dns",
                    confirm=None)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def config_args(**kwargs):
    defaults = dict(project_dir=None, view="system", write=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_do_scp_eval_composes_the_command(monkeypatch, stub_project,
                                          fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_scp(make_interpreter(), scp_args())

    assert exit_info.value.code == 0
    assert "192.0.2.10:/src" in capsys.readouterr().out


def test_do_scp_eval_hands_the_arguments_over(monkeypatch, stub_project,
                                              fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_scp(make_interpreter(),
                           scp_args(handoff=["-r", "a", "b"]))

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "/usr/bin/scp -r a b"


def test_do_scp_reports_the_missing_operands(monkeypatch, stub_project,
                                             fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_scp(make_interpreter(), scp_args(sources=[]))

    assert exit_info.value.code == 2
    assert "required" in capsys.readouterr().err


def test_do_scp_reports_the_resolution_error(monkeypatch, stub_project,
                                             fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_scp(make_interpreter(),
                           scp_args(destination="unknown:/dst"))

    assert exit_info.value.code == 1
    assert "Cannot resolve" in capsys.readouterr().err


def test_do_scp_executes_the_command(monkeypatch, stub_project, fake_tools):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))
    executed = stub_the_execution(monkeypatch)

    Interpreter.do_scp(make_interpreter(), scp_args(eval=False))

    assert executed[0][0] == "/usr/bin/scp"


def test_do_sftp_eval_composes_the_command(monkeypatch, stub_project,
                                           fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_sftp(make_interpreter(), sftp_args())

    assert exit_info.value.code == 0
    assert "admin@192.0.2.10" in capsys.readouterr().out


def test_do_sftp_eval_hands_the_arguments_over(monkeypatch, stub_project,
                                               fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_sftp(make_interpreter(),
                            sftp_args(handoff=["-b", "batch", "host"]))

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "/usr/bin/sftp -b batch host"


def test_do_sftp_reports_the_resolution_error(monkeypatch, stub_project,
                                              fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_sftp(make_interpreter(),
                            sftp_args(destination="unknown"))

    assert exit_info.value.code == 1
    assert "Cannot resolve" in capsys.readouterr().err


def test_do_sftp_executes_the_command(monkeypatch, stub_project, fake_tools):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))
    executed = stub_the_execution(monkeypatch)

    Interpreter.do_sftp(make_interpreter(), sftp_args(eval=False))

    assert executed[0][0] == "/usr/bin/sftp"


def test_do_ssh_connect_eval_composes_the_command(monkeypatch, stub_project,
                                                  fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_connect(make_interpreter(), ssh_args())

    assert exit_info.value.code == 0
    command = shlex.split(capsys.readouterr().out)
    assert command[command.index("-l") + 1] == "admin"
    assert command[-1] == "192.0.2.10"


def test_do_ssh_connect_eval_hands_the_arguments_over(monkeypatch,
                                                      stub_project,
                                                      fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_connect(make_interpreter(),
                                   ssh_args(handoff=["--help"]))

    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "/usr/bin/ssh --help"


def test_do_ssh_connect_reports_the_resolution_error(monkeypatch,
                                                     stub_project,
                                                     fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_connect(make_interpreter(),
                                   ssh_args(host="unknown"))

    assert exit_info.value.code == 1
    assert "Cannot resolve" in capsys.readouterr().err


def test_do_ssh_connect_executes_the_command(monkeypatch, stub_project,
                                             fake_tools):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))
    executed = stub_the_execution(monkeypatch)

    Interpreter.do_ssh_connect(make_interpreter(), ssh_args(eval=False))

    assert executed[0][0] == "/usr/bin/ssh"


def test_do_ssh_rescan_eval_prints_the_actions(monkeypatch, stub_project,
                                               fake_tools, capsys,
                                               tmp_path):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))
    store = tmp_path / "store"

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(
            make_interpreter(),
            rescan_args(known_hosts_file=str(store)))

    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    assert "ssh-keygen -R web" in out
    assert "ssh-keyscan" in out
    assert not store.exists(), "the --eval option created the store"


def test_do_ssh_rescan_eval_with_the_remove_phase_only(monkeypatch,
                                                       stub_project,
                                                       fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit):
        Interpreter.do_ssh_rescan(
            make_interpreter(), rescan_args(remove=True))

    out = capsys.readouterr().out
    assert "ssh-keygen" in out
    assert "ssh-keyscan" not in out


def test_do_ssh_rescan_eval_with_the_scan_phase_only(monkeypatch,
                                                     stub_project,
                                                     fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit):
        Interpreter.do_ssh_rescan(
            make_interpreter(), rescan_args(scan=True))

    out = capsys.readouterr().out
    assert "ssh-keyscan" in out
    assert "ssh-keygen" not in out


def test_do_ssh_rescan_reports_the_expansion_error(monkeypatch, stub_project,
                                                   fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(
            make_interpreter(), rescan_args(hosts=["broken"]))

    assert exit_info.value.code == 1
    assert "Cannot expand" in capsys.readouterr().err


def test_do_ssh_rescan_fails_when_nothing_matches(monkeypatch, stub_project,
                                                  fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(
            make_interpreter(), rescan_args(hosts=["none"]))

    assert exit_info.value.code == 1
    assert "No hosts matched" in capsys.readouterr().err


def test_do_ssh_rescan_eval_requires_a_store(monkeypatch, stub_project,
                                             fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"]),
             "ssh": {"known_hosts": "project"}}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(make_interpreter(), rescan_args())

    assert exit_info.value.code == 1
    assert "does not declare a known_hosts store" \
        in capsys.readouterr().err


def test_do_ssh_rescan_refreshes_the_hosts(monkeypatch, stub_project,
                                           fake_tools, fake_binary,
                                           tmp_path):
    import base64
    binaries = dict(fake_tools["binaries"])
    binaries["ssh-keyscan"] = fake_binary(
        "valid-keyscan",
        "#!/bin/sh\nprintf '%s\\n' '192.0.2.10 ssh-ed25519 "
        + base64.b64encode(b'\x21' * 32).decode('ascii') + "'\n")
    stub_the_project(monkeypatch, stub_project(raw={"binaries": binaries}))
    store = tmp_path / "store"

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(
            make_interpreter(),
            rescan_args(eval=False, known_hosts_file=str(store)))

    assert exit_info.value.code == 0
    assert store.read_text().strip()


def test_do_ssh_rescan_reports_the_failed_hosts(monkeypatch, stub_project,
                                                fake_tools, fake_binary,
                                                capsys, tmp_path):
    binaries = dict(fake_tools["binaries"])
    binaries["ssh-keyscan"] = fake_binary(
        "silent-keyscan", "#!/bin/sh\nexit 0\n")
    stub_the_project(monkeypatch, stub_project(raw={"binaries": binaries}))
    store = tmp_path / "store"

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(
            make_interpreter(),
            rescan_args(eval=False, known_hosts_file=str(store)))

    assert exit_info.value.code == 1
    assert "Cannot refresh" in capsys.readouterr().err


def test_do_ssh_rescan_reports_the_store_error(monkeypatch, stub_project,
                                               fake_tools, capsys):
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"]),
             "ssh": {"known_hosts": "project"}}))

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_rescan(
            make_interpreter(), rescan_args(eval=False))

    assert exit_info.value.code == 1
    assert "Cannot rescan" in capsys.readouterr().err


def test_do_ssh_config_write_reports_the_error(monkeypatch, stub_project,
                                               capsys, tmp_path):
    """A write which the filesystem refuses aborts with the error; the
    expanded path is mocked so the test cannot touch the operator's
    own '~/.ssh/config'."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory\n")
    monkeypatch.setattr(cli_module.os.path, "expanduser",
                        lambda path: str(blocker / "sub"))
    stub_the_project(monkeypatch, stub_project())

    with pytest.raises(SystemExit) as exit_info:
        Interpreter.do_ssh_config(
            make_interpreter(),
            config_args(write=True, project_dir=str(tmp_path)))

    assert exit_info.value.code == 1


@pytest.mark.parametrize("handler,args_factory", [
    ("do_scp", scp_args),
    ("do_sftp", sftp_args),
    ("do_ssh_connect", ssh_args),
    ("do_ssh_rescan", rescan_args),
    ("do_ssh_config", config_args),
])
def test_handlers_report_the_project_errors(monkeypatch, stub_project,
                                            capsys, handler, args_factory):
    """A project directory which cannot be opened aborts the handler
    with the error message and the exit code 1."""
    monkeypatch.setattr(
        cli_module, "ProjectDir",
        mock.Mock(side_effect=IsADirectoryError("locked")))

    with pytest.raises(SystemExit) as exit_info:
        getattr(Interpreter, handler)(make_interpreter(), args_factory())

    assert exit_info.value.code == 1
    assert "locked" in capsys.readouterr().err


def test_ssh_connect_requires_a_destination(capsys):
    """The section parser dispatches on the first token; the connect
    parser reports the missing destination on its own."""
    cli = Subcommands(["debops", "ssh", "placeholder"])
    cli.args = ["debops", "ssh"]

    with pytest.raises(SystemExit) as exit_info:
        cli.do_ssh_connect()

    assert exit_info.value.code == 2
    assert "destination" in capsys.readouterr().err


def test_scp_requires_the_operands(capsys):
    with pytest.raises(SystemExit) as exit_info:
        Subcommands(["debops", "scp"])

    assert exit_info.value.code == 2
    assert "at least two operands" in capsys.readouterr().err


def test_sftp_requires_a_destination(capsys):
    with pytest.raises(SystemExit) as exit_info:
        Subcommands(["debops", "sftp"])

    assert exit_info.value.code == 2
    assert "destination" in capsys.readouterr().err


def test_scp_help_parses_without_the_operands(capsys):
    """The '--help' output parses before the operand requirement fires."""
    with pytest.raises(SystemExit) as exit_info:
        Subcommands(["debops", "scp", "--help"])

    assert exit_info.value.code == 0
    assert "copy files" in capsys.readouterr().out


def test_scp_parses_multiple_sources(capsys):
    cli = Subcommands(["debops", "scp", "-V", "system", "f1", "f2",
                       "web:/dst"])

    assert cli.args.sources == ["f1", "f2"]
    assert cli.args.destination == "web:/dst"


def test_do_ssh_rescan_prints_the_host_count_and_estimate(
        monkeypatch, stub_project, fake_tools, capsys, tmp_path):
    """The estimate is not shown for scans below the threshold; the
    composed actions are."""
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))
    monkeypatch.setattr('socket.getaddrinfo',
                        mock.Mock(side_effect=socket.gaierror('no dns')))
    store = tmp_path / "store"

    with pytest.raises(SystemExit):
        Interpreter.do_ssh_rescan(
            make_interpreter(),
            rescan_args(eval=True, known_hosts_file=str(store),
                        hosts=["multi", "solo"]))

    out = capsys.readouterr().out
    assert "ssh-keygen" in out
    assert "Scanning 3 hosts" not in out


def test_do_ssh_rescan_skips_the_estimate_for_short_scans(
        monkeypatch, stub_project, fake_tools, capsys):
    """A scan of a few hosts is fast enough for interactive
    operation; no estimate is printed for it."""
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))

    with pytest.raises(SystemExit):
        Interpreter.do_ssh_rescan(
            make_interpreter(),
            rescan_args(eval=True, hosts=["multi", "solo"]))

    assert "estimated time" not in capsys.readouterr().out


def test_do_ssh_rescan_prints_the_estimate_for_long_scans(
        monkeypatch, stub_project, fake_tools, capsys):
    """A scan of a hundred hosts crosses the three minute threshold
    and the estimate is shown."""
    stub_the_project(monkeypatch, stub_project(
        raw={"binaries": dict(fake_tools["binaries"])}))
    monkeypatch.setattr('socket.getaddrinfo',
                        mock.Mock(side_effect=socket.gaierror('no dns')))

    with pytest.raises(SystemExit):
        Interpreter.do_ssh_rescan(
            make_interpreter(), rescan_args(eval=True, hosts=["many"]))

    out = capsys.readouterr().out
    assert "Scanning 100 hosts" in out
    assert "estimated time: 3 minutes" in out
