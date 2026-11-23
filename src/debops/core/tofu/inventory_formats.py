# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The hosts-file renderers of the inventory bridge.

One renderer per hosts-file format -- 'ini', 'yaml', 'json' and
'toml' -- each shape verified against its inventory plugin: the
value quoting of the ini round-trip, the children as a mapping for
the YAML plugin and as a list for the TOML one, the JSON subset
carrying no comments. The renderers are pure: the seed records in,
the file content out; the file writes and the manifest stay in the
bridge module.
"""

import json

import toml
import yaml

from .inventory_seed import _root_groups


def _render_hosts_ini(hosts, records, all_record, view):
    """Render the hosts file in the 'ini' format.

    The full host line -- the hostname, the address and the scalar
    variables -- is written once, in the
    first group section of the host or in '[ungrouped]' when the
    host declares no groups; the other group sections list the host
    bare, the inline variables apply to the host regardless of the
    section which carries them. Every group is declared by a member
    section, so that the ':children' and ':vars' sections which
    follow never reference an undefined group."""
    host_by_name = {host['name']: host for host in hosts}
    body = []
    if all_record and all_record['vars']:
        body.append('[all:vars]')
        for name in sorted(all_record['vars']):
            body.append('{}={}'.format(
                name, _ini_value(all_record['vars'][name])))
        body.append('')
    ungrouped = sorted(
        (host for host in hosts if not host['groups']),
        key=lambda host: host['name'])
    if ungrouped:
        body.append('[ungrouped]')
        for host in ungrouped:
            body.append(_ini_host_line(host))
        body.append('')
    for name in sorted(records):
        body.append('[{}]'.format(name))
        for member in sorted(records[name]['members']):
            host = host_by_name[member]
            if host['groups'] and min(host['groups']) == name:
                body.append(_ini_host_line(host))
            else:
                body.append(host['name'])
        body.append('')
    for name in sorted(records):
        if records[name]['children']:
            body.append('[{}:children]'.format(name))
            for child in sorted(records[name]['children']):
                body.append(child)
            body.append('')
    for name in sorted(records):
        if records[name]['vars']:
            body.append('[{}:vars]'.format(name))
            for var in sorted(records[name]['vars']):
                body.append('{}={}'.format(
                    var, _ini_value(records[name]['vars'][var])))
            body.append('')
    return _header(view) + '\n'.join(body).rstrip('\n') + '\n'


def _hosts_filename(base, fmt):
    """Return the hosts file name of one format: the configured base
    name carries the format's canonical extension, appended when the
    name lacks one of the extensions the inventory plugin claims.
    The ini format needs no extension: the ini plugin accepts any
    file name."""
    extensions = FORMAT_EXTENSIONS[fmt]
    if extensions and not base.endswith(extensions):
        return base + extensions[0]
    return base


def _render_hosts_json(doc):
    """JSON is a YAML subset the yaml inventory plugin claims, but
    it carries no comments: the do-not-edit header of the other
    formats is left out."""
    return json.dumps(doc, indent=2, sort_keys=True) + '\n'


def _header(view):
    return '\n'.join(line.format(view=view) for line in _HEADER) + '\n\n'


FORMATS = ('ini', 'yaml', 'json', 'toml')


FORMAT_EXTENSIONS = {
    'ini': (),
    'yaml': ('.yml', '.yaml'),
    'json': ('.json',),
    'toml': ('.toml',),
}


def _yaml_json_doc(hosts, records, all_record):
    """The logical inventory of the 'yaml' and 'json' formats: the
    hosts with their connection target and plain variables under
    'all.hosts', the global variables under 'all.vars', the group
    hierarchy under 'all.children'. The seed's own variables win
    over the resolved connection target when they name one."""
    doc = {'all': {'hosts': {}}}
    for host in sorted(hosts, key=lambda host: host['name']):
        mapping = {'ansible_host': host['ansible_host']}
        mapping.update(host['vars'])
        doc['all']['hosts'][host['name']] = mapping
    if all_record and all_record['vars']:
        doc['all']['vars'] = dict(sorted(all_record['vars'].items()))
    children = {name: _group_node(name, records)
                for name in _root_groups(records)}
    children = {name: node for name, node in children.items()
                if node is not None}
    if children:
        doc['all']['children'] = children
    return doc


def _ini_host_line(host):
    """The host line of the 'ini' format: the inventory hostname,
    the connection target and the scalar plain variables. The
    seed's own 'ansible_host' variable wins over the resolved
    connection target; the jump rides 'ansible_ssh_common_args'
    among the plain variables, composed at the seed record."""
    connection = host['vars'].get('ansible_host', host['ansible_host'])
    parts = [host['name'],
             'ansible_host={}'.format(_ini_value(connection))]
    for name in sorted(host['vars']):
        if name == 'ansible_host':
            continue
        if _is_scalar(host['vars'][name]):
            parts.append('{}={}'.format(name, _ini_value(
                host['vars'][name])))
    return ' '.join(parts)


_HEADER = (
    "# This file is rendered by 'debops tofu inventory' from the",
    "# OpenTofu outputs of the view '{view}'. Do not edit it by hand:",
    '# the next render replaces it.',
)


def _is_scalar(value):
    """Whether the value rides the hosts file inline in the 'ini'
    format: the scalars do, the lists and maps ride the variables
    files."""
    return isinstance(value, (str, bool, int, float))


def _ini_value(value):
    """The inline form of a scalar value: the repr of the value,
    which the ini parser reads back through ast.literal_eval with a
    string fallback.

    The host lines are shlex-stripped before the literal_eval, the
    ':vars' sections are not -- one quoted form cannot satisfy both
    surfaces, and the wrap which satisfied the host lines put
    literal quotes into the ':vars' strings. The bare repr restores
    the ':vars' round trip; the values the host-line strip corrupts
    -- numeric-looking strings, backslashes -- parse as their Python
    look-alikes instead, accepted for the quoting which reads
    naturally (2026-11-20)."""
    return repr(value)


def _render_hosts_toml(hosts, records, all_record, view):
    """Render the hosts file in the 'toml' format.

    The shape is flat, unlike the nested 'yaml' one: the groups are
    top-level tables and the children are name lists which the
    inventory plugin resolves itself, so the group nodes are not
    nested inside each other. The plugin requires the children as a
    list -- the opposite of the yaml plugin, which requires a
    mapping."""
    doc = {'all': {'hosts': {}}}
    for host in sorted(hosts, key=lambda host: host['name']):
        mapping = {'ansible_host': host['ansible_host']}
        mapping.update(dict(sorted(host['vars'].items())))
        doc['all']['hosts'][host['name']] = mapping
    if all_record and all_record['vars']:
        doc['all']['vars'] = dict(sorted(all_record['vars'].items()))
    top = _root_groups(records)
    if top:
        doc['all']['children'] = top
    for name in sorted(records):
        record = records[name]
        node = {'hosts': {member: {}
                          for member in sorted(record['members'])}}
        if record['children']:
            node['children'] = sorted(record['children'])
        if record['vars']:
            node['vars'] = dict(sorted(record['vars'].items()))
        doc[name] = node
    return _header(view) + toml.dumps(doc)


def _group_node(name, records):
    """The rendered node of one group: its members, variables and
    the nested nodes of its child groups. A group which declares
    nothing renders as null."""
    record = records[name]
    node = {}
    if record['members']:
        node['hosts'] = {member: None
                         for member in sorted(record['members'])}
    if record['vars']:
        node['vars'] = dict(sorted(record['vars'].items()))
    if record['children']:
        node['children'] = {child: _group_node(child, records)
                            for child in sorted(record['children'])}
    return node or None


def _render_hosts_yaml(doc, view):
    return _header(view) + yaml.safe_dump(
        doc, default_flow_style=False, sort_keys=True, width=4096)
