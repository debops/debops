# Copyright (C) 2026 Maciej Delmanowski <admin@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import ast
import json
import logging
import os
import shlex
from unittest import mock

import pytest
import yaml

import debops.core.tofu.inventory as inventory_module
from debops.core.tofu.inventory import MANIFEST_NAME, render_inventory

# The outputs the tests render: two hosts, one of them grouped, one
# with a jump host, complex and sensitive variables.
SEED = {
    'web-1': {
        'address': '10.42.7.101', 'host': 'web.example.com',
        'groups': ['web', 'frontend'], 'jump': 'tethys.example.com',
        'vars': {'ansible_user': 'admin', 'port': 22,
                 'tags': ['a', 'b']},
        'sensitive_vars': {'host_token': 's3cr3t'}},
    'cache-1': {
        'address': '10.42.7.103', 'status': 'Running',
        'vars': {'ansible_user': 'admin'}},
}
GROUPS = {
    'all': {'vars': {'debops_legacy_vars': True}},
    'web': {'vars': {'http_port': 8080}, 'children': ['frontend']},
    'frontend': {},
}


def outputs(seed=SEED, groups=GROUPS):
    """The 'tofu output -json' document which carries the seed and
    the groups."""
    document = {'inventory_seed': {'value': seed}}
    if groups is not None:
        document['inventory_groups'] = {'value': groups}
    return json.dumps(document)


@pytest.fixture
def inventory_project(stub_project):
    """A modern stub project whose Ansible view's inventory directory
    exists, holding the scaffold hosts file the project init writes.

    Returns a factory which takes the 'tofu.inventory' section the
    project's configuration carries."""
    def _make(inventory_section=None):
        raw = {}
        if inventory_section is not None:
            raw['tofu'] = {'inventory': inventory_section}
        project = stub_project(project_type='modern', raw=raw)
        inventory_dir = os.path.join(project.path, 'ansible', 'views',
                                     'system', 'inventory')
        os.makedirs(inventory_dir)
        with open(os.path.join(inventory_dir, 'hosts'), 'w') as handle:
            handle.write('# scaffold comment\n\n[debops_all_hosts]\n')
        return project
    return _make


def view_root(project):
    return os.path.join(project.path, 'ansible', 'views', 'system')


def inventory_dir(project):
    return os.path.join(view_root(project), 'inventory')


def read(project, relative):
    with open(os.path.join(view_root(project), relative)) as handle:
        return handle.read()


def parse_host_line(line):
    """The ini plugin's host-line parse, replicated hermetically:
    posix shlex strips one quote level, then the values go through
    ast.literal_eval with a string fallback (ansible-core 2.18,
    'ini.py' _parse_host_definition)."""
    tokens = shlex.split(line, comments=True)
    values = {}
    for token in tokens[1:]:
        key, value = token.split('=', 1)
        try:
            values[key] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            values[key] = value
    return values


def parse_vars_line(line):
    """The ini plugin's ':vars' parse: the raw value goes through
    ast.literal_eval with a string fallback, no shlex ('ini.py'
    _parse_variable_definition)."""
    key, value = [element.strip() for element in line.split('=', 1)]
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def test_the_ini_hosts_file_carries_the_contract(inventory_project):
    """The hosts file in the 'ini' format: the full host line in the
    first group section of the host, the bare membership lines in
    the others, the ungrouped hosts, the 'all' variables and the
    group hierarchy."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    content = read(project, 'inventory/hosts')
    assert "view 'system'" in content
    assert "[all:vars]\ndebops_legacy_vars=True\n" in content
    assert "[ungrouped]\ncache-1 ansible_host='10.42.7.103' " \
        "ansible_user='admin'\n" in content
    # the full line in the alphabetically first group of the host,
    # the bare line in the other one
    assert "web.example.com ansible_host='10.42.7.101' " \
        "ansible_ssh_common_args='-o ProxyJump=tethys.example.com' " \
        "ansible_user='admin'" in content
    assert "[frontend]\nweb.example.com ansible_host=" in content
    assert "[web]\nweb.example.com\n" in content
    assert "[web:children]\nfrontend\n" in content
    assert "[web:vars]\nhttp_port=8080\n" in content


def test_the_ini_scalars_round_trip_their_types(inventory_project):
    """The ini parser reads the inline values back through
    ast.literal_eval with a string fallback: strings are quoted, the
    other scalars are written as Python literals."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    content = read(project, 'inventory/hosts')
    assert 'port=22' in content
    assert 'debops_legacy_vars=True' in content
    assert 'http_port=8080' in content
    assert "ansible_user='admin'" in content


def test_the_ini_values_carry_the_bare_repr(inventory_project):
    """The values render as the bare repr. The ':vars' sections read
    the raw value through ast.literal_eval, so their strings survive;
    the host lines lose one quote level to the shlex strip -- the
    numeric-looking strings and the backslashes parse as their
    Python look-alikes there, accepted for the quoting which reads
    naturally."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'vars': {'version': '23',
                               'path': 'a\\b',
                               'quote': 'a"b'}}}
    project = inventory_project()
    render_inventory(project, 'system', outputs(seed=seed, groups=None))

    content = read(project, 'inventory/hosts')
    assert "version='23'" in content
    assert "path='a\\\\b'" in content
    assert "quote='a\"b'" in content


def test_the_rendered_ini_values_parse_back(inventory_project):
    """The rendered values parse back the way the ini plugin reads
    them: the host lines through the shlex strip, the ':vars'
    sections without it -- the strings, the ints and the booleans
    come back with the types the seed carries."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'host': 'web.example.com',
                      'jump': 'tethys.example.com',
                      'vars': {'ansible_user': 'admin',
                               'port': 22}}}
    groups = {'all': {'vars': {'debops_legacy_vars': True}},
              'web': {'vars': {'http_port': 8080,
                               'tier': 'frontend'}}}
    project = inventory_project()
    render_inventory(project, 'system', outputs(seed=seed,
                                                groups=groups))

    content = read(project, 'inventory/hosts')
    host_line = [line for line in content.splitlines()
                 if line.startswith('web.example.com ')][0]
    assert parse_host_line(host_line) == {
        'ansible_host': '10.42.7.101',
        'ansible_ssh_common_args': '-o ProxyJump=tethys.example.com',
        'ansible_user': 'admin',
        'port': 22}

    lines = content.splitlines()
    assert parse_vars_line(
        [line for line in lines if line.startswith('tier=')][0]
    ) == 'frontend'
    assert parse_vars_line(
        [line for line in lines if line.startswith('http_port=')][0]
    ) == 8080
    assert parse_vars_line(
        [line for line in lines
         if line.startswith('debops_legacy_vars=')][0]) is True


def test_the_complex_ini_variables_ride_the_vars_file(inventory_project):
    """The 'ini' hosts file cannot carry lists and maps: they ride
    the variables file, beside the sensitive lookups -- the shared
    default name merges the two file kinds into one file."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    content = read(project,
                   'inventory/host_vars/web.example.com/tofu_inventory.yml')
    data = yaml.safe_load(content)
    assert data['tags'] == ['a', 'b']
    assert data['host_token'] == (
        '{{ lookup("file", inventory_dir + '
        '"/../secret/tofu/web-1/sensitive/host_token/content") }}')


def test_the_distinct_vars_filenames_split_the_files(inventory_project):
    """When the plain and the sensitive file names differ, the two
    file kinds split: the complex plain variables in the one, the
    sensitive lookups in the other."""
    project = inventory_project({
        'vars_filename': 'plain.yml',
        'secret': {'vars_filename': 'secret.yml'}})
    render_inventory(project, 'system', outputs())

    plain = yaml.safe_load(read(
        project, 'inventory/host_vars/web.example.com/plain.yml'))
    secret = yaml.safe_load(read(
        project, 'inventory/host_vars/web.example.com/secret.yml'))
    assert plain == {'tags': ['a', 'b']}
    assert list(secret) == ['host_token']


def test_the_native_formats_carry_the_plain_vars_inline(inventory_project):
    """The 'yaml', 'json' and 'toml' hosts files carry the plain
    variables of every type natively; their variables files hold the
    sensitive lookups only."""
    project = inventory_project()
    for fmt, extension in (('yaml', 'yml'), ('json', 'json'),
                           ('toml', 'toml')):
        project.config.merge({'tofu': {'inventory': {'hosts_format':
                                                     fmt}}})
        render_inventory(project, 'system', outputs())

        content = read(project, 'inventory/hosts.' + extension)
        if fmt == 'yaml':
            data = yaml.safe_load(content)
            assert data['all']['hosts']['web.example.com']['tags'] == \
                ['a', 'b']
        if fmt != 'json':
            assert "view 'system'" in content
        vars_file = yaml.safe_load(read(
            project,
            'inventory/host_vars/web.example.com/tofu_inventory.yml'))
        assert list(vars_file) == ['host_token']


def test_the_json_hosts_file_carries_no_header(inventory_project):
    """JSON carries no comments: the do-not-edit header of the other
    formats is left out."""
    project = inventory_project({'hosts_format': 'json'})
    render_inventory(project, 'system', outputs())

    content = read(project, 'inventory/hosts.json')
    assert not content.startswith('#')
    assert json.loads(content)['all']['hosts']['web.example.com']


def test_the_toml_children_are_a_list(inventory_project):
    """The toml inventory plugin requires the children as a list,
    the opposite of the yaml plugin: the group hierarchy renders
    flat, the groups as top-level tables."""
    project = inventory_project({'hosts_format': 'toml'})
    render_inventory(project, 'system', outputs())

    content = read(project, 'inventory/hosts.toml')
    assert 'children = [ "web",]' in content
    assert '[web]' in content
    assert '[web.vars]\nhttp_port = 8080' in content
    # a hostname which carries dots is quoted by the encoder
    assert '[web.hosts."web.example.com"]' in content


def test_the_group_hierarchy_nests_in_the_yaml_format(inventory_project):
    """The yaml plugin requires the children as a mapping: the child
    group's node nests inside its parent, the parentless groups
    under 'all.children'."""
    project = inventory_project({'hosts_format': 'yaml'})
    render_inventory(project, 'system', outputs())

    data = yaml.safe_load(read(project, 'inventory/hosts.yml'))
    assert data['all']['children']['web']['children']['frontend'] == \
        {'hosts': {'web.example.com': None}}
    assert 'frontend' not in data['all']['children']


def test_the_configured_hosts_name_gets_the_extension(inventory_project):
    """A configured hosts file name which carries none of the
    extensions the inventory plugin claims gets the format's
    canonical suffix appended; the ini name is left alone."""
    project = inventory_project({
        'hosts_format': 'yaml', 'hosts_filename_yaml': 'rendered'})
    render_inventory(project, 'system', outputs())
    assert read(project, 'inventory/rendered.yml')

    project.config.merge({'tofu': {'inventory': {
        'hosts_format': 'ini',
        'hosts_filename_ini': 'rendered-hosts'}}})
    render_inventory(project, 'system', outputs())
    assert read(project, 'inventory/rendered-hosts')


def test_the_first_render_claims_the_scaffold(inventory_project):
    """The scaffold hosts file the project init writes is replaced
    by the first render; on a format switch the scaffold of another
    format is claimed and removed."""
    project = inventory_project({'hosts_format': 'yaml'})
    render_inventory(project, 'system', outputs())

    assert not os.path.exists(
        os.path.join(inventory_dir(project), 'hosts'))
    assert read(project, 'inventory/hosts.yml')


def test_a_user_hosts_file_is_not_touched(inventory_project):
    """A hosts file of another format which the user wrote is left
    alone: only the scaffold placeholder and the files the renderer
    owns are removed."""
    project = inventory_project({'hosts_format': 'yaml'})
    with open(os.path.join(inventory_dir(project), 'hosts'), 'w') as \
            handle:
        handle.write('[own]\nlocalhost ansible_host=127.0.0.1\n')
    render_inventory(project, 'system', outputs())

    assert read(project, 'inventory/hosts') == \
        '[own]\nlocalhost ansible_host=127.0.0.1\n'


def test_the_format_switch_prunes_the_old_file(inventory_project):
    """Switching the format prunes the hosts file of the previous
    render and renders the new one."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())
    render_inventory(project, 'system',
                     outputs(seed=SEED, groups=GROUPS),
                     )
    render_inventory(project, 'system', outputs())  # unchanged: no-op
    project.config.merge({'tofu': {'inventory': {'hosts_format':
                                                 'yaml'}}})
    render_inventory(project, 'system', outputs())

    assert not os.path.exists(
        os.path.join(inventory_dir(project), 'hosts'))
    assert read(project, 'inventory/hosts.yml')


def test_the_sensitive_values_land_in_the_store(inventory_project):
    """The sensitive values are written as exact bytes into the
    store -- no trailing newline, the lookup returns the value
    as-is. The paths are keyed by the seed key, the tofu-side
    identity."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    content = read(project,
                   'secret/tofu/web-1/sensitive/host_token/content')
    assert content == 's3cr3t'


def test_non_string_sensitive_values_are_serialized(inventory_project):
    """A sensitive value which is not a string is JSON-serialized:
    the user parses it with the 'from_json' filter."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'sensitive_vars': {'count': 3,
                                         'tokens': ['a', 'b']}}}
    project = inventory_project()
    render_inventory(project, 'system', outputs(seed=seed, groups=None))

    assert read(project,
                'secret/tofu/web-1/sensitive/count/content') == '3'
    assert read(project,
                'secret/tofu/web-1/sensitive/tokens/content') == \
        '["a", "b"]'


def test_the_absolute_sensitive_path(inventory_project):
    """A sensitive path template which starts with '/' is absolute:
    the content file is written there and the lookup uses the path
    as-is."""
    import tempfile
    external = tempfile.mkdtemp(dir='/tmp/opencode')
    project = inventory_project({
        'secret': {'sensitive_path': external + '/tofu/%s/%s'}})
    render_inventory(project, 'system', outputs())

    with open(os.path.join(external, 'tofu', 'web-1',
                           'host_token')) as handle:
        assert handle.read() == 's3cr3t'
    vars_file = yaml.safe_load(read(
        project, 'inventory/host_vars/web.example.com/tofu_inventory.yml'))
    assert vars_file['host_token'] == (
        '{{ lookup("file", "' + external + '/tofu/web-1/host_token") }}')


def test_the_sensitive_path_template_is_validated(inventory_project):
    """A sensitive path template with a broken placeholder is
    refused with the option named."""
    project = inventory_project({
        'secret': {'sensitive_path': 'secret/tofu/%s/%s/extra/%z'}})
    with pytest.raises(ValueError, match='sensitive_path'):
        render_inventory(project, 'system', outputs())


def test_the_lookup_expression_escapes_the_path(inventory_project):
    """The lookup path expression composes through 'json.dumps': a
    quote anywhere in the composed path cannot break out of the
    Jinja string literal it rides in."""
    project = inventory_project({
        'secret': {'sensitive_path': 'secret/to"fu/%s/sensitive/%s/content'}})
    render_inventory(project, 'system', outputs())

    data = yaml.safe_load(read(
        project, 'inventory/host_vars/web.example.com/tofu_inventory.yml'))
    assert data['host_token'] == (
        '{{ lookup("file", inventory_dir + '
        '"/../secret/to\\"fu/web-1/sensitive/host_token/content") }}')


def test_the_status_filter_skips_the_unconfigured_statuses(
        inventory_project, caplog):
    """A status the 'host_status' map does not name is skipped, with
    a notice naming the host; the running status is included by
    default and hosts without a status are always rendered."""
    seed = {'running-1': {'address': '10.42.7.101',
                          'status': 'Running'},
            'stopped-1': {'address': '10.42.7.102',
                          'status': 'Stopped'},
            'quiet-1': {'address': '10.42.7.103'}}
    project = inventory_project()
    with caplog.at_level(logging.INFO):
        render_inventory(project, 'system',
                         outputs(seed=seed, groups=None))

    content = read(project, 'inventory/hosts')
    assert 'running-1' in content
    assert 'quiet-1' in content
    assert 'stopped-1' not in content
    assert "status 'Stopped'" in caplog.text
    assert 'stopped-1' in caplog.text


def test_the_status_matching_is_case_insensitive(inventory_project):
    """The status values are matched lowercased: the providers
    export them capitalized."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'status': 'RUNNING'}}
    project = inventory_project()
    render_inventory(project, 'system', outputs(seed=seed, groups=None))
    assert 'web-1' in read(project, 'inventory/hosts')


def test_the_status_map_accepts_future_statuses(inventory_project):
    """The open 'host_status' section: a status key the defaults do
    not carry is accepted when the configuration names its
    handling."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'status': 'Running'},
            'stopped-1': {'address': '10.42.7.102',
                          'status': 'Stopped'}}
    project = inventory_project({
        'output': {'host_status': {'running': 'skip',
                                   'stopped': 'include'}}})
    render_inventory(project, 'system', outputs(seed=seed, groups=None))

    content = read(project, 'inventory/hosts')
    assert 'stopped-1' in content
    assert 'web-1' not in content


def test_an_invalid_status_handling_is_refused(inventory_project):
    project = inventory_project({
        'output': {'host_status': {'running': 'bogus'}}})
    with pytest.raises(ValueError, match="'include' or 'skip'"):
        render_inventory(project, 'system', outputs())


def test_a_stopped_host_without_an_address_is_skipped(inventory_project,
                                                      caplog):
    """A stopped instance exports no address: the host is skipped by
    the status filter before the address check runs, so the seed
    carries the null address without refusing the render."""
    seed = {'running-1': {'address': '10.42.7.101',
                          'status': 'Running'},
            'stopped-1': {'address': None,
                          'status': 'Stopped'}}
    project = inventory_project()
    with caplog.at_level(logging.INFO):
        render_inventory(project, 'system',
                         outputs(seed=seed, groups=None))

    content = read(project, 'inventory/hosts')
    assert 'running-1' in content
    assert 'stopped-1' not in content


def test_an_included_host_without_an_address_skips_with_a_notice(
        inventory_project, caplog):
    """A host the status filter includes which still carries no
    address skips with the staleness notice: the observable case is
    the lease which landed late, and the way out is the '--force'
    option, which refreshes the state before the render."""
    seed = {'running-1': {'address': '10.42.7.101',
                          'status': 'Running'},
            'late-1': {'address': None,
                       'status': 'Running'}}
    project = inventory_project()
    with caplog.at_level(logging.INFO):
        render_inventory(project, 'system',
                         outputs(seed=seed, groups=None))

    content = read(project, 'inventory/hosts')
    assert 'running-1' in content
    assert 'late-1' not in content
    assert "no address" in caplog.text
    assert 'late-1' in caplog.text
    assert '--force' in caplog.text


def test_the_seed_contract_is_validated(inventory_project):
    """The seed entries are validated: unknown attributes and a
    non-map entry are refused with the entry named."""
    project = inventory_project()
    with pytest.raises(ValueError, match='unknown attributes'):
        render_inventory(project, 'system', outputs(seed={
            'web-1': {'address': '10.42.7.101',
                      'sensitve_vars': {}}}, groups=None))
    with pytest.raises(ValueError, match='not a map'):
        render_inventory(project, 'system', outputs(seed={
            'web-1': 'broken'}, groups=None))


def test_a_duplicate_inventory_hostname_is_refused(inventory_project):
    """Two seed entries which render as the same inventory hostname
    would silently overwrite each other: refused, both keys named."""
    seed = {'one': {'address': '10.42.7.101', 'host': 'same.name'},
            'two': {'address': '10.42.7.102', 'host': 'same.name'}}
    project = inventory_project()
    with pytest.raises(ValueError, match="'one' and 'two'"):
        render_inventory(project, 'system', outputs(seed=seed,
                                                    groups=None))


@pytest.mark.parametrize('name', ['../evil', 'a/b', '.', '..hidden',
                                  'with space'])
def test_unrenderable_entry_names_are_refused(inventory_project, name):
    """The seed keys cross into file paths, INI sections and lookup
    expressions: a traversal, a section break or a leading dot
    refuses the render, named."""
    project = inventory_project()
    with pytest.raises(ValueError, match='not renderable'):
        render_inventory(project, 'system', outputs(
            seed={name: {'address': '10.42.7.101'}}, groups=None))


def test_unrenderable_group_names_are_refused(inventory_project):
    """The group names and the group list entries ride the INI
    sections and the rendered hierarchy: an unsafe one refuses the
    render, named."""
    project = inventory_project()
    with pytest.raises(ValueError, match='not renderable'):
        render_inventory(project, 'system', outputs(groups={
            'bad]group': {}}))
    with pytest.raises(ValueError, match='not renderable'):
        render_inventory(project, 'system', outputs(groups={
            'web': {'children': ['a child']}}))


def test_unrenderable_variable_names_are_refused(inventory_project):
    """Variable names ride the vars files as YAML keys and the
    sensitive ones into the store paths and the lookup expressions:
    a quote or a traversal refuses the render."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'vars': {'bad"name': 'v'},
                      'sensitive_vars': {'../dot': 'v'}}}
    project = inventory_project()
    with pytest.raises(ValueError, match='not renderable'):
        render_inventory(project, 'system', outputs(seed=seed,
                                                    groups=None))


def test_the_host_attribute_is_a_validated_name(inventory_project):
    """The 'host' attribute renders as the inventory hostname: an
    unsafe one refuses the render like the seed keys do."""
    seed = {'web-1': {'address': '10.42.7.101', 'host': 'a[b]'}}
    project = inventory_project()
    with pytest.raises(ValueError, match="'host' attribute"):
        render_inventory(project, 'system', outputs(seed=seed,
                                                    groups=None))


def test_an_address_with_injected_variables_is_refused(inventory_project):
    """The address rides the INI host line as one token: whitespace
    or '=' would inject further inline variables into the
    inventory."""
    seed = {'web-1': {'address': '10.42.7.101 ansible_port=2222'}}
    project = inventory_project()
    with pytest.raises(ValueError, match='address'):
        render_inventory(project, 'system', outputs(seed=seed,
                                                    groups=None))


def test_a_jump_with_injected_options_is_refused(inventory_project):
    """The jump composes into 'ansible_ssh_common_args', which
    Ansible splits into SSH options: a whitespace would smuggle an
    option like 'ProxyCommand' into the connection."""
    seed = {'web-1': {'address': '10.42.7.101',
                      'jump': 'bastion -o ProxyCommand=evil'}}
    project = inventory_project()
    with pytest.raises(ValueError, match='jump'):
        render_inventory(project, 'system', outputs(seed=seed,
                                                    groups=None))


def test_an_empty_jump_and_host_are_the_fallbacks(inventory_project):
    """An empty 'jump' is no jump -- the host connects directly; an
    empty 'host' renders under the seed key. Both are seed
    conventions the validation accepts."""
    seed = {'web-1': {'address': '10.42.7.101', 'jump': '',
                      'host': ''}}
    project = inventory_project()
    render_inventory(project, 'system', outputs(seed=seed, groups=None))

    content = read(project, 'inventory/hosts')
    assert 'web-1 ansible_host=' in content
    assert 'ProxyJump' not in content


def test_a_broken_output_document_is_refused(inventory_project):
    """The 'tofu output -json' document is validated: a document
    which is not JSON and a missing 'inventory_seed' output are
    refused."""
    project = inventory_project()
    with pytest.raises(ValueError, match='not valid JSON'):
        render_inventory(project, 'system', 'not-json')
    with pytest.raises(ValueError, match='inventory_seed'):
        render_inventory(project, 'system', json.dumps({'other': {}}))


def test_a_group_hierarchy_cycle_is_refused(inventory_project):
    """A group hierarchy which carries a cycle would never
    terminate the render: refused, the group named."""
    groups = {'web': {'children': ['frontend']},
              'frontend': {'children': ['web']}}
    project = inventory_project()
    with pytest.raises(ValueError, match='cycle'):
        render_inventory(project, 'system', outputs(groups=groups))


def test_the_missing_inventory_directory_is_refused(stub_project):
    """The bridge renders into the Ansible view's inventory
    directory; a view without it is refused with the path named."""
    project = stub_project(project_type='modern')
    with pytest.raises(FileNotFoundError, match='inventory'):
        render_inventory(project, 'system', outputs())


def test_the_prune_removes_the_dropped_entries(inventory_project):
    """A host dropped from the seed loses its variables file and its
    secret content files, and the directories it left empty are
    pruned; the removals ride the change records."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    seed = {'cache-1': {'address': '10.42.7.103'}}
    changes = render_inventory(project, 'system',
                               outputs(seed=seed, groups=None))

    assert not os.path.exists(os.path.join(
        view_root(project), 'inventory', 'host_vars',
        'web.example.com'))
    assert not os.path.exists(os.path.join(
        view_root(project), 'secret', 'tofu', 'web-1'))
    manifest = yaml.safe_load(read(project, 'inventory/' +
                                   MANIFEST_NAME))
    assert manifest['files'] == ['inventory/hosts']

    removals = [change for change in changes
                if change['action'] == 'remove']
    assert len(removals) == 2
    vars_change = [change for change in removals
                   if 'host_vars' in change['path']][0]
    assert vars_change['secret'] is False
    assert vars_change['diff'] is not None
    secret_change = [change for change in removals
                     if 'secret' in change['path']][0]
    assert secret_change['secret'] is True
    assert secret_change['diff'] is None
    assert 's3cr3t' not in str(secret_change)


def test_a_prune_outside_the_view_root_refuses_the_render(
        inventory_project):
    """The manifest is recorded state: an entry which resolves
    outside of the view root -- a tampered one -- refuses the render
    instead of deleting files elsewhere, even when the path stays
    inside the project directory."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    outside = os.path.join(project.path, 'outside')
    os.makedirs(outside)
    target = os.path.join(outside, 'target')
    with open(target, 'w') as handle:
        handle.write('keep\n')
    with open(os.path.join(inventory_dir(project), MANIFEST_NAME),
              'w') as handle:
        yaml.safe_dump({'files': ['../../../outside/target']}, handle)

    with pytest.raises(ValueError, match='outside of the project'):
        render_inventory(project, 'system', outputs())

    assert os.path.exists(target)


def test_a_stale_absolute_sensitive_file_is_not_pruned(
        inventory_project, caplog):
    """An absolute 'sensitive_path' template writes outside of the
    view root: the render records the file but does not prune it
    when the seed drops the host -- the operator cleans it by hand,
    the render names it."""
    import tempfile
    external = tempfile.mkdtemp(dir='/tmp/opencode')
    project = inventory_project({
        'secret': {'sensitive_path': external + '/tofu/%s/%s'}})
    render_inventory(project, 'system', outputs())
    with caplog.at_level(logging.INFO):
        render_inventory(project, 'system', outputs(seed={
            'cache-1': {'address': '10.42.7.103'}}, groups=None))

    assert os.path.exists(os.path.join(
        external, 'tofu', 'web-1', 'host_token'))
    assert 'web-1' in caplog.text
    assert 'outside of the view root' in caplog.text


def test_the_render_is_idempotent(inventory_project):
    """A render which changes nothing records no changes and
    rewrites nothing: the files keep their content."""
    project = inventory_project()
    changes = render_inventory(project, 'system', outputs())
    assert changes
    before = {change['path']: open(change['path']).read()
              for change in changes}
    assert render_inventory(project, 'system', outputs()) == []
    assert {path: open(path).read()
            for path in before} == before


def test_the_dry_run_writes_nothing(inventory_project):
    """The dry run reports the changes and writes nothing: the
    scaffold hosts file stays, the store stays empty, the manifest
    is not written; a real render after it applies the changes."""
    project = inventory_project()
    changes = render_inventory(project, 'system', outputs(),
                               dry_run=True)

    assert [change['action'] for change in changes] == \
        ['create', 'update', 'create']
    assert changes[0]['secret'] is True
    assert changes[0]['diff'] is None
    assert changes[1]['diff'] is not None
    assert read(project, 'inventory/hosts') == \
        '# scaffold comment\n\n[debops_all_hosts]\n'
    assert not os.path.exists(os.path.join(
        view_root(project), 'secret', 'tofu'))
    assert not os.path.exists(os.path.join(
        inventory_dir(project), MANIFEST_NAME))

    render_inventory(project, 'system', outputs())
    assert read(project,
                'secret/tofu/web-1/sensitive/host_token/content') == \
        's3cr3t'
    assert render_inventory(project, 'system', outputs(),
                            dry_run=True) == []


def test_the_changes_carry_the_diffs(inventory_project):
    """The change records carry the unified diffs of the files: an
    update of a rendered file shows the removed and the added
    lines."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())
    seed = dict(SEED)
    seed['web-1'] = dict(SEED['web-1'])
    seed['web-1']['vars'] = dict(SEED['web-1']['vars'])
    seed['web-1']['vars']['port'] = 8022
    changes = render_inventory(project, 'system', outputs(seed=seed))

    update = [change for change in changes
              if change['action'] == 'update'][0]
    lines = update['diff'].splitlines()
    assert any(line.startswith('-') and 'port=22' in line
               for line in lines)
    assert any(line.startswith('+') and 'port=8022' in line
               for line in lines)
    assert 'a/ansible/views/system/inventory/hosts' in update['diff']


def test_the_secret_changes_carry_no_diff(inventory_project):
    """The sensitive content files record their action but no diff:
    the old and the new values must not reach the terminal."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())
    seed = {'web-1': {'address': '10.42.7.101',
                      'sensitive_vars': {'host_token': 'n3w'}}}
    changes = render_inventory(project, 'system', outputs(seed=seed,
                                                          groups=None))

    update = [change for change in changes if change['secret']][0]
    assert update['action'] == 'update'
    assert update['diff'] is None
    assert 's3cr3t' not in str(update)
    assert 'n3w' not in str(update)


def test_the_unchanged_files_report_at_info(inventory_project, caplog):
    """The unchanged files report at the INFO level: the terminal
    shows them at '-vv', the default run stays quiet about them."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())
    with caplog.at_level(logging.INFO):
        render_inventory(project, 'system', outputs())

    messages = [record.getMessage() for record in caplog.records
                if record.levelno == logging.INFO]
    assert any('inventory/hosts' in message and
               'is unchanged' in message for message in messages)


def test_the_render_internals_report_at_debug(inventory_project,
                                              caplog):
    """The render internals report at the DEBUG level: the collected
    outputs and the effective options, visible at '-vvv'."""
    project = inventory_project()
    with caplog.at_level(logging.DEBUG):
        render_inventory(project, 'system', outputs())

    messages = [record.getMessage() for record in caplog.records
                if record.levelno == logging.DEBUG]
    assert any('Rendering the inventory' in message
               for message in messages)
    assert any('sensitive_path' in message for message in messages)


def test_the_unknown_hosts_format_is_refused(inventory_project):
    """The hosts format comes from the schema enum; a hand-edited
    configuration which carries another value is refused."""
    project = inventory_project({'hosts_format': 'xml'})
    with pytest.raises(ValueError, match='hosts_format'):
        render_inventory(project, 'system', outputs())


# The 'debops tofu inventory' operation: the interpreter collects the
# outputs of the view through the runner machinery, cycles the Ansible
# secret store around the render and prints the rendered paths.

def inventory_operation(monkeypatch, rc=0, output='{}', changes=None,
                        unlock=True, render_error=None, dry_run=False,
                        diff=False, force=False, state_refresh=False,
                        refresh_rc=0):
    """Run the interpreter's inventory operation with the runner, the
    secret store and the renderer stubbed; returns the stubs."""
    from types import SimpleNamespace
    import debops.cli.interpreter as cli_module

    runner = mock.Mock()
    runner.execute.return_value = (rc, output)
    if force or state_refresh:
        runner.execute.side_effect = [refresh_rc, (rc, output)]
    runner_stub = mock.Mock(return_value=runner)
    monkeypatch.setattr(inventory_module, "TofuRunner", runner_stub)
    store = mock.Mock()
    store.unlock.return_value = unlock
    monkeypatch.setattr(inventory_module, "SecretManager",
                        mock.Mock(return_value=mock.Mock(
                            store=mock.Mock(return_value=store))))
    if render_error is not None:
        monkeypatch.setattr(inventory_module, "render_inventory",
                            mock.Mock(side_effect=render_error))
    else:
        monkeypatch.setattr(inventory_module, "render_inventory",
                            mock.Mock(return_value=changes or []))
    args = SimpleNamespace(bell=False, workspace=None, dry_run=dry_run,
                           diff=diff, force=force, no_color=False,
                           allow_missing_state=False)
    raw = {'tofu': {'inventory': {'state_refresh': state_refresh}}}
    project = SimpleNamespace(view='system', path='/tmp/opencode/x',
                              config=SimpleNamespace(raw=raw))
    # A bare interpreter instance: the operation prints through the
    # real '_render_tofu_changes', which a Mock self would swallow
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    interpreter._do_tofu_inventory(args, project)
    return runner_stub, store, inventory_module.render_inventory


def test_the_inventory_operation_collects_through_the_runner(
        monkeypatch, capsys):
    """The operation runs 'tofu output -json' with the capture mode
    and the machine-consumption color stripped, cycles the Ansible
    store around the render and prints the changes it applies."""
    runner_stub, store, render = inventory_operation(
        monkeypatch, output='{"inventory_seed": {}}',
        changes=[{'path': '/x/inventory/hosts', 'action': 'create',
                  'diff': None, 'secret': False}])

    runner_stub.assert_called_once()
    assert runner_stub.call_args.args[1] == ['output', '-json']
    assert runner_stub.call_args.kwargs['no_color'] is True
    runner = runner_stub.return_value
    runner.execute.assert_called_once_with(capture=True)
    render.assert_called_once()
    store.unlock.assert_called_once()
    store.lock.assert_called_once()
    assert capsys.readouterr().out == 'Create /x/inventory/hosts\n'


def test_the_dry_run_operation_reports_without_applying(
        monkeypatch, capsys):
    """The '--dry-run' option rides into the renderer and the
    reported actions carry the 'Would' prefix; the '--diff' option
    prints the diff of a change which carries one."""
    _, _, render = inventory_operation(
        monkeypatch, output='{"inventory_seed": {}}', dry_run=True,
        changes=[{'path': '/x/inventory/hosts', 'action': 'create',
                  'diff': None, 'secret': False},
                 {'path': '/x/secret/tofu/x/content', 'action': 'update',
                  'diff': None, 'secret': True}])

    assert render.call_args.kwargs['dry_run'] is True
    assert capsys.readouterr().out == (
        'Would create /x/inventory/hosts\n'
        'Would update /x/secret/tofu/x/content\n')


def test_the_store_cycle_reports_at_debug(monkeypatch, caplog):
    """The store cycle of the operation reports at the DEBUG level:
    the unlock and the lock back of the Ansible store."""
    with caplog.at_level(logging.DEBUG):
        inventory_operation(monkeypatch,
                            output='{"inventory_seed": {}}')

    messages = [record.getMessage() for record in caplog.records]
    assert any("'system' unlocked" in message for message in messages)
    assert any("'system' locked back" in message
               for message in messages)


def test_the_forced_inventory_refreshes_the_state_first(
        monkeypatch):
    """The '--force' option runs 'tofu refresh' before the outputs
    are collected: the in-place changes and the late leases land in
    the render. The refresh streams, the outputs capture."""
    runner_stub, _, render = inventory_operation(
        monkeypatch, output='{"inventory_seed": {}}', force=True,
        changes=[])
    assert [call.args[1][0] for call in runner_stub.call_args_list] \
        == ['refresh', 'output']
    runner = runner_stub.return_value
    assert runner.execute.call_args_list == [mock.call(),
                                             mock.call(capture=True)]
    render.assert_called_once()


def test_the_state_refresh_option_refreshes_before_the_render(
        monkeypatch):
    """The 'tofu.inventory.state_refresh' option drives the same
    refresh-then-render sequence without the '--force' flag."""
    runner_stub, _, _ = inventory_operation(
        monkeypatch, output='{"inventory_seed": {}}',
        state_refresh=True, changes=[])
    assert [call.args[1][0] for call in runner_stub.call_args_list] \
        == ['refresh', 'output']


def test_the_default_render_does_not_refresh(monkeypatch):
    """The default renders the state as of the last refresh or
    apply: the operation collects the outputs only."""
    runner_stub, _, _ = inventory_operation(
        monkeypatch, output='{"inventory_seed": {}}', changes=[])
    assert [call.args[1][0] for call in runner_stub.call_args_list] \
        == ['output']


def test_a_failed_refresh_refuses_the_render(monkeypatch, capsys):
    """A 'tofu refresh' which fails exits with its code: nothing is
    rendered and the outputs are never collected."""
    with pytest.raises(SystemExit) as exc:
        inventory_operation(monkeypatch, force=True, refresh_rc=3,
                            changes=[])

    assert exc.value.code == 3
    assert "failed with exit code 3" in capsys.readouterr().err


def test_a_failed_output_operation_exits_with_its_code(
        monkeypatch, capsys):
    """The 'tofu output' operation which fails refuses the render:
    the exit code carries, nothing is rendered and the store stays
    locked."""
    with pytest.raises(SystemExit) as exc:
        inventory_operation(monkeypatch, rc=3)

    assert exc.value.code == 3
    assert 'failed with exit code 3' in capsys.readouterr().err


def test_a_refused_render_locks_the_store_back(monkeypatch, capsys):
    """A render which refuses the outputs exits with the error named;
    the store cycles back in the meantime."""
    with pytest.raises(SystemExit) as exc:
        inventory_operation(
            monkeypatch,
            output='{"inventory_seed": {"web-1": {"address": ""}}}',
            render_error=ValueError("The seed host 'web-1' carries "
                                    "no 'address'"))

    assert exc.value.code == 1
    assert "no 'address'" in capsys.readouterr().err


def test_an_already_unlocked_store_is_not_locked(monkeypatch):
    """The interpreter does not lock what it did not unlock: a store
    which was already unlocked stays unlocked."""
    _, store, _ = inventory_operation(monkeypatch, unlock=False,
                                      changes=[{'path': 'inventory/hosts',
                                                'action': 'create',
                                                'diff': None,
                                                'secret': False}])

    store.unlock.assert_called_once()
    store.lock.assert_not_called()
