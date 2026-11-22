# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The seed contract of the inventory bridge.

The 'inventory_seed' and 'inventory_groups' outputs of a tofu view
carry the hosts, the groups, their attributes and their variables;
this module validates the shape of the outputs and resolves them
into the records the renderers consume. A seed which carries
anything the bridge cannot render safely is refused here, with the
offending entry named.
"""


import json


import logging


import re


logger = logging.getLogger(__name__)


GROUP_ATTRIBUTES = ('children', 'sensitive_vars', 'vars')


HOST_ATTRIBUTES = ('address', 'groups', 'host', 'jump', 'status',
                   'sensitive_vars', 'vars')


def _check_hierarchy(records):
    """Refuse a group hierarchy which carries a cycle: the rendered
    nesting would never terminate."""
    def walk(name, path):
        if name in path:
            raise ValueError(
                'The group hierarchy of the inventory outputs '
                'carries a cycle at {!r}.'.format(name))
        for child in records[name]['children']:
            walk(child, path | {name})

    for name in records:
        walk(name, frozenset())


def _collect_outputs(output_json):
    """Parse the 'tofu output -json' document into the two outputs
    the bridge consumes.

    The document carries every output of the view as a map of
    {name: {sensitive, type, value}} entries; the bridge consumes the
    'inventory_seed' output, required, and the 'inventory_groups'
    output, optional. The other outputs are the user's business.
    """
    try:
        outputs = json.loads(output_json)
    except json.JSONDecodeError as errmsg:
        raise ValueError(
            "The 'tofu output -json' document of the view is not "
            'valid JSON: {}'.format(errmsg))
    if not isinstance(outputs, dict):
        raise ValueError(
            "The 'tofu output -json' document of the view is not a "
            'map of outputs.')

    seed = _output_value(outputs, 'inventory_seed')
    if not isinstance(seed, dict):
        raise ValueError(
            "The 'inventory_seed' output is missing from the view or "
            'is not a map of hosts: the bridge renders the inventory '
            'from it.')
    for name, entry in seed.items():
        _validate_entry(name, entry, HOST_ATTRIBUTES, 'seed host')

    groups_value = _output_value(outputs, 'inventory_groups')
    if groups_value is not None and not isinstance(groups_value, dict):
        raise ValueError(
            "The 'inventory_groups' output of the view is not a map "
            'of groups.')
    groups = _mapping(groups_value)
    for name, entry in groups.items():
        _validate_entry(name, entry, GROUP_ATTRIBUTES, 'group')
    return seed, groups


def _filter_hosts(seed, host_status):
    """Return the seed entries the bridge renders, per the
    'tofu.inventory.output.host_status' handling map.

    The status of an entry decides: a status which the map names is
    followed, a status it does not name is skipped with a notice, an
    entry without a status is always rendered. The status values are
    matched lowercased: the providers export them capitalized.
    """
    rendered = {}
    for name, entry in seed.items():
        status = entry.get('status')
        if not status:
            rendered[name] = entry
            continue
        handling = host_status.get(str(status).lower())
        if handling not in ('include', 'skip'):
            if handling is not None:
                raise ValueError(
                    "The handling '{}' of the status '{}' is not "
                    "'include' or 'skip'.".format(handling, status))
            logger.notice(
                "The status '{status}' of the host '{name}' is not "
                "named in the 'tofu.inventory.output.host_status' "
                'option: the host is not rendered'.format(
                    status=status, name=name),
                extra={'allow': 'stderr'})
            continue
        if handling == 'include':
            rendered[name] = entry
    return rendered


def _group_records(groups, hosts):
    """Return the group records: the variables, the sensitive
    variables, the child groups and the member hostnames.

    The 'all' group is a record like the others; its children are
    ignored -- the group is the implicit root which contains every
    host. The groups which only appear in the children lists of
    other groups are records of their own, empty until the outputs
    carry them."""
    records = {}
    for name, entry in groups.items():
        records[name] = {
            'vars': dict(entry.get('vars') or {}),
            'sensitive_vars': dict(entry.get('sensitive_vars') or {}),
            'children': [child for child in entry.get('children', [])
                         if child != 'all'],
            'members': [],
        }
    for host in hosts:
        for name in host['groups']:
            records.setdefault(name, {
                'vars': {}, 'sensitive_vars': {},
                'children': [], 'members': []})
            records[name]['members'].append(host['name'])
    for record in list(records.values()):
        for child in record['children']:
            records.setdefault(child, {
                'vars': {}, 'sensitive_vars': {},
                'children': [], 'members': []})
    return records


def _host_records(seed):
    """Return the host records the inventory renders: the inventory
    hostname, the secret key, the address, the jump host, the
    declared groups and the plain and sensitive variables.

    The inventory hostname is the 'host' attribute when the entry
    carries one, the seed key otherwise; the secret paths are keyed
    by the seed key, the tofu-side identity which survives a
    hostname change. The check runs after the status filter: a host
    which a status skip removes from the render never needs an
    address -- a stopped instance exports none. A host the filter
    includes which still carries no address skips with the
    staleness notice: the observable case is the lease which landed
    late, and the way out is the '--force' option, which refreshes
    the state before the render."""
    records = []
    hostnames = {}
    for key, entry in seed.items():
        if not entry.get('address'):
            logger.notice(
                "The state of the host '{}' carries no address: "
                'the render skips it. Run \'debops tofu inventory '
                "--force' to refresh the state if the address was "
                'expected.'.format(key),
                extra={'allow': 'stderr'})
            continue
        name = entry.get('host') or key
        if name in hostnames:
            raise ValueError(
                "The seed hosts '{}' and '{}' both render as the "
                "inventory hostname '{}'.".format(
                    hostnames[name], key, name))
        hostnames[name] = key
        records.append({
            'name': name,
            'key': key,
            'address': str(entry['address']),
            'jump': entry.get('jump'),
            'groups': [group for group in entry.get('groups', [])
                       if group != 'all'],
            'vars': dict(entry.get('vars') or {}),
            'sensitive_vars': dict(entry.get('sensitive_vars') or {}),
        })
    return records


def _mapping(value):
    """Return *value* when it is a mapping, an empty mapping
    otherwise."""
    return value if isinstance(value, dict) else {}


def _output_value(outputs, name):
    """Return the value of one output of the document, None when the
    output is not there."""
    try:
        return outputs[name]['value']
    except (KeyError, TypeError):
        return None


def _root_groups(records):
    """The names of the groups which no other group names as its
    child: the root of the group hierarchy."""
    return sorted(name for name in records
                  if not any(name in records[parent]['children']
                             for parent in records))


def _validate_address(name, kind, address):
    """The address rides the INI host line as a single token:
    whitespace or '=' would inject further inline variables."""
    if isinstance(address, str) and re.search(r'[\s=]', address):
        raise ValueError(
            "The address of the {} '{}' carries whitespace or '=': "
            'the address rides the host line as a single '
            'token.'.format(kind, name))


def _validate_entry(name, entry, attributes, kind):
    """Check the shape of one host or group entry: a mapping of the
    known attributes with the types the renderer reads them as. The
    names the entry carries cross into file paths and rendered
    syntax, so they are validated as such."""
    _validate_name(name, kind)
    if not isinstance(entry, dict):
        raise ValueError(
            "The {} '{}' of the inventory outputs is not a map of "
            'attributes.'.format(kind, name))
    unknown = set(entry) - set(attributes)
    if unknown:
        raise ValueError(
            "The {} '{}' carries unknown attributes: {}. The known "
            'attributes are: {}.'.format(
                kind, name, ', '.join(sorted(unknown)),
                ', '.join(sorted(attributes))))
    for attr in ('vars', 'sensitive_vars'):
        if attr in entry and not isinstance(entry[attr], dict):
            raise ValueError(
                "The '{}' attribute of the {} '{}' is not a map of "
                'variables.'.format(attr, kind, name))
    for attr in ('vars', 'sensitive_vars'):
        for var in entry.get(attr, {}):
            _validate_name(
                var, "the variables of the {} '{}'".format(kind, name))
    for attr in ('groups', 'children'):
        if attr in entry:
            _validate_groups_list(name, entry[attr])
    if entry.get('host'):
        _validate_name(
            entry['host'],
            "the 'host' attribute of the {} '{}'".format(kind, name))
    if 'address' in entry:
        _validate_address(name, kind, entry['address'])
    if 'jump' in entry:
        _validate_jump(name, kind, entry['jump'])


def _validate_groups_list(name, groups):
    if not isinstance(groups, list) or \
            not all(isinstance(group, str) for group in groups):
        raise ValueError(
            "The group list of the entry '{}' is not a list of group "
            'names.'.format(name))
    for group in groups:
        _validate_name(
            group, "the group list of the entry '{}'".format(name))


def _validate_jump(name, kind, jump):
    """The jump composes into 'ansible_ssh_common_args', which
    Ansible splits into SSH options at runtime: whitespace or quotes
    would smuggle options into the connection. An empty jump is no
    jump: the host connects directly."""
    if not jump:
        return
    if isinstance(jump, str) and \
            not re.fullmatch(r'[A-Za-z0-9._@,:-]+', jump):
        raise ValueError(
            "The jump of the {} '{}' carries characters outside of "
            '[A-Za-z0-9._@,:-]: it composes into '
            "'ansible_ssh_common_args', which Ansible splits into "
            'SSH options.'.format(kind, name))


def _validate_name(name, what):
    """Check one name which crosses into file paths, INI sections and
    lookup expressions: only a safe path component and INI token
    renders."""
    if isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9._-]+', name) \
            and not name.startswith('.'):
        return
    raise ValueError(
        "The name '{}' of {} is not renderable: the bridge needs "
        'names of [A-Za-z0-9._-] without a leading dot, they cross '
        'into file paths and rendered syntax.'.format(name, what))
