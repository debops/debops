# Copyright (C) 2020-2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_PACKAGE_DATA
from .exceptions import OptionNotFoundError
from .utils import unexpanduser, strtobool, write_file
import copy
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


def _config_leaves(path, node, leaves):
    """Collect the leaf options of a configuration subtree.

    An empty section counts as a leaf: it has a location in the tree
    and an origin, even though it holds no options.
    """
    if isinstance(node, dict) and node:
        for key in node:
            _config_leaves(path + [key], node[key], leaves)
    else:
        leaves.append((path, node))


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

    def __init__(self, defaults=None, paths=None, schema=None,
                 env_prefix=None, env_files=None):
        """Build a configuration.

        Without arguments, this is the configuration of the DebOps
        tool: the packaged defaults, the system and user configuration
        directories, the packaged schema which validates every loaded
        file, the DebOps environment files and the 'DEBOPS_CONFIG__'
        environment overrides.

        With arguments, a standalone configuration is built only from
        the sources the caller provides, with the same semantics: the
        files and directories are merged in the given order, the
        values expand '$VARIABLE' and '${VARIABLE}' references, and
        the options are validated against the schema when one is
        given.

        The 'defaults' is a dictionary, or a path to a TOML, JSON or
        YAML file which is rendered as a Jinja template first, so that
        the defaults can be computed from the environment. The 'paths'
        is a list of configuration files or directories, merged in the
        given order; every item is a path recorded in the 'system'
        layer, or a (path, scope) tuple which names its layer in the
        origin output. The 'schema' is a path to a JSON Schema file;
        without it, the options are not validated and their values
        from the environment and 'config_set' are parsed as JSON when
        they look like JSON and kept as strings otherwise. The
        'env_prefix' enables the environment overrides: every
        environment variable named '<PREFIX>__<SECTION>__<KEY>'
        overrides the option at the matching path of the tree. The
        'env_files' is a list of environment files, merged in order
        into the environment of the commands this configuration
        describes.
        """
        self._env_files = []
        self._env_vars = {}
        self._env_overrides = []
        self._violations = []
        self._layers = []
        self._config = {}
        self._config_files = []
        self._schema_source = 'debops'
        self._schema_instance = None
        self._env_prefix = 'DEBOPS_CONFIG__'

        if (defaults is not None or paths is not None
                or schema is not None or env_prefix is not None
                or env_files is not None):
            # A standalone configuration: only the sources the caller
            # asked for, none of DebOps' own
            self._schema_source = schema
            self._env_prefix = env_prefix
            if isinstance(defaults, dict):
                self._config = self._record_layer(
                    'defaults', 'defaults', defaults)
            elif defaults is not None:
                self._load_defaults(defaults)
            for item in (paths or []):
                if isinstance(item, (tuple, list)):
                    path, scope = item
                else:
                    path, scope = item, 'system'
                self.merge(path, scope=scope)
            for env_file in (env_files or []):
                self.merge_env(env_file)
        else:
            # The configuration of the DebOps tool itself
            self.set_env('DEBOPS_ANSIBLE_COLLECTIONS_PATH',
                         unexpanduser(os.path.join(
                             DEBOPS_PACKAGE_DATA, 'ansible',
                             'collections')))
            self.merge_env(os.path.join('/etc', 'default', 'debops'))
            self.merge_env(os.path.join(xdg_config_home, 'debops',
                                        'environment'))
            self._load_defaults(os.path.join(DEBOPS_PACKAGE_DATA,
                                             'defaults.toml'))
            self._config_dirs = [
                ('/usr/lib/debops/conf.d', 'system'),
                ('/usr/local/lib/debops/conf.d', 'system'),
                ('/etc/debops/conf.d', 'system'),
                (os.path.join(xdg_config_home, 'debops', 'conf.d'),
                 'user')
            ]
            for config_dir, config_scope in self._config_dirs:
                self.merge(config_dir, scope=config_scope)

        # The environment overrides are the last configuration layer
        # for clients which use the Configuration on its own; project
        # directories re-apply them after their own files are merged
        self.apply_env_overrides()

    def _load_defaults(self, path):
        """Load the default configuration options from a file.

        The file is rendered as a Jinja template first, so that the
        defaults can be computed from the environment; the rendered
        text is parsed according to the file extension. The defaults
        are the base of the configuration tree, the layer every other
        layer merges on top of.
        """
        with open(path, 'r') as fp:
            template = jinja2.Template(fp.read(), trim_blocks=True)
        rendered = template.render(env=os.environ)
        if path.endswith('.toml'):
            data = toml.loads(rendered)
        elif path.endswith('.json'):
            data = json.loads(rendered)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            data = yaml.safe_load(rendered)
        else:
            raise ValueError('Unsupported defaults file format: '
                             + path)
        self._config = self._record_layer(
            'defaults', path, self._validated(path, data) or {})

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

    def load(self, path, scope=None):
        if os.path.exists(path):
            if os.path.isfile(path):
                return self._load_config_file(path, scope=scope)
            elif os.path.isdir(path):
                data = {}
                for config_file in sorted(os.listdir(path)):
                    if os.path.isfile(os.path.join(path, config_file)):
                        self._merge_dict(
                            data,
                            self._load_config_file(
                                os.path.join(path, config_file),
                                scope=scope))
                return data

        # Path doesn't exist, return empty dictionary for merging
        return dict()

    def merge(self, data, scope=None, origin=None):
        """Merge a file, a directory or a dictionary into the tree.

        The scope and the origin name the configuration layer the data
        belongs to, for the 'debops config get --show-origin' output;
        the scope is one of 'defaults', 'system', 'user', 'project',
        'runtime' or 'override', and the origin is the file path or
        the label of the source.
        """
        if isinstance(data, str):
            self._merge_dict(self._config, self.load(data, scope=scope))
        elif isinstance(data, dict):
            self._record_layer(scope, origin or 'configuration-data',
                               data)
            self._merge_dict(self._config, data)

    def apply_env_overrides(self, environ=None):
        """Apply configuration overrides from the environment.

        Each variable named '<PREFIX>__<SECTION>__<KEY>' sets the
        value at the matching path of the configuration tree, with the
        path segments separated by '__' -- for the DebOps
        configuration the prefix is 'DEBOPS_CONFIG__', for a
        standalone configuration the prefix given at construction, and
        without a prefix the environment is not scanned at all. The
        segments are matched case-insensitively; keys which contain a
        hyphen, like the binary names, keep it in the variable name.

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
        if not self._env_prefix:
            return
        for name, value in sorted(environ.items()):
            if not name.startswith(self._env_prefix):
                continue
            tail = name[len(self._env_prefix):]
            segments = [segment.lower()
                        for segment in tail.split('__') if segment]
            if not segments:
                self._record_violation(
                    'override', None, name, True,
                    "ignoring environment override '{}': no "
                    "configuration path".format(name))
                continue
            try:
                option_value = self._coerce_override(segments, value)
            except (ValueError, TypeError) as errmsg:
                self._record_violation(
                    'override', None, name, True,
                    "ignoring environment override '{}': {}".format(
                        name, errmsg))
                continue
            if option_value is None:
                self._record_violation(
                    'override', None, name, True,
                    "ignoring environment override '{}': {}".format(
                        name, self._unknown_option_message(
                            _dotted(segments))))
                continue
            override = self._merge_override(
                segments, self._expand_env_vars(option_value))
            self._layers.append(('override', name,
                                 copy.deepcopy(override)))
            if name not in self._env_overrides:
                self._env_overrides.append(name)

    def _coerce_override(self, segments, value):
        """Convert an environment override value to the option's type.

        Returns None when the path cannot name a configuration option.
        """
        validator = self._schema()
        if validator is None:
            return _parse_scalar(value)
        node = _resolve_schema_node(validator.schema, segments)
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
        """Merge one override value at its path of the tree.

        Returns the dictionary of the merged option, for the layer
        recording.
        """
        data = {}
        node = data
        for segment in segments[:-1]:
            node = node.setdefault(segment, {})
        node[segments[-1]] = value
        self._merge_dict(self._config, data)
        return data

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
                    self._unknown_option_message(_dotted(segments)))
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

    def config_set(self, key, value):
        """Set a configuration option in the configuration tree.

        The option is addressed by its dotted path. A string value is
        converted to the type which the schema defines for the option,
        like the environment overrides are; any other value is checked
        against the schema when it defines one for the option, and
        stored as given. Options unknown to the schema are refused,
        except under the 'custom' section of the DebOps configuration.
        The change is recorded as the last configuration layer, so
        that the origin output names it.

        Raises ValueError when the option cannot be set.
        """
        segments = [segment.lower() for segment in key.split('.')
                    if segment]
        if not segments:
            raise ValueError('No configuration option specified')
        validator = self._schema()
        if isinstance(value, str):
            try:
                option_value = self._coerce_override(segments, value)
            except (ValueError, TypeError) as errmsg:
                raise ValueError('{}: {}'.format(_dotted(segments),
                                                 errmsg))
            if option_value is None:
                raise ValueError(
                    self._unknown_option_message(_dotted(segments)))
        else:
            option_value = value
        if validator is not None and not isinstance(value, str):
            node = _resolve_schema_node(validator.schema, segments)
            if node is None:
                raise ValueError(
                    self._unknown_option_message(_dotted(segments)))
            if node is not _UNTYPED:
                errors = list(validator.evolve(
                    schema=node).iter_errors(value))
                if errors:
                    raise ValueError('{}: {}'.format(
                        _dotted(segments), errors[0].message))
        merged = self._merge_override(segments, option_value)
        self._layers.append(('override', 'config_set',
                             copy.deepcopy(merged)))

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
                self._record_violation(
                    'parse', path, None, True,
                    'the file does not contain a dictionary of options, '
                    'ignoring it')
                return {}
            return data
        validator = self._schema()
        if validator is None:
            return data
        # The errors are collected before any option is dropped: the
        # validator walks the data lazily, and dropping an option while
        # it is being validated would desynchronize the walk
        for error in list(validator.iter_errors(data)):
            self._report_violation(path, data, error)
        return data

    def _record_violation(self, kind, path, option, dropped, message):
        """Record a configuration violation and report it.

        The ledger of recorded violations is what 'debops config
        check' turns into an exit code, and what a configuration
        reload can present as the list of problems found.
        """
        self._violations.append({'kind': kind, 'file': path,
                                 'option': option, 'dropped': dropped,
                                 'message': message})
        if path is None:
            # The violation does not belong to a file, the message
            # names its source on its own
            logger.warning(message)
        else:
            logger.warning("Configuration file %s: %s", path, message)

    def _record_layer(self, scope, origin, data):
        """Record a configuration layer and return its data.

        The layers record where every option of the tree came from;
        the data is recorded as a deep copy, because the merged tree
        shares the objects of the merged data and the later merges
        would otherwise modify the recorded layers in place, changing
        the origins they report.
        """
        self._layers.append((scope, origin, copy.deepcopy(data)))
        return data

    def _schema(self):
        """Return the JSON Schema validator of this configuration.

        Returns None when the configuration has no schema: the options
        are then not validated, and their values from the environment
        overrides and 'config_set' are parsed as JSON when they look
        like JSON and kept as strings otherwise.
        """
        if self._schema_source is None:
            return None
        if self._schema_source == 'debops':
            return _schema_validator()
        if self._schema_instance is None:
            with open(self._schema_source, 'r') as fp:
                self._schema_instance = jsonschema.Draft7Validator(
                    json.load(fp))
        return self._schema_instance

    def _unknown_option_message(self, option):
        """The message for an option which the schema does not know.

        The DebOps configuration reserves the 'custom' section for
        options defined outside of DebOps and points to it; a
        standalone configuration has no such convention.
        """
        message = "unknown option '{}'".format(option)
        if self._schema_source == 'debops':
            message += ", custom options belong under the 'custom' " \
                       "section"
        return message

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
                    self._record_violation(
                        'unknown', path, _dotted(segments), False,
                        "unknown option '{}'".format(_dotted(segments)))
                else:
                    self._record_violation('unknown', path, key, False,
                                           self._unknown_option_message(
                                               key))
            return
        segments = list(error.absolute_path)
        if not segments:
            self._record_violation('schema', path, None, False,
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
        option = _dotted(segments)
        self._record_violation(error.validator, path, option, True,
                               "option '{}' {}".format(
                                   option, _violation_reason(error)))
        del node[key]

    def _load_config_file(self, path, scope=None):

        # Ignore "hidden" files but make exception for legacy '.debops.cfg'
        if (os.path.basename(path).startswith('.')
                and not os.path.basename(path) == '.debops.cfg'):
            # Return an empty dictionary with no data
            return dict()

        if path.endswith('.toml'):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                try:
                    data = toml.loads(fp.read())
                except toml.TomlDecodeError as errmsg:
                    self._record_violation(
                        'parse', path, None, True,
                        'the file cannot be parsed: {}'.format(errmsg))
                    return {}
                data = self._expand_env_vars(data)
                return self._record_layer(scope, path,
                                          self._validated(path, data))
        elif path.endswith('.json'):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                try:
                    data = json.loads(fp.read())
                except json.JSONDecodeError as errmsg:
                    self._record_violation(
                        'parse', path, None, True,
                        'the file cannot be parsed: {}'.format(errmsg))
                    return {}
                data = self._expand_env_vars(data)
                return self._record_layer(scope, path,
                                          self._validated(path, data))
        elif (path.endswith('.yaml') or path.endswith('.yml')):
            self._config_files.append(path)
            with open(path, 'r') as fp:
                try:
                    data = yaml.safe_load(fp.read())
                    data = self._expand_env_vars(data)
                    return self._record_layer(scope, path,
                                              self._validated(path, data))
                except yaml.YAMLError as errmsg:
                    self._record_violation(
                        'parse', path, None, True,
                        'the file cannot be parsed: {}'.format(errmsg))

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
            return self._record_layer(scope, path, self._converted_data)

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

    def config_origins(self, key):
        """Return the origin of every option under a configuration path.

        Returns a list of (dotted_path, scope, origin, value) tuples,
        one for each leaf option found under the path in the final
        configuration tree. The scope and the origin name the
        configuration layer which last set the option: the packaged
        defaults, a configuration file of one of the layers, the
        runtime state of the project or an environment override.

        Raises OptionNotFoundError when the option is not defined.
        """
        key_path = list(filter(None, key.split('.'))) if key != '.' else []
        node = self._config
        try:
            for element in key_path:
                node = node[element]
        except (KeyError, TypeError):
            raise OptionNotFoundError('The "' + key + '" option is not '
                                      'defined in the DebOps '
                                      'configuration')

        leaves = []
        _config_leaves(key_path, node, leaves)
        origins = []
        for leaf_path, value in leaves:
            scope = None
            origin = None
            for layer_scope, layer_origin, layer_data in self._layers:
                layer_node = layer_data
                found = True
                for element in leaf_path:
                    if (isinstance(layer_node, dict)
                            and element in layer_node):
                        layer_node = layer_node[element]
                    else:
                        found = False
                        break
                if found:
                    scope, origin = layer_scope, layer_origin
            origins.append((_dotted(leaf_path) or '.', scope, origin,
                            value))
        return origins

    def config_get(self, key, format='unix', keys=False, root=False,
                   show_origin=False, show_scope=False):
        """Return the value of a configuration option, rendered in the
        requested format.

        With 'root' set, the option is rendered nested under its full
        path from the root of the configuration tree, which shows where
        in the tree the option is defined.

        With 'show_origin' or 'show_scope' set, the options are
        rendered as plain text, one line per option: the columns asked
        for (the scope, the origin) separated by tabs, and the option
        with its value joined by '=' as the last column, so that the
        values which contain whitespace stay in one place. This
        rendering cannot be combined with the other formats or
        options.

        Raises OptionNotFoundError when the option is not defined; the
        clients decide how absence is presented.
        """
        if show_origin or show_scope:
            if format != 'unix' or keys or root:
                raise ValueError('The origin of the options is rendered '
                                 'as plain text and cannot be combined '
                                 'with other formats or options')
            lines = []
            for option, scope, origin, value in self.config_origins(key):
                rendered = (value if isinstance(value, str)
                            else json.dumps(value))
                columns = []
                if show_scope:
                    columns.append(scope or 'unknown')
                if show_origin:
                    columns.append(origin or 'unknown')
                columns.append('='.join([option, rendered]))
                lines.append('\t'.join(columns))
            return '\n'.join(lines) if lines else None
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
