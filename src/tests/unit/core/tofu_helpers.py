# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The test helpers of the tofu modules: the functions the test
modules call directly, not pytest fixtures."""

import os

import pytest

from debops.core.tofu.modules import resolve_modules
from debops.core.tofu.providers import resolve_providers
from debops.core.tofu.registry import view_drop_in_path
from debops.core.tofu.view import create_view
from debops.core.utils import write_file


RELEASE_KEY_FINGERPRINT = 'E3E6E43D84CB852EADB0051D0C0AF313E5FD9F80'


def mkview(project, providers=None, modules=None, encrypt='plain',
           keys=None):
    """Create the view the way 'debops tofu mkview' does; the tests
    create store-less stub projects, so the explicit 'plain' decision
    is the default here."""
    create_view(project, project.view,
                providers=resolve_providers(project, providers),
                modules=resolve_modules(project, modules),
                encrypt=encrypt, keys=keys)


def write_drop_in(project, providers, binary_version=None):
    """Write the view's configuration drop-in, the way the view
    creation does, and merge the recorded set into the live
    configuration."""
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    os.makedirs(os.path.dirname(drop_in), exist_ok=True)
    with open(drop_in, "w") as handle:
        handle.write('[views."{}".tofu]\nproviders = {}\n'.format(
            project.view, providers))
        if binary_version is not None:
            handle.write("binary_version = '{}'\n".format(binary_version))
    recorded = {'providers': providers}
    if binary_version is not None:
        recorded['binary_version'] = binary_version
    project.config.merge({'views': {project.view: {'tofu': recorded}}})
    return drop_in


def keyring_config(stub, tmp_path):
    """The configuration fragment which wires the stub gpg, the
    keyring and the upstream options into the project configuration:
    the release base and the release key fingerprint of the install
    verification."""
    return {
        'binaries': {'gpg': str(stub)},
        'gpg': {'debops': {'keyring': {
            'path': str(tmp_path / 'keyring'),
            'gpg_conf': {'keyserver': 'hkps://keyserver.ubuntu.com'},
        }}},
        'tofu': {'upstream': {
            'release_base': ('https://github.com/opentofu/opentofu/'
                             'releases/download/v{version}'),
            'release_key': {
                'fingerprint': RELEASE_KEY_FINGERPRINT}}},
    }
