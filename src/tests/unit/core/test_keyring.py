# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.keyring``."""

import os
import stat
import textwrap

import pytest

from debops.core.keyring import KeyringManager

FINGERPRINT = 'E3E6E43D84CB852EADB0051D0C0AF313E5FD9F80'


@pytest.fixture
def keyring(tmp_path, monkeypatch):
    """A KeyringManager over a stub gpg(1) binary, with a stub
    configuration.

    The stub records its argv and responds to the operations the
    manager runs: '--list-keys' with the fingerprints of the imported
    keys, '--recv-keys' by importing the requested key, '--verify'
    with a fixed exit code and the 'Primary key fingerprint' report.
    Environment variables steer the canned behavior; the argv log is
    what the tests inspect.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "gpg"
    stub.write_text(textwrap.dedent('''\
        #!/bin/sh
        echo "$@" >> "$GPG_ARGV_LOG"
        case " $* " in
          *" --list-keys "*)
            cat "$GPG_IMPORTED_LOG" 2>/dev/null || true
            exit 0
            ;;
          *" --recv-keys "*)
            if [ -n "$GPG_RECV_FAIL" ]; then
              echo "gpg: keyserver error" >&2
              exit 1
            fi
            fpr="$*"
            if [ -n "$GPG_RECV_KEY" ]; then
              fpr="$GPG_RECV_KEY"
            fi
            echo "fpr:::::::::${fpr##* }:" >> "$GPG_IMPORTED_LOG"
            exit 0
            ;;
          *" --verify "*)
            if [ -n "$GPG_VERIFY_FAIL" ]; then
              echo "gpg: Bad signature" >&2
              exit 1
            fi
            echo "[GNUPG:] VALIDSIG $GPG_SIGNING_KEY 0 0 0 0 0 0 0 0 $GPG_SIGNING_KEY"
            exit 0
            ;;
        esac
        exit 0
        '''))
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv('GPG_ARGV_LOG', str(tmp_path / 'gpg-argv.log'))
    monkeypatch.setenv('GPG_IMPORTED_LOG',
                       str(tmp_path / 'gpg-imported.log'))
    monkeypatch.setenv('GPG_SIGNING_KEY', FINGERPRINT)

    class StubConfig:
        raw = {
            'binaries': {'gpg': str(stub)},
            'gpg': {'debops': {'keyring': {
                'path': str(tmp_path / 'keyring'),
                'gpg_conf': {
                    'keyserver': 'hkps://keyserver.ubuntu.com',
                    'fixed-list-mode': True,
                    'no-greeting': True,
                    'no-emit-version': True,
                    'no-comments': True,
                },
            }}},
        }

    return KeyringManager(StubConfig), StubConfig, str(tmp_path / 'gpg-argv.log')


def test_keyring_homedir_is_created_private(keyring):
    """The keyring homedir is created with the user-only access mode:
    a GnuPG homedir wider than 0700 is refused by gpg."""
    manager, config, argv_log = keyring
    manager.ensure_keyring()
    assert os.path.isdir(manager.path)
    assert stat.S_IMODE(os.stat(manager.path).st_mode) == 0o700


def test_empty_path_resolves_to_the_xdg_data_location(keyring, tmp_path,
                                                      monkeypatch):
    """An empty 'gpg.debops.keyring.path' resolves to the 'debops/gnupg'
    directory of the XDG data location, shared across projects."""
    manager, config, argv_log = keyring
    monkeypatch.setattr('debops.core.keyring.xdg_data_home',
                        str(tmp_path / 'xdg-data'))
    config.raw['gpg']['debops']['keyring']['path'] = ''
    xdg_manager = KeyringManager(config)
    xdg_path = os.path.join(str(tmp_path / 'xdg-data'),
                            'debops', 'gnupg')
    assert xdg_manager.path == xdg_path


def test_gpg_conf_is_rendered_from_the_config(keyring):
    """The keyring's gpg.conf is rendered from the 'gpg_conf' subtree:
    strings render as 'name value', booleans as the flag name alone."""
    manager, config, argv_log = keyring
    manager.ensure_keyring()
    with open(os.path.join(manager.path, 'gpg.conf')) as handle:
        content = handle.read()
    assert 'keyserver hkps://keyserver.ubuntu.com' in content
    assert 'fixed-list-mode' in content
    assert 'no-greeting' in content
    assert 'no-emit-version' in content
    assert 'no-comments' in content


def test_gpg_conf_is_rerendered_when_the_config_changes(keyring):
    """The keyring is DebOps-managed: the rendered gpg.conf follows the
    configuration when it changes."""
    manager, config, argv_log = keyring
    manager.ensure_keyring()
    config.raw['gpg']['debops']['keyring']['gpg_conf']['keyserver'] = \
        'hkps://keys.openpgp.org'
    manager.ensure_keyring()
    with open(os.path.join(manager.path, 'gpg.conf')) as handle:
        content = handle.read()
    assert 'keyserver hkps://keys.openpgp.org' in content


def test_ensure_key_imports_a_missing_key(keyring):
    """A key which the keyring does not hold is imported from the
    keyserver, and the import is announced."""
    manager, config, argv_log = keyring
    assert manager.ensure_key(FINGERPRINT) is True
    invocations = open(argv_log).read().splitlines()
    assert any('--recv-keys' in line and FINGERPRINT in line
               for line in invocations)


def test_ensure_key_is_idempotent(keyring):
    """A key which the keyring already holds is not imported again."""
    manager, config, argv_log = keyring
    manager.ensure_key(FINGERPRINT)
    imports = len([line for line in open(argv_log).read().splitlines()
                   if '--recv-keys' in line])
    assert manager.ensure_key(FINGERPRINT) is False
    assert len([line for line in open(argv_log).read().splitlines()
                if '--recv-keys' in line]) == imports


def test_ensure_key_normalizes_the_fingerprint(keyring):
    """A human-formatted fingerprint -- spaces and grouping as the
    upstream documentation prints it -- resolves to the same pin as
    the compact form."""
    manager, config, argv_log = keyring
    spaced = 'E3E6 E43D 84CB 852E ADB0  051D 0C0A F313 E5FD 9F80'
    assert manager.ensure_key(spaced) is True
    assert manager.ensure_key(FINGERPRINT) is False


def test_ensure_key_refuses_when_the_import_fails(keyring, monkeypatch):
    """A key which the keyserver does not carry refuses the operation
    with the way out: the manual import into the keyring."""
    manager, config, argv_log = keyring
    monkeypatch.setenv('GPG_RECV_FAIL', '1')
    with pytest.raises(ValueError, match='cannot be imported'):
        manager.ensure_key(FINGERPRINT)


def test_missing_gpg_refuses_the_operation(keyring, tmp_path):
    """A gpg binary which the 'binaries.gpg' option names but the
    system does not carry refuses the operation with the way out."""
    manager, config, argv_log = keyring
    config.raw['binaries']['gpg'] = str(tmp_path / 'missing-gpg')
    with pytest.raises(ValueError, match='is not available'):
        KeyringManager(config).ensure_key(FINGERPRINT)


def test_ensure_key_refuses_a_fingerprint_mismatch(keyring, monkeypatch):
    """A key which the keyserver carries under a different fingerprint
    refuses the operation: the imported key must match the pin."""
    manager, config, argv_log = keyring
    monkeypatch.setenv('GPG_RECV_KEY', 'AAAA' + FINGERPRINT[4:])
    with pytest.raises(ValueError, match='does not match'):
        manager.ensure_key(FINGERPRINT)


def test_verify_signature_checks_the_signing_key(keyring):
    """A signature made by the pinned key verifies."""
    manager, config, argv_log = keyring
    manager.verify_signature('/dev/null', '/dev/null', FINGERPRINT)


def test_verify_signature_refuses_a_wrong_key(keyring, monkeypatch):
    """A signature made by another key fails regardless of its
    validity: the pin names the primary key which the signature must
    carry."""
    manager, config, argv_log = keyring
    monkeypatch.setenv('GPG_SIGNING_KEY', 'AAAA' + FINGERPRINT[4:])
    with pytest.raises(ValueError, match='not by the pinned key'):
        manager.verify_signature('/dev/null', '/dev/null', FINGERPRINT)


def test_verify_signature_refuses_a_bad_signature(keyring, monkeypatch):
    """A signature which does not verify at all refuses with the gpg
    report."""
    manager, config, argv_log = keyring
    monkeypatch.setenv('GPG_VERIFY_FAIL', '1')
    with pytest.raises(ValueError, match='does not verify'):
        manager.verify_signature('/dev/null', '/dev/null', FINGERPRINT)
