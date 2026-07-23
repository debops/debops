# Copyright 2015-2026, Maciej Delmanowski <drybjed@drybjed.net>
# SPDX-License-Identifier: GPL-3.0-or-later

'''Fallback configuration loading for DebOps lookup plugins.

When the debops Python module is not installed (e.g. collection
installed via Ansible Galaxy), override paths are read from:

1. A project-local ``.debops.{yaml,yml,json,toml}`` file.
2. Global config directories (``~/.config/debops/conf.d/`` etc.).

This module centralises that logic so that ``file_src``, ``template_src``,
and ``task_src`` stay thin wrappers.
'''

import json
import os

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

try:
    import yaml
except ImportError:
    yaml = None


def _load_file(path):
    '''Parse a JSON, TOML, or YAML file and return the resulting dict,
    or *None* on any failure.'''

    try:
        if path.endswith('.json'):
            with open(path) as fh:
                return json.load(fh)
        if path.endswith('.toml') and tomllib is not None:
            with open(path, 'rb') as fh:
                return tomllib.load(fh)
        if path.endswith(('.yaml', '.yml')) and yaml is not None:
            with open(path) as fh:
                return yaml.safe_load(fh)
    except Exception:
        pass

    return None


def _extract_paths(parsed, conf_key):
    '''Return a list of absolute directory paths from *parsed* under
    ``override_paths.<conf_key>``, or an empty list.'''

    override_value = (
        parsed.get('override_paths', {}).get(conf_key)
        if isinstance(parsed, dict) else None
    )
    if not override_value:
        return []

    result = []
    for path_item in override_value.split(':'):
        if os.path.isabs(path_item):
            result.append(path_item)
        else:
            result.append(os.path.join(os.getcwd(), path_item))
    return result


def load_fallback_paths(conf_key):
    '''Return override directories when the debops Python module is absent.

    *conf_key* is the config key name (e.g. ``"files_path"``,
    ``"templates_path"``, ``"tasks_path"``).

    Resolution order:

    1. Project-local ``.debops.{yaml,yml,json,toml}`` in the current
       working directory.
    2. Global config directories (most-specific to least-specific):
       ``$XDG_CONFIG_HOME/debops/conf.d/``, ``/etc/debops/conf.d/``,
       ``/usr/local/lib/debops/conf.d/``, ``/usr/lib/debops/conf.d/``.

    Returns a list of absolute directory paths.  An empty list means no
    override paths were found.
    '''

    # 1. Project-local .debops.{yaml,yml,json,toml}
    for ext in ('.yaml', '.yml', '.json', '.toml'):
        project_path = os.path.join(os.getcwd(), '.debops' + ext)
        if os.path.isfile(project_path):
            parsed = _load_file(project_path)
            paths = _extract_paths(parsed, conf_key)
            if paths:
                return paths
            break

    # 2. Global config directories (most → least specific)
    xdg = os.environ.get(
        'XDG_CONFIG_HOME',
        os.path.join(os.path.expanduser('~'), '.config'))
    cfg_dirs = [
        os.path.join(xdg, 'debops', 'conf.d'),
        '/etc/debops/conf.d',
        '/usr/local/lib/debops/conf.d',
        '/usr/lib/debops/conf.d',
    ]

    for cfg_dir in cfg_dirs:
        if not os.path.isdir(cfg_dir):
            continue
        for filename in sorted(os.listdir(cfg_dir)):
            filepath = os.path.join(cfg_dir, filename)
            if filename.startswith('.') or not os.path.isfile(filepath):
                continue
            parsed = _load_file(filepath)
            paths = _extract_paths(parsed, conf_key)
            if paths:
                return paths

    return []
