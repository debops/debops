# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""SSHFP-based verification of scanned SSH host keys.

The DNS zone of a host can publish its SSH public key fingerprints as
SSHFP resource records (RFC 4255). Scanned keys whose fingerprints
match such records can be stored without human confirmation; keys
which contradict the DNS answer are refused. On a DNSSEC-signed zone
the records themselves are authenticated, which makes the match a
genuine third-party verification. On an unsigned zone the match
grants no trust of its own -- RFC 4255 forbids trusting
unauthenticated SSHFP records -- and the callers decide what the keys
fall back to.
"""

import base64
import hashlib
import ipaddress

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
    SSHFP algorithm number and the fingerprints of the key blob in
    lowercase hex, keyed by the SSHFP fingerprint type numbers
    (1: SHA-1, 2: SHA-256) -- a zone can publish either digest and
    ssh verifies both. Returns (None, None) when the key type is
    unknown or the blob is not valid base64.
    """
    algorithm = ALGORITHMS.get(key_type)
    if algorithm is None:
        return None, None
    try:
        blob = base64.b64decode(key_blob)
    except (ValueError, TypeError):
        return None, None
    return algorithm, {1: hashlib.sha1(blob).hexdigest(),
                       2: hashlib.sha256(blob).hexdigest()}


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


def is_link_local(address):
    """Report whether the address is an unreachable link-local one.

    A link-local address without the interface scope identifier
    cannot be reached: the connection has no interface to go through.
    An address which carries the scope ('fe80::1%eth0') is reachable
    and does not count.
    """
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    return parsed.is_link_local and '%' not in address


def lookup_sshfp(hostname):
    """Look up the SSHFP records of a host name.

    Returns ``(authenticated, records)``: whether a validating resolver
    marked the answer with the authenticated-data flag, and the set of
    '(algorithm, fingerprint_type, fingerprint)' triples the zone
    publishes; the fingerprint types are limited to the SHA-1 and
    SHA-256 digests the comparison knows. Lookup failures raise the
    dnspython exceptions.
    """
    import dns.flags
    import dns.resolver

    answer = dns.resolver.resolve(hostname, 'SSHFP', want_dnssec=True)
    authenticated = bool(answer.response.flags & dns.flags.AD)
    records = set()
    for rdata in answer:
        fields = rdata.to_text().split()
        if len(fields) < 3:
            continue
        try:
            algorithm, digest_type = int(fields[0]), int(fields[1])
        except ValueError:
            continue
        if digest_type not in (1, 2):
            # The other fingerprint types are reserved; their records
            # carry no digest the keys can be compared against
            continue
        records.add((algorithm, digest_type, fields[2].lower()))
    return authenticated, records
