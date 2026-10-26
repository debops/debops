# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.config``."""

import os
from unittest import mock

import pytest

from debops import config as config_module


def test_expand_env_vars_expands_a_string(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VALUE", "hello")

    assert configuration._expand_env_vars("$DEBOPS_TEST_VALUE") == "hello"


def test_expand_env_vars_walks_a_dictionary(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VALUE", "hello")

    assert configuration._expand_env_vars(
        {"a": "$DEBOPS_TEST_VALUE"}) == {"a": "hello"}


def test_expand_env_vars_walks_a_list(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VALUE", "hello")

    assert configuration._expand_env_vars(
        ["$DEBOPS_TEST_VALUE"]) == ["hello"]


@pytest.mark.parametrize("value", [42, None, True])
def test_expand_env_vars_leaves_other_types_alone(configuration, value):
    assert configuration._expand_env_vars(value) == value


def test_merge_dict_overwrites_a_scalar(configuration):
    data = {"a": 1}

    configuration._merge_dict(data, {"a": 2})

    assert data == {"a": 2}


def test_merge_dict_adds_missing_keys(configuration):
    data = {"a": 1}

    configuration._merge_dict(data, {"b": 2})

    assert data == {"a": 1, "b": 2}


def test_merge_dict_merges_nested_dictionaries(configuration):
    data = {"a": {"b": 1, "c": 2}}

    configuration._merge_dict(data, {"a": {"b": 9, "d": 3}})

    assert data == {"a": {"b": 9, "c": 2, "d": 3}}


def test_merge_dict_extends_lists(configuration):
    data = {"a": [1, 2]}

    configuration._merge_dict(data, {"a": [3]})

    assert data == {"a": [1, 2, 3]}


def test_merge_dict_replaces_on_a_type_mismatch(configuration):
    data = {"a": [1]}

    configuration._merge_dict(data, {"a": {"b": 1}})

    assert data == {"a": {"b": 1}}


@pytest.mark.parametrize("source", [None, {}])
def test_merge_dict_ignores_an_empty_source(configuration, source):
    data = {"a": 1}

    configuration._merge_dict(data, source)

    assert data == {"a": 1}


def test_get_returns_the_whole_configuration_without_items(configuration):
    configuration._config = {"a": 1}

    assert configuration.get() == {"a": 1}


def test_get_accepts_a_single_key(configuration):
    configuration._config = {"a": {"b": 2}}

    assert configuration.get("a") == {"b": 2}


def test_get_walks_a_list_of_keys(configuration):
    configuration._config = {"a": {"b": {"c": 3}}}

    assert configuration.get(["a", "b", "c"]) == 3


def test_get_returns_an_empty_dict_for_a_missing_key(configuration):
    configuration._config = {"a": 1}

    assert configuration.get("nope") == {}


def test_load_returns_empty_for_a_missing_path(configuration, tmp_path):
    assert configuration.load(str(tmp_path / "nope")) == {}


@pytest.mark.parametrize("extension", ["toml", "json", "yaml"])
def test_load_reads_a_single_file(configuration, tmp_path, extension):
    content = {
        "toml": 'a = "b"\n',
        "json": '{"a": "b"}\n',
        "yaml": "a: b\n",
    }[extension]
    path = tmp_path / ("config." + extension)
    path.write_text(content)

    assert configuration.load(str(path)) == {"a": "b"}
    assert str(path) in configuration._config_files


def test_load_expands_environment_variables(configuration, tmp_path,
                                            monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VALUE", "hello")
    path = tmp_path / "config.toml"
    path.write_text('a = "$DEBOPS_TEST_VALUE"\n')

    assert configuration.load(str(path)) == {"a": "hello"}


def test_load_merges_a_directory_in_sorted_order(configuration, tmp_path):
    (tmp_path / "10-first.toml").write_text('a = 1\nb = 1\n')
    (tmp_path / "20-second.toml").write_text('b = 2\n')

    assert configuration.load(str(tmp_path)) == {"a": 1, "b": 2}


def test_load_ignores_subdirectories(configuration, tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "a.toml").write_text('a = 1\n')

    assert configuration.load(str(tmp_path)) == {"a": 1}


def test_load_returns_empty_for_a_special_file(configuration, tmp_path):
    path = tmp_path / "special"
    os.mkfifo(str(path))

    assert configuration.load(str(path)) == {}


def test_load_ignores_hidden_files(configuration, tmp_path):
    (tmp_path / ".hidden.toml").write_text('a = 1\n')
    (tmp_path / "visible.toml").write_text('b = 2\n')

    assert configuration.load(str(tmp_path)) == {"b": 2}


def test_load_reports_invalid_yaml_and_keeps_going(configuration, tmp_path,
                                                   capsys):
    (tmp_path / "broken.yaml").write_text("a: [unterminated\n")
    (tmp_path / "ok.toml").write_text('b = 2\n')

    assert configuration.load(str(tmp_path)) == {"b": 2}
    assert "broken.yaml" in capsys.readouterr().err


def test_load_converts_the_legacy_debops_cfg(configuration, tmp_path):
    path = tmp_path / ".debops.cfg"
    path.write_text("[ansible defaults]\n"
                    "become = True\n"
                    "inventory = hosts\n"
                    "\n"
                    "[general]\n"
                    "verbose = 1\n"
                    "name = debops\n")

    assert configuration.load(str(path)) == {
        "ansible": {"defaults": {"become": True, "inventory": "hosts"}},
        "general": {"verbose": True, "name": "debops"},
    }


def test_merge_env_reads_a_dotenv_directory(configuration, tmp_path,
                                            monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_FROM_ENV", "placeholder")
    env_file = tmp_path / ".env"
    env_file.write_text("DEBOPS_TEST_FROM_ENV=value\n")

    # The 'dotenv' machinery writes the process environment directly, which
    # otherwise leaks into every test which runs afterwards through the
    # shared pytest environment; the patch isolates the writes and restores
    # the original state afterwards.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(tmp_path))

        assert configuration._env_files == [str(env_file)]
        assert configuration._env_vars == {"DEBOPS_TEST_FROM_ENV": "value"}
        assert os.environ["DEBOPS_TEST_FROM_ENV"] == "value"


def test_merge_env_reads_a_direct_file(configuration, tmp_path, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_FROM_ENV", "placeholder")
    env_file = tmp_path / "environment"
    env_file.write_text("DEBOPS_TEST_FROM_ENV=value\n")

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(env_file))

        assert configuration._env_files == [str(env_file)]
        assert configuration._env_vars == {"DEBOPS_TEST_FROM_ENV": "value"}
        assert os.environ["DEBOPS_TEST_FROM_ENV"] == "value"


def test_merge_env_accepts_a_key_without_a_value(configuration, tmp_path):
    (tmp_path / ".env").write_text("BARE_KEY\n")

    with mock.patch.dict(os.environ):
        configuration.merge_env(str(tmp_path))

    assert configuration._env_vars["BARE_KEY"] is None
    assert "BARE_KEY" not in os.environ


def test_merge_env_ignores_a_directory_without_dotenv(configuration, tmp_path):
    configuration.merge_env(str(tmp_path))

    assert configuration._env_files == []
    assert configuration._env_vars == {}


def test_merge_env_applies_a_self_reference_once(configuration, tmp_path,
                                                 monkeypatch):
    """A variable which references its own previous value, for example
    'PATH=/extra/bin:${PATH}', must be applied only once. Parsing the file
    with 'dotenv.load_dotenv()' and then again with 'dotenv.dotenv_values()'
    interpolates the second parse against the results of the first, which
    doubles such references."""
    monkeypatch.setenv("PATH", "/usr/bin")
    env_file = tmp_path / "environment"
    env_file.write_text("PATH=/venv/bin:${PATH}\n")

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(env_file))

        assert os.environ["PATH"] == "/venv/bin:/usr/bin"
        assert configuration._env_vars["PATH"] == "/venv/bin:/usr/bin"


def test_merge_env_expands_a_tilde_in_path(configuration, tmp_path,
                                           monkeypatch):
    """A '~' in a PATH entry must be expanded to the home directory; the
    shell does not expand it during command lookup, so a literal tilde would
    silently never match."""
    home = os.path.expanduser("~")
    monkeypatch.setenv("PATH", "/usr/bin")
    env_file = tmp_path / "environment"
    env_file.write_text("PATH=~/venv/bin:${PATH}\n")

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(env_file))

        expected = home + "/venv/bin:/usr/bin"
        assert os.environ["PATH"] == expected
        assert configuration._env_vars["PATH"] == expected


def test_merge_env_expands_a_tilde_in_other_path_variables(configuration,
                                                           tmp_path):
    env_file = tmp_path / "environment"
    env_file.write_text("PYTHONPATH=~/lib:~root/lib\n")

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(env_file))

        expected = (os.path.expanduser("~") + "/lib:"
                    + os.path.expanduser("~root") + "/lib")
        assert configuration._env_vars["PYTHONPATH"] == expected


def test_merge_env_keeps_a_literal_tilde_in_other_variables(configuration,
                                                            tmp_path):
    env_file = tmp_path / "environment"
    env_file.write_text("DEBOPS_TEST_TILDE=~/literal\n")

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(env_file))

        assert configuration._env_vars["DEBOPS_TEST_TILDE"] == "~/literal"


def test_merge_env_ignores_a_missing_path(configuration, tmp_path):
    configuration.merge_env(str(tmp_path / "nope"))

    assert configuration._env_files == []
    assert configuration._env_vars == {}


def test_set_env_writes_the_environment(configuration, monkeypatch):
    monkeypatch.delenv("DEBOPS_TEST_ENV", raising=False)

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.set_env("DEBOPS_TEST_ENV", 1)

        assert os.environ["DEBOPS_TEST_ENV"] == "1"
        assert configuration._env_vars["DEBOPS_TEST_ENV"] == "1"


def test_get_env_returns_none_when_unset(configuration, monkeypatch):
    monkeypatch.delenv("DEBOPS_TEST_ENV", raising=False)

    assert configuration.get_env("DEBOPS_TEST_ENV") is None


def test_get_env_returns_the_value(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_ENV", "value")

    assert configuration.get_env("DEBOPS_TEST_ENV") == "value"


def test_section_returns_items_for_a_known_section(configuration):
    configuration._config = mock.Mock()
    configuration._config.has_section.return_value = True
    configuration._config.items.return_value = [("a", "b")]

    assert configuration.section("general") == [("a", "b")]


def test_section_returns_empty_for_an_unknown_section(configuration):
    configuration._config = mock.Mock()
    configuration._config.has_section.return_value = False

    assert configuration.section("general") == []


def test_config_get_prints_a_scalar(configuration, capsys):
    configuration._config = {"a": "b"}

    configuration.config_get("a")

    assert capsys.readouterr().out.strip() == "b"


def test_config_get_prints_a_nested_key(configuration, capsys):
    configuration._config = {"a": {"b": "c"}}

    configuration.config_get("a.b")

    assert capsys.readouterr().out.strip() == "c"


def test_config_get_prints_the_whole_configuration_for_dot(configuration,
                                                           capsys):
    configuration._config = {"a": "b"}

    configuration.config_get(".")

    assert capsys.readouterr().out.strip() == "a: b"


def test_config_get_formats_a_boolean_as_json(configuration, capsys):
    configuration._config = {"a": True}

    configuration.config_get("a")

    assert capsys.readouterr().out.strip() == "true"


def test_config_get_prints_list_entries(configuration, capsys):
    configuration._config = {"a": ["x", "y"]}

    configuration.config_get("a")

    assert capsys.readouterr().out.splitlines() == ["x", "y"]


def test_config_get_json_sorts_keys(configuration, capsys):
    configuration._config = {"b": 1, "a": 2}

    configuration.config_get(".", format="json")

    out = capsys.readouterr().out
    assert out.index('"a"') < out.index('"b"')


def test_config_get_exits_for_a_missing_key(configuration, capsys):
    configuration._config = {"a": "b"}

    with pytest.raises(SystemExit) as exc:
        configuration.config_get("nope", format="json")

    assert exc.value.code == 1
    assert capsys.readouterr().out.strip() == "{}"


def test_config_get_prints_nothing_for_a_missing_key(configuration, capsys):
    configuration._config = {"a": "b"}

    with pytest.raises(SystemExit):
        configuration.config_get("nope")

    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("fmt", ["json", "toml"])
def test_config_get_formats_a_boolean_in_every_style(
        configuration, fmt, capsys):
    """Boolean values print as JSON literals in the 'json' and 'toml'
    formats, keeping the output comparable across the callers.
    """
    configuration._config = {"a": True}

    configuration.config_get("a", format=fmt)

    assert capsys.readouterr().out.strip() == "true"


def test_config_get_formats_a_list_as_yaml(configuration, capsys):
    configuration._config = {"a": ["x", "y"]}

    configuration.config_get("a", format="yaml")

    assert capsys.readouterr().out.strip() == "- x\n- y"


@pytest.mark.parametrize("fmt", ["json", "toml"])
def test_config_get_formats_a_scalar_in_every_style(configuration, fmt,
                                                    capsys):
    configuration._config = {"a": "b"}

    configuration.config_get("a", format=fmt)

    assert capsys.readouterr().out.strip() == '"b"'


def test_init_loads_the_default_configuration(tmp_path, monkeypatch):
    # xdg_config_home is imported into the module at import time, so the
    # environment variable alone is not enough
    monkeypatch.setattr(config_module, "xdg_config_home", str(tmp_path))
    monkeypatch.setenv("DEBOPS_ANSIBLE_COLLECTIONS_PATH", "sentinel")

    config = config_module.Configuration()

    assert config.raw["binaries"]["ansible"] == "ansible"
    assert config.raw["git"]["init_message"] == \
        "Initialize new DebOps project directory"
    assert os.environ["DEBOPS_ANSIBLE_COLLECTIONS_PATH"] != "sentinel"


def test_merge_accepts_a_dictionary(configuration):
    configuration._config = {"a": 1}

    configuration.merge({"b": 2})

    assert configuration.raw == {"a": 1, "b": 2}


def test_merge_loads_from_a_directory(configuration, tmp_path):
    (tmp_path / "10-extra.toml").write_text('extra = "yes"\n')

    configuration.merge(str(tmp_path))

    assert configuration.raw["extra"] == "yes"


def test_config_list_prints_env_and_config_files(configuration, capsys,
                                                 tmp_path):
    env_file = tmp_path / "project" / ".env"
    config_file = tmp_path / "project" / ".debops.cfg"
    configuration._env_files = [str(env_file)]
    configuration._config_files = [str(config_file)]

    configuration.config_list()

    out = capsys.readouterr().out
    assert "# Environment files:" in out
    assert "# Configuration files:" in out
    assert ".env" in out
    assert ".debops.cfg" in out


def test_config_list_without_env_files(configuration, capsys, tmp_path):
    configuration._config_files = [str(tmp_path / "project" / ".debops.cfg")]

    configuration.config_list()

    out = capsys.readouterr().out
    assert "# Environment files:" not in out
    assert "# Configuration files:" in out


def test_config_get_formats_a_dict_as_toml(configuration, capsys):
    configuration._config = {"a": {"b": 1}}

    configuration.config_get("a", format="toml")

    assert "b = 1" in capsys.readouterr().out


def test_config_get_formats_a_list_as_json(configuration, capsys):
    configuration._config = {"a": ["x", "y"]}

    configuration.config_get("a", format="json")

    assert '["x", "y"]' in capsys.readouterr().out


def test_config_get_formats_a_scalar_as_yaml(configuration, capsys):
    configuration._config = {"a": "b"}

    configuration.config_get("a", format="yaml")

    assert "b" in capsys.readouterr().out


def test_config_get_formats_a_boolean_as_yaml(configuration, capsys):
    configuration._config = {"a": True}

    configuration.config_get("a", format="yaml")

    assert "true" in capsys.readouterr().out


def test_config_get_lists_the_keys_of_a_dict(configuration, capsys):
    configuration._config = {"a": {"b": 1, "c": 2}}

    configuration.config_get("a", keys=True)

    out = capsys.readouterr().out
    assert "b" in out
    assert "c" in out


def test_config_get_keys_on_a_scalar_returns_an_empty_list(configuration,
                                                           capsys):
    configuration._config = {"a": 1}

    configuration.config_get("a", keys=True)

    assert capsys.readouterr().out == ""
