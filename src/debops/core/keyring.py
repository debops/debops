# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The managed GnuPG keyring of the DebOps tool.

The :class:`KeyringManager` maintains a DebOps-owned GnuPG homedir,
separate from the user's own GnuPG home, which the tool uses to verify
signatures of the artifacts it downloads. The trust anchor is the
fingerprint of the expected signing key, recorded in the
configuration: the key is imported from the configured keyserver and
the imported key's fingerprint must match the pin, the same check the
signature-aware upstream installers perform.

The keyring is not project-specific: it lives under the user's data
directory and is shared across projects. The binary is resolved
through the existing 'binaries.gpg' option.
"""

from xdg.BaseDirectory import xdg_data_home
import logging
import os
import stat
import subprocess

logger = logging.getLogger(__name__)


class KeyringManager(object):

    """Manage a DebOps-owned GnuPG keyring.

    The keyring is a GnuPG homedir at
    ``~/.local/share/debops/gnupg`` by default, with its ``gpg.conf``
    rendered from the 'gpg.<name>.keyring.gpg_conf' configuration
    subtree. The options without values -- the gpg.conf flags -- are
    encoded as booleans: 'true' emits the option name alone, 'false'
    omits the line, letting the option's gpg default apply.
    """

    def __init__(self, config, name='debops'):
        self._config = config
        self._name = name
        self._gpg = config.raw['binaries']['gpg']
        keyring = config.raw['gpg'][name]['keyring']
        self._path = self._contained_path(keyring['path'])
        self._gpg_conf = keyring.get('gpg_conf') or {}

    def _contained_path(self, path):
        """Resolve the keyring homedir path and keep it inside the
        DebOps data location.

        The keyring is DebOps-owned infrastructure: its homedir is
        created and made private, which must not happen to an
        arbitrary directory a project configuration names. The path
        resolves strictly under the DebOps data location
        ('~/.local/share/debops/'); anything outside refuses the
        manager with the way out."""
        expanded = os.path.expanduser(path) if path \
            else os.path.join(xdg_data_home, 'debops', 'gnupg')
        root = os.path.realpath(os.path.join(xdg_data_home, 'debops'))
        resolved = os.path.realpath(expanded)
        if resolved == root or not resolved.startswith(root + os.sep):
            raise ValueError(
                "The keyring path {!r} must stay inside the DebOps "
                "data location '{}': the keyring directory is created "
                'and made private, which must not reach the paths '
                'outside it.'.format(path, root))
        return expanded

    @property
    def path(self):
        """The keyring homedir path."""
        return self._path

    def _run(self, args, stdin=None, timeout=60):
        """Run gpg against the keyring homedir, returning the result.

        A missing gpg binary refuses the operation: the keyring
        cannot verify without it. A hung gpg -- a wedged keyserver
        connection, a stuck agent -- is cut off at the timeout and
        refused; the way out is the manual key import into the
        DebOps keyring."""
        try:
            return subprocess.run(
                [self._gpg, '--homedir', self._path] + args,
                input=stdin, capture_output=True, timeout=timeout)
        except FileNotFoundError:
            raise ValueError(
                "The '{}' binary which the 'binaries.gpg' option names "
                'is not available: install it, or point the option at '
                'the gpg binary of the system.'.format(self._gpg))
        except subprocess.TimeoutExpired:
            raise ValueError(
                "The '{}' operation of gpg timed out after {} seconds; "
                'the keyserver may be unreachable or the agent stuck. '
                'Import the key manually into the DebOps keyring to '
                'proceed.'.format(args[0] if args else 'gpg', timeout))

    def ensure_keyring(self):
        """Create the keyring homedir and its gpg.conf when missing.

        The homedir is private: a GnuPG homedir wider than 0700 makes
        gpg refuse it. The gpg.conf is re-rendered when its content
        changed, so that the configuration stays the user's record of
        the keyring's options.
        """
        os.makedirs(self._path, exist_ok=True)
        os.chmod(self._path, stat.S_IRWXU)
        conf_path = os.path.join(self._path, 'gpg.conf')
        content = self._render_gpg_conf()
        try:
            with open(conf_path, 'r') as fp:
                current = fp.read()
        except FileNotFoundError:
            current = None
        if current != content:
            with open(conf_path, 'w') as fp:
                fp.write(content)
            os.chmod(conf_path, stat.S_IRUSR | stat.S_IWUSR)

    def _render_gpg_conf(self):
        """Render the gpg.conf content from the gpg_conf subtree.

        A string value renders as 'name value', a list as 'name v1
        v2' -- gpg.conf's own multi-value syntax -- a boolean 'true'
        as the option name alone, and 'false' omits the line.
        """
        lines = []
        for option, value in self._gpg_conf.items():
            if value is False:
                continue
            if value is True:
                lines.append(option)
            elif isinstance(value, list):
                lines.append(' '.join([option] + [str(item)
                                                  for item in value]))
            else:
                lines.append('{} {}'.format(option, value))
        return '\n'.join(lines) + '\n' if lines else ''

    def _key_fingerprints(self):
        """Return the fingerprints of the keys the keyring holds."""
        result = self._run(['--list-keys', '--with-colons'])
        if result.returncode != 0:
            return []
        fingerprints = []
        for line in result.stdout.decode('utf-8', 'replace').splitlines():
            if line.startswith('fpr:'):
                fingerprints.append(line.split(':')[9])
        return fingerprints

    def ensure_key(self, fingerprint):
        """Make sure the keyring holds the key of a fingerprint.

        The fingerprint is the pin: the key is imported from the
        configured keyserver when missing, and the imported key's
        fingerprint must match the pin. Raises ValueError naming the
        way out when gpg is missing, the keyserver is unreachable or
        the imported key does not match.
        """
        self.ensure_keyring()
        normalized = ''.join(fingerprint.split()).upper()
        if normalized in self._key_fingerprints():
            return False

        result = self._run(['--recv-keys', normalized], timeout=120)
        if result.returncode != 0:
            error = result.stderr.decode('utf-8', 'replace').strip()
            raise ValueError(
                "The GPG key '{}' cannot be imported into the DebOps "
                "keyring '{}':\n  {}\nImport the key manually into "
                'the keyring to proceed.'.format(
                    fingerprint, self._path, error.replace('\n', '\n  ')))

        if normalized not in self._key_fingerprints():
            raise ValueError(
                "The key imported into the DebOps keyring does not "
                "match the fingerprint '{}'.".format(fingerprint))
        logger.notice(
            "Imported the GPG key '{}' into the DebOps keyring".format(
                fingerprint),
            extra={'allow': ['stderr', 'syslog']})
        return True

    def verify_signature(self, data_path, signature_path, fingerprint):
        """Verify a detached signature against the keyring.

        The signature must verify and the signing key's fingerprint
        must match the pin: a signature made by any other key fails
        regardless of its validity. Raises ValueError naming the way
        out on a mismatch.
        """
        self.ensure_keyring()
        normalized = ''.join(fingerprint.split()).upper()
        result = self._run(['--verify', '--status-fd', '1',
                            signature_path, data_path])
        if result.returncode != 0:
            error = result.stderr.decode('utf-8', 'replace').strip()
            raise ValueError(
                'The signature of the downloaded file does not '
                'verify:\n  {}'.format(error.replace('\n', '\n  ')))

        signing_key = self._signing_key_fingerprint(result)
        if signing_key != normalized:
            raise ValueError(
                "The signature of the downloaded file is made by the "
                "key '{}', not by the pinned key '{}'.".format(
                    signing_key, normalized))

    def _signing_key_fingerprint(self, result):
        """Return the primary key fingerprint of the key which made
        the signature, from the VALIDSIG status report.

        The status report is locale-independent: the human-readable
        'Primary key fingerprint' report is localized, and gpg only
        emits it for signatures made by a subkey. The VALIDSIG line
        carries the signing key's fingerprint and the primary key's
        fingerprint as its last field; the pin names the primary key.
        """
        for line in result.stdout.decode('utf-8', 'replace').splitlines():
            if line.startswith('[GNUPG:] VALIDSIG '):
                return line.split()[-1]
        return None
