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
entries the seed dropped against it. The seed contract lives in
'inventory_seed.py', the hosts-file renderers in
'inventory_formats.py'; this module owns the file writes, the
manifest reconcile and the operation orchestration.
"""

import json
import logging
import os

import yaml

from ..ansible.inventory import AnsibleInventory
from ..secrets import SecretManager, unlocked_store
from ..utils import remove_dir, remove_file, write_file
from .changes import change_label, file_change
from .registry import view_tofu_options
from .inventory_formats import (FORMATS, _header, _hosts_filename,
                                _is_scalar, _render_hosts_ini,
                                _render_hosts_json, _render_hosts_toml,
                                _render_hosts_yaml, _yaml_json_doc)
from .inventory_seed import (_check_hierarchy, _collect_outputs,
                             _filter_hosts, _group_records,
                             _host_records, _mapping)
from .plans import PLAN_DIR, PLAN_FILE_PREFIX, plan_file_names
from .runner import TofuOperationFailed, TofuRunner
from .secrets import TofuSecretStore

logger = logging.getLogger(__name__)

MANIFEST_NAME = '.tofu-inventory-manifest.yml'


def inventory_config(project, view=None):
    """Return the bridge options of the project, with the defaults
    for the options the configuration does not carry.

    The 'to_view' option comes from the view's own option tree: it
    names the Ansible view the render targets, instead of the mirror
    view of the same name. The '--to-view' option of the command line
    overrides it."""
    try:
        section = project.config.raw['tofu']['inventory']
    except (KeyError, TypeError):
        section = {}
    section = _mapping(section)
    secret = _mapping(section.get('secret'))
    to_view = None
    if view:
        view_section = _mapping(
            view_tofu_options(project, view).get('inventory'))
        to_view = view_section.get('to_view') or None
    return {
        'hosts_format': section.get('hosts_format', 'ini'),
        'hosts_filename': section.get('hosts_filename', 'hosts'),
        'ansible_host_format': section.get('ansible_host_format',
                                           'fqdn'),
        'state_refresh': section.get('state_refresh', False),
        'vars_filename': section.get('vars_filename',
                                     'tofu_inventory.yml'),
        'host_path': secret.get(
            'host_path', 'secret/tofu/host_vars/%s/sensitive/%s/content'),
        'group_path': secret.get(
            'group_path',
            'secret/tofu/group_vars/%s/sensitive/%s/content'),
        'host_status': dict(_mapping(section.get('host_status'))) or
        {'running': 'include'},
        'to_view': to_view,
    }


def _sensitive_location(config, view_root, kind, name, var):
    """Return the write path, the lookup path expression and the
    containment root of one sensitive value. The kind selects the
    template: the host values key by the seed key under the
    'host_path' template, the group values by the group name under
    the 'group_path' one -- the two namespaces do not collide when a
    group carries the name of a host. A template which starts
    with '/' is absolute: the content file is written there, the
    lookup uses it as-is and the write carries no containment root --
    the operator configured the destination. A relative template is
    resolved against the Ansible view's root directory, which the
    'inventory_dir' variable of the lookup expression walks out of;
    the write stays inside the view root. The expression composes
    through 'json.dumps': the path rides a Jinja string literal, a
    quote in it must not break out of it."""
    if kind == 'host':
        template = config['host_path']
        option = 'tofu.inventory.secret.host_path'
    else:
        template = config['group_path']
        option = 'tofu.inventory.secret.group_path'
    try:
        relative = template % (name, var)
    except (TypeError, ValueError) as errmsg:
        raise ValueError(
            "The '{}' option is not a valid path template: "
            '{}'.format(option, errmsg))
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
    label = change_label(path, project_root)
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
    changes.append(file_change(path, action, old, content, project_root,
                               secret=secret))
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
    changes.append(file_change(path, 'remove', existing, None,
                               project_root, secret=secret))
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
    """Return the file paths and the sensitive paths the previous
    render recorded, relative to the Ansible view's root directory.
    A missing or unreadable manifest means nothing is owned yet."""
    try:
        with open(os.path.join(inventory_dir, MANIFEST_NAME)) as handle:
            manifest = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError):
        return [], []
    manifest = _mapping(manifest)
    files = manifest.get('files', [])
    sensitive = manifest.get('sensitive', [])
    return (files if isinstance(files, list) else [],
            sensitive if isinstance(sensitive, list) else [])


def _write_manifest(inventory_dir, files, sensitive, project):
    content = ("# The files which 'debops tofu inventory' renders in "
               'the view. The next\n# render prunes the entries the '
               'seed dropped against this record.\n\n')
    content += yaml.safe_dump({'files': sorted(files),
                               'sensitive': sorted(sensitive)},
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
                 dry_run, manifest_sensitive):
    """Remove the recorded files which the render no longer
    produces, and the directories they leave empty.

    The removals stay inside the view root: an entry which resolves
    outside of it refuses the render, the manifest is recorded state
    and a tampered one must not delete files elsewhere. The absolute
    entries which an absolute store path template records by design
    are skipped with a notice -- their stale files the operator
    cleans by hand. The removals ride the change records; the
    sensitive ones record no diff, the removed content is the secret
    itself."""
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
            secret=relative in manifest_sensitive)
        if removed:
            _prune_empty_dirs(os.path.dirname(path), view_root)


def _reconcile_sensitive(desired, sensitive, changes, config,
                         view_root, project_root, kind, name,
                         sensitive_vars, dry_run):
    """Record and apply the sensitive values of one host or group
    into the store, recording the content files in the desired set
    and the sensitive flag in the sensitive set: the prune decides
    the masking of a removal record from the writer's knowledge, not
    from the path -- a custom store path template which does not
    live under 'secret/' must not leak its removed values through
    the '--diff' output."""
    for var in sorted(sensitive_vars):
        path, _, containment = _sensitive_location(
            config, view_root, kind, name, var)
        _reconcile_file(path, _sensitive_value(sensitive_vars[var]),
                        changes, project_root, containment, dry_run,
                        secret=True)
        manifest_path = _manifest_path(view_root, path)
        desired.add(manifest_path)
        sensitive.add(manifest_path)


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
                       sensitive, store_key, view, dry_run):
    """Render the variables file of one host or group.

    The 'ini' hosts file carries the scalar plain variables inline;
    the complex ones ride the variables file. The other formats
    carry every plain variable natively, so nothing plain rides the
    file for them. The sensitive variables ride the same file in
    every format, as 'file' lookup references into the store,
    keyed by the seed key of the host or the name of the group."""
    if fmt == 'ini':
        complex_vars = {key: plain[key] for key in sorted(plain)
                        if not _is_scalar(plain[key])}
    else:
        complex_vars = {}
    lookups = {}
    sensitive_kind = 'host' if kind == 'host_vars' else 'group'
    for var in sorted(sensitive):
        expression = _sensitive_location(
            config, view_root, sensitive_kind, store_key, var)[1]
        # No str.format() here: the doubled braces of the Jinja
        # delimiters would be read as literal-brace escapes
        lookups[var] = '{{ lookup("file", ' + expression + ') }}'
    merged = dict(complex_vars)
    merged.update(lookups)
    _write_vars_file(desired, changes, inventory_dir, kind, name,
                     config['vars_filename'], merged, view,
                     view_root, project_root, dry_run)


def render_view_inventory(project, view, force=False, dry_run=False,
                          allow_missing_state=False, bell=False,
                          to_view=None):
    """Run the 'debops tofu inventory' operation: refresh the state
    when asked, collect the outputs through the runner machinery,
    cycle the Ansible secret store around the render and return the
    change records the render applies.

    The render targets the Ansible view the '--to-view' option or
    the 'views.<view>.tofu.inventory.to_view' option names, the
    Ansible view of the same name as the source when neither does.
    The captured 'tofu output -json' carries the sensitive values of
    the seed in plaintext: the output is collected, never streamed
    to the terminal. The render writes into the Ansible secret store
    of the target view, which cycles around it -- the runner's own
    cycle has already locked the tofu store back, this one is a
    fresh unlock/lock pair. The failures raise: 'TofuOperationFailed'
    carries the return code of the failed tofu operation, the
    renderer's 'ValueError' and 'FileNotFoundError' propagate.
    """
    config = inventory_config(project, view)
    target_view = to_view or config['to_view'] or view
    if force or config['state_refresh']:
        runner = TofuRunner(project, ['refresh'], bell=bell,
                            allow_missing_state=allow_missing_state)
        rc = runner.execute()
        if rc != 0:
            raise TofuOperationFailed(
                "The 'tofu refresh' operation of the view {!r} "
                'failed with exit code {}'.format(view, rc), rc)

    runner = TofuRunner(project, ['output', '-json'], no_color=True,
                        allow_missing_state=allow_missing_state)
    rc, output = runner.execute(capture=True)
    if rc != 0:
        raise TofuOperationFailed(
            "The 'tofu output' operation of the view {!r} failed "
            'with exit code {}'.format(view, rc), rc)

    store = SecretManager(project, target_view).store('ansible')
    with unlocked_store(store,
                        label="The Ansible store of the view "
                              "'{}'".format(target_view)):
        return render_inventory(project, view, output,
                                dry_run=dry_run,
                                target_view=target_view)


def render_inventory(project, view, output_json, dry_run=False,
                     target_view=None):
    """Render the OpenTofu inventory outputs of a view into the
    inventory directory of a target Ansible view.

    The target is the Ansible view the '--to-view' option or the
    'views.<view>.tofu.inventory.to_view' option names, the Ansible
    view of the same name as the source when neither does. The
    source view names the outputs in the rendered header; the target
    view receives the files and the sensitive values.

    Returns the list of the changes the render applies: the records
    the '--diff' option prints and the dry run reports. With
    'dry_run' the changes are computed and reported, nothing is
    written -- the render reads the current files, which needs the
    Ansible store unlocked around it as a writing render does."""
    seed, groups = _collect_outputs(output_json)
    config = inventory_config(project, view)
    target_view = target_view or config['to_view'] or view
    if config['ansible_host_format'] not in ('fqdn', 'ip'):
        raise ValueError(
            "The 'tofu.inventory.ansible_host_format' option is "
            "'{}': the bridge composes the connection target as an "
            "'fqdn' or an 'ip'.".format(config['ansible_host_format']))
    seed = _filter_hosts(seed, config['host_status'])
    hosts = _host_records(seed, config['ansible_host_format'])
    records = _group_records(groups, hosts)
    _check_hierarchy(records)
    all_record = records.pop('all', None)

    inventory = AnsibleInventory(project, target_view)
    view_root = inventory.root_path
    inventory_dir = inventory.path
    if not os.path.isdir(inventory_dir):
        raise FileNotFoundError(
            "The inventory directory of the Ansible view '{}' does "
            'not exist: {}. Create the view first, then run the '
            'render again.'.format(target_view, inventory_dir))
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
        'hosts_filename={}, ansible_host_format={}, '
        'vars_filename={}'.format(
            view, fmt, config['hosts_filename'],
            config['ansible_host_format'], config['vars_filename']))

    desired = set()
    sensitive = set()

    # The sensitive values into the store, before the files which
    # reference them
    if all_record:
        _reconcile_sensitive(desired, sensitive, changes, config,
                             view_root, project_root, 'group', 'all',
                             all_record['sensitive_vars'], dry_run)
    for host in hosts:
        _reconcile_sensitive(desired, sensitive, changes, config,
                             view_root, project_root, 'host',
                             host['key'], host['sensitive_vars'],
                             dry_run)
    for name in sorted(records):
        _reconcile_sensitive(desired, sensitive, changes, config,
                             view_root, project_root, 'group', name,
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
    hosts_name = _hosts_filename(config['hosts_filename'], fmt)
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
        path = os.path.join(inventory_dir,
                            _hosts_filename(config['hosts_filename'],
                                            other))
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

    owned, manifest_sensitive = _read_manifest(inventory_dir)
    _prune_stale(view_root, project_root, owned, desired, changes,
                 dry_run, manifest_sensitive)
    if not dry_run:
        _write_manifest(inventory_dir, desired, sensitive, view_root)
    return changes
