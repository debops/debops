# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu binary versions of a DebOps project.

The views pin the OpenTofu binary version they run with: the
'views.<view>.tofu.binary_version' option of their configuration
drop-in records the version, seeded from the
'tofu.upstream.known_version' configuration when the view is
created. The pinned binaries are
installed version-keyed in the DebOps data directory, shared across
the projects of the user: the 'debops tofu install' command
reconciles the project's views with the installed binaries.

The release archives are downloaded from the release base of the
'tofu.upstream.release_base' configuration -- the OpenTofu GitHub
releases by default -- and verified against the release checksums,
whose signature the DebOps-managed keyring authenticates against the
pinned release key: the fingerprint of the key which signs the
releases is the trust anchor, recorded in the
'tofu.upstream.release_key' configuration.
"""

import hashlib
import logging
import os
import platform
import shutil
import sys
import tempfile
import urllib.request
import zipfile

from xdg.BaseDirectory import xdg_data_home

from ..keyring import KeyringManager

logger = logging.getLogger(__name__)

# The machine names of the running platform, mapped to the release
# architecture names of the OpenTofu releases
TOFU_ARCHITECTURES = {
    'x86_64': 'amd64',
    'amd64': 'amd64',
    'aarch64': 'arm64',
    'arm64': 'arm64',
    'i686': '386',
    'i386': '386',
    'armv7l': 'arm',
    'armv6l': 'arm',
}

# The system names of the running platform, mapped to the release
# system names of the OpenTofu releases
TOFU_SYSTEMS = {
    'linux': 'linux',
    'darwin': 'darwin',
    'freebsd': 'freebsd',
    'openbsd': 'openbsd',
}


def binary_install_root():
    """Return the root of the DebOps-managed OpenTofu binaries."""
    return os.path.join(xdg_data_home, 'debops', 'tofu')


def managed_binary_path(version):
    """Return the path of the managed OpenTofu binary of a version."""
    return os.path.join(binary_install_root(), version, 'tofu')


def known_version(project):
    """Return the known-good OpenTofu version of the debops package,
    from the 'tofu.upstream.known_version' configuration.

    The version seeds the 'binary_version' option of a new view's
    configuration drop-in: it comes from the configuration only, and
    an empty or non-string value refuses the view creation.
    """
    try:
        version = project.config.raw['tofu']['upstream']['known_version']
    except (KeyError, TypeError):
        version = None
    if not isinstance(version, str) or not version.strip():
        raise ValueError(
            "The 'tofu.upstream.known_version' option which names the "
            'OpenTofu version which the views of the project are '
            'seeded with is not set to a version.')
    return version


def resolve_binary(project, view):
    """Return the binary which the view runs with.

    The view's configuration drop-in records the pinned version; the
    managed binary of that version runs when it is installed -- the
    binary of the view is the pinned one from the DebOps data
    directory, the way the 'binaries.ansible*' options point at the
    virtualenv's binaries when the project venv is in use. A view
    whose pinned binary is missing falls back to the configured
    binary: the system-wide or user-wide installation, when one is
    available. A view without a recorded version -- a hand-made one
    -- runs the configured binary, unmanaged. When no installation is
    available, the resolution fails: there is no OpenTofu binary to
    run.
    """
    try:
        version = project.config.raw['views'][view]['tofu'][
            'binary_version']
    except (KeyError, TypeError):
        version = None
    if version:
        managed = managed_binary_path(version)
        if os.path.isfile(managed):
            return managed
        logger.warning(
            'The binary of the version {!r} which the view {!r} pins '
            'is not installed: run \'debops tofu install\' to install '
            'it; the configured binary runs meanwhile'.format(
                version, view),
            extra={'allow': ['stderr', 'syslog']})
    binary = project.config.raw['binaries']['tofu']
    if shutil.which(binary) is None:
        raise ValueError(
            "The OpenTofu binary which the 'binaries.tofu' option "
            'names ({!r}) is not available: install OpenTofu, or '
            'point the option at the binary to run.'.format(binary))
    return binary


def reconcile_binaries(project):
    """Install the pinned binaries of the project's views.

    The views which record a pinned version are collected; the
    missing binaries are installed into the managed location.
    Returns the list of the versions which were installed.
    """
    versions = set()
    for view, config in (project.config.raw.get('views') or {}).items():
        try:
            version = config['tofu']['binary_version']
        except (KeyError, TypeError):
            continue
        if version:
            versions.add(version)
    installed = []
    for version in sorted(versions):
        if install_binary(project, version):
            installed.append(version)
    return installed


def install_binary(project, version, force=False):
    """Install the OpenTofu binary of a version into the managed
    location.

    The release archive is downloaded from the OpenTofu releases and
    verified against the release checksums, whose signature the
    DebOps-managed keyring authenticates against the pinned release
    key. The keyring holds the release key: it is imported from the
    configured keyserver when missing, and the imported key's
    fingerprint must match the pin. A missing gpg binary, an
    unreachable keyserver or a fingerprint mismatch refuse the
    install; the way out is the manual import of the key into the
    DebOps keyring. Returns True when the binary was installed, False
    when it was already present.
    """
    target = managed_binary_path(version)
    if os.path.isfile(target) and not force:
        return False

    fingerprint = _release_fingerprint(project)
    release_base = _release_base(project)
    keyring = KeyringManager(project.config)
    keyring.ensure_key(fingerprint)

    release_url = release_base.format(version=version)
    archive_name = 'tofu_{}_{}_{}.zip'.format(version, _release_system(),
                                              _release_arch())
    sums_name = 'tofu_{}_SHA256SUMS'.format(version)

    with tempfile.TemporaryDirectory() as tmp:
        archive = os.path.join(tmp, archive_name)
        sums = os.path.join(tmp, sums_name)
        signature = os.path.join(tmp, sums_name + '.gpgsig')
        _download('{}/{}'.format(release_url, archive_name), archive)
        _download('{}/{}'.format(release_url, sums_name), sums)
        _download('{}/{}'.format(release_url, sums_name + '.gpgsig'),
                  signature)
        _verify_checksums(archive, sums, archive_name)
        keyring.verify_signature(sums, signature, fingerprint)
        with zipfile.ZipFile(archive) as zf:
            zf.extract('tofu', tmp)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.move(os.path.join(tmp, 'tofu'), target)
        os.chmod(target, 0o755)
    logger.notice(
        'Installed the OpenTofu binary of the version {!r} into '
        '{!r}'.format(version, target),
        extra={'allow': ['stderr', 'syslog']})
    return True


def _release_fingerprint(project):
    """Return the fingerprint of the OpenTofu release key, from the
    'tofu.upstream.release_key' configuration.

    The fingerprint is the trust anchor of the install verification:
    it comes from the configuration only, and an empty or non-string
    value refuses the install.
    """
    try:
        fingerprint = project.config.raw['tofu']['upstream'][
            'release_key']['fingerprint']
    except (KeyError, TypeError):
        fingerprint = None
    if not isinstance(fingerprint, str) or not fingerprint.strip():
        raise ValueError(
            "The 'tofu.upstream.release_key.fingerprint' option which "
            'names the key which signs the OpenTofu releases is not '
            'set to a fingerprint: the install verification refuses '
            'to proceed without it.')
    return fingerprint


def _release_base(project):
    """Return the base of the OpenTofu release downloads, from the
    'tofu.upstream.release_base' configuration.

    The base is a URL template whose '{version}' placeholder is
    substituted with the version of the release to install: the
    option points the install at a mirror of the releases. It comes
    from the configuration only, and an empty or non-string value
    refuses the install.
    """
    try:
        base = project.config.raw['tofu']['upstream']['release_base']
    except (KeyError, TypeError):
        base = None
    if not isinstance(base, str) or not base.strip():
        raise ValueError(
            "The 'tofu.upstream.release_base' option which names the "
            'base of the OpenTofu release downloads is not set to a '
            'URL.')
    return base


def _release_system():
    """Return the system name of the release archive."""
    return TOFU_SYSTEMS.get(sys.platform, sys.platform)


def _release_arch():
    """Return the architecture name of the release archive."""
    machine = platform.machine()
    return TOFU_ARCHITECTURES.get(machine, machine)


def _download(url, path):
    """Download a URL into a file."""
    request = urllib.request.Request(url, headers={'User-Agent': 'debops'})
    with urllib.request.urlopen(request, timeout=60) as response, \
            open(path, 'wb') as fh:
        shutil.copyfileobj(response, fh)


def _release_keyring():
    """Return the armored release keyring which ships with the debops
    package, or None when it is not available."""
    try:
        return pkgutil.get_data('debops', TOFU_KEYRING)
    except (FileNotFoundError, OSError):
        return None


def _verify_checksums(archive, sums, archive_name):
    """Verify the SHA256 checksum of the release archive against the
    release checksums file."""
    with open(sums) as fh:
        for line in fh:
            checksum, _, name = line.strip().partition('  ')
            if name.strip() == archive_name:
                break
        else:
            raise ValueError(
                'The release checksums do not carry the {!r} '
                'archive'.format(archive_name))
    digest = hashlib.sha256()
    with open(archive, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != checksum:
        raise ValueError(
            'The checksum of the {!r} archive does not match the '
            'release checksums'.format(archive_name))
