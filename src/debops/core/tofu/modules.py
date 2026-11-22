# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu modules of a DebOps project view.

The module instantiations of a view are recorded in the
'views.<view>.tofu.modules' option of its configuration drop-in and
drive the generated 'modules.tf' file of the view, which the reconcile
keeps in step. Each entry is a table keyed by the local module name,
carrying the module source address in the OpenTofu registry notation
-- 'namespace/name[/submodule]', or 'hostname/...' for modules outside
the public registry -- an optional version pin and the inputs of the
module instance.

The input values are configuration values: the literals render as
their HCL equivalents, and strings which carry the 'hcl:' prefix carry
raw HCL expressions which the rendered file emits verbatim. The
prefix is a configuration convention defined in
:mod:`debops.core.config`, which is not OpenTofu-specific.


The 'tofu.mkview.default_modules' read is not guarded: the package defaults
guarantee the table."""

import logging
import re

from ..config import hcl_value
from .registry import view_tofu_options, reconcile_managed_file, render_template

logger = logging.getLogger(__name__)

# The shape of a bare HCL identifier: an object key which matches it
# is emitted unquoted
_HCL_IDENTIFIER = re.compile(r'[A-Za-z_][A-Za-z0-9_-]*\Z')


def _hcl_string(value):
    """Render a Python string as an HCL string literal.

    The escapes cover the characters which change the meaning of an
    HCL string: the backslash, the quote, the template sequences
    '${' and '%{' -- which HCL escapes as '$${' and '%%{' -- and the
    control characters which a quoted string cannot carry.
    """
    escaped = (value.replace('\\', '\\\\')
                    .replace('"', '\\"')
                    .replace('${', '$${')
                    .replace('%{', '%%{')
                    .replace('\n', '\\n')
                    .replace('\t', '\\t')
                    .replace('\r', '\\r'))
    return '"' + escaped + '"'


def _hcl_expression(value):
    """Render a configuration value as an HCL expression.

    A string which carries the 'hcl:' prefix is emitted verbatim when
    the prefix is single -- the payload is the HCL expression -- and
    as the literal string when the prefix is doubled. The Python
    literals render as their HCL equivalents: strings, numbers,
    booleans and 'null', lists as HCL arrays and tables as HCL
    objects. A value which has no HCL equivalent is refused.
    """
    raw = hcl_value(value)
    if raw is not None:
        kind, payload = raw
        if kind == 'raw':
            return payload
        return _hcl_string(payload)
    if isinstance(value, str):
        return _hcl_string(value)
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if value is None:
        return 'null'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value or value in (float('inf'), float('-inf')):
            raise ValueError('The value {!r} is not a finite number '
                             'and has no HCL equivalent'.format(value))
        return repr(value)
    if isinstance(value, list):
        return '[' + ', '.join(_hcl_expression(item) for item in value) + ']'
    if isinstance(value, dict):
        if not value:
            return '{}'
        return '{ ' + ', '.join(
            '{} = {}'.format(_hcl_key(key), _hcl_expression(val))
            for key, val in value.items()) + ' }'
    raise ValueError('The value {!r} of type {!r} has no HCL '
                     'equivalent'.format(value, type(value).__name__))


def _hcl_key(key):
    """Render a configuration table key as an HCL object key."""
    if _HCL_IDENTIFIER.match(key):
        return key
    return _hcl_string(key)


def render_inputs(inputs):
    """Render the inputs table of a module as HCL attribute lines.

    The attributes are indented to the level of the module block and
    their names are aligned to the longest name of the table, which
    is the layout 'tofu fmt' produces: the generated file is
    fmt-clean, so running 'tofu fmt' on the view does not churn it.
    """
    width = max((len(name) for name in inputs), default=0)
    return '\n'.join('  {} = {}'.format(name.ljust(width),
                                        _hcl_expression(value))
                     for name, value in inputs.items())


def resolve_modules(project, modules=None):
    """Return the module set which a new view is created with.

    The '--module' options of the command line replace the
    'tofu.default_modules' configuration option, which itself defaults
    to an empty table: a view without modules. The resolution applies
    when a view is created -- the 'tofu.mkview.default_modules' option is
    consulted only there; the module set of an existing view lives in
    its configuration drop-in, which the user owns.
    """
    if modules:
        return parse_module_specs(modules)
    return project.config.raw['tofu']['mkview']['default_modules']


def _local_name(source):
    """Derive the local name of a registry module source address.

    The local name is the package name of the registry path: the
    second segment of 'namespace/name[/submodule]', or the third
    segment of 'hostname/namespace/name[/submodule]'. A hostname is
    the first segment which carries a '.' or a ':', or the literal
    'localhost'.
    """
    path = source.partition('//')[0]
    segments = path.split('/')
    if (len(segments) > 2 and ('.' in segments[0] or ':' in segments[0]
                               or segments[0] == 'localhost')):
        return segments[2]
    return segments[1]


def parse_module_specs(specs):
    """Parse the '--module' arguments into the recorded module table.

    Each argument is a module source address in the OpenTofu registry
    notation, optionally with a version pin separated by '='. The
    local name of each module is derived from the source address; two
    arguments which derive the same local name are a mistake and are
    refused -- OpenTofu refuses the same collision in the generated
    file.
    """
    modules = {}
    for spec in specs:
        source, _, version = spec.partition('=')
        name = _local_name(source)
        if name in modules:
            raise ValueError(
                "The '--module' options derive the local name {!r} "
                'from more than one module source: the sources {!r} '
                'and {!r} collide, and OpenTofu refuses duplicate '
                'module names.'.format(name, modules[name]['source'],
                                       source))
        modules[name] = {'source': source, 'version': version}
    return modules


def module_entries(modules):
    """Split the recorded module table into the template's entries.

    Each entry carries the local name, the source address, the
    version pin and the rendered inputs of the module instance. The
    table key is the local module name of user-recorded modules; the
    '--module' options derive it from the source address.
    """
    entries = []
    for name, spec in modules.items():
        entries.append({
            'name': name,
            'source': spec.get('source', ''),
            'version': spec.get('version', ''),
            'inputs': render_inputs(spec.get('inputs') or {}),
        })
    return entries


def render_modules(entries):
    """Render the content of the generated 'modules.tf' file."""
    return render_template('modules.tf.j2', modules=entries) + '\n'


def reconcile_modules(project, view, force=False, dry_run=False):
    """Reconcile the generated 'modules.tf' file of a view.

    The file is derived from the 'views.<view>.tofu.modules' option of
    the view's configuration drop-in, which the reconcile keeps in
    step with the recorded set. An empty recorded set removes the
    generated file.

    Returns the list of proposed changes; with 'dry_run' nothing is
    written. Raises ValueError on the user-owned conflict without
    'force'.
    """
    try:
        modules = view_tofu_options(project, view).get('modules')
    except (KeyError, TypeError):
        modules = {}
    entries = module_entries(modules or {})
    expected = render_modules(entries) if entries else None
    entries_repr = ', '.join(
        '{}{}'.format(entry['source'],
                      '=' + entry['version'] if entry['version'] else '')
        for entry in entries)
    return reconcile_managed_file(project, view, 'modules.tf', expected,
                                  set_name='module set',
                                  entries_repr=entries_repr,
                                  force=force, dry_run=dry_run)
