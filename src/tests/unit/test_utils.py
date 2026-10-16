# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.utils``."""

import pytest

from debops import utils


@pytest.fixture
def home(monkeypatch, tmp_path):
    """A fake home directory the helpers can recognise."""
    home = str(tmp_path / "home")
    monkeypatch.setattr(utils, "DEBOPS_USER_HOME_DIR", home)
    return home


def test_unexpanduser_replaces_a_leading_home(home):
    assert utils.unexpanduser(home + "/file") == "~/file"


def test_unexpanduser_replaces_the_home_prefix_itself(home):
    assert utils.unexpanduser(home) == "~"


def test_unexpanduser_keeps_a_path_without_the_home(home):
    assert utils.unexpanduser("/etc/debops") == "/etc/debops"


def test_unexpanduser_ignores_the_home_in_the_middle(home):
    assert utils.unexpanduser("/opt" + home) == "/opt" + home


def test_unexpanduser_replaces_only_the_first_occurrence(home):
    # A symlinked home can otherwise appear more than once inside the path
    assert utils.unexpanduser(home + home) == "~" + home


@pytest.mark.parametrize("value", ["y", "yes", "on", "1", "true", "t"])
def test_strtobool_accepts_truthy_values(value):
    assert utils.strtobool(value) is True


@pytest.mark.parametrize("value", ["n", "no", "f", "false", "off", "0"])
def test_strtobool_accepts_falsy_values(value):
    assert utils.strtobool(value) is False


@pytest.mark.parametrize("value", ["Y", "YES", "On", "TRUE", "T"])
def test_strtobool_is_case_insensitive(value):
    assert utils.strtobool(value) is True


def test_strtobool_rejects_an_unknown_value():
    with pytest.raises(ValueError):
        utils.strtobool("maybe")


def test_write_file_creates_missing_directories(tmp_path):
    target = tmp_path / "a" / "b" / "file.txt"

    assert utils.write_file(str(target), "hello\n") is True
    assert target.read_text() == "hello\n"


def test_write_file_keeps_an_existing_file(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("mine\n")

    assert utils.write_file(str(target), "generated\n") is False
    assert target.read_text() == "mine\n"


def test_write_file_overwrites_when_asked(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("mine\n")

    assert utils.write_file(str(target), "generated\n", overwrite=True) is True
    assert target.read_text() == "generated\n"


def test_write_file_writes_empty_content(tmp_path):
    target = tmp_path / "empty"

    assert utils.write_file(str(target), "") is True
    assert target.read_text() == ""


def test_host_is_controller_on_debian(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(utils.distro, "id", lambda: "Debian")

    assert utils.host_is_controller() is True


def test_host_is_controller_accepts_ubuntu(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(utils.distro, "id", lambda: "Ubuntu")

    assert utils.host_is_controller() is True


def test_host_is_controller_is_case_insensitive(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(utils.distro, "id", lambda: "DEBIAN")

    assert utils.host_is_controller() is True


def test_host_is_controller_rejects_other_distributions(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(utils.distro, "id", lambda: "Fedora")

    assert utils.host_is_controller() is False


def test_host_is_controller_rejects_other_systems(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Darwin")

    def fail(**kwargs):
        raise AssertionError("the distribution must not be read off Linux")

    monkeypatch.setattr(utils.distro, "id", fail)

    assert utils.host_is_controller() is False
