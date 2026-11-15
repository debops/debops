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
KEY_SHA1 = hashlib.sha1(KEY_BLOB).hexdigest()


def test_key_fingerprint_maps_the_algorithm_and_computes_the_hashes():
    """The fingerprints are keyed by the SSHFP fingerprint type
    numbers; a zone can publish either digest."""
    algorithm, digests = key_fingerprint('ssh-ed25519', KEY_B64)

    assert algorithm == 4
    assert digests == {1: KEY_SHA1, 2: KEY_FINGERPRINT}


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
    assert records == {(4, 2, KEY_FINGERPRINT), (1, 1, 'deadbeef')}
    resolver.assert_called_once_with('web.example.org', 'SSHFP',
                                     want_dnssec=True)


def test_lookup_sshfp_skips_records_without_comparable_digests():
    """Records of the reserved fingerprint types and malformed records
    carry no digest the keys can be compared against."""
    answer = mock.MagicMock()
    answer.response = SimpleNamespace(flags=0)
    answer.__iter__.return_value = iter([
        mock.Mock(to_text=mock.Mock(return_value='4 2 ' + KEY_FINGERPRINT)),
        mock.Mock(to_text=mock.Mock(return_value='4 9 cafebabe')),
        mock.Mock(to_text=mock.Mock(return_value='4 x notanumber')),
        mock.Mock(to_text=mock.Mock(return_value='4 2')),
    ])
    resolver = mock.Mock(return_value=answer)

    with mock.patch.object(dns_module.dns.resolver, 'resolve', resolver):
        _, records = lookup_sshfp('web.example.org')

    assert records == {(4, 2, KEY_FINGERPRINT)}
