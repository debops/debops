# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import os
from unittest import mock

import pytest
import yaml

import debops.core.tofu.inventory as inventory_module
from debops.core.tofu.inventory import MANIFEST_NAME, render_inventory

# The outputs the tests render: two hosts, one of them grouped, one
# with a jump host, complex and sensitive variables.
SEED = {
    'web-1': {
        'address': '10.42.7.101', 'host': 'web.fracki.pl',
        'groups': ['web', 'frontend'], 'jump': 'tethys.fracki.pl',
        'vars': {'ansible_user': 'drybjed', 'port': 22,
                 'tags': ['a', 'b']},
        'sensitive_vars': {'host_token': 's3cr3t'}},
    'cache-1': {
        'address': '10.42.7.103', 'status': 'Running',
        'vars': {'ansible_user': 'drybjed'}},
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
        "ansible_user='drybjed'\n" in content
    # the full line in the alphabetically first group of the host,
    # the bare line in the other one
    assert "web.fracki.pl ansible_host='10.42.7.101' " \
        "ansible_ssh_common_args='-o ProxyJump=tethys.fracki.pl' " \
        "ansible_user='drybjed'" in content
    assert "[frontend]\nweb.fracki.pl ansible_host=" in content
    assert "[web]\nweb.fracki.pl\n" in content
    assert "[web:children]\nfrontend\n" in content
    assert "[web:vars]\nhttp_port=8080\n" in content


def test_the_ini_scalars_round_trip_their_types(inventory_project):
    """The ini parser reads the inline values back through
    ast.literal_eval: strings are quoted, the other scalars are
    written as Python literals."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    content = read(project, 'inventory/hosts')
    assert "port=22" in content
    assert "debops_legacy_vars=True" in content
    assert "http_port=8080" in content
    assert "ansible_user='drybjed'" in content


def test_the_complex_ini_variables_ride_the_vars_file(inventory_project):
    """The 'ini' hosts file cannot carry lists and maps: they ride
    the variables file, beside the sensitive lookups -- the shared
    default name merges the two file kinds into one file."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    content = read(project,
                   'inventory/host_vars/web.fracki.pl/tofu_inventory.yml')
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
        project, 'inventory/host_vars/web.fracki.pl/plain.yml'))
    secret = yaml.safe_load(read(
        project, 'inventory/host_vars/web.fracki.pl/secret.yml'))
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
            assert data['all']['hosts']['web.fracki.pl']['tags'] == \
                ['a', 'b']
        if fmt != 'json':
            assert "view 'system'" in content
        vars_file = yaml.safe_load(read(
            project,
            'inventory/host_vars/web.fracki.pl/tofu_inventory.yml'))
        assert list(vars_file) == ['host_token']


def test_the_json_hosts_file_carries_no_header(inventory_project):
    """JSON carries no comments: the do-not-edit header of the other
    formats is left out."""
    project = inventory_project({'hosts_format': 'json'})
    render_inventory(project, 'system', outputs())

    content = read(project, 'inventory/hosts.json')
    assert not content.startswith('#')
    assert json.loads(content)['all']['hosts']['web.fracki.pl']


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
    assert '[web.hosts."web.fracki.pl"]' in content


def test_the_group_hierarchy_nests_in_the_yaml_format(inventory_project):
    """The yaml plugin requires the children as a mapping: the child
    group's node nests inside its parent, the parentless groups
    under 'all.children'."""
    project = inventory_project({'hosts_format': 'yaml'})
    render_inventory(project, 'system', outputs())

    data = yaml.safe_load(read(project, 'inventory/hosts.yml'))
    assert data['all']['children']['web']['children']['frontend'] == \
        {'hosts': {'web.fracki.pl': None}}
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
        project, 'inventory/host_vars/web.fracki.pl/tofu_inventory.yml'))
    assert vars_file['host_token'] == (
        '{{ lookup("file", "' + external + '/tofu/web-1/host_token") }}')


def test_the_sensitive_path_template_is_validated(inventory_project):
    """A sensitive path template with a broken placeholder is
    refused with the option named."""
    project = inventory_project({
        'secret': {'sensitive_path': 'secret/tofu/%s/%s/extra/%z'}})
    with pytest.raises(ValueError, match='sensitive_path'):
        render_inventory(project, 'system', outputs())


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


def test_an_included_host_without_an_address_is_refused(inventory_project):
    """A host the status filter includes must carry an address: the
    rendered inventory cannot reach it."""
    seed = {'web-1': {'address': None, 'status': 'Running'}}
    project = inventory_project()
    with pytest.raises(ValueError, match="'address'"):
        render_inventory(project, 'system', outputs(seed=seed,
                                                    groups=None))


def test_the_seed_contract_is_validated(inventory_project):
    """The seed entries are validated: unknown attributes, a missing
    address and a non-map entry are refused with the entry named."""
    project = inventory_project()
    with pytest.raises(ValueError, match='unknown attributes'):
        render_inventory(project, 'system', outputs(seed={
            'web-1': {'address': '10.42.7.101',
                      'sensitve_vars': {}}}, groups=None))
    with pytest.raises(ValueError, match="'address'"):
        render_inventory(project, 'system', outputs(seed={
            'web-1': {'host': 'web.fracki.pl'}}, groups=None))
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
    pruned."""
    project = inventory_project()
    render_inventory(project, 'system', outputs())

    seed = {'cache-1': {'address': '10.42.7.103'}}
    render_inventory(project, 'system', outputs(seed=seed, groups=None))

    assert not os.path.exists(os.path.join(
        view_root(project), 'inventory', 'host_vars',
        'web.fracki.pl'))
    assert not os.path.exists(os.path.join(
        view_root(project), 'secret', 'tofu', 'web-1'))
    manifest = yaml.safe_load(read(project, 'inventory/' +
                                   MANIFEST_NAME))
    assert manifest['files'] == ['inventory/hosts']


def test_the_render_is_idempotent(inventory_project):
    """A render which changes nothing rewrites nothing: the files
    keep their content, the manifest keeps its entries."""
    project = inventory_project()
    paths = render_inventory(project, 'system', outputs())
    before = {path: read(project, path) for path in paths}
    render_inventory(project, 'system', outputs())
    assert {path: read(project, path) for path in paths} == before


def test_the_unknown_hosts_format_is_refused(inventory_project):
    """The hosts format comes from the schema enum; a hand-edited
    configuration which carries another value is refused."""
    project = inventory_project({'hosts_format': 'xml'})
    with pytest.raises(ValueError, match='hosts_format'):
        render_inventory(project, 'system', outputs())


# The 'debops tofu inventory' operation: the interpreter collects the
# outputs of the view through the runner machinery, cycles the Ansible
# secret store around the render and prints the rendered paths.

def inventory_operation(monkeypatch, rc=0, output='{}', paths=None,
                        unlock=True, render_error=None):
    """Run the interpreter's inventory operation with the runner, the
    secret store and the renderer stubbed; returns the stubs."""
    from types import SimpleNamespace
    import debops.cli.interpreter as cli_module

    runner = mock.Mock()
    runner.execute.return_value = (rc, output)
    monkeypatch.setattr(cli_module, "TofuRunner",
                        mock.Mock(return_value=runner))
    store = mock.Mock()
    store.unlock.return_value = unlock
    monkeypatch.setattr(cli_module, "SecretManager",
                        mock.Mock(return_value=mock.Mock(
                            store=mock.Mock(return_value=store))))
    if render_error is not None:
        monkeypatch.setattr(cli_module, "render_inventory",
                            mock.Mock(side_effect=render_error))
    else:
        monkeypatch.setattr(cli_module, "render_inventory",
                            mock.Mock(return_value=paths or []))
    args = SimpleNamespace(bell=False, workspace=None)
    project = SimpleNamespace(view='system', path='/tmp/opencode/x')
    cli_module.Interpreter._do_tofu_inventory(
        mock.Mock(), args, project)
    return runner, store, cli_module.render_inventory


def test_the_inventory_operation_collects_through_the_runner(
        monkeypatch, capsys):
    """The operation runs 'tofu output -json' with the capture mode
    and the machine-consumption color stripped, cycles the Ansible
    store around the render and prints the rendered paths."""
    runner, store, render = inventory_operation(
        monkeypatch, output='{"inventory_seed": {}}',
        paths=['inventory/hosts'])

    cli_runner = __import__('debops.cli.interpreter',
                            fromlist=['TofuRunner']).TofuRunner
    cli_runner.assert_called_once()
    assert cli_runner.call_args.args[1] == ['output', '-json']
    assert cli_runner.call_args.kwargs['no_color'] is True
    runner.execute.assert_called_once_with(capture=True)
    render.assert_called_once()
    store.unlock.assert_called_once()
    store.lock.assert_called_once()
    assert capsys.readouterr().out == 'inventory/hosts\n'


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
                                      paths=['inventory/hosts'])

    store.unlock.assert_called_once()
    store.lock.assert_not_called()
