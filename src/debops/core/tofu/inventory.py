# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The 'debops tofu inventory' bridge.

The static renderer which turns the OpenTofu inventory outputs of a
tofu view into the Ansible view's inventory: the hosts file in the
configured format, the variables files in the 'host_vars/' and
'group_vars/' directories and the sensitive variable values into the
view's secret store. The files the renderer owns are recorded in a
manifest inside the inventory directory; the next render prunes the
entries the seed dropped against it.
"""

import difflib
import json
import logging
import os
import re

import toml
import yaml

from ..ansible.inventory import AnsibleInventory
from ..utils import remove_dir, remove_file, write_file

logger = logging.getLogger(__name__)

# The hosts file formats the bridge renders, the filenames which name
# them by default and the extensions the respective inventory plugins
# claim. A configured hosts file name which carries none of the
# format's extensions gets the format's canonical suffix appended.
FORMATS = ('ini', 'yaml', 'json', 'toml')

DEFAULT_HOSTS_FILENAMES = {
    'ini': 'hosts',
    'yaml': 'hosts.yml',
    'json': 'hosts.json',
    'toml': 'hosts.toml',
}

FORMAT_EXTENSIONS = {
    'ini': (),
    'yaml': ('.yaml', '.yml'),
    'json': ('.json',),
    'toml': ('.toml',),
}

# The manifest of the files the renderer owns, kept inside the
# inventory directory. The directory inventory source skips hidden
# files, so the manifest never enters the inventory itself.
MANIFEST_NAME = '.tofu-inventory-manifest.yml'

# The attributes of a host entry of the 'inventory_seed' output and
# of a group entry of the 'inventory_groups' output. An entry which
# carries anything else is refused: the bridge names the unknown
# attributes instead of rendering a typo silently.
HOST_ATTRIBUTES = ('address', 'groups', 'host', 'jump', 'status',
                   'sensitive_vars', 'vars')
GROUP_ATTRIBUTES = ('children', 'sensitive_vars', 'vars')

# The header which marks the files the renderer rewrites on every
# run. The sensitive content files in the store carry no header:
# they hold the exact value the 'file' lookup returns.
_HEADER = (
    "# This file is rendered by 'debops tofu inventory' from the",
    "# OpenTofu outputs of the view '{view}'. Do not edit it by hand:",
    '# the next render replaces it.',
)


def _header(view):
    return '\n'.join(line.format(view=view) for line in _HEADER) + '\n\n'


def _mapping(value):
    """Return *value* when it is a mapping, an empty mapping
    otherwise."""
    return value if isinstance(value, dict) else {}


def _inventory_config(project):
    """Return the bridge options of the project, with the defaults
    for the options the configuration does not carry."""
    try:
        section = project.config.raw['tofu']['inventory']
    except (KeyError, TypeError):
        section = {}
    section = _mapping(section)
    secret = _mapping(section.get('secret'))
    output = _mapping(section.get('output'))
    host_status = output.get('host_status')
    return {
        'hosts_format': section.get('hosts_format', 'ini'),
        'vars_filename': section.get('vars_filename',
                                     'tofu_inventory.yml'),
        'secret_vars_filename': secret.get('vars_filename',
                                           'tofu_inventory.yml'),
        'sensitive_path': secret.get(
            'sensitive_path', 'secret/tofu/%s/sensitive/%s/content'),
        'host_status': dict(_mapping(host_status)) or
        {'running': 'include'},
        'hosts_filenames': {
            fmt: section.get('hosts_filename_' + fmt,
                             DEFAULT_HOSTS_FILENAMES[fmt])
            for fmt in FORMATS},
    }


def _hosts_filename(config, fmt):
    """Return the hosts file name of one format, with the format's
    canonical extension appended when the configured name carries
    none of the extensions the inventory plugin claims."""
    name = config['hosts_filenames'][fmt]
    extensions = FORMAT_EXTENSIONS[fmt]
    if extensions and not name.endswith(extensions):
        name += DEFAULT_HOSTS_FILENAMES[fmt][len('hosts'):]
    return name


def _output_value(outputs, name):
    """Return the value of one output of the document, None when the
    output is not there."""
    try:
        return outputs[name]['value']
    except (KeyError, TypeError):
        return None


def _validate_groups_list(name, groups):
    if not isinstance(groups, list) or \
            not all(isinstance(group, str) for group in groups):
        raise ValueError(
            "The group list of the entry '{}' is not a list of group "
            'names.'.format(name))
    for group in groups:
        _validate_name(
            group, "the group list of the entry '{}'".format(name))


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


def _validate_address(name, kind, address):
    """The address rides the INI host line as a single token:
    whitespace or '=' would inject further inline variables."""
    if isinstance(address, str) and re.search(r'[\s=]', address):
        raise ValueError(
            "The address of the {} '{}' carries whitespace or '=': "
            'the address rides the host line as a single '
            'token.'.format(kind, name))


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


def _host_records(seed):
    """Return the host records the inventory renders: the inventory
    hostname, the secret key, the address, the jump host, the
    declared groups and the plain and sensitive variables.

    The inventory hostname is the 'host' attribute when the entry
    carries one, the seed key otherwise; the secret paths are keyed
    by the seed key, the tofu-side identity which survives a
    hostname change. The check runs after the status filter: a host
    which a status skip removes from the render never needs an
    address -- a stopped instance exports none."""
    records = []
    hostnames = {}
    for key, entry in seed.items():
        if not entry.get('address'):
            raise ValueError(
                "The seed host '{}' carries no 'address' attribute: "
                'the rendered inventory cannot reach it.'.format(key))
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


def _root_groups(records):
    """The names of the groups which no other group names as its
    child: the root of the group hierarchy."""
    return sorted(name for name in records
                  if not any(name in records[parent]['children']
                             for parent in records))


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


def _ini_host_line(host):
    """The host line of the 'ini' format: the inventory hostname,
    the address, the composed jump arguments and the scalar plain
    variables."""
    parts = [host['name'],
             'ansible_host={}'.format(_ini_value(host['address']))]
    if host['jump']:
        parts.append('ansible_ssh_common_args={}'.format(
            _ini_value('-o ProxyJump={}'.format(host['jump']))))
    for name in sorted(host['vars']):
        if _is_scalar(host['vars'][name]):
            parts.append('{}={}'.format(name, _ini_value(
                host['vars'][name])))
    return ' '.join(parts)


def _render_hosts_ini(hosts, records, all_record, view):
    """Render the hosts file in the 'ini' format.

    The full host line -- the hostname, the address, the jump
    arguments and the scalar variables -- is written once, in the
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


def _yaml_json_doc(hosts, records, all_record):
    """The logical inventory of the 'yaml' and 'json' formats: the
    hosts with their plain variables under 'all.hosts', the global
    variables under 'all.vars', the group hierarchy under
    'all.children'."""
    doc = {'all': {'hosts': {}}}
    for host in sorted(hosts, key=lambda host: host['name']):
        doc['all']['hosts'][host['name']] = host['vars'] or None
    if all_record and all_record['vars']:
        doc['all']['vars'] = dict(sorted(all_record['vars'].items()))
    children = {name: _group_node(name, records)
                for name in _root_groups(records)}
    children = {name: node for name, node in children.items()
                if node is not None}
    if children:
        doc['all']['children'] = children
    return doc


def _render_hosts_yaml(doc, view):
    return _header(view) + yaml.safe_dump(
        doc, default_flow_style=False, sort_keys=True, width=4096)


def _render_hosts_json(doc):
    """JSON is a YAML subset the yaml inventory plugin claims, but
    it carries no comments: the do-not-edit header of the other
    formats is left out."""
    return json.dumps(doc, indent=2, sort_keys=True) + '\n'


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
        doc['all']['hosts'][host['name']] = dict(
            sorted(host['vars'].items()))
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


def _sensitive_location(config, view_root, name, var):
    """Return the write path, the lookup path expression and the
    containment root of one sensitive value. A template which starts
    with '/' is absolute: the content file is written there, the
    lookup uses it as-is and the write carries no containment root --
    the operator configured the destination. A relative template is
    resolved against the Ansible view's root directory, which the
    'inventory_dir' variable of the lookup expression walks out of;
    the write stays inside the view root. The expression composes
    through 'json.dumps': the path rides a Jinja string literal, a
    quote in it must not break out of it."""
    try:
        relative = config['sensitive_path'] % (name, var)
    except (TypeError, ValueError) as errmsg:
        raise ValueError(
            "The 'tofu.inventory.secret.sensitive_path' option is "
            'not a valid path template: {}'.format(errmsg))
    if relative.startswith('/'):
        return relative, json.dumps(relative), None
    return (os.path.join(view_root, relative),
            'inventory_dir + ' + json.dumps('/../' + relative),
            view_root)


def _sensitive_value(value):
    """The exact bytes of one sensitive value: strings are written
    as they are, the other types are JSON-serialized and the user
    parses them with the 'from_json' filter."""
    return value if isinstance(value, str) else json.dumps(value)


def _manifest_path(view_root, path):
    """The manifest form of a file path: relative to the view root
    when the path is inside it, absolute otherwise."""
    path = os.path.normpath(path)
    view_root = os.path.normpath(view_root)
    if path.startswith(view_root + os.sep):
        return os.path.relpath(path, view_root)
    return path


def _unified_diff(old_content, new_content, label):
    """Return the unified diff between two file contents, labeled with
    the change label of the path."""
    return ''.join(difflib.unified_diff(
        (old_content or '').splitlines(keepends=True),
        (new_content or '').splitlines(keepends=True),
        fromfile='a/' + label, tofile='b/' + label))


def _change_label(path, project_root):
    """The path form the change records print and label: relative to
    the project directory when the path is inside it, absolute
    otherwise."""
    path = os.path.normpath(path)
    project_root = os.path.normpath(project_root)
    if path.startswith(project_root + os.sep):
        return os.path.relpath(path, project_root)
    return path


def _reconcile_file(path, content, changes, project_root, containment,
                    dry_run, secret=False):
    """Record the change of one file and apply it: create, update or
    nothing.

    The files inside the encrypted store are re-encrypted on every
    write -- the ciphertext of an unchanged value differs per save --
    so a render which changes nothing writes nothing and the store
    of the view stays clean. The diff rides the record for the
    '--diff' option; the sensitive files record none, their values
    must not reach the terminal -- the action line names the file
    instead. Nothing is written in the dry run. The containment
    root, when given, refuses a path which resolves outside of it."""
    label = _change_label(path, project_root)
    try:
        with open(path) as handle:
            existing = handle.read()
    except OSError:
        existing = None
    if existing == content:
        logger.info("The file '{}' is unchanged".format(label))
        return
    if existing is None:
        action, old = 'create', ''
    else:
        action, old = 'update', existing
    changes.append({
        'path': path,
        'action': action,
        'diff': None if secret else _unified_diff(old, content, label),
        'secret': secret,
    })
    if not dry_run:
        write_file(path, content, overwrite=True, project=containment)


def _reconcile_removal(path, changes, project_root, containment,
                       dry_run, secret=False):
    """Record the removal of one file and apply it; report whether
    the file was removed, so that the caller can prune the
    directories it left behind. The sensitive files record no diff:
    the removed content is the secret itself."""
    try:
        with open(path) as handle:
            existing = handle.read()
    except OSError:
        return False
    label = _change_label(path, project_root)
    changes.append({
        'path': path,
        'action': 'remove',
        'diff': None if secret else _unified_diff(existing, '', label),
        'secret': secret,
    })
    if dry_run:
        return False
    return remove_file(path, project=containment)


def _is_scaffold(path):
    """Whether the file holds only the placeholder which the project
    init writes: comments and the '[debops_all_hosts]' section
    header, with the host line still commented out."""
    try:
        with open(path) as handle:
            lines = handle.read().splitlines()
    except OSError:
        return False
    content = [line.strip() for line in lines
               if line.strip() and not line.strip().startswith('#')]
    return content in ([], ['[debops_all_hosts]'])


def _read_manifest(inventory_dir):
    """Return the file paths the previous render recorded, relative
    to the Ansible view's root directory. A missing or unreadable
    manifest means nothing is owned yet."""
    try:
        with open(os.path.join(inventory_dir, MANIFEST_NAME)) as handle:
            manifest = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return []
    files = _mapping(manifest).get('files', [])
    return files if isinstance(files, list) else []


def _write_manifest(inventory_dir, files, project):
    content = ("# The files which 'debops tofu inventory' renders in "
               'the view. The next\n# render prunes the entries the '
               'seed dropped against this record.\n\n')
    content += yaml.safe_dump({'files': sorted(files)},
                              default_flow_style=False, width=4096)
    write_file(os.path.join(inventory_dir, MANIFEST_NAME), content,
               overwrite=True, project=project)


def _prune_empty_dirs(directory, view_root):
    """Remove the directories a pruned file left behind, stopping at
    the direct children of the view root: the 'inventory/' and
    'secret/' directories stay even when a render empties them."""
    directory = os.path.normpath(directory)
    view_root = os.path.normpath(view_root)
    if not directory.startswith(view_root + os.sep):
        return
    while directory != view_root and \
            os.path.dirname(directory) != view_root:
        if not remove_dir(directory, project=view_root):
            break
        directory = os.path.dirname(directory)


def _prune_stale(view_root, project_root, owned, desired, changes,
                 dry_run):
    """Remove the recorded files which the render no longer
    produces, and the directories they leave empty.

    The removals stay inside the view root: an entry which resolves
    outside of it refuses the render, the manifest is recorded state
    and a tampered one must not delete files elsewhere. The absolute
    entries which an absolute 'sensitive_path' template records by
    design are skipped with a notice -- their stale files the
    operator cleans by hand. The removals ride the change records;
    the sensitive ones record no diff, the removed content is the
    secret itself."""
    for relative in owned:
        if relative in desired:
            continue
        if os.path.isabs(relative):
            logger.notice(
                "The stale file '{}' is outside of the view root: "
                'the render does not prune it, clean it by '
                'hand.'.format(relative),
                extra={'allow': 'stderr'})
            continue
        path = os.path.join(view_root, relative)
        removed = _reconcile_removal(
            path, changes, project_root, view_root, dry_run,
            secret=relative.startswith('secret' + os.sep))
        if removed:
            _prune_empty_dirs(os.path.dirname(path), view_root)


def _reconcile_sensitive(desired, changes, config, view_root,
                         project_root, name, sensitive_vars, dry_run):
    """Record and apply the sensitive values of one host or group
    into the store, recording the content files in the desired set."""
    for var in sorted(sensitive_vars):
        path, _, containment = _sensitive_location(config, view_root,
                                                   name, var)
        _reconcile_file(path, _sensitive_value(sensitive_vars[var]),
                        changes, project_root, containment, dry_run,
                        secret=True)
        desired.add(_manifest_path(view_root, path))


def _write_vars_file(desired, changes, inventory_dir, kind, name,
                     filename, data, view, view_root, project_root,
                     dry_run):
    """Render one variables file of a host or group; a file with
    nothing to carry is not written."""
    if not data:
        return
    path = os.path.join(inventory_dir, kind, name, filename)
    content = _header(view) + yaml.safe_dump(
        data, default_flow_style=False, sort_keys=True, width=4096)
    _reconcile_file(path, content, changes, project_root, view_root,
                    dry_run)
    desired.add(os.path.join('inventory', kind, name, filename))


def _render_vars_files(desired, changes, config, fmt, view_root,
                       inventory_dir, project_root, kind, name, plain,
                       sensitive, secret_name, view, dry_run):
    """Render the variables files of one host or group.

    The 'ini' hosts file carries the scalar plain variables inline;
    the complex ones ride the plain variables file. The other
    formats carry every plain variable natively, so their plain
    variables file is never written. The sensitive variables ride
    their own file in every format, as 'file' lookup references
    into the store. When the two file names are distinct the file
    kinds split; the shared default name merges them into one
    file."""
    if fmt == 'ini':
        complex_vars = {key: plain[key] for key in sorted(plain)
                        if not _is_scalar(plain[key])}
    else:
        complex_vars = {}
    lookups = {}
    for var in sorted(sensitive):
        expression = _sensitive_location(
            config, view_root, secret_name, var)[1]
        # No str.format() here: the doubled braces of the Jinja
        # delimiters would be read as literal-brace escapes
        lookups[var] = '{{ lookup("file", ' + expression + ') }}'
    if config['vars_filename'] == config['secret_vars_filename']:
        merged = dict(complex_vars)
        merged.update(lookups)
        _write_vars_file(desired, changes, inventory_dir, kind, name,
                         config['vars_filename'], merged, view,
                         view_root, project_root, dry_run)
    else:
        _write_vars_file(desired, changes, inventory_dir, kind, name,
                         config['vars_filename'], complex_vars, view,
                         view_root, project_root, dry_run)
        _write_vars_file(desired, changes, inventory_dir, kind, name,
                         config['secret_vars_filename'], lookups,
                         view, view_root, project_root, dry_run)


def render_inventory(project, view, output_json, dry_run=False):
    """Render the OpenTofu inventory outputs of a view into the
    Ansible view's inventory directory.

    Returns the list of the changes the render applies: the records
    the '--diff' option prints and the dry run reports. With
    'dry_run' the changes are computed and reported, nothing is
    written -- the render reads the current files, which needs the
    Ansible store unlocked around it as a writing render does."""
    seed, groups = _collect_outputs(output_json)
    config = _inventory_config(project)
    seed = _filter_hosts(seed, config['host_status'])
    hosts = _host_records(seed)
    records = _group_records(groups, hosts)
    _check_hierarchy(records)
    all_record = records.pop('all', None)

    inventory = AnsibleInventory(project, view)
    view_root = inventory.root_path
    inventory_dir = inventory.path
    if not os.path.isdir(inventory_dir):
        raise FileNotFoundError(
            "The inventory directory of the Ansible view '{}' does "
            'not exist: {}'.format(view, inventory_dir))
    project_root = project.path
    changes = []

    fmt = config['hosts_format']
    if fmt not in FORMATS:
        raise ValueError(
            "The 'tofu.inventory.hosts_format' option is '{}': the "
            'bridge renders one of {}.'.format(fmt, ', '.join(FORMATS)))
    logger.debug(
        "Rendering the inventory of the view '{}' from {} hosts and "
        '{} group records in the {} format'.format(
            view, len(hosts), len(records), fmt))
    logger.debug(
        "The inventory options of the view '{}': hosts_format={}, "
        'vars_filename={}, secret.vars_filename={}, '
        'sensitive_path={}'.format(
            view, fmt, config['vars_filename'],
            config['secret_vars_filename'], config['sensitive_path']))

    desired = set()

    # The sensitive values into the store, before the files which
    # reference them
    if all_record:
        _reconcile_sensitive(desired, changes, config, view_root,
                             project_root, 'all',
                             all_record['sensitive_vars'], dry_run)
    for host in hosts:
        _reconcile_sensitive(desired, changes, config, view_root,
                             project_root, host['key'],
                             host['sensitive_vars'], dry_run)
    for name in sorted(records):
        _reconcile_sensitive(desired, changes, config, view_root,
                             project_root, name,
                             records[name]['sensitive_vars'], dry_run)

    # The hosts file in the configured format
    if fmt == 'ini':
        content = _render_hosts_ini(hosts, records, all_record, view)
    elif fmt == 'yaml':
        content = _render_hosts_yaml(
            _yaml_json_doc(hosts, records, all_record), view)
    elif fmt == 'json':
        content = _render_hosts_json(
            _yaml_json_doc(hosts, records, all_record))
    else:
        content = _render_hosts_toml(hosts, records, all_record, view)
    hosts_name = _hosts_filename(config, fmt)
    _reconcile_file(os.path.join(inventory_dir, hosts_name), content,
                    changes, project_root, view_root, dry_run)
    desired.add(os.path.join('inventory', hosts_name))

    # The hosts files of the other formats are the renderer's
    # namespace as well: the manifest prune removes the ones a
    # previous render wrote, the scaffold placeholder which the
    # project init writes is claimed by the first render
    for other in FORMATS:
        if other == fmt:
            continue
        path = os.path.join(inventory_dir, _hosts_filename(config, other))
        if os.path.isfile(path) and _is_scaffold(path):
            _reconcile_removal(path, changes, project_root, view_root,
                               dry_run)

    # The variables files of the hosts and the groups
    for host in hosts:
        _render_vars_files(desired, changes, config, fmt, view_root,
                           inventory_dir, project_root, 'host_vars',
                           host['name'], host['vars'],
                           host['sensitive_vars'], host['key'], view,
                           dry_run)
    if all_record:
        _render_vars_files(desired, changes, config, fmt, view_root,
                           inventory_dir, project_root, 'group_vars',
                           'all', all_record['vars'],
                           all_record['sensitive_vars'], 'all', view,
                           dry_run)
    for name in sorted(records):
        record = records[name]
        _render_vars_files(desired, changes, config, fmt, view_root,
                           inventory_dir, project_root, 'group_vars',
                           name, record['vars'],
                           record['sensitive_vars'], name, view,
                           dry_run)

    owned = _read_manifest(inventory_dir)
    _prune_stale(view_root, project_root, owned, desired, changes,
                 dry_run)
    if not dry_run:
        _write_manifest(inventory_dir, desired, view_root)
    return changes
