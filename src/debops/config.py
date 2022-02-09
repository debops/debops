# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .utils import unexpanduser
import os
import sys
import dotenv
import pkgutil
import jinja2
import collections.abc
import toml
import json
import yaml
from distutils.util import strtobool
from xdg.BaseDirectory import xdg_config_home
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class Configuration(object):

    def __init__(self):

        self._env_files = []

        # Include variables from the system-wide configuration
        self.merge_env(os.path.join('/etc', 'default', 'debops'))

        # Include global DebOps environment variables defined by the user
        self.merge_env(os.path.join(xdg_config_home, 'debops', 'environment'))

        # Instantiate project configuration
        self._config = {}

        # Load the default configuration options defined by DebOps
        self._config_template = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data', 'defaults.toml'))
                .decode('utf-8'), trim_blocks=True)
        self._config = toml.loads(self._config_template.render(env=os.environ))

        # Load configuration files in known directories
        self._config_dirs = [
            '/usr/lib/debops/conf.d',
            '/usr/local/lib/debops/conf.d',
            '/etc/debops/conf.d',
            os.path.join(xdg_config_home, 'debops', 'conf.d')
        ]
        self._config_files = []
        for config_dir in self._config_dirs:
            self.merge(config_dir)

    def _merge_dict(self, d1, d2):
        """
        Modifies d1 in-place to contain values from d2. If any value
        in d1 is a dictionary (or dict-like), *and* the corresponding
        value in d2 is also a dictionary, then merge them in-place.
        If any value in d1 is a list and corresponding value in d2 is also
        a list, the lists are combined together.
        """
        if d2:
            for k, v2 in d2.items():
                v1 = d1.get(k)  # returns None if v1 has no value for this key
                if (isinstance(v1, collections.abc.Mapping) and
                        isinstance(v2, collections.abc.Mapping)):
                    self._merge_dict(v1, v2)
                elif (isinstance(v1, list) and
                        isinstance(v2, list)):
                    d1[k].extend(v2)
                else:
                    d1[k] = v2

    def section(self, section):
        if self._config.has_section(section):
            return self._config.items(section)
        else:
            return list()

    @property
    def raw(self):
        return self._config

    def get_env(self, key):
        return os.environ[key]

    def set_env(self, key, value):
        os.environ[key] = str(value)

    def get(self, items=None):
        if items:
            if not isinstance(items, list):
                items = [items]
            data = self._config
            for key in items:
                try:
                    data = data[key]
                except KeyError:
                    data = {}
            return data
        else:
            return self._config

    def merge_env(self, path):
        if os.path.exists(os.path.join(path, '.env')):
            if os.path.isfile(os.path.join(path, '.env')):
                self._env_files.append(os.path.join(path, '.env'))
                dotenv.load_dotenv(os.path.join(path, '.env'), override=True)
        elif os.path.exists(path):
            if os.path.isfile(path):
                self._env_files.append(path)
                dotenv.load_dotenv(path, override=True)

    def load(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return self._load_config_file(path)
            elif os.path.isdir(path):
                data = {}
                for config_file in os.listdir(path):
                    if os.path.isfile(os.path.join(path, config_file)):
                        self._merge_dict(data,
                                         self._load_config_file(
                                             os.path.join(path, config_file)))
                return data

        # Path doesn't exist, return empty dictionary for merging
        return dict()

    def merge(self, data):
        if isinstance(data, str):
            self._merge_dict(self._config, self.load(data))
        elif isinstance(data, dict):
            self._merge_dict(self._config, data)

    def _load_config_file(self, path):

        # Ignore "hidden" files but make exception for legacy '.debops.cfg'
        if (os.path.basename(path).startswith('.')
                and not os.path.basename(path) == '.debops.cfg'):
            # Return an empty dictionary with no data
            return dict()

        if path.endswith('.toml'):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                data = toml.loads(fp.read())
                return data
        elif path.endswith('.json'):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                data = json.loads(fp.read())
                return data
        elif (path.endswith('.yaml') or path.endswith('.yml')):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                try:
                    data = yaml.safe_load(fp.read())
                    return data
                except yaml.YAMLError as e:
                    print('Error in configuration file:', path + ':\n', e,
                          file=sys.stderr)

        elif path.endswith('/.debops.cfg'):
            self._config_files.append(path)
            self._data = configparser.ConfigParser(
                    strict=False)
            self._data.read(path)

            # Convert the legacy '.debops.cfg' configuration to TOML
            self._converted_data = {}
            for section in self._data.sections():
                items = self._data.items(section)
                if section.startswith('ansible '):
                    if 'ansible' not in self._converted_data:
                        self._converted_data['ansible'] = {}
                    new_section = section.split()[1]
                    self._converted_data['ansible'][new_section] = {}
                    for key, value in items:
                        try:
                            boolvalue = bool(strtobool(value))
                            (self._converted_data['ansible']
                             [new_section].update({key: boolvalue}))
                        except ValueError:
                            (self._converted_data['ansible']
                             [new_section].update({key: value}))
                else:
                    self._converted_data[section] = {}
                    for key, value in items:
                        try:
                            boolvalue = bool(strtobool(value))
                            self._converted_data[section].update(
                                    {key: boolvalue})
                        except ValueError:
                            (self._converted_data[section]
                             .update({key: value}))
            return self._converted_data

    def show_env(self):
        for key, value in os.environ.items():
            print('{}={}'.format(key, value))

    def show(self, format='toml'):
        if format == 'toml':
            relative_root = os.path.relpath(os.path.abspath('/'))
            if self._env_files:
                print('# Environment files:')
                for filename in self._env_files:
                    relative_file = os.path.relpath(unexpanduser(filename))
                    print('#    ', relative_file.replace(relative_root, '', 1))
                print()
            if self._config_files:
                print('# Configuration files:')
                for filename in self._config_files:
                    relative_file = os.path.relpath(unexpanduser(filename))
                    print('#   ', relative_file.replace(relative_root, '', 1))
                print()
            print(toml.dumps(self._config).strip())
        elif format == 'json':
            print(json.dumps(self._config, sort_keys=True, indent=4))
