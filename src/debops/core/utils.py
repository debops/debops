# Copyright (C) 2022 David Härdeman <david@hardeman.nu>
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2022-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR
import distro
import hashlib
import logging
import os
import platform
import re
import shutil
import subprocess
import textwrap

logger = logging.getLogger(__name__)


def verify_gpg_recipients(gpg, keys):
    """Check that the GPG recipients can actually receive an encrypted
    secret.

    Each recipient is probed with a real encryption to the null device,
    the same operation :command:`git-crypt` performs when adding a
    user: a key which is missing, expired, revoked or carries no
    encryption-capable subkey fails here, before a project is created
    around it. An empty list is an error as well -- encryption without
    a recipient would seal the secrets away from everyone, including
    the operator.

    Raises ValueError naming the recipient and carrying the gpg error
    when a recipient cannot be used.
    """
    if not keys:
        raise ValueError('List of GPG recipients not specified')

    for key in keys.split(','):
        result = subprocess.run(
            [gpg, '--batch', '--yes', '--encrypt', '-r', key,
             '--output', os.devnull],
            input=b'', capture_output=True)
        if result.returncode != 0:
            error = result.stderr.decode('utf-8', 'replace').strip()
            if '\n' in error:
                # A gpg report is several lines; indent them under the
                # message instead of riding on the first line
                raise ValueError(
                    'The GPG key "{}" cannot be used for encryption:\n'
                    '  {}'.format(key, error.replace('\n', '\n  ')))
            raise ValueError(
                'The GPG key "{}" cannot be used for encryption: '
                '{}'.format(key, error))


def unexpanduser(path):
    """Replace the absolute path of the home directory with '~'

    This function will replace the full path of the home directory with the '~'
    shorthand, but only if it is present at the start of the absolute path.
    This workaround is needed in cases where home directory string can be
    encountered inside of the path, for example if home directory is symlinked
    from a different place in the filesystem."""
    if path.startswith(DEBOPS_USER_HOME_DIR):
        return path.replace(DEBOPS_USER_HOME_DIR, '~', 1)
    else:
        return path


def _unexpand_homes(text):
    """Replace the occurrences of the home directory path with '~'.

    The unexpansion applies to the whole message text: paths can appear
    anywhere in it, not only at the start. A replacement happens when the
    home path is followed by a path separator or by a non-word character,
    so that '/home/<user>' and '/home/<user>/src/...' unexpand, while a
    different user's '/home/<user2>/...' stays absolute.
    """
    pattern = re.escape(DEBOPS_USER_HOME_DIR) + r'(?=[^A-Za-z0-9_]|$)'
    return re.sub(pattern, '~', text)


def wrap_message(text, width=None):
    """Wrap a message to the terminal width.

    Lines which are longer than the terminal width are wrapped with a
    hanging indent; shorter lines and their indentation are left alone,
    so that multi-line messages with their own structure -- indented
    error details, code blocks -- survive the wrapping. The home
    directory path inside the text is unexpanded to '~' first.

    The width is clamped to 72-80 columns: terminal reports without a
    size (piped output) and narrow terminals both get a comfortable,
    deterministic width. The wrapping is for the terminal only; journal
    and syslog records keep their single-line form.
    """
    if width is None:
        width = shutil.get_terminal_size().columns
    width = max(72, min(80, width))

    text = _unexpand_homes(text)
    lines = []
    for line in text.splitlines():
        if len(line) <= width:
            lines.append(line)
        else:
            lines.extend(textwrap.wrap(line, width=width,
                                       break_long_words=False,
                                       break_on_hyphens=False,
                                       subsequent_indent='    '))
    return '\n'.join(lines)


def path_key(path, name, view=''):
    """Return the namespacing key of a project path and view.

    Resources that several projects share -- sockets, run log
    directories, caches -- are namespaced by this key so that
    same-named projects cannot collide and the views of one project
    stay apart. The hash of the real path provides the distinction,
    the sanitized directory name keeps the key recognizable to a
    human, and a view extends the name. Without a view the key names
    the project as a whole.
    """
    digest = hashlib.sha256(
        '{}\0{}'.format(os.path.realpath(path),
                        view).encode('utf-8', 'replace'))
    key = re.sub(r'[^A-Za-z0-9._-]', '-', str(name or 'project'))
    if view:
        key += '-' + re.sub(r'[^A-Za-z0-9._-]', '-', str(view))
    return '{}-{}'.format(digest.hexdigest()[:8], key)


def strtobool(value):
    """according to deprecated
    https://docs.python.org/3.11/distutils/apiref.html#distutils.util.strtobool
    """
    value = value.lower()
    if value in ("y", "yes", "on", "1", "true", "t"):
        return True
    elif value in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError


def path_inside_project(path, project):
    """Report whether the path resolves inside the project directory.

    The comparison uses real paths, so symbolic links cannot be used to
    escape the project.
    """
    root = os.path.realpath(project)
    target = os.path.realpath(path)
    return target.startswith(root + os.sep)


def write_file(path, content, overwrite=False, project=None):
    """Write text to path, creating missing parent directories.

    An existing file is left alone unless overwrite is True, which keeps
    hand-edited files from being replaced by generated content.

    When the project directory is given, the write is refused when the
    target path resolves outside of it, so that a mistyped path cannot
    scatter generated files across the file system.

    Returns True if the file was written, False if it already existed and
    overwriting was not requested.
    """
    if project is not None and not path_inside_project(path, project):
        raise ValueError('Refusing to write outside of the project '
                         'directory: ' + path)

    if os.path.exists(path) and not overwrite:
        return False

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(content)

    return True


def host_is_controller():
    """Report whether the local host can run DebOps playbooks itself.

    DebOps common plays assume a Debian-family system; anywhere else the local
    host is only an Ansible controller and not a managed one.
    """
    return (platform.system() == 'Linux' and
            distro.id().lower() in ('debian', 'ubuntu'))
