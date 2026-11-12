# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_PACKAGE_DATA
from .exceptions import OptionNotFoundError
from .utils import unexpanduser, strtobool, write_file
import os
import logging
import dotenv
import pkgutil
import jinja2
import string
import collections.abc
import toml
import json
import jsonschema
import yaml
from xdg.BaseDirectory import xdg_config_home
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

logger = logging.getLogger(__name__)

# The JSON Schema which describes the configuration tree. It is loaded
# on first use, so that the package data is read where it is needed,
# not at import time.
_config_schema_path = os.path.join('_data', 'debops', 'config',
                                   'schema.json')
_config_validator = None


def _schema_validator():
    """Return the JSON Schema validator of the configuration tree."""
    global _config_validator
    if _config_validator is None:
        schema = json.loads(
            pkgutil.get_data('debops', _config_schema_path).decode('utf-8'))
        _config_validator = jsonschema.Draft7Validator(schema)
    return _config_validator


def _dotted(segments):
    """Render a path of the configuration tree as an option name."""
    return '.'.join(str(segment) for segment in segments)


def _violation_reason(error):
    """Describe a schema violation in plain words."""
    if error.validator == 'type':
        expected = error.validator_value
        if isinstance(expected, list):
            expected = ' or '.join(expected)
        return ('must be of type {}, not {}'
                .format(expected, type(error.instance).__name__))
    if error.validator == 'enum':
        return 'must be one of: ' + ', '.join(
            str(value) for value in error.validator_value)
    return error.message


# Marker for a configuration path which the schema does not type: the
# option lives inside a section left open, and its value is parsed as
# JSON when it looks like JSON and kept as a string otherwise.
_UNTYPED = object()


def _parse_scalar(value):
    """Parse an environment value as JSON, or keep it as a string."""
    try:
        return json.loads(value)
    except ValueError:
        return value


def _prune_empty(data, segments):
    """Remove the sections left empty by removing an option.

    Walks from the parent of the removed option towards the root,
    dropping the parent sections which became empty dictionaries, and
    stops at the first section which is not empty.
    """
    for depth in range(len(segments) - 1, 0, -1):
        node = data
        for segment in segments[:depth]:
            node = node[segment]
        if node != {}:
            break
        parent = data
        for segment in segments[:depth - 1]:
            parent = parent[segment]
        del parent[segments[depth - 1]]


def _resolve_schema_node(schema, segments):
    """Find the schema node at the given path of the tree.

    Returns the schema node which describes the option at the path,
    None when the path cannot name a configuration option, or the
    _UNTYPED marker when the path enters a section which the schema
    leaves open.
    """
    node = schema
    for segment in segments:
        if not isinstance(node, dict):
            return None
        if node.get('type') not in (None, 'object'):
            # The path descends past a scalar option
            return None
        properties = node.get('properties', {})
        if segment in properties:
            node = properties[segment]
        elif isinstance(node.get('additionalProperties'), dict):
            node = node['additionalProperties']
        elif node.get('additionalProperties') is False:
            return None
        else:
            return _UNTYPED
    return node


class Configuration(object):

    def __init__(self):

        self._env_files = []
        self._env_vars = {}
        self._env_overrides = []

        # Set default environment variables at runtime
        self.set_env('DEBOPS_ANSIBLE_COLLECTIONS_PATH',
                     unexpanduser(os.path.join(DEBOPS_PACKAGE_DATA, 'ansible',
                                               'collections')))

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

        # The environment overrides are the last configuration layer
        # for clients which use the Configuration on its own; project
        # directories re-apply them after their own files are merged
        self.apply_env_overrides()

    def _expand_env_vars(self, data):
        """Expand '$VAR' and '${VAR}' references in configuration values.

        The references resolve against the process environment with the
        variables the project itself recorded on top, so that a value
        like 'DEBOPS_PROJECT_PATH' expands in the configuration files
        which are read after it was recorded. Unknown references are
        left as they are written.
        """
        if isinstance(data, str):
            if '$' not in data:
                return data
            env = {**os.environ, **self._env_vars}
            return string.Template(data).safe_substitute(env)
        elif isinstance(data, dict):
            return {k: self._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_env_vars(v) for v in data]
        else:
            return data

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

    @property
    def raw(self):
        return self._config

    def get_env(self, key):
        """Return the value of an environment variable.

        A variable set in the actual environment wins over one the
        project configuration generated, so that an operator's explicit
        choice -- for example a custom 'DEBOPS_ANSIBLE_INVENTORY' --
        cannot be overridden by the generated value.
        """
        try:
            return os.environ[key]
        except KeyError:
            return self._env_vars.get(key)

    def set_env(self, key, value):
        """Record a generated environment variable.

        The variable is stored in the project's environment mapping,
        which the clients hand to the commands they run; the process
        environment of the DebOps command itself is not modified.
        """
        self._env_vars[key] = str(value)

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

    def _merge_env_file(self, path):
        """Parse an environment file once and merge it into the environment.

        The file is parsed only once so that a variable which references its
        own previous value (for example 'PATH=/extra/bin:${PATH}') is not
        applied twice; a 'dotenv.load_dotenv()' call followed by
        'dotenv.dotenv_values()' would interpolate the second parse against
        the results of the first.

        In PATH-style variables (PATH itself and any variable ending with
        'PATH'), a '~' at the start of a colon-separated entry is expanded
        to the home directory; the shell and shutil.which() do not expand it
        during command lookup, so a literal tilde would silently never match
        (other variables are left alone, their consumers like Ansible expand
        '~' on their own).
        """
        values = {}
        for key, value in dotenv.dotenv_values(path).items():
            if value is not None and (key == 'PATH'
                                      or key.endswith('PATH')):
                value = ':'.join(os.path.expanduser(entry)
                                 for entry in value.split(':'))
            if value is not None:
                values[key] = value
        self._env_vars.update(values)

    def merge_env(self, path):
        if os.path.exists(os.path.join(path, '.env')):
            if os.path.isfile(os.path.join(path, '.env')):
                self._env_files.append(os.path.join(path, '.env'))
                self._merge_env_file(os.path.join(path, '.env'))
        elif os.path.exists(path):
            if os.path.isfile(path):
                self._env_files.append(path)
                self._merge_env_file(path)

    def load(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                return self._load_config_file(path)
            elif os.path.isdir(path):
                data = {}
                for config_file in sorted(os.listdir(path)):
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

    def apply_env_overrides(self, environ=None):
        """Apply configuration overrides from the environment.

        Each variable named 'DEBOPS_CONFIG__<SECTION>__<KEY>' sets the
        value at the matching path of the configuration tree, with the
        path segments separated by '__', for example
        'DEBOPS_CONFIG__SYSLOG__LEVEL'. The segments are matched
        case-insensitively; keys which contain a hyphen, like the
        binary names, keep it in the variable name.

        The value is converted to the type which the configuration
        schema defines for the path. Unknown paths and values which do
        not fit their type are reported as warnings and skipped. The
        overrides merge as the last configuration layer, above the
        configuration files of the project directory; a project
        directory re-applies them after its own configuration is
        merged.
        """
        if environ is None:
            environ = os.environ
        for name, value in sorted(environ.items()):
            if not name.startswith('DEBOPS_CONFIG__'):
                continue
            tail = name[len('DEBOPS_CONFIG__'):]
            segments = [segment.lower()
                        for segment in tail.split('__') if segment]
            if not segments:
                logger.warning("Ignoring environment override '%s': no "
                               "configuration path", name)
                continue
            try:
                option_value = self._coerce_override(segments, value)
            except (ValueError, TypeError) as errmsg:
                logger.warning("Ignoring environment override '%s': %s",
                               name, errmsg)
                continue
            if option_value is None:
                logger.warning("Ignoring environment override '%s': not "
                               "a DebOps configuration option", name)
                continue
            self._merge_override(segments,
                                 self._expand_env_vars(option_value))
            if name not in self._env_overrides:
                self._env_overrides.append(name)

    def _coerce_override(self, segments, value):
        """Convert an environment override value to the option's type.

        Returns None when the path cannot name a configuration option.
        """
        node = _resolve_schema_node(_schema_validator().schema, segments)
        if node is None:
            return None
        if node is _UNTYPED:
            return _parse_scalar(value)
        schema_type = node.get('type')
        if isinstance(schema_type, list):
            schema_type = schema_type[0]
        if schema_type is None:
            return _parse_scalar(value)
        if schema_type == 'boolean':
            return bool(strtobool(value))
        if schema_type == 'integer':
            return int(value)
        if schema_type == 'number':
            try:
                return int(value)
            except ValueError:
                return float(value)
        if schema_type == 'array':
            parsed = _parse_scalar(value)
            if isinstance(parsed, list):
                return parsed
            return [entry.strip()
                    for entry in value.split(',') if entry.strip()]
        if schema_type == 'object':
            parsed = _parse_scalar(value)
            if not isinstance(parsed, dict):
                raise ValueError('the value must be a JSON object')
            return parsed
        return value

    def _merge_override(self, segments, value):
        """Merge one override value at its path of the tree."""
        data = {}
        node = data
        for segment in segments[:-1]:
            node = node.setdefault(segment, {})
        node[segments[-1]] = value
        self._merge_dict(self._config, data)

    def option_file(self, directory):
        """Return the configuration file managed by 'config set'.

        The files whose names end with '_config_set.json' are the ones
        the command manages; the numeric prefix of the name decides
        where the options rank among the files of the directory, so
        when the operator creates a file with a different prefix, it
        replaces the default one. Returns the path of the file to
        operate on; the file itself is not created.
        """
        matches = []
        if os.path.isdir(directory):
            for name in sorted(os.listdir(directory)):
                path = os.path.join(directory, name)
                if (os.path.isfile(path)
                        and name.endswith('_config_set.json')
                        and not name.startswith('.')):
                    matches.append(path)
        if not matches:
            return os.path.join(directory, '99_config_set.json')
        if len(matches) > 1:
            raise ValueError(
                'Multiple configuration files managed by '
                "'debops config set' in " + directory + ': '
                + ', '.join(unexpanduser(m) for m in matches))
        return matches[0]

    def write_option(self, path, key, value=None, delete=False):
        """Set or remove a configuration option in a JSON file.

        The option is addressed by its dotted path in the
        configuration tree. When set, the value is converted to the
        type the configuration schema defines for the option, and
        options unknown to the schema are refused, except under the
        'custom' section, which is reserved for options defined
        outside of DebOps. When removed, the option is deleted from
        the file together with the sections left empty by its removal;
        options unknown to the schema are removed as well, so that the
        command can clean up configurations which predate the schema.

        Raises ValueError when the option cannot be set or removed;
        the file is written only when the operation succeeds.
        """
        segments = [segment.lower() for segment in key.split('.')
                    if segment]
        if not segments:
            raise ValueError('No configuration option specified')
        if not delete and value is None:
            raise ValueError("No value specified for the '{}' option"
                             .format(_dotted(segments)))

        data = {}
        if os.path.isfile(path):
            with open(path, 'r') as fp:
                content = fp.read()
            try:
                data = json.loads(content) if content.strip() else {}
            except json.JSONDecodeError as errmsg:
                raise ValueError('{}: {}'.format(path, errmsg))
        if not isinstance(data, dict):
            raise ValueError('{}: the file does not contain a '
                             'dictionary of options'.format(path))

        if delete:
            node = data
            for segment in segments[:-1]:
                if not isinstance(node, dict) or segment not in node:
                    raise ValueError("The '{}' option is not set in {}"
                                     .format(_dotted(segments), path))
                node = node[segment]
            leaf = segments[-1]
            if not isinstance(node, dict) or leaf not in node:
                raise ValueError("The '{}' option is not set in {}"
                                 .format(_dotted(segments), path))
            del node[leaf]
            _prune_empty(data, segments)
        else:
            try:
                option_value = self._coerce_override(segments, value)
            except (ValueError, TypeError) as errmsg:
                raise ValueError('{}: {}'.format(_dotted(segments),
                                                 errmsg))
            if option_value is None:
                raise ValueError(
                    "The '{}' option is not defined in the DebOps "
                    "configuration; custom options belong under the "
                    "'custom' section".format(_dotted(segments)))
            option_value = self._expand_env_vars(option_value)
            node = data
            for segment in segments[:-1]:
                child = node.get(segment)
                if not isinstance(child, dict):
                    child = {}
                    node[segment] = child
                node = child
            node[segments[-1]] = option_value

        write_file(path, json.dumps(data, indent=2, sort_keys=True)
                   + '\n', overwrite=True)

    def _validated(self, path, data):
        """Validate a parsed configuration file against the schema.

        A violation is reported as a warning. An option with a value of
        a wrong type is dropped, so that a mistyped value cannot
        corrupt the merged configuration and the configured default
        applies. An unknown option is reported but kept: nothing in
        DebOps reads it, and dropping it would break the scripts and
        integrations which do. An option violated inside an array is
        dropped whole, with the offending element named in the warning.
        """
        if not isinstance(data, dict):
            if data is not None:
                logger.warning("Configuration file %s does not contain a "
                               "dictionary of options, ignoring it", path)
                return {}
            return data
        # The errors are collected before any option is dropped: the
        # validator walks the data lazily, and dropping an option while
        # it is being validated would desynchronize the walk
        for error in list(_schema_validator().iter_errors(data)):
            self._report_violation(path, data, error)
        return data

    def _report_violation(self, path, data, error):
        """Report one schema violation and apply the dropping policy.

        Unknown options are kept, options of a wrong type are dropped;
        an option already dropped by an earlier violation is not
        reported again.
        """
        if error.validator == 'additionalProperties':
            # The error reports the container of the unexpected options;
            # the schema comparison names them without parsing messages.
            # Unknown options are kept, the warning is their trace
            known = set(error.schema.get('properties', {}))
            for key in sorted(set(error.instance) - known):
                if error.absolute_path:
                    segments = list(error.absolute_path) + [key]
                    logger.warning("Configuration file %s: unknown option "
                                   "'%s'", path, _dotted(segments))
                else:
                    logger.warning("Configuration file %s: unknown option "
                                   "'%s', custom options belong under the "
                                   "'custom' section", path, key)
            return
        segments = list(error.absolute_path)
        if not segments:
            logger.warning("Configuration file %s: %s", path,
                           error.message)
            return
        # A violation inside an array drops the whole option, the
        # offending element is named by the rendered path
        while segments and isinstance(segments[-1], int):
            segments.pop()
        node = data
        for segment in segments[:-1]:
            try:
                node = node[segment]
            except (KeyError, IndexError, TypeError):
                return
        key = segments[-1]
        if key not in node:
            return
        logger.warning("Configuration file %s: option '%s' %s",
                       path, _dotted(segments), _violation_reason(error))
        del node[key]

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
                data = self._expand_env_vars(data)
                return self._validated(path, data)
        elif path.endswith('.json'):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                data = json.loads(fp.read())
                data = self._expand_env_vars(data)
                return self._validated(path, data)
        elif (path.endswith('.yaml') or path.endswith('.yml')):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                try:
                    data = yaml.safe_load(fp.read())
                    data = self._expand_env_vars(data)
                    return self._validated(path, data)
                except yaml.YAMLError as e:
                    logger.warning('Error in configuration file: %s:\n %s',
                                   path, e)

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

            # The legacy file is a fragment of a view configuration, not
            # a whole configuration tree: it is merged under a view,
            # whose sections are free-form, so it is not validated
            # against the schema
            return self._converted_data

    def config_list(self):
        """Return the lines describing where the configuration comes from."""
        lines = []
        relative_root = os.path.relpath(os.path.abspath('/'))
        if self._env_overrides:
            lines.append('# Environment variable overrides:')
            for name in self._env_overrides:
                lines.append(name)
            lines.append('')
        if self._env_files:
            lines.append('# Environment files:')
            for filename in self._env_files:
                relative_file = os.path.relpath(unexpanduser(filename))
                lines.append(relative_file.replace(relative_root, '', 1))
            lines.append('')
        if self._config_files:
            lines.append('# Configuration files:')
            for filename in self._config_files:
                relative_file = os.path.relpath(unexpanduser(filename))
                lines.append(relative_file.replace(relative_root, '', 1))
        return lines

    def config_get(self, key, format='unix', keys=False, root=False):
        """Return the value of a configuration option, rendered in the
        requested format.

        With 'root' set, the option is rendered nested under its full
        path from the root of the configuration tree, which shows where
        in the tree the option is defined.

        Raises OptionNotFoundError when the option is not defined; the
        clients decide how absence is presented.
        """
        key_path = ['.']
        if key != '.':
            key_path = list(filter(None, key.split('.')))
        key_found = True

        _config = self._config
        if key_path[0] != '.':
            for element in key_path:
                try:
                    _config = _config[element]
                except KeyError:
                    key_found = False

        if key_found and keys:
            try:
                _config = list(_config.keys())
            except AttributeError:
                # The value is present, but we are interested in just the keys,
                # so let's return an empty list instead of a dictionary to
                # preserve the output type. This also causes the return code to
                # be 0 instead of 1 so that the process knows that there was no
                # error.
                _config = []

        if not key_found:
            raise OptionNotFoundError('The "' + key + '" option is not '
                                      'defined in the DebOps configuration')

        if root and key != '.':
            for element in reversed(key_path):
                _config = {element: _config}

        if isinstance(_config, dict):
            if format in ['unix', 'yaml']:
                return yaml.dump(_config).strip()
            elif format == 'json':
                return json.dumps(_config, sort_keys=True, indent=2)
            elif format == 'toml':
                return toml.dumps(_config).strip()
        elif isinstance(_config, bool):
            if format == 'unix':
                return json.dumps(_config)
            elif format == 'yaml':
                return yaml.dump(_config).strip()
            elif format in ['json', 'toml']:
                return json.dumps(_config)
        elif isinstance(_config, list):
            if format == 'unix':
                # An empty list renders as nothing at all
                return '\n'.join(str(entry) for entry in _config) or None
            elif format == 'yaml':
                return yaml.dump(_config).strip()
            elif format in ['json', 'toml']:
                return json.dumps(_config, sort_keys=True)
        else:
            if format == 'unix':
                return str(_config)
            elif format == 'yaml':
                return yaml.dump(_config).strip()
            elif format in ['json', 'toml']:
                return json.dumps(_config)
