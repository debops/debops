# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import fcntl
import hashlib
import json
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import time
from unittest import mock
import zipfile

import pytest

import debops.core.runner as runner_base_module
import debops.core.tofu.binary as binary_module
import debops.core.keyring as keyring_module
import debops.core.tofu.runner as runner_module
from debops.core.tofu import plans as plans_module
from debops.core.tofu.plans import plan_rows, resolve_plan_file
from debops.core.tofu.runner import TofuRunner
from debops.core.tofu.rekey import rekey_view
from debops.core.tofu.view import create_view, reconcile_view
from debops.core.tofu.providers import resolve_providers
from debops.core.tofu.modules import resolve_modules
from debops.core.secrets import SecretManager
from tests.unit.core.tofu_helpers import (
    RELEASE_KEY_FINGERPRINT, keyring_config, mkview, write_drop_in)


@pytest.fixture(autouse=True)
def patched_data_homes(tmp_path, monkeypatch):
    """The module-level XDG data homes of the binary and the keyring
    modules resolve under the test's tmp path: the managed binaries
    and the keyring homedir land inside the test's own data
    location."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(keyring_module, "xdg_data_home", str(tmp_path))


@pytest.mark.parametrize("known", ["", "  ", None, 1139])
def test_known_version_refuses_an_invalid_value(tofu_project, known):
    """The known-good version comes from the configuration only: an
    empty or non-string value refuses the view creation."""
    project = tofu_project(project_type="modern")
    project.config.raw['tofu']['upstream']['known_version'] = known

    with pytest.raises(ValueError, match="is not set"):
        binary_module.known_version(project)


def test_known_version_refuses_when_the_option_is_absent(tofu_project):
    """The known-good version option is configuration-only: a
    configuration without it refuses the view creation."""
    project = tofu_project(project_type="modern")
    del project.config.raw['tofu']['upstream']['known_version']

    with pytest.raises(ValueError, match="is not set"):
        binary_module.known_version(project)


def test_managed_binary_path_refuses_traversal_versions():
    """The managed binary paths compose from the version: a
    traversal-shaped value is refused instead of placing the binary
    outside the managed root -- or on the operator's PATH."""
    for version in ('../../../bin', '', None, '.hidden', 'a..b'):
        with pytest.raises(ValueError, match='version'):
            binary_module.managed_binary_path(version)


def test_managed_binary_path_accepts_release_versions():
    """The release version strings resolve inside the managed root."""
    managed = binary_module.managed_binary_path('1.13.9')
    assert managed.startswith(
        binary_module.binary_install_root() + os.sep)


def test_resolve_binary_runs_the_managed_binary(tofu_project, tmp_path,
                                                monkeypatch):
    """A view which pins a version runs the managed binary of that
    version when it is installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': version}}}})

    assert binary_module.resolve_binary(project, project.view) == managed


def test_resolve_binary_falls_back_when_the_pin_is_missing(
        tofu_project, tmp_path, monkeypatch):
    """A view which pins a version runs the configured binary when the
    managed binary of the version is not installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': "1.13.9"}}}})

    assert binary_module.resolve_binary(project, project.view) == "tofu"


def test_resolve_binary_leaves_a_hand_made_view_unmanaged(tofu_project):
    """A view without a recorded version runs the configured binary:
    the system-wide or user-wide installation, unmanaged."""
    project = tofu_project(project_type="modern")
    assert binary_module.resolve_binary(project, project.view) == "tofu"


def test_resolve_binary_refuses_when_no_installation_is_available(
        tofu_project):
    """When the configured binary is not available -- no system-wide
    or user-wide installation carries it -- the resolution fails:
    there is no OpenTofu binary to run."""
    project = tofu_project(project_type="modern")
    project.config.merge({'binaries': {'tofu': 'missing-tofu'}})

    with pytest.raises(ValueError, match="is not available"):
        binary_module.resolve_binary(project, project.view)


def test_resolve_binary_refuses_when_the_pin_is_missing_and_no_fallback(
        tofu_project, tmp_path, monkeypatch):
    """A view whose pinned binary is not installed falls back to the
    configured binary; when that is not available either, the
    resolution fails."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'binaries': {'tofu': 'missing-tofu'},
                          'views': {project.view: {'tofu': {
                              'binary_version': "1.13.9"}}}})

    with pytest.raises(ValueError, match="is not available"):
        binary_module.resolve_binary(project, project.view)


def test_effective_binary_runs_the_managed_binary(tofu_project, tmp_path,
                                                  monkeypatch):
    """The lenient resolution runs the managed binary of the version
    which the view pins, when it is installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': version}}}})

    assert binary_module.effective_binary(project, project.view) \
        == managed


def test_effective_binary_falls_back_without_refusing(tofu_project,
                                                      tmp_path,
                                                      monkeypatch):
    """The lenient resolution falls back to the configured binary
    when the pinned one is not installed, without refusing: the
    runtime configuration reports the effective binary, the runner
    enforces."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': "1.13.9"}}}})

    assert binary_module.effective_binary(project, project.view) \
        == "tofu"


def test_effective_binary_leaves_a_hand_made_view_unmanaged(tofu_project):
    """A view without a recorded version resolves to the configured
    binary."""
    project = tofu_project(project_type="modern")
    assert binary_module.effective_binary(project, project.view) \
        == "tofu"


def test_install_binary_downloads_verifies_and_installs(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The 'debops tofu install' command downloads the release
    archive, verifies it against the release checksums -- whose
    signature the DebOps keyring authenticates -- and installs the
    binary into the managed location."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    assert binary_module.install_binary(project, version) is True
    managed = binary_module.managed_binary_path(version)
    assert os.path.isfile(managed)
    assert open(managed).read() == "#!/bin/sh\nexit 0\n"
    assert os.stat(managed).st_mode & 0o111


def test_install_binary_downloads_from_the_configured_base(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The 'tofu.upstream.release_base' option steers the downloads:
    the '{version}' placeholder is substituted with the version to
    install."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    monkeypatch.setattr(binary_module, "_verify_checksums", mock.Mock())
    version = "1.13.9"

    urls = []

    def download(url, path):
        urls.append(url)
        if url.endswith(".zip"):
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
        else:
            with open(path, "wb") as handle:
                handle.write(b"stub")

    monkeypatch.setattr(binary_module, "_download", download)

    raw = keyring_config(stub_gpg, tmp_path)
    raw['tofu']['upstream']['release_base'] = \
        'https://mirror.example/tofu/v{version}'

    project = tofu_project(project_type="modern", raw=raw)
    assert binary_module.install_binary(project, version) is True

    assert len(urls) == 3
    assert all(url.startswith("https://mirror.example/tofu/v1.13.9/")
               for url in urls)


def test_install_binary_is_idempotent(tofu_project, tmp_path, monkeypatch):
    """The binary which is already installed is not downloaded
    again."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    download = mock.Mock()
    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern")
    assert binary_module.install_binary(project, version) is False
    download.assert_not_called()


def test_install_binary_refuses_a_mismatched_checksum(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The archive whose checksum does not match the release checksums
    is refused."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format("0" * 64, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="does not match"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_checksums_without_the_archive(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The checksums file which does not carry the archive's entry
    refuses the install."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    sums = releases / sums_name
    sums.write_text("{}  other.zip\n".format("0" * 64))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="do not carry"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_a_missing_gpg(tofu_project, tmp_path,
                                              monkeypatch):
    """The install which the keyring cannot run -- a missing gpg --
    refuses: an unverified download is exactly what the pin guards
    against."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    project = tofu_project(project_type="modern", raw={
        'binaries': {'gpg': str(tmp_path / 'missing-gpg')},
        'gpg': {'debops': {'keyring': {
            'path': str(tmp_path / 'keyring')}}},
        'tofu': {'upstream': {
            'release_base': ('https://github.com/opentofu/opentofu/'
                             'releases/download/v{version}'),
            'release_key': {
                'fingerprint': RELEASE_KEY_FINGERPRINT}}}})
    with pytest.raises(ValueError, match="is not available"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_without_the_fingerprint_option(
        tofu_project, tmp_path, monkeypatch):
    """The install refuses when the release key fingerprint option is
    absent: the trust anchor is configuration-only, there is no
    fallback."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    project = tofu_project(project_type="modern")
    with pytest.raises(ValueError, match="is not set"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


@pytest.mark.parametrize("fingerprint", ["", "  ", None, 4096, True])
def test_install_binary_refuses_an_invalid_fingerprint(
        tofu_project, stub_gpg, tmp_path, monkeypatch, fingerprint):
    """The install refuses when the release key fingerprint is empty
    or not a string: the option carries the trust anchor or it
    carries nothing."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    raw = keyring_config(stub_gpg, tmp_path)
    raw['tofu']['upstream']['release_key']['fingerprint'] = fingerprint

    project = tofu_project(project_type="modern", raw=raw)
    with pytest.raises(ValueError, match="is not set"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


@pytest.mark.parametrize("base", ["", "  ", None, 404])
def test_install_binary_refuses_an_invalid_release_base(
        tofu_project, stub_gpg, tmp_path, monkeypatch, base):
    """The install refuses when the release base is empty or not a
    string: the downloads come from the configuration or not at
    all."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    raw = keyring_config(stub_gpg, tmp_path)
    raw['tofu']['upstream']['release_base'] = base

    project = tofu_project(project_type="modern", raw=raw)
    with pytest.raises(ValueError, match="is not set"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_an_unreachable_keyserver(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The key which the keyserver does not carry refuses the install
    with the way out: the manual import into the DebOps keyring."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setenv('GPG_RECV_FAIL', '1')
    version = "1.13.9"

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="cannot be imported"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_a_fingerprint_mismatch(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The key which the keyserver carries under a different
    fingerprint refuses the install: the imported key must match the
    pin."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setenv('GPG_RECV_KEY',
                       'AAAA' + RELEASE_KEY_FINGERPRINT[4:])
    version = "1.13.9"

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="does not match"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_a_bad_signature(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The release checksums whose signature does not verify refuse
    the install."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    monkeypatch.setenv('GPG_VERIFY_FAIL', '1')
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="does not verify"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_reconcile_binaries_installs_the_missing_versions(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The 'debops tofu install' command installs the binaries which
    the project's views pin."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    write_drop_in(project, [], binary_version=version)

    assert binary_module.reconcile_binaries(project) == [version]
    assert os.path.isfile(binary_module.managed_binary_path(version))


def test_reconcile_binaries_skips_the_installed_versions(
        tofu_project, tmp_path, monkeypatch):
    """The binaries which are already installed are not downloaded
    again."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    download = mock.Mock()
    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern")
    write_drop_in(project, [], binary_version=version)

    assert binary_module.reconcile_binaries(project) == []
    download.assert_not_called()


def test_reconcile_binaries_force_reinstalls_the_versions(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The '--force' option reinstalls the binaries which are
    installed already: the download, the verification and the
    install run again."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    downloads = []

    def download(url, path):
        downloads.append(url)
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    write_drop_in(project, [], binary_version=version)

    assert binary_module.reconcile_binaries(project) == [version]
    assert len(downloads) == 3

    assert binary_module.reconcile_binaries(project, force=True) \
        == [version]
    assert len(downloads) == 6
    assert open(binary_module.managed_binary_path(version)).read() \
        == "#!/bin/sh\nexit 0\n"
