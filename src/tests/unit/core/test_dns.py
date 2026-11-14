# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ssh.dns``.

The SSHFP lookups are driven through a monkeypatched resolver, so no
live DNS is touched.
"""

import base64
import hashlib
from types import SimpleNamespace
from unittest import mock

import dns.flags

import debops.core.ssh.dns as dns_module
from debops.core.ssh.dns import is_ip_address, key_fingerprint, \
    lookup_sshfp, ssh_fingerprint

KEY_BLOB = b'\x21' * 32
KEY_B64 = base64.b64encode(KEY_BLOB).decode('ascii')
KEY_FINGERPRINT = hashlib.sha256(KEY_BLOB).hexdigest()


def test_key_fingerprint_maps_the_algorithm_and_computes_the_hash():
    algorithm, fingerprint = key_fingerprint('ssh-ed25519', KEY_B64)

    assert algorithm == 4
    assert fingerprint == KEY_FINGERPRINT


def test_key_fingerprint_rejects_unknown_types_and_blobs():
    assert key_fingerprint('ssh-quantum', KEY_B64) == (None, None)
    assert key_fingerprint('ssh-ed25519', 'not base64!!') == (None, None)


def test_ssh_fingerprint_uses_the_form_ssh_prints():
    expected = 'SHA256:' + base64.b64encode(
        bytes.fromhex(KEY_FINGERPRINT)).decode('ascii').rstrip('=')

    assert ssh_fingerprint(KEY_FINGERPRINT) == expected
    assert ssh_fingerprint(KEY_FINGERPRINT).startswith('SHA256:')


def test_is_ip_address_recognizes_literals():
    assert is_ip_address('192.0.2.10')
    assert is_ip_address('2001:db8::1')
    assert not is_ip_address('web.example.org')
    assert not is_ip_address('not an address')


def test_lookup_sshfp_parses_records_and_the_authenticated_flag():
    answer = mock.MagicMock()
    answer.response = SimpleNamespace(
        flags=dns.flags.AD | dns.flags.QR)
    answer.__iter__.return_value = iter([
        mock.Mock(to_text=mock.Mock(return_value='4 2 ' + KEY_FINGERPRINT)),
        mock.Mock(to_text=mock.Mock(return_value='1 1 deadbeef')),
    ])
    resolver = mock.Mock(return_value=answer)

    with mock.patch.object(dns_module.dns.resolver, 'resolve', resolver):
        authenticated, records = lookup_sshfp('web.example.org')

    assert authenticated
    assert records == {(4, KEY_FINGERPRINT), (1, 'deadbeef')}
    resolver.assert_called_once_with('web.example.org', 'SSHFP',
                                     want_dnssec=True)
