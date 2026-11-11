# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.utils``."""

import re

import pytest

from debops.core import utils


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


def test_write_file_without_a_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert utils.write_file("file.txt", "hello\n") is True
    assert (tmp_path / "file.txt").read_text() == "hello\n"


def test_write_file_inside_the_project(tmp_path):
    project = tmp_path / "project"
    target = project / "generated" / "file.txt"

    assert utils.write_file(str(target), "hello\n",
                            project=str(project)) is True
    assert target.read_text() == "hello\n"


def test_write_file_refuses_a_target_outside_the_project(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    project = tmp_path / "project"

    with pytest.raises(ValueError):
        utils.write_file(str(outside / "file.txt"), "hello\n",
                         project=str(project))


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


def test_path_key_separates_same_named_projects(tmp_path):
    # The path hash distinguishes two projects whose directories share a name
    first = tmp_path / "alpha" / "web"
    second = tmp_path / "beta" / "web"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    assert utils.path_key(str(first), "web") != utils.path_key(str(second), "web")


def test_path_key_separates_the_views_of_one_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    assert (utils.path_key(str(project), "project", "prod")
            != utils.path_key(str(project), "project", "stage"))


def test_path_key_resolves_symlinks_to_the_real_project(tmp_path):
    # A project reached through a symlink is the same project
    real = tmp_path / "real"
    link = tmp_path / "link"
    real.mkdir()
    link.symlink_to(real)
    assert utils.path_key(str(real), "proj") == utils.path_key(str(link), "proj")


def test_path_key_sanitizes_the_name_and_the_view(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    key = utils.path_key(str(project), "web server/!", "prod env")
    tail = key.split("-", 1)[1]
    assert re.fullmatch(r"[A-Za-z0-9._-]+(-[A-Za-z0-9._-]+)?", tail)


def test_path_key_without_a_view_names_the_project_alone(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    key = utils.path_key(str(project), "project")
    assert key == utils.path_key(str(project), "project", "")
    assert key.count("-") == 1  # the hash-name separator only


def test_path_key_extends_the_name_with_the_view(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    assert utils.path_key(str(project), "project", "prod").endswith("-prod")


def test_path_key_falls_back_when_the_name_is_empty(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    assert utils.path_key(str(project), "").endswith("-project")
    assert utils.path_key(str(project), None).endswith("-project")


def test_verify_gpg_recipients_accepts_a_working_key(gpg_stub):
    gpg = gpg_stub()
    utils.verify_gpg_recipients(gpg, "key@example.org")


def test_verify_gpg_recipients_rejects_an_unusable_key(gpg_stub):
    gpg = gpg_stub(exit_code=2, message="gpg: Unusable public key")

    with pytest.raises(ValueError, match="Unusable public key"):
        utils.verify_gpg_recipients(gpg, "broken@example.org")


def test_verify_gpg_recipients_names_the_recipient(gpg_stub):
    gpg = gpg_stub(exit_code=2, message="gpg: Unusable public key")

    with pytest.raises(ValueError, match='"broken@example.org"'):
        utils.verify_gpg_recipients(gpg, "broken@example.org")


def test_verify_gpg_recipients_indents_a_multiline_error(gpg_stub):
    gpg = gpg_stub(exit_code=2, message="first line\nsecond line")

    with pytest.raises(ValueError) as caught:
        utils.verify_gpg_recipients(gpg, "broken@example.org")

    message = str(caught.value)
    assert message.startswith('The GPG key "broken@example.org" cannot '
                              'be used for encryption:\n')
    assert "\n  first line\n  second line" in message


def test_verify_gpg_recipients_checks_every_recipient(gpg_stub):
    # The first key passes the probe, the second one fails
    gpg = gpg_stub(exit_code=2, message="gpg: Unusable public key",
                   fail_from=2)

    with pytest.raises(ValueError, match='"second@example.org"'):
        utils.verify_gpg_recipients(
            gpg, "first@example.org,second@example.org")


def test_verify_gpg_recipients_requires_recipients(gpg_stub):
    gpg = gpg_stub()

    with pytest.raises(ValueError,
                       match="List of GPG recipients not specified"):
        utils.verify_gpg_recipients(gpg, None)
