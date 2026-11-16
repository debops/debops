# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures shared by the unit tests."""

import configparser
import os
import shlex
import stat

import pytest

from debops import set_project_context
from debops.core.config import Configuration

HOST_VARS = ('{"ansible_host": "192.0.2.10", "ansible_user": "admin", '
             '"ansible_port": 2222,'
             ' "ansible_ssh_private_key_file": "/keys/web",'
             ' "ansible_ssh_common_args": "-J jump@bastion",'
             ' "ansible_ssh_extra_args": "-o Foo=1"}')

FAKE_KEY = "|1|hashed|key| ssh-ed25519 AAAAfakekey"


def write_fake_binary(path, body):
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP
               | stat.S_IXOTH)
    return str(path)


@pytest.fixture
def fake_binary(tmp_path):
    """Write a fake executable into the temporary directory."""
    def _make(name, body):
        return write_fake_binary(tmp_path / name, body)
    return _make


@pytest.fixture
def inventory_fake(fake_binary):
    """Return a builder of an 'ansible-inventory' fake which answers
    the '--host' mode and the '--list --limit' mode alike: the
    '--list' dump carries the given variables as the hostvars of the
    'web' host, whatever pattern it is asked for."""
    def build(name, hostvars_json):
        return fake_binary(
            name,
            "#!/bin/sh\n"
            'if [ "$1" = "--list" ]; then\n'
            "    printf '%s' '{\"all\": {\"hosts\": [\"web\"]}, "
            "\"_meta\": {\"hostvars\": {\"web\": "
            + hostvars_json + "}}}'\n"
            "else\n"
            "    printf '%s' '" + hostvars_json + "'\n"
            "fi\n")
    return build


@pytest.fixture
def fake_tools(tmp_path):
    """Fake external tools: an inventory which knows the 'web' host and
    rejects everything else, an 'ansible' which answers the
    '--list-hosts' expansion, a key scan which answers for 'web' and
    its address only, and a key removal which logs its arguments. The
    'binaries' dict uses the configuration keys the library reads."""
    log = tmp_path / "keygen.log"

    inventory = write_fake_binary(tmp_path / "fake-ansible-inventory",
                                  "#!/bin/sh\n"
                                  'if [ "$1" = "--host" ]; then\n'
                                  'if [ "$2" = "web" ]; then\n'
                                  "    printf '%s' '" + HOST_VARS + "'\n"
                                  "else\n"
                                  "    echo 'ERROR! You must pass a single "
                                  "valid host to --host parameter' >&2\n"
                                  "    exit 5\n"
                                  "fi\n"
                                  'elif [ "$1" = "--list" ]; then\n'
                                  'case "$3" in\n'
                                  '"broken")\n'
                                  "    echo 'the expansion failed' >&2\n"
                                  "    exit 3\n"
                                  "    ;;\n"
                                  '"multi")\n'
                                  "    printf '%s' '{\"all\": "
                                  "{\"hosts\": [\"web-1\", \"web-2\"]}, "
                                  "\"_meta\": "
                                  "{\"hostvars\": {\"web-1\": {}, "
                                  "\"web-2\": {}}}}'\n"
                                  "    ;;\n"
                                  '"solo")\n'
                                  "    printf '%s' '{\"all\": "
                                  "{\"hosts\": [\"web-3\"]}, "
                                  "\"_meta\": "
                                  "{\"hostvars\": {\"web-3\": {}}}}'\n"
                                  "    ;;\n"
                                  '"web")\n'
                                  "    printf '%s' '{\"all\": "
                                  "{\"hosts\": [\"web\"]}, "
                                  "\"_meta\": "
                                  "{\"hostvars\": {\"web\": "
                                  + HOST_VARS + "}}}'\n"
                                  "    ;;\n"
                                  '"many")\n'
                                  "    printf '%s' '{\"all\": "
                                  "{\"hosts\": ['\n"
                                  "    first=1\n"
                                  "    i=1\n"
                                  "    while [ \"$i\" -le 100 ]; do\n"
                                  "        if [ \"$first\" = 0 ]; then\n"
                                  "            printf '%s' ', '\n"
                                  "        fi\n"
                                  "        printf '\"many-host-%s\"' "
                                  "\"$i\"\n"
                                  "        first=0\n"
                                  "        i=$((i+1))\n"
                                  "    done\n"
                                  "    printf '%s' ']}, \"_meta\": "
                                  "{\"hostvars\": {}}}'\n"
                                  "    ;;\n"
                                  "*)\n"
                                  "    printf '%s' '{\"_meta\": "
                                  "{\"hostvars\": {}}}'\n"
                                  "    ;;\n"
                                  "esac\n"
                                  "fi\n")
    keygen = write_fake_binary(tmp_path / "fake-ssh-keygen",
                               "#!/bin/sh\n"
                               "printf '%s\\n' \"$*\" >> "
                               + shlex.quote(str(log)) + "\n")
    keyscan = write_fake_binary(tmp_path / "fake-ssh-keyscan",
                                "#!/bin/sh\n"
                                'for name in "$@"; do\n'
                                '    if [ "$name" = "web" ] || '
                                '[ "$name" = "192.0.2.10" ]; then\n'
                                "        printf '%s\\n' '" + FAKE_KEY
                                + "'\n"
                                "    fi\n"
                                "done\n")
    ansible = write_fake_binary(tmp_path / "fake-ansible",
                                "#!/bin/sh\n"
                                'if [ "$1" = "none" ]; then\n'
                                "    exit 0\n"
                                "fi\n"
                                'if [ "$1" = "broken" ]; then\n'
                                "    echo 'the expansion failed' >&2\n"
                                "    exit 3\n"
                                "fi\n"
                                'if [ "$1" = "solo" ]; then\n'
                                "    printf 'hosts (1):\\n    web-3\\n'\n"
                                "    exit 0\n"
                                "fi\n"
                                'if [ "$1" = "multi" ]; then\n'
                                "    printf 'hosts (2):\\n    web-1\\n"
                                "    web-2\\n'\n"
                                "    exit 0\n"
                                "fi\n"
                                'if [ "$1" = "web" ]; then\n'
                                "    printf 'hosts (1):\\n    web\\n'\n"
                                "    exit 0\n"
                                "fi\n"
                                'if [ "$1" = "many" ]; then\n'
                                "    printf 'hosts (100):\\n'\n"
                                "    i=1\n"
                                "    while [ $i -le 100 ]; do\n"
                                "        printf '    many-host-%s\\n' \"$i\"\n"
                                "        i=$((i+1))\n"
                                "    done\n"
                                "    exit 0\n"
                                "fi\n"
                                "exit 0\n")
    return {
        "binaries": {"ansible": ansible, "ansible-inventory": inventory,
                     "ssh-keygen": keygen, "ssh-keyscan": keyscan,
                     "ssh": "/usr/bin/ssh",
                     "scp": "/usr/bin/scp", "sftp": "/usr/bin/sftp"},
        "log": str(log),
    }


@pytest.fixture(autouse=True)
def _clear_project_context():
    """Keep the project context from leaking between tests: project
    constructions set it, and only the tests which assert on it should
    see it."""
    set_project_context(None, None)
    yield
    set_project_context(None, None)


class StubConfig:
    """The parts of ``debops.core.config.Configuration`` the runners read."""

    def __init__(self, raw=None, env_vars=None):
        self.raw = raw if raw is not None else {}
        self._env_vars = env_vars if env_vars is not None else {}


class StubAnsibleConfig:
    """A stand-in for ``debops.core.ansible.ansibleconfig.AnsibleConfig``.

    ``get_option`` returns the configured value, or raises ``NoOptionError``
    for an unknown option. Passing *error* makes every call raise that
    exception instead, which is how the missing-section paths are tested.
    """

    def __init__(self, path, options=None, error=None):
        self.path = str(path)
        self._options = options if options is not None else {}
        self._error = error

    def get_option(self, option, section="defaults"):
        if self._error is not None:
            raise self._error
        if option in self._options:
            return self._options[option]
        raise configparser.NoOptionError(option, section)


class StubProject:
    """The minimum project a runner reads from its constructor."""

    def __init__(self, path, view="system", project_type="legacy",
                 config=None, ansible_cfg=None):
        self.path = str(path)
        self.name = os.path.basename(self.path)
        self.view = view
        self.project_type = project_type
        self.config = config if config is not None else StubConfig()
        self.ansible_cfg = ansible_cfg

    def environment(self):
        """The environment a project command runs in, composed the way
        the real ProjectDir composes it."""
        env = os.environ.copy()
        env.update(self.config._env_vars)
        return env


DEFAULT_BINARIES = {
    "ansible": "ansible",
    "ansible-playbook": "ansible-playbook",
    "git": "git",
    "git-crypt": "git-crypt",
    "gpg": "gpg",
    "encfs": "encfs",
    "umount": "umount",
    "fusermount": "fusermount",
}


@pytest.fixture
def stub_project(tmp_path):
    """Build a project a runner can be constructed with.

    The constructor of the runners is exercised; the inventory and the
    actual Ansible execution are replaced in the tests themselves.
    """
    def _make(inventory="ansible/inventory", collections="", config=None,
              project_type="legacy", view="system", cfg_options=None,
              cfg_error=None, env_vars=None, raw=None):
        if cfg_options is None:
            cfg_options = {"inventory": inventory,
                           "collections_path": collections}
        ansible_cfg = StubAnsibleConfig(tmp_path / "ansible.cfg",
                                        options=cfg_options,
                                        error=cfg_error)

        if config is None:
            full_raw = {"binaries": dict(DEFAULT_BINARIES),
                        "project": {}, "views": {}}
            if raw:
                for key, value in raw.items():
                    if key == "binaries":
                        full_raw["binaries"].update(value)
                    else:
                        full_raw[key] = value
            config = StubConfig(raw=full_raw, env_vars=env_vars)
        elif env_vars is not None:
            config._env_vars = env_vars

        return StubProject(tmp_path, view=view, project_type=project_type,
                           config=config, ansible_cfg=ansible_cfg)

    return _make


@pytest.fixture
def gpg_stub(tmp_path):
    """A stub gpg binary whose encryption probes fail or succeed on
    demand.

    Returns a factory: ``gpg_stub(exit_code=0, message='',
    fail_from=1) -> path``. Each probe invocation is counted, so a stub
    can accept the first recipients and refuse from the Nth one on.
    """
    bin_dir = tmp_path / "bin"
    counter = tmp_path / "probe-count"
    bin_dir.mkdir(exist_ok=True)

    def _make(exit_code=0, message="", fail_from=1):
        stub = bin_dir / "gpg"
        stub.write_text(
            "#!/bin/sh\n"
            "count=$(cat {} 2>/dev/null || echo 0)\n"
            "count=$((count + 1))\n"
            "echo $count > {}\n"
            "printf '%s' '{}' >&2\n"
            "if [ $count -ge {} ]; then\n"
            "  exit {}\n"
            "fi\n"
            "exit 0\n".format(counter, counter, message, fail_from,
                              exit_code))
        stub.chmod(0o755)
        return str(stub)

    return _make


@pytest.fixture
def configuration():
    """A Configuration with none of its filesystem or environment access.

    The real constructor reads ``/etc``, the user's XDG directories and the
    packaged defaults. The unit tests only need the in-memory state that the
    methods under test operate on, so the object is built without running
    ``__init__``.
    """
    config = Configuration.__new__(Configuration)
    config._config = {}
    config._config_files = []
    config._env_files = []
    config._env_overrides = []
    config._violations = []
    config._layers = []
    config._schema_source = "debops"
    config._schema_instance = None
    config._env_prefix = "DEBOPS_CONFIG__"
    config._env_vars = {}
    return config
