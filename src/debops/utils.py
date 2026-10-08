# Copyright (C) 2022 David Härdeman <david@hardeman.nu>
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2022-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR
import distro
import os
import platform


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


def write_file(path, content, overwrite=False):
    """Write text to path, creating missing parent directories.

    An existing file is left alone unless overwrite is True, which keeps
    hand-edited files from being replaced by generated content.

    Returns True if the file was written, False if it already existed and
    overwriting was not requested.
    """
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
            distro.linux_distribution(full_distribution_name=False)[0].lower()
            in ('debian', 'ubuntu'))
