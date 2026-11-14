#
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""SSHFP-based verification of scanned SSH host keys.

The DNS zone of a host can publish its SSH public key fingerprints as
SSHFP resource records (RFC 4255). Scanned keys whose fingerprints
match such records can be stored without human confirmation; keys
which contradict the DNS answer are refused. On a DNSSEC-signed zone
the records themselves are authenticated, which makes the match a
genuine third-party verification; on an unsigned zone it is trust
transferred to DNS, and callers should say so in their reports.
"""

import base64
import hashlib
import ipaddress

import dns.flags
import dns.resolver

# The SSHFP algorithm numbers of the key types ssh-keyscan reports,
# per RFC 4255 and its updates.
ALGORITHMS = {
    'ssh-rsa': 1,
    'ssh-dss': 2,
    'ecdsa-sha2-nistp256': 3,
    'ecdsa-sha2-nistp384': 3,
    'ecdsa-sha2-nistp521': 3,
    'ssh-ed25519': 4,
}


def key_fingerprint(key_type, key_blob):
    """Return the SSHFP identity of a scanned key.

    The key type is the token ssh-keyscan reports ('ssh-ed25519',
    'ssh-rsa', ...), the key blob is its base64 encoding. Returns the
    SSHFP algorithm number and the SHA-256 fingerprint in lowercase
    hex, or (None, None) when the key type is unknown or the blob is
    not valid base64.
    """
    algorithm = ALGORITHMS.get(key_type)
    if algorithm is None:
        return None, None
    try:
        blob = base64.b64decode(key_blob)
    except (ValueError, TypeError):
        return None, None
    return algorithm, hashlib.sha256(blob).hexdigest()


def ssh_fingerprint(fingerprint):
    """Render a hex fingerprint in the 'SHA256:...' form used by ssh.

    Comparing fingerprints of the same form is easier than comparing
    hex against base64.
    """
    raw = bytes.fromhex(fingerprint)
    return 'SHA256:' + base64.b64encode(raw).decode('ascii').rstrip('=')


def is_ip_address(text):
    """Report whether the text is an IP address literal."""
    try:
        ipaddress.ip_address(text)
    except ValueError:
        return False
    return True


def lookup_sshfp(hostname):
    """Look up the SSHFP records of a host name.

    Returns ``(authenticated, records)``: whether a validating resolver
    marked the answer with the authenticated-data flag, and the set of
    ``(algorithm, fingerprint)`` pairs the zone publishes. Lookup
    failures raise the dnspython exceptions.
    """
    answer = dns.resolver.resolve(hostname, 'SSHFP', want_dnssec=True)
    authenticated = bool(answer.response.flags & dns.flags.AD)
    records = set()
    for rdata in answer:
        fields = rdata.to_text().split()
        records.add((int(fields[0]), fields[2].lower()))
    return authenticated, records
