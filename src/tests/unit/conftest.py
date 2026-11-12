# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures shared by the unit tests."""

import configparser
import os

import pytest

from debops import set_project_context
from debops.core.config import Configuration


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

    def get_option(self, option):
        if self._error is not None:
            raise self._error
        if option in self._options:
            return self._options[option]
        raise configparser.NoOptionError(option, "defaults")


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
              cfg_error=None, env_vars=None):
        if cfg_options is None:
            cfg_options = {"inventory": inventory,
                           "collections_path": collections}
        ansible_cfg = StubAnsibleConfig(tmp_path / "ansible.cfg",
                                        options=cfg_options,
                                        error=cfg_error)

        if config is None:
            config = StubConfig(raw={"binaries": dict(DEFAULT_BINARIES),
                                     "project": {},
                                     "views": {}},
                                env_vars=env_vars)
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
    config._env_vars = {}
    return config
