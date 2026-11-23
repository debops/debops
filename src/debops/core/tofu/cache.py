# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu cache of the project views.

The data dirs of the views and the shared plugin cache live under the
DebOps cache root, ``~/.cache/debops/tofu/``. The data dirs are keyed
by the project path and view through the
:func:`debops.core.utils.path_key` notation, the plugin cache is
shared between all views and projects. The module inspects and cleans
the cache: the data dir of a view is re-derivable from the project --
the backend metadata from the view's 'main.tf', the provider binaries
from the registry against the committed lock file, the modules from
their recorded sources -- while the irreplaceable state lives in the
view's secret store, not in the cache.

The shared plugin cache holds provider binaries only: OpenTofu links
the working copy of each provider from the shared cache into the data
dir, while the modules are unpacked into the data dir directly -- there
is no shared module cache. Cleaning the plugin cache therefore costs
network re-downloads, cleaning a data dir does not.
"""

import json
import os
import re
import shutil

from ..utils import path_key
from xdg.BaseDirectory import xdg_cache_home

# The shape of the cache entry keys: the first 8 characters hold the
# digest of the project path and view, the rest the sanitized key
_KEY_DIGEST = re.compile(r'[0-9a-f]{8}-')


def cache_root():
    """Return the root directory of the DebOps OpenTofu cache."""
    return os.path.join(xdg_cache_home, 'debops', 'tofu')


def plugin_cache():
    """Return the shared plugin cache of all views."""
    return os.path.join(cache_root(), 'plugins')


def data_dir(project):
    """Return the data directory of the project's resolved view."""
    return os.path.join(cache_root(),
                        path_key(project.path, project.name,
                                 project.view))


def human_size(size):
    """Render a byte count in the 'du' style: '972B', '4.0K', '12M'."""
    for unit in ('B', 'K', 'M', 'G', 'T', 'P'):
        if size < 1024:
            if unit == 'B':
                return '{}B'.format(int(size))
            return '{:.1f}{}'.format(size, unit)
        size /= 1024.0
    return '{:.1f}P'.format(size)


def _dir_size(path):
    """Return the size of a directory tree in bytes. The walk does not
    descend into symlinked directories and does not count their size:
    the provider working copies of a data dir are symlinks into the
    shared plugin cache, which the data dir does not own."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path,
                                                followlinks=False):
        dirnames[:] = [entry for entry in dirnames
                       if not os.path.islink(os.path.join(dirpath,
                                                          entry))]
        for filename in filenames:
            try:
                total += os.lstat(os.path.join(dirpath,
                                               filename)).st_size
            except OSError:
                pass
    return total


def _state_backend(path):
    """Return the backend type recorded in the data dir's state
    pointer, or '-' when the data dir holds no readable one."""
    try:
        with open(os.path.join(path, 'terraform.tfstate'),
                  'r', encoding='utf-8') as _file:
            state = json.load(_file)
        return state.get('backend', {}).get('type', '-')
    except (OSError, ValueError):
        return '-'


def project_data_dirs(project):
    """Return the cache entry keys of the project's views.

    The enumeration parses the cache entries into their view keys and
    recomputes the path key of each candidate against the project's
    real path: same-named projects elsewhere in the filesystem are
    filtered out, and the data dirs of a project which moved away are
    not reported -- the keys of the stale entries no longer match the
    recomputed digest, and only '--reset' reaches them.
    """
    root = cache_root()
    if not os.path.isdir(root):
        return []
    name = re.sub(r'[^A-Za-z0-9._-]', '-', str(project.name or 'project'))
    dirs = []
    for entry in sorted(os.listdir(root)):
        entry_path = os.path.join(root, entry)
        if entry == 'plugins' or not os.path.isdir(entry_path):
            continue
        if not _KEY_DIGEST.match(entry):
            continue
        rest = entry[9:]
        if rest == name:
            view = ''
        elif rest.startswith(name + '-'):
            view = rest[len(name) + 1:]
        else:
            continue
        if path_key(project.path, project.name, view) == entry:
            dirs.append(entry)
    return dirs


def in_tree_dirs(project):
    """Return the '.terraform/' directories inside the project's tofu
    tree: the leftovers of the views which predate the relocation of
    the data dir into the cache, where 'tofu init' left the working
    state inside the project."""
    root = os.path.join(project.path, 'tofu')
    dirs = []
    if not os.path.isdir(root):
        return dirs
    for dirpath, dirnames, _ in os.walk(root):
        if '.terraform' in dirnames:
            dirs.append(os.path.join(dirpath, '.terraform'))
            dirnames.remove('.terraform')
    return dirs


def cache_rows(project):
    """Return the cache entries of the project as (path, size, note)
    rows: the data dirs of the project's views, the in-tree
    '.terraform/' leftovers and the shared plugin cache. Every row
    carries the full path of the entry."""
    rows = []
    root = cache_root()
    for entry in project_data_dirs(project):
        path = os.path.join(root, entry)
        rows.append((path, _dir_size(path), _state_backend(path)))
    for path in in_tree_dirs(project):
        rows.append((path, _dir_size(path), 'in-tree'))
    plugins = plugin_cache()
    if os.path.isdir(plugins):
        rows.append((plugins, _dir_size(plugins), 'shared'))
    return rows


def clean_data_dir(project):
    """Remove the data dir of the project's resolved view. Return the
    removed path, or None when the data dir does not exist."""
    path = data_dir(project)
    if not os.path.isdir(path):
        return None
    shutil.rmtree(path)
    return path


def clean_project(project):
    """Remove the data dirs of the project's views. Return the list of
    the removed paths."""
    root = cache_root()
    removed = []
    for entry in project_data_dirs(project):
        path = os.path.join(root, entry)
        shutil.rmtree(path)
        removed.append(path)
    return removed


def clean_plugins():
    """Remove the shared plugin cache of all views. Return the removed
    path, or None when it does not exist."""
    path = plugin_cache()
    if not os.path.isdir(path):
        return None
    shutil.rmtree(path)
    return path


def reset_cache():
    """Remove the whole cache root: the data dirs of all projects, the
    shared plugin cache and the stale entries of the projects which
    moved away. Return the removed root path, or None when the cache
    does not exist."""
    path = cache_root()
    if not os.path.isdir(path):
        return None
    shutil.rmtree(path)
    return path
