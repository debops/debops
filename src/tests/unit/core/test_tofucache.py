# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import pytest

import debops.core.tofu.cache as cache_module
from debops.core.tofu.cache import (
    cache_root,
    clean_data_dir,
    clean_plugins,
    clean_project,
    data_dir,
    human_size,
    in_tree_dirs,
    plugin_cache,
    project_data_dirs,
    reset_cache,
)


@pytest.fixture
def tofu_cache(tmp_path, monkeypatch):
    """Relocate the cache root into the test tree: the module reads the
    XDG cache home through its own import, so the patch redirects it."""
    monkeypatch.setattr(cache_module, "xdg_cache_home", str(tmp_path))
    return tmp_path


@pytest.fixture
def cache_project(stub_project):
    """A stub project whose data dir entry the tests can build."""
    def _make(view="system"):
        return stub_project(view=view)
    return _make


def _state_entry(root, project, size=128):
    """Create the cache entry of the project's resolved view with a
    state pointer inside."""
    entry = data_dir(project)
    os.makedirs(entry)
    with open(os.path.join(entry, 'terraform.tfstate'), 'w') as _file:
        _file.write('x' * size)
    return entry


def test_cache_root_and_plugin_cache_follow_the_xdg_cache_home(tofu_cache):
    assert cache_root() == os.path.join(str(tofu_cache), 'debops', 'tofu')
    assert plugin_cache() == os.path.join(cache_root(), 'plugins')


def test_data_dir_keys_by_the_project_path_and_view(tofu_cache,
                                                    cache_project):
    project = cache_project()

    assert data_dir(project) == os.path.join(
        cache_root(), cache_module.path_key(project.path, project.name,
                                            project.view))


def test_human_size_renders_du_style():
    assert human_size(972) == '972B'
    assert human_size(4096) == '4.0K'
    assert human_size(12 * 1024 * 1024) == '12.0M'
    assert human_size(1024 * 1024 * 1024) == '1.0G'


def test_dir_size_skips_the_symlinked_directories(tofu_cache):
    os.makedirs(os.path.join(str(tofu_cache), 'entry', 'real'))
    os.makedirs(os.path.join(str(tofu_cache), 'shared', 'binary'))
    with open(os.path.join(str(tofu_cache), 'entry', 'real', 'file'),
              'w') as _file:
        _file.write('x' * 100)
    with open(os.path.join(str(tofu_cache), 'shared', 'binary', 'big'),
              'w') as _file:
        _file.write('x' * 10000)
    os.symlink(os.path.join(str(tofu_cache), 'shared'),
               os.path.join(str(tofu_cache), 'entry', 'real', 'link'))

    assert cache_module._dir_size(os.path.join(str(tofu_cache),
                                               'entry')) == 100


def test_project_data_dirs_enumerate_the_project_views(tofu_cache,
                                                       cache_project):
    project = cache_project()
    dev_project = cache_project('dev')
    _state_entry(tofu_cache, dev_project)
    _state_entry(tofu_cache, project)
    # The view-less entry of the project as a whole
    whole = os.path.join(cache_root(),
                         cache_module.path_key(project.path, project.name,
                                               ''))
    os.makedirs(whole)

    keys = sorted([cache_module.path_key(project.path, project.name, ''),
                   cache_module.path_key(project.path, project.name,
                                         'system'),
                   cache_module.path_key(project.path, project.name,
                                         'dev')])
    assert project_data_dirs(project) == keys


def test_project_data_dirs_skip_the_plugins_and_the_foreign_entries(
        tofu_cache, cache_project):
    project = cache_project()
    _state_entry(tofu_cache, project)
    os.makedirs(plugin_cache())
    foreign = os.path.join(cache_root(), 'aa11bb22-elsewhere')
    os.makedirs(foreign)

    assert project_data_dirs(project) == [
        cache_module.path_key(project.path, project.name, 'system')]


def test_project_data_dirs_filter_the_relocated_project(tofu_cache):
    """A project which moved away leaves its cache entries behind: the
    enumeration recomputes the keys against the current path and
    filters the stale ones -- only '--reset' reaches them."""
    stale = os.path.join(cache_root(), 'aa11bb22-tofu-live')
    os.makedirs(stale)

    class RemoteProject:
        path = '/tmp/opencode/tofu-live'
        name = 'tofu-live'
        view = ''

    assert project_data_dirs(RemoteProject) == []


def test_in_tree_dirs_find_the_terraform_leftovers(tofu_cache,
                                                   cache_project):
    project = cache_project()
    leftover = os.path.join(project.path, 'tofu', 'views', 'system',
                            '.terraform')
    os.makedirs(leftover)

    assert in_tree_dirs(project) == [leftover]


def test_in_tree_dirs_walk_the_whole_view_tree(tofu_cache, cache_project):
    project = cache_project()
    first = os.path.join(project.path, 'tofu', 'views', 'system',
                         '.terraform')
    second = os.path.join(project.path, 'tofu', 'views', 'dev',
                          '.terraform')
    os.makedirs(first)
    os.makedirs(second)

    assert sorted(in_tree_dirs(project)) == sorted([first, second])


def test_cache_rows_compose_the_entries(tofu_cache, cache_project):
    project = cache_project()
    _state_entry(tofu_cache, project)
    os.makedirs(plugin_cache())
    with open(os.path.join(plugin_cache(), 'blob'), 'w') as _file:
        _file.write('x' * 512)

    rows = cache_module.cache_rows(project)
    assert len(rows) == 2
    entry = [row for row in rows
             if row[0] == os.path.join(
                 cache_root(),
                 cache_module.path_key(project.path, project.name,
                                       project.view))][0]
    assert entry[1] == 128
    assert entry[2] == '-'
    plugins = [row for row in rows if row[0] == plugin_cache()][0]
    assert plugins[1] == 512
    assert plugins[2] == 'shared'


def test_clean_data_dir_removes_the_resolved_view_entry(tofu_cache,
                                                        cache_project):
    project = cache_project()
    entry = _state_entry(tofu_cache, project)

    assert clean_data_dir(project) == entry
    assert not os.path.exists(entry)


def test_clean_data_dir_with_no_cache_returns_none(tofu_cache,
                                                   cache_project):
    project = cache_project()

    assert clean_data_dir(project) is None


def test_clean_project_removes_the_project_views_only(tofu_cache,
                                                      cache_project):
    project = cache_project()
    own = _state_entry(tofu_cache, project)
    other_view = _state_entry(tofu_cache, cache_project('dev'))
    foreign = os.path.join(cache_root(), 'aa11bb22-elsewhere')
    os.makedirs(foreign)

    assert sorted(clean_project(project)) == sorted([own, other_view])
    assert os.path.exists(foreign)


def test_clean_plugins_removes_the_shared_cache(tofu_cache):
    os.makedirs(plugin_cache())

    assert clean_plugins() == plugin_cache()
    assert not os.path.exists(plugin_cache())


def test_clean_plugins_with_no_cache_returns_none(tofu_cache):
    assert clean_plugins() is None


def test_reset_cache_removes_the_whole_root(tofu_cache, cache_project):
    project = cache_project()
    _state_entry(tofu_cache, project)
    os.makedirs(plugin_cache())
    foreign = os.path.join(cache_root(), 'aa11bb22-elsewhere')
    os.makedirs(foreign)

    assert reset_cache() == cache_root()
    assert not os.path.exists(cache_root())


def test_reset_cache_with_no_cache_returns_none(tofu_cache):
    assert reset_cache() is None
