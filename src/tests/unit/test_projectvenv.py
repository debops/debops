# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the project Python virtual environment in ``debops.projectvenv``.

The ``venv``, ``pip`` and ``ansible-galaxy`` commands are replaced with
stubs; the file operations run against temporary directories.
"""

import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

import json

import debops.projectvenv as projectvenv_module
from debops.projectvenv import (EXTERNAL_DEPS, ProjectVenv,
                                comment_external_deps,
                                find_missing_external_deps,
                                seed_names, seed_requirements)


DEFAULT_RAW = {
    "binaries": {"ansible-galaxy": "ansible-galaxy"},
    "project": {"venv": {"enabled": True}},
}


def make_project(tmp_path, raw=None, project_type="modern"):
    return SimpleNamespace(
        path=str(tmp_path),
        project_type=project_type,
        auto_commit=mock.Mock(),
        config=SimpleNamespace(
            raw=raw if raw is not None else dict(DEFAULT_RAW)))


def make_venv(tmp_path, raw=None, **kwargs):
    return ProjectVenv(make_project(tmp_path, raw=raw, **kwargs))


def fake_venv_python(venv):
    """Create the file which marks an existing virtual environment."""
    bin_dir = os.path.join(venv.venv_path, "bin")
    os.makedirs(bin_dir)
    open(os.path.join(bin_dir, "python"), "w").close()


def test_seed_requirements_list_the_ansible_packages():
    names = seed_names()

    assert "ansible" in names
    assert "ansible-core" in names
    assert "cryptography" in names


def test_seed_names_strip_comments_and_version_specifiers(monkeypatch):
    monkeypatch.setattr(projectvenv_module, "seed_requirements",
                        lambda: ("# comment\n\nansible>=9\nnetaddr[extras]\n"
                                 "toml # inline comment\n"))

    assert seed_names() == ["ansible", "netaddr", "toml"]


def test_requires_a_modern_project(tmp_path):
    with pytest.raises(ValueError, match="modern"):
        make_venv(tmp_path, project_type="legacy")


def test_requires_the_venv_to_be_enabled(tmp_path):
    raw = {"project": {"venv": {"enabled": False}}}

    with pytest.raises(ValueError, match="not enabled"):
        make_venv(tmp_path, raw=raw)


def test_paths_come_from_the_configuration(tmp_path):
    raw = {"binaries": {},
           "project": {"venv": {"enabled": True,
                                "path": "custom/venv",
                                "requirements": "custom/requirements.txt",
                                "python": "python3.12"}}}
    venv = make_venv(tmp_path, raw=raw)

    assert venv.venv_path == str(tmp_path / "custom" / "venv")
    assert venv.requirements_path == str(tmp_path / "custom"
                                         / "requirements.txt")
    assert venv.interpreter == "python3.12"


def test_exists_detects_the_environment(tmp_path):
    venv = make_venv(tmp_path)
    assert venv.exists() is False

    fake_venv_python(venv)

    assert venv.exists() is True


def test_create_builds_the_environment(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)

    assert venv.create() is True

    python = os.path.join(venv.venv_path, "bin", "python")
    assert run.call_args_list[0].args[0] == ["python3", "-m", "venv",
                                             venv.venv_path]
    assert run.call_args_list[1].args[0] == [python, "-m", "pip", "install",
                                             "--upgrade", "pip"]


def test_create_is_a_noop_when_the_environment_exists(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)

    assert venv.create() is False
    run.assert_not_called()


def test_create_reports_a_failure(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    monkeypatch.setattr(ProjectVenv, "_run", mock.Mock(return_value=1))

    with pytest.raises(ChildProcessError):
        venv.create()


def test_install_creates_and_installs_the_environment(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    freeze = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "freeze", freeze)
    collections = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "install_collections", collections)
    monkeypatch.setattr(projectvenv_module, "find_missing_external_deps",
                        mock.Mock(return_value={}))

    venv.install()

    python = os.path.join(venv.venv_path, "bin", "python")
    run.assert_any_call([python, "-m", "pip", "install", "-r",
                         venv.requirements_path])
    freeze.assert_called_once_with("all")
    collections.assert_called_once_with()

    # The requirements file was seeded before the installation
    assert os.path.isfile(venv.requirements_path)
    assert "ansible-core" in open(venv.requirements_path).read()


def test_install_keeps_an_existing_requirements_file(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    os.makedirs(os.path.dirname(venv.requirements_path))
    with open(venv.requirements_path, "w") as fh:
        fh.write("netaddr\n")
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    monkeypatch.setattr(ProjectVenv, "freeze", mock.Mock())
    monkeypatch.setattr(ProjectVenv, "install_collections", mock.Mock())

    venv.install(scope="python")

    assert open(venv.requirements_path).read() == "netaddr\n"


@pytest.mark.parametrize("scope", ["python", "collections", "all"])
def test_install_honors_the_scope(tmp_path, monkeypatch, scope):
    venv = make_venv(tmp_path)
    monkeypatch.setattr(ProjectVenv, "_run", mock.Mock(return_value=0))
    freeze = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "freeze", freeze)
    collections = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "install_collections", collections)
    monkeypatch.setattr(projectvenv_module, "find_missing_external_deps",
                        mock.Mock(return_value={}))

    venv.install(scope=scope)

    freeze.assert_called_once_with(scope)
    assert collections.called == (scope in ("collections", "all"))


def test_install_rejects_an_unknown_scope(tmp_path):
    venv = make_venv(tmp_path)

    with pytest.raises(ValueError, match="scope"):
        venv.install(scope="bogus")


def test_upgrade_requires_an_existing_environment(tmp_path):
    venv = make_venv(tmp_path)

    with pytest.raises(FileNotFoundError, match="does not exist"):
        venv.upgrade()


def test_upgrade_moves_only_the_seed_packages_in_the_lock(tmp_path,
                                                          monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    os.makedirs(os.path.dirname(venv.requirements_path), exist_ok=True)
    with open(venv.requirements_path, "w") as fh:
        # 'ansible' and 'netaddr' are in the seed, 'jmespath' is not
        fh.write("ansible==12.3.0\njmespath==1.0.1\nnetaddr==1.3.0\n")
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    freeze = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "freeze", freeze)
    collections = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "install_collections", collections)

    venv.upgrade()

    python = os.path.join(venv.venv_path, "bin", "python")
    argv = run.call_args.args[0]
    assert argv[:5] == [python, "-m", "pip", "install", "--upgrade"]
    # Seed packages present in the lock are upgraded, in the seed order;
    # 'jmespath' and seed packages not in the lock are left alone
    assert argv[5:] == ["ansible", "netaddr"]
    freeze.assert_called_once_with("all")
    collections.assert_called_once_with(upgrade=True)


def test_upgrade_without_seed_packages_in_the_lock_only_freezes(
        tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    os.makedirs(os.path.dirname(venv.requirements_path), exist_ok=True)
    with open(venv.requirements_path, "w") as fh:
        fh.write("jmespath==1.0.1\n")
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    freeze = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "freeze", freeze)
    monkeypatch.setattr(ProjectVenv, "install_collections", mock.Mock())

    venv.upgrade(scope="python")

    run.assert_not_called()
    freeze.assert_called_once_with("python")


def test_recreate_replaces_the_environment(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    install = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "install", install)

    venv.recreate()

    assert not os.path.exists(venv.venv_path)
    install.assert_called_once_with(scope="all")


def test_recreate_reinstalls_the_collections(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    collections = tmp_path / "ansible" / "collections" / "ansible_collections"
    collections.mkdir(parents=True)
    (collections / "sentinel").touch()
    install = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "install", install)

    venv.recreate(scope="collections")

    assert not collections.exists()
    assert (tmp_path / "ansible" / "collections").exists()
    install.assert_called_once_with(scope="collections")


def test_freeze_writes_the_pinned_versions(tmp_path, monkeypatch, capsys):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    process = mock.Mock()
    process.communicate.return_value = (b"ansible==9.0.1\nnetaddr==1.3.0\n",
                                        b"")
    process.returncode = 0
    monkeypatch.setattr(projectvenv_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    freeze_collections = mock.Mock()
    monkeypatch.setattr(ProjectVenv, "freeze_collections",
                        freeze_collections)

    venv.freeze()

    with open(venv.requirements_path) as fh:
        content = fh.read()
    assert "debops project venv" in content
    assert "ansible==9.0.1\n" in content
    assert "netaddr==1.3.0\n" in content
    venv.project.auto_commit.assert_called_once_with()
    assert "Writing the pinned Python package versions to" in \
        capsys.readouterr().out


def test_freeze_requires_an_existing_environment(tmp_path):
    venv = make_venv(tmp_path)

    with pytest.raises(FileNotFoundError, match="does not exist"):
        venv.freeze()


def test_freeze_reports_a_failure(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    process = mock.Mock()
    process.communicate.return_value = (b"", b"boom")
    process.returncode = 1
    monkeypatch.setattr(projectvenv_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    monkeypatch.setattr(ProjectVenv, "freeze_collections", mock.Mock())

    with pytest.raises(ChildProcessError):
        venv.freeze()
    venv.project.auto_commit.assert_not_called()


def test_install_collections_uses_the_galaxy_binary(tmp_path, monkeypatch):
    requirements = tmp_path / "ansible" / "collections" / "requirements.yml"
    requirements.parent.mkdir(parents=True)
    requirements.write_text("---\ncollections: []\n")
    raw = {"binaries": {"ansible-galaxy": "/venv/bin/ansible-galaxy"},
           "project": {"venv": {"enabled": True}}}
    venv = make_venv(tmp_path, raw=raw)
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="/venv/bin/ansible-galaxy"))

    venv.install_collections()

    assert run.call_args.args[0] == [
            "/venv/bin/ansible-galaxy", "collection", "install", "-r",
            str(requirements)]


def test_install_collections_force_installs_on_upgrade(tmp_path, monkeypatch):
    requirements = tmp_path / "ansible" / "collections" / "requirements.yml"
    requirements.parent.mkdir(parents=True)
    requirements.write_text("---\ncollections: []\n")
    venv = make_venv(tmp_path)
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    venv.install_collections(upgrade=True)

    assert "--force" in run.call_args.args[0]


def test_install_collections_requires_the_galaxy_binary(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value=None))

    with pytest.raises(FileNotFoundError, match="not available"):
        venv.install_collections()


def test_install_collections_requires_the_requirements_file(tmp_path,
                                                            monkeypatch):
    venv = make_venv(tmp_path)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    with pytest.raises(FileNotFoundError, match="requirements"):
        venv.install_collections()


def test_install_collections_reports_a_failure(tmp_path, monkeypatch):
    requirements = tmp_path / "ansible" / "collections" / "requirements.yml"
    requirements.parent.mkdir(parents=True)
    requirements.write_text("---\ncollections: []\n")
    venv = make_venv(tmp_path)
    monkeypatch.setattr(ProjectVenv, "_run", mock.Mock(return_value=1))
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    with pytest.raises(ChildProcessError):
        venv.install_collections()


def make_include_dir(tmp_path):
    """A directory tree with all of the files the detection looks for."""
    include = tmp_path / "include"
    (include / "sasl").mkdir(parents=True)
    (include / "Python.h").touch()
    (include / "ldap.h").touch()
    (include / "sasl" / "sasl.h").touch()
    return include


def test_os_family_detects_macos(monkeypatch):
    monkeypatch.setattr(projectvenv_module.platform, "system",
                        lambda: "Darwin")

    assert projectvenv_module._os_family() == "macos"


def test_os_family_uses_the_distro_lineage(monkeypatch):
    monkeypatch.setattr(projectvenv_module.platform, "system",
                        lambda: "Linux")
    monkeypatch.setattr(projectvenv_module.distro, "id", lambda: "ubuntu")
    monkeypatch.setattr(projectvenv_module.distro, "like", lambda: "debian")

    assert projectvenv_module._os_family() == "debian"


def test_os_family_is_none_for_an_unknown_linux(monkeypatch):
    monkeypatch.setattr(projectvenv_module.platform, "system",
                        lambda: "Linux")
    monkeypatch.setattr(projectvenv_module.distro, "id", lambda: "gentoo")
    monkeypatch.setattr(projectvenv_module.distro, "like", lambda: "")

    assert projectvenv_module._os_family() is None


def test_find_missing_ignores_packages_without_external_deps():
    assert find_missing_external_deps(["toml", "netaddr"]) == {}


def test_find_missing_when_everything_is_present(tmp_path, monkeypatch):
    include = make_include_dir(tmp_path)
    monkeypatch.setattr(projectvenv_module, "_has_compiler", lambda: True)
    monkeypatch.setattr(projectvenv_module, "_python_include_dir",
                        lambda interpreter: str(include))
    monkeypatch.setattr(projectvenv_module, "_header_dirs",
                        lambda: [str(include)])

    assert find_missing_external_deps(["python-ldap"]) == {}


@pytest.mark.parametrize("broken", ["compiler", "python_h", "ldap", "sasl"])
def test_find_missing_flags_python_ldap(tmp_path, monkeypatch, broken):
    include = make_include_dir(tmp_path)
    if broken == "python_h":
        (include / "Python.h").unlink()
    elif broken == "ldap":
        (include / "ldap.h").unlink()
    elif broken == "sasl":
        (include / "sasl" / "sasl.h").unlink()
    monkeypatch.setattr(projectvenv_module, "_has_compiler",
                        lambda: broken != "compiler")
    monkeypatch.setattr(projectvenv_module, "_python_include_dir",
                        lambda interpreter: str(include))
    monkeypatch.setattr(projectvenv_module, "_header_dirs",
                        lambda: [str(include)])

    missing = find_missing_external_deps(["python-ldap", "toml"])

    assert list(missing) == ["python-ldap"]
    assert missing["python-ldap"] is EXTERNAL_DEPS["python-ldap"]


def test_find_missing_checks_the_target_interpreter(tmp_path, monkeypatch):
    include = make_include_dir(tmp_path)
    seen = {}

    def fake_include_dir(interpreter):
        seen["interpreter"] = interpreter
        return str(include)

    monkeypatch.setattr(projectvenv_module, "_has_compiler", lambda: True)
    monkeypatch.setattr(projectvenv_module, "_python_include_dir",
                        fake_include_dir)
    monkeypatch.setattr(projectvenv_module, "_header_dirs",
                        lambda: [str(include)])

    find_missing_external_deps(["python-ldap"], interpreter="python3.12")

    assert seen["interpreter"] == "python3.12"


def test_find_missing_without_an_interpreter(tmp_path, monkeypatch):
    monkeypatch.setattr(projectvenv_module, "_has_compiler", lambda: True)
    monkeypatch.setattr(projectvenv_module, "_python_include_dir",
                        lambda interpreter: None)
    monkeypatch.setattr(projectvenv_module, "_header_dirs",
                        lambda: [str(make_include_dir(tmp_path))])

    assert list(find_missing_external_deps(["python-ldap"])) == [
        "python-ldap"]


def test_comment_external_deps_replaces_the_package(monkeypatch):
    monkeypatch.setattr(projectvenv_module, "_os_family", lambda: "debian")
    content = "netaddr\npython-ldap\ntoml\n"

    result = comment_external_deps(
            content, {"python-ldap": EXTERNAL_DEPS["python-ldap"]})

    lines = result.splitlines()
    assert "netaddr" in lines
    assert "toml" in lines
    assert "python-ldap" not in lines
    assert "#python-ldap" in lines
    assert "# Skipped: python-ldap needs" in result
    assert "sudo apt install build-essential" in result
    assert '"debops project venv install"' in result
    # The explanation goes above the commented-out package
    assert result.index("# Skipped") < result.index("#python-ldap")
    # The comment lines stay within a readable width
    assert all(len(line) <= 78 for line in result.splitlines())


def test_comment_external_deps_keeps_the_trailing_newline(monkeypatch):
    monkeypatch.setattr(projectvenv_module, "_os_family", lambda: "debian")
    missing = {"python-ldap": EXTERNAL_DEPS["python-ldap"]}

    assert comment_external_deps("python-ldap\n", missing).endswith("\n")
    assert not comment_external_deps("python-ldap", missing).endswith("\n")


def test_comment_external_deps_uses_the_macos_hint(monkeypatch):
    monkeypatch.setattr(projectvenv_module, "_os_family", lambda: "macos")

    result = comment_external_deps(
            "python-ldap\n", {"python-ldap": EXTERNAL_DEPS["python-ldap"]})

    # Flatten the wrapped comment lines before checking the hint
    flat = result.replace("\n# ", " ")
    assert "brew install openldap cyrus-sasl" in flat
    assert "keg-only" in flat


def test_comment_external_deps_has_a_generic_hint_for_unknown_systems(
        monkeypatch):
    monkeypatch.setattr(projectvenv_module, "_os_family", lambda: None)

    result = comment_external_deps(
            "python-ldap\n", {"python-ldap": EXTERNAL_DEPS["python-ldap"]})

    assert "system package manager" in result
    assert "apt install" not in result


def test_comment_external_deps_without_missing_packages():
    content = "netaddr\npython-ldap\n"

    assert comment_external_deps(content, {}) == content


def test_install_comments_out_missing_external_deps(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    monkeypatch.setattr(ProjectVenv, "_run", mock.Mock(return_value=0))
    monkeypatch.setattr(ProjectVenv, "freeze", mock.Mock())
    monkeypatch.setattr(ProjectVenv, "install_collections", mock.Mock())
    monkeypatch.setattr(projectvenv_module, "find_missing_external_deps",
                        mock.Mock(return_value={
                            "python-ldap": EXTERNAL_DEPS["python-ldap"]}))
    monkeypatch.setattr(projectvenv_module, "_os_family", lambda: "debian")

    venv.install(scope="python")

    with open(venv.requirements_path) as fh:
        content = fh.read()
    assert "\nansible\n" in content
    assert "#python-ldap" in content
    assert "# Skipped: python-ldap" in content


def test_freeze_readds_the_missing_external_dep_comments(tmp_path,
                                                         monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    process = mock.Mock()
    process.communicate.return_value = (b"ansible==12.3.0\ntoml==0.10.2\n",
                                        b"")
    process.returncode = 0
    monkeypatch.setattr(projectvenv_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    monkeypatch.setattr(ProjectVenv, "freeze_collections", mock.Mock())
    monkeypatch.setattr(projectvenv_module, "_os_family", lambda: "debian")

    venv.freeze()

    with open(venv.requirements_path) as fh:
        content = fh.read()
    assert "ansible==12.3.0\n" in content
    assert "#python-ldap" in content
    assert "# Skipped: python-ldap" in content


def test_freeze_omits_the_comment_for_installed_packages(tmp_path,
                                                         monkeypatch):
    venv = make_venv(tmp_path)
    fake_venv_python(venv)
    process = mock.Mock()
    process.communicate.return_value = (b"python-ldap==3.4.4\ntoml==0.10.2\n",
                                        b"")
    process.returncode = 0
    monkeypatch.setattr(projectvenv_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    monkeypatch.setattr(ProjectVenv, "freeze_collections", mock.Mock())

    venv.freeze()

    with open(venv.requirements_path) as fh:
        content = fh.read()
    assert "python-ldap==3.4.4\n" in content
    assert "#python-ldap" not in content
    assert "# Skipped" not in content


def write_collections_requirements(tmp_path, content):
    requirements = tmp_path / "ansible" / "collections" / "requirements.yml"
    requirements.parent.mkdir(parents=True)
    requirements.write_text(content)
    return requirements


def mock_installed_collections(venv, installed):
    """Make the venv report the given collection versions as installed."""
    venv._installed_collections = mock.Mock(return_value=installed)


def test_freeze_collections_pins_the_installed_versions(tmp_path,
                                                        monkeypatch,
                                                        capsys):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, (
            "---\ncollections:\n\n"
            "  - name: 'ansible.posix'\n    version: '*'\n\n"
            "  - name: 'debops.debops'\n    version: '3.3.2'\n"))
    mock_installed_collections(venv, {"ansible.posix": "2.1.0",
                                      "debops.debops": "3.3.2",
                                      "ansible._protomatter": "2.19.14"})

    venv.freeze_collections()

    content = Path(venv.collections_lock).read_text()
    assert "debops project venv freeze" in content
    assert "  - name: 'ansible.posix'\n    version: '2.1.0'\n" in content
    assert "  - name: 'debops.debops'\n    version: '3.3.2'\n" in content
    # Bundled collections from the 'ansible' package are not included
    assert "protomatter" not in content
    assert "Writing the Ansible Collection lock file" in \
        capsys.readouterr().out


def test_freeze_collections_prefers_the_project_copy(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path,
                                   "---\ncollections:\n"
                                   "  - name: 'ansible.posix'\n")
    mock_installed_collections(venv, {"ansible.posix": "2.1.0"})

    venv.freeze_collections()

    assert "version: '2.1.0'" in Path(venv.collections_lock).read_text()


def test_freeze_collections_preserves_non_galaxy_entries(tmp_path,
                                                         monkeypatch):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, (
            "---\ncollections:\n\n"
            "  - name: 'example.collection'\n"
            "    source: 'git+https://git.example.org/example/collection.git'"
            "\n"
            "    type: git\n"
            "    version: 'main'\n"))
    mock_installed_collections(venv, {"example.collection": "1.2.3"})

    venv.freeze_collections()

    content = Path(venv.collections_lock).read_text()
    # The git ref is preserved as written, the installed version is recorded
    # in a comment
    assert "    source: 'git+https://git.example.org/example/collection.git'" in content
    assert "    type: 'git'\n" in content
    assert "    version: 'main'\n" in content
    assert "  # installed: 1.2.3\n" in content


def test_freeze_collections_preserves_url_named_git_entries(tmp_path,
                                                            monkeypatch):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, (
            "---\ncollections:\n\n"
            "  - name: 'https://git.example.org/example/collection.git'\n"
            "    type: git\n"
            "    version: 'main'\n"))
    mock_installed_collections(venv, {"example.collection": "1.2.3"})

    venv.freeze_collections()

    content = Path(venv.collections_lock).read_text()
    assert "  - name: 'https://git.example.org/example/collection.git'" in content
    # The installed version cannot be mapped back to the URL, so no comment
    assert "# installed:" not in content


def test_freeze_collections_skips_uninstalled_entries(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, (
            "---\ncollections:\n\n"
            "  - name: 'ansible.posix'\n\n"
            "  - name: 'debops.debops'\n"))
    mock_installed_collections(venv, {"debops.debops": "3.3.2"})

    venv.freeze_collections()

    content = Path(venv.collections_lock).read_text()
    assert "ansible.posix" not in content
    assert "debops.debops" in content


def test_freeze_collections_writes_nothing_without_requirements(tmp_path,
                                                                monkeypatch):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, "---\ncollections: []\n")

    venv.freeze_collections()

    assert not Path(venv.collections_lock).exists()


def test_freeze_collections_reports_a_list_failure(tmp_path, monkeypatch):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path,
                                   "---\ncollections:\n"
                                   "  - name: 'ansible.posix'\n")
    process = mock.Mock()
    process.communicate.return_value = (b"", b"boom")
    process.returncode = 1
    monkeypatch.setattr(projectvenv_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    with pytest.raises(ChildProcessError):
        venv.freeze_collections()


def test_installed_collections_prefers_the_project_copy(tmp_path,
                                                        monkeypatch):
    venv = make_venv(tmp_path)
    listing = json.dumps({
            str(tmp_path / "other" / "ansible_collections"): {
                "ansible.posix": {"version": "9.9.9"}},
            str(tmp_path / "ansible" / "collections"
                / "ansible_collections"): {
                "ansible.posix": {"version": "2.1.0"}},
            str(tmp_path / "venv" / "lib" / "ansible_collections"): {
                "ansible._protomatter": {"version": "2.19.14"}},
    }).encode("utf-8")
    process = mock.Mock()
    process.communicate.return_value = (listing, b"")
    process.returncode = 0
    monkeypatch.setattr(projectvenv_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    installed = venv._installed_collections()

    assert installed == {"ansible.posix": "2.1.0",
                         "ansible._protomatter": "2.19.14"}


def test_install_collections_uses_the_lock_file_first(tmp_path, monkeypatch,
                                                      capsys):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, "---\ncollections: []\n")
    Path(venv.collections_lock).write_text("---\ncollections: []\n")
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    venv.install_collections()

    calls = [call.args[0] for call in run.call_args_list]
    assert calls[0][-1] == venv.collections_lock
    assert calls[1][-1] == venv.collections_requirements
    assert "--force" not in calls[1]

    # Each processed file is announced, in order
    out = capsys.readouterr().out
    lock_msg = "from the lock file, " + venv.collections_lock
    req_msg = "from " + venv.collections_requirements
    assert lock_msg in out
    assert req_msg in out
    assert out.index(lock_msg) < out.index(req_msg)


def test_install_collections_skips_a_missing_lock_file(tmp_path, monkeypatch,
                                                       capsys):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, "---\ncollections: []\n")
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    venv.install_collections()

    assert run.call_count == 1
    assert run.call_args.args[0][-1] == venv.collections_requirements

    out = capsys.readouterr().out
    assert "from the lock file" not in out
    assert "from " + venv.collections_requirements in out


def test_install_collections_upgrade_ignores_the_lock_file(tmp_path,
                                                           monkeypatch,
                                                           capsys):
    venv = make_venv(tmp_path)
    write_collections_requirements(tmp_path, "---\ncollections: []\n")
    Path(venv.collections_lock).write_text("---\ncollections: []\n")
    run = mock.Mock(return_value=0)
    monkeypatch.setattr(ProjectVenv, "_run", run)
    monkeypatch.setattr(projectvenv_module.shutil, "which",
                        mock.Mock(return_value="ansible-galaxy"))

    venv.install_collections(upgrade=True)

    assert run.call_count == 1
    argv = run.call_args.args[0]
    assert venv.collections_requirements in argv
    assert "--force" in argv
    assert "Force-upgrading Ansible Collections" in capsys.readouterr().out
