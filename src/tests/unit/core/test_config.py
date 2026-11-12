# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.config``."""

import json
import os
from unittest import mock

import pytest

from debops.core import config as config_module
from debops.core.exceptions import OptionNotFoundError
from debops.core.utils import unexpanduser


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
        "toml": '[syslog]\naddress = "log"\n',
        "json": '{"syslog": {"address": "log"}}\n',
        "yaml": "syslog:\n  address: log\n",
    }[extension]
    path = tmp_path / ("config." + extension)
    path.write_text(content)

    assert configuration.load(str(path)) == {"syslog": {"address": "log"}}
    assert str(path) in configuration._config_files


def test_load_expands_environment_variables(configuration, tmp_path,
                                            monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VALUE", "hello")
    path = tmp_path / "config.toml"
    path.write_text('[syslog]\naddress = "$DEBOPS_TEST_VALUE"\n')

    assert configuration.load(str(path)) == {"syslog": {"address": "hello"}}


def test_load_merges_a_directory_in_sorted_order(configuration, tmp_path):
    (tmp_path / "10-first.toml").write_text('[syslog]\naddress = "one"\n')
    (tmp_path / "20-second.toml").write_text('[syslog]\naddress = "two"\n')

    assert configuration.load(str(tmp_path)) == {"syslog": {"address": "two"}}


def test_load_ignores_subdirectories(configuration, tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "options.toml").write_text('[git]\ninit_message = "msg"\n')

    assert configuration.load(str(tmp_path)) == {"git": {"init_message":
                                                         "msg"}}


def test_load_returns_empty_for_a_special_file(configuration, tmp_path):
    path = tmp_path / "special"
    os.mkfifo(str(path))

    assert configuration.load(str(path)) == {}


def test_load_ignores_hidden_files(configuration, tmp_path):
    (tmp_path / ".hidden.toml").write_text('[git]\ninit_message = "x"\n')
    (tmp_path / "visible.toml").write_text('[git]\ninit_message = "y"\n')

    assert configuration.load(str(tmp_path)) == {"git": {"init_message": "y"}}


def test_load_reports_invalid_yaml_and_keeps_going(configuration, tmp_path,
                                                   caplog):
    (tmp_path / "broken.yaml").write_text("a: [unterminated\n")
    (tmp_path / "ok.toml").write_text('[git]\ninit_message = "msg"\n')

    assert configuration.load(str(tmp_path)) == {"git": {"init_message":
                                                         "msg"}}
    assert "broken.yaml" in caplog.text


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


def test_load_warns_and_keeps_an_unknown_root_option(
        configuration, tmp_path, caplog):
    typo = tmp_path / "typo.toml"
    typo.write_text('[versionchek]\n'
                    'enabled = true\n')

    configuration.merge(str(tmp_path))

    assert configuration.raw["versionchek"] == {"enabled": True}
    assert "typo.toml" in caplog.text
    assert ("unknown option 'versionchek', custom options belong under "
            "the 'custom' section") in caplog.text


def test_load_warns_and_keeps_an_unknown_nested_option(
        configuration, tmp_path, caplog):
    typo = tmp_path / "typo.toml"
    typo.write_text('[syslog]\n'
                    'flcility = "user"\n')

    configuration.merge(str(tmp_path))

    assert configuration.raw["syslog"]["flcility"] == "user"
    assert "unknown option 'syslog.flcility'" in caplog.text
    # The migration hint is for the root level, where the custom
    # section lives
    assert "custom options belong" not in caplog.text


def test_load_merges_the_custom_section(configuration, tmp_path, caplog):
    (tmp_path / "custom.yaml").write_text('custom:\n'
                                          '  myscript:\n'
                                          '    retries: 5\n'
                                          '    hosts:\n'
                                          '      - alpha\n'
                                          '      - beta\n')

    configuration.merge(str(tmp_path))

    assert configuration.raw["custom"]["myscript"] == {
        "retries": 5,
        "hosts": ["alpha", "beta"],
    }
    assert "unknown option" not in caplog.text


def test_config_get_reads_the_custom_section(configuration):
    configuration._config = {"custom": {"myscript": {"retries": 5}}}

    assert configuration.config_get("custom.myscript.retries") == "5"


def test_apply_env_overrides_sets_custom_options(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__CUSTOM__MYSCRIPT__RETRIES", "5")
    monkeypatch.setenv("DEBOPS_CONFIG__CUSTOM__MYSCRIPT__TOKEN", "abc")

    configuration.apply_env_overrides()

    assert configuration.raw["custom"]["myscript"]["retries"] == 5
    assert configuration.raw["custom"]["myscript"]["token"] == "abc"


def test_load_drops_an_option_with_a_value_of_a_wrong_type(
        configuration, tmp_path, caplog):
    options = tmp_path / "options.toml"
    options.write_text('[syslog]\n'
                       'port = "five"\n'
                       'address = "/dev/log"\n')

    configuration.merge(str(tmp_path))

    assert "port" not in configuration.raw["syslog"]
    assert configuration.raw["syslog"]["address"] == "/dev/log"
    assert ("option 'syslog.port' must be of type integer, not str"
            in caplog.text)


def test_load_drops_an_option_outside_of_its_enum(configuration, tmp_path,
                                                  caplog):
    (tmp_path / "options.toml").write_text('[syslog]\n'
                                           'level = "notice"\n')

    configuration.merge(str(tmp_path))

    assert "level" not in configuration.raw["syslog"]
    assert "must be one of" in caplog.text


def test_load_drops_an_option_violated_inside_an_array(
        configuration, tmp_path, caplog):
    views = tmp_path / "views.yml"
    views.write_text('views:\n'
                     '  prod:\n'
                     '    playbook_collections:\n'
                     "      - 'debops.debops'\n"
                     '      - 5\n')

    configuration.merge(str(tmp_path))

    assert "playbook_collections" not in configuration.raw["views"]["prod"]
    assert "views.prod.playbook_collections" in caplog.text


def test_load_accepts_the_documented_options(configuration, tmp_path,
                                             caplog):
    (tmp_path / "options.yaml").write_text('views:\n'
                                           '  prod:\n'
                                           '    playbook_collections:\n'
                                           "      - 'debops.debops'\n"
                                           '    ansible:\n'
                                           '      defaults:\n'
                                           "        inventory: 'inventory'\n")

    configuration.merge(str(tmp_path))

    assert (configuration.raw["views"]["prod"]["ansible"]["defaults"]
            ["inventory"]) == "inventory"
    assert "unknown option" not in caplog.text


def test_load_allows_unknown_sections_inside_a_view(configuration, tmp_path,
                                                    caplog):
    """Legacy project directories merge free-form '.debops.cfg' sections
    under their view; a view is not closed to unknown sections."""
    (tmp_path / "views.yml").write_text('views:\n'
                                        '  system:\n'
                                        '    globals:\n'
                                        '      verbose: 1\n')

    configuration.merge(str(tmp_path))

    assert configuration.raw["views"]["system"]["globals"] == {"verbose": 1}
    assert "unknown option" not in caplog.text


def test_load_ignores_a_file_without_a_dictionary_of_options(configuration,
                                                             tmp_path,
                                                             caplog):
    (tmp_path / "list.yaml").write_text("- a\n"
                                        "- b\n")
    (tmp_path / "ok.toml").write_text('[git]\ninit_message = "msg"\n')

    assert configuration.load(str(tmp_path)) == {"git": {"init_message":
                                                         "msg"}}
    assert "list.yaml" in caplog.text


@pytest.mark.parametrize("name,content", [
    ("broken.json", '[syslog]\nport = 514\n'),
    ("broken.toml", '[syslog\n'),
])
def test_load_reports_broken_json_and_toml_files(configuration, tmp_path,
                                                 caplog, name, content):
    (tmp_path / name).write_text(content)
    (tmp_path / "ok.toml").write_text('[git]\ninit_message = "msg"\n')

    assert configuration.load(str(tmp_path)) == {"git": {"init_message":
                                                         "msg"}}
    assert name in caplog.text
    assert configuration._violations[0]["kind"] == "parse"
    assert configuration._violations[0]["dropped"] is True


def test_packaged_defaults_match_the_schema(caplog):
    import jinja2
    import pkgutil
    import toml

    from debops.core.config import _schema_validator

    template = jinja2.Template(
        pkgutil.get_data("debops", os.path.join("_data", "defaults.toml"))
        .decode("utf-8"), trim_blocks=True)
    defaults = toml.loads(template.render(env=os.environ))

    errors = list(_schema_validator().iter_errors(defaults))

    assert not errors
    assert not caplog.text


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


def test_merge_env_reads_a_direct_file(configuration, tmp_path, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_FROM_ENV", "placeholder")
    env_file = tmp_path / "environment"
    env_file.write_text("DEBOPS_TEST_FROM_ENV=value\n")

    # See 'test_merge_env_reads_a_dotenv_directory' for the reason.
    with mock.patch.dict(os.environ):
        configuration.merge_env(str(env_file))

        assert configuration._env_files == [str(env_file)]
        assert configuration._env_vars == {"DEBOPS_TEST_FROM_ENV": "value"}


def test_merge_env_accepts_a_key_without_a_value(configuration, tmp_path):
    (tmp_path / ".env").write_text("BARE_KEY\n")

    with mock.patch.dict(os.environ):
        configuration.merge_env(str(tmp_path))

    # A key without a value cannot be exported, so nothing is recorded
    assert "BARE_KEY" not in configuration._env_vars


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


def test_set_env_records_the_environment(configuration):
    configuration.set_env("DEBOPS_TEST_ENV", 1)

    assert configuration._env_vars["DEBOPS_TEST_ENV"] == "1"


def test_get_env_returns_none_when_unset(configuration, monkeypatch):
    monkeypatch.delenv("DEBOPS_TEST_ENV", raising=False)

    assert configuration.get_env("DEBOPS_TEST_ENV") is None


def test_get_env_returns_the_value(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_ENV", "value")

    assert configuration.get_env("DEBOPS_TEST_ENV") == "value"


def test_config_get_returns_a_scalar(configuration):
    configuration._config = {"a": "b"}

    assert configuration.config_get("a") == "b"


def test_config_get_returns_a_nested_key(configuration):
    configuration._config = {"a": {"b": "c"}}

    assert configuration.config_get("a.b") == "c"


def test_config_get_returns_the_whole_configuration_for_dot(configuration):
    configuration._config = {"a": "b"}

    assert configuration.config_get(".") == "a: b"


def test_config_get_formats_a_boolean_as_json(configuration):
    configuration._config = {"a": True}

    assert configuration.config_get("a", format="json") == "true"


def test_config_get_returns_list_entries(configuration):
    configuration._config = {"a": ["x", "y"]}

    assert configuration.config_get("a").splitlines() == ["x", "y"]


def test_config_get_json_sorts_keys(configuration):
    configuration._config = {"b": 1, "a": 2}

    out = configuration.config_get(".", format="json")
    assert out.index('"a"') < out.index('"b"')


def test_config_get_raises_for_a_missing_key(configuration):
    configuration._config = {"a": "b"}

    with pytest.raises(OptionNotFoundError):
        configuration.config_get("nope", format="json")


def test_config_get_raises_for_a_missing_key_in_every_format(configuration):
    configuration._config = {"a": "b"}

    for fmt in ("unix", "yaml", "json", "toml"):
        with pytest.raises(OptionNotFoundError):
            configuration.config_get("nope", format=fmt)


@pytest.mark.parametrize("fmt", ["json", "toml"])
def test_config_get_formats_a_boolean_in_every_style(configuration, fmt):
    """Boolean values render as JSON literals in the 'json' and 'toml'
    formats, keeping the output comparable across the callers.
    """
    configuration._config = {"a": True}

    assert configuration.config_get("a", format=fmt) == "true"


def test_config_get_formats_a_list_as_yaml(configuration):
    configuration._config = {"a": ["x", "y"]}

    assert configuration.config_get("a", format="yaml") == "- x\n- y"


@pytest.mark.parametrize("fmt", ["json", "toml"])
def test_config_get_formats_a_scalar_in_every_style(configuration, fmt):
    configuration._config = {"a": "b"}

    assert configuration.config_get("a", format=fmt) == '"b"'


def test_init_loads_the_default_configuration(tmp_path, monkeypatch):
    # xdg_config_home is imported into the module at import time, so the
    # environment variable alone is not enough
    monkeypatch.setattr(config_module, "xdg_config_home", str(tmp_path))
    monkeypatch.setenv("DEBOPS_ANSIBLE_COLLECTIONS_PATH", "sentinel")

    config = config_module.Configuration()

    assert config.raw["binaries"]["ansible"] == "ansible"
    assert config.raw["git"]["init_message"] == \
        "Initialize new DebOps project directory"
    assert (config._env_vars["DEBOPS_ANSIBLE_COLLECTIONS_PATH"]
            != "sentinel")


def test_init_reads_the_user_configuration_and_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module, "xdg_config_home", str(tmp_path))
    monkeypatch.setenv("DEBOPS_ANSIBLE_COLLECTIONS_PATH", "sentinel")
    monkeypatch.setenv("DEBOPS_TEST_MARKER", "sentinel")
    user_conf_d = tmp_path / "debops" / "conf.d"
    user_conf_d.mkdir(parents=True)
    (user_conf_d / "10-user.toml").write_text(
        'git = { init_message = "custom" }\n')
    (tmp_path / "debops" / "environment").write_text(
        "DEBOPS_TEST_MARKER=from-user-env\n")

    config = config_module.Configuration()

    # The user configuration directory and environment file are read from
    # the lowercase 'debops' directory under the XDG configuration home
    assert config.raw["git"]["init_message"] == "custom"
    assert config._env_vars["DEBOPS_TEST_MARKER"] == "from-user-env"
    # The variable is stored with the home directory collapsed to '~'
    assert config._env_vars["DEBOPS_ANSIBLE_COLLECTIONS_PATH"] == unexpanduser(
        os.path.join(config_module.DEBOPS_PACKAGE_DATA, "ansible",
                     "collections"))


def test_init_records_the_scope_of_the_configuration_layers(
        tmp_path, monkeypatch):
    monkeypatch.setattr(config_module, "xdg_config_home", str(tmp_path))
    user_conf_d = tmp_path / "debops" / "conf.d"
    user_conf_d.mkdir(parents=True)
    (user_conf_d / "10-user.toml").write_text(
        'git = { init_message = "custom" }\n')

    config = config_module.Configuration()

    origins = dict(
        (option, (scope, origin))
        for option, scope, origin, value in
        config.config_origins("git.init_message"))

    assert origins["git.init_message"] == (
        "user", str(user_conf_d / "10-user.toml"))


def test_merge_accepts_a_dictionary(configuration):
    configuration._config = {"a": 1}

    configuration.merge({"b": 2})

    assert configuration.raw == {"a": 1, "b": 2}


def test_merge_loads_from_a_directory(configuration, tmp_path):
    (tmp_path / "10-extra.toml").write_text('[git]\ninit_message = "msg"\n')

    configuration.merge(str(tmp_path))

    assert configuration.raw["git"] == {"init_message": "msg"}


def test_config_list_returns_env_and_config_files(configuration, tmp_path):
    env_file = tmp_path / "project" / ".env"
    config_file = tmp_path / "project" / ".debops.cfg"
    configuration._env_files = [str(env_file)]
    configuration._config_files = [str(config_file)]

    lines = configuration.config_list()

    assert "# Environment files:" in lines
    assert "# Configuration files:" in lines
    assert any(".env" in line for line in lines)
    assert any(".debops.cfg" in line for line in lines)


def test_config_list_without_env_files(configuration, tmp_path):
    configuration._config_files = [str(tmp_path / "project" / ".debops.cfg")]

    lines = configuration.config_list()

    assert "# Environment files:" not in lines
    assert "# Configuration files:" in lines


def test_config_get_formats_a_dict_as_toml(configuration):
    configuration._config = {"a": {"b": 1}}

    assert "b = 1" in configuration.config_get("a", format="toml")


def test_config_get_formats_a_list_as_json(configuration):
    configuration._config = {"a": ["x", "y"]}

    assert '["x", "y"]' in configuration.config_get("a", format="json")


def test_config_get_formats_a_scalar_as_yaml(configuration):
    configuration._config = {"a": "b"}

    assert "b" in configuration.config_get("a", format="yaml")


def test_config_get_formats_a_boolean_as_yaml(configuration):
    configuration._config = {"a": True}

    assert "true" in configuration.config_get("a", format="yaml")


def test_config_get_lists_the_keys_of_a_dict(configuration):
    configuration._config = {"a": {"b": 1, "c": 2}}

    out = configuration.config_get("a", keys=True)
    assert "b" in out
    assert "c" in out


def test_config_get_keys_on_a_scalar_renders_nothing(configuration):
    configuration._config = {"a": 1}

    assert configuration.config_get("a", keys=True) is None


def test_config_get_root_renders_the_full_path(configuration):
    configuration._config = {"views": {"system": {"ansible": {
        "defaults": {"inventory": "hosts"}}}}}

    out = configuration.config_get("views.system.ansible", root=True)

    assert "views:" in out
    assert "  system:" in out
    assert "    ansible:" in out
    assert "        inventory: hosts" in out


def test_config_get_root_renders_nested_json(configuration):
    import json

    configuration._config = {"syslog": {"level": "NOTICE"}}

    out = configuration.config_get("syslog.level", format="json", root=True)

    assert json.loads(out) == {"syslog": {"level": "NOTICE"}}


def test_config_get_root_wraps_a_scalar(configuration):
    configuration._config = {"syslog": {"facility": "user"}}

    out = configuration.config_get("syslog.facility", root=True)

    assert "syslog:" in out
    assert "  facility: user" in out


def test_config_get_root_leaves_the_whole_tree_unchanged(configuration):
    configuration._config = {"syslog": {"facility": "user"}}

    out = configuration.config_get(".", root=True)

    assert "syslog:" in out
    assert "  facility: user" in out
    assert out.count("syslog:") == 1


def test_config_get_root_wraps_the_key_listing(configuration):
    configuration._config = {"views": {"system": {"ansible": {}}}}

    out = configuration.config_get("views.system.ansible", keys=True,
                                   root=True)

    assert "ansible:" in out


def test_config_get_root_raises_for_a_missing_option(configuration):
    with pytest.raises(OptionNotFoundError):
        configuration.config_get("views.system.nope", root=True)


def test_apply_env_overrides_sets_a_nested_option(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__PORT", "514")

    configuration.apply_env_overrides()

    assert configuration.raw["syslog"]["port"] == 514


def test_apply_env_overrides_coerces_a_boolean(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__VERSION_CHECK__ENABLED", "true")

    configuration.apply_env_overrides()

    assert configuration.raw["version_check"]["enabled"] is True


def test_apply_env_overrides_parses_a_list(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__VIEWS__PROD__PLAYBOOK_COLLECTIONS",
                       "debops.debops, custom.collection")

    configuration.apply_env_overrides()

    assert (configuration.raw["views"]["prod"]["playbook_collections"]
            == ["debops.debops", "custom.collection"])


def test_apply_env_overrides_expands_variables(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_USER", "joe")
    monkeypatch.setenv("DEBOPS_CONFIG__GIT__INIT_MESSAGE",
                       "set by ${DEBOPS_TEST_USER}")

    configuration.apply_env_overrides()

    assert configuration.raw["git"]["init_message"] == "set by joe"


def test_apply_env_overrides_keeps_a_hyphenated_key(configuration,
                                                    monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__BINARIES__ANSIBLE-INVENTORY",
                       "/usr/bin/ansible-inventory")

    configuration.apply_env_overrides()

    assert (configuration.raw["binaries"]["ansible-inventory"]
            == "/usr/bin/ansible-inventory")


def test_apply_env_overrides_matches_segments_case_insensitively(
        configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__ADDRESS", "/dev/log")

    configuration.apply_env_overrides()

    assert configuration.raw["syslog"]["address"] == "/dev/log"


def test_apply_env_overrides_ignores_an_unknown_option(configuration,
                                                       monkeypatch,
                                                       caplog):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__FLCILITY", "user")

    configuration.apply_env_overrides()

    assert "flcility" not in configuration.raw
    assert "DEBOPS_CONFIG__SYSLOG__FLCILITY" in caplog.text
    assert "unknown option 'syslog.flcility'" in caplog.text


def test_apply_env_overrides_ignores_a_value_of_a_wrong_type(configuration,
                                                             monkeypatch,
                                                             caplog):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__PORT", "five")

    configuration.apply_env_overrides()

    assert "syslog" not in configuration.raw
    assert "DEBOPS_CONFIG__SYSLOG__PORT" in caplog.text


def test_apply_env_overrides_rank_above_the_configuration_files(
        configuration, tmp_path, monkeypatch):
    (tmp_path / "options.toml").write_text('[syslog]\nport = 999\n')

    configuration.merge(str(tmp_path))
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__PORT", "514")

    configuration.apply_env_overrides()

    assert configuration.raw["syslog"]["port"] == 514


def test_apply_env_overrides_parses_json_in_an_open_section(configuration,
                                                            monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__VIEWS__PROD__ANSIBLE",
                       '{"defaults": {"inventory": "hosts"}}')

    configuration.apply_env_overrides()

    assert (configuration.raw["views"]["prod"]["ansible"]
            == {"defaults": {"inventory": "hosts"}})


def test_apply_env_overrides_keep_a_string_in_an_open_section(configuration,
                                                              monkeypatch):
    monkeypatch.setenv(
        "DEBOPS_CONFIG__VIEWS__PROD__ANSIBLE__DEFAULTS__INVENTORY",
        "hosts")

    configuration.apply_env_overrides()

    assert (configuration.raw["views"]["prod"]["ansible"]["defaults"]
            ["inventory"]) == "hosts"


def test_config_list_lists_the_environment_overrides(configuration,
                                                     monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__LEVEL", "DEBUG")

    configuration.apply_env_overrides()

    lines = configuration.config_list()

    assert "# Environment variable overrides:" in lines
    assert "DEBOPS_CONFIG__SYSLOG__LEVEL" in lines


def test_option_file_defaults_to_99(configuration, tmp_path):
    path = configuration.option_file(str(tmp_path))

    assert path == str(tmp_path / "99_config_set.json")


def test_option_file_uses_the_existing_file(configuration, tmp_path):
    (tmp_path / "50_config_set.json").write_text("{}\n")

    path = configuration.option_file(str(tmp_path))

    assert path == str(tmp_path / "50_config_set.json")


def test_option_file_skips_hidden_and_unrelated_files(configuration,
                                                      tmp_path):
    (tmp_path / ".99_config_set.json").write_text("{}\n")
    (tmp_path / "config_set.json").write_text("{}\n")
    (tmp_path / "options.yml").write_text("a: 1\n")

    path = configuration.option_file(str(tmp_path))

    assert path == str(tmp_path / "99_config_set.json")


def test_option_file_refuses_ambiguous_files(configuration, tmp_path):
    (tmp_path / "50_config_set.json").write_text("{}\n")
    (tmp_path / "99_config_set.json").write_text("{}\n")

    with pytest.raises(ValueError):
        configuration.option_file(str(tmp_path))


def test_write_option_sets_a_typed_option(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"

    configuration.write_option(str(path), "syslog.port", "514")

    assert json.loads(path.read_text()) == {"syslog": {"port": 514}}


def test_write_option_sets_a_boolean(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"

    configuration.write_option(str(path), "version_check.enabled",
                               "true")

    assert json.loads(path.read_text()) == {"version_check":
                                            {"enabled": True}}


def test_write_option_creates_the_parent_sections(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"

    configuration.write_option(str(path), "views.system.ansible",
                               '{"defaults": {}}')

    assert json.loads(path.read_text()) == {
        "views": {"system": {"ansible": {"defaults": {}}}}}


def test_write_option_updates_the_file_in_place(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"

    configuration.write_option(str(path), "custom.myscript.retries", "5")
    configuration.write_option(str(path), "custom.myscript.token", "abc")

    assert json.loads(path.read_text()) == {
        "custom": {"myscript": {"retries": 5, "token": "abc"}}}


def test_write_option_sets_a_custom_object(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"

    configuration.write_option(str(path), "custom.myscript",
                               '{"a": 1}')

    assert json.loads(path.read_text()) == {
        "custom": {"myscript": {"a": 1}}}


def test_write_option_expands_variables(configuration, tmp_path,
                                        monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VALUE", "hello")
    path = tmp_path / "99_config_set.json"

    configuration.write_option(str(path), "custom.myscript.token",
                               "$DEBOPS_TEST_VALUE")

    assert json.loads(path.read_text()) == {
        "custom": {"myscript": {"token": "hello"}}}


def test_write_option_refuses_an_unknown_option(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"

    with pytest.raises(ValueError) as errmsg:
        configuration.write_option(str(path), "myscript.retries", "5")

    assert "custom options belong under the 'custom' section" \
        in str(errmsg.value)
    assert not path.exists()


def test_write_option_refuses_a_value_of_a_wrong_type(configuration,
                                                      tmp_path):
    path = tmp_path / "99_config_set.json"

    with pytest.raises(ValueError):
        configuration.write_option(str(path), "syslog.port", "five")

    assert not path.exists()


def test_write_option_refuses_a_missing_value(configuration, tmp_path):
    with pytest.raises(ValueError):
        configuration.write_option(str(tmp_path / "f.json"),
                                   "syslog.port")


def test_write_option_removes_an_option(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"
    path.write_text('{"syslog": {"port": 514, "address": "/dev/log"}}\n')

    configuration.write_option(str(path), "syslog.port", delete=True)

    assert json.loads(path.read_text()) == {
        "syslog": {"address": "/dev/log"}}


def test_write_option_prunes_the_empty_sections(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"
    path.write_text('{"git": {"init_message": "msg"}}\n')

    configuration.write_option(str(path), "git.init_message",
                               delete=True)

    assert json.loads(path.read_text()) == {}


def test_write_option_removes_an_unknown_option(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"
    path.write_text('{"myscript": {"retries": 5, "token": "abc"}}\n')

    configuration.write_option(str(path), "myscript.retries",
                               delete=True)

    assert json.loads(path.read_text()) == {"myscript": {"token": "abc"}}


def test_write_option_refuses_to_remove_a_missing_option(configuration,
                                                         tmp_path):
    path = tmp_path / "99_config_set.json"
    path.write_text('{"syslog": {"address": "/dev/log"}}\n')

    with pytest.raises(ValueError):
        configuration.write_option(str(path), "syslog.port",
                                   delete=True)


def test_write_option_refuses_to_remove_without_a_file(configuration,
                                                       tmp_path):
    with pytest.raises(ValueError):
        configuration.write_option(str(tmp_path / "f.json"),
                                   "syslog.port", delete=True)


def test_write_option_refuses_a_broken_file(configuration, tmp_path):
    path = tmp_path / "99_config_set.json"
    path.write_text('not json at all')

    with pytest.raises(ValueError):
        configuration.write_option(str(path), "syslog.port", "514")


def test_violations_record_a_dropped_option(configuration, tmp_path):
    (tmp_path / "options.toml").write_text('[syslog]\n'
                                           'port = "five"\n')

    configuration.merge(str(tmp_path))

    assert configuration._violations == [{
        "kind": "type",
        "file": str(tmp_path / "options.toml"),
        "option": "syslog.port",
        "dropped": True,
        "message": "option 'syslog.port' must be of type integer, "
                   "not str",
    }]


def test_violations_record_unknown_options_as_kept(configuration, tmp_path):
    (tmp_path / "typo.toml").write_text('[versionchek]\n'
                                        'enabled = true\n')

    configuration.merge(str(tmp_path))

    assert len(configuration._violations) == 1
    assert configuration._violations[0]["kind"] == "unknown"
    assert configuration._violations[0]["dropped"] is False


def test_violations_record_a_broken_file(configuration, tmp_path):
    (tmp_path / "broken.yaml").write_text("a: [unterminated\n")

    configuration.merge(str(tmp_path))

    assert configuration._violations[0]["kind"] == "parse"
    assert configuration._violations[0]["dropped"] is True


def test_violations_record_a_skipped_override(configuration, monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__PORT", "five")

    configuration.apply_env_overrides()

    assert len(configuration._violations) == 1
    violation = configuration._violations[0]
    assert violation["kind"] == "override"
    assert violation["file"] is None
    assert violation["option"] == "DEBOPS_CONFIG__SYSLOG__PORT"
    assert violation["dropped"] is True
    assert "invalid literal" in violation["message"]


def test_merge_records_the_configuration_layers(configuration):
    data = {"syslog": {"address": "/dev/log"}}

    configuration.merge(data, scope="project", origin="/project/a.yml")

    assert configuration._layers == [
        ("project", "/project/a.yml", {"syslog": {"address": "/dev/log"}}),
    ]


def test_recorded_layers_are_isolated_from_the_tree(configuration):
    data = {"syslog": {"address": "/dev/log"}}

    configuration.merge(data, scope="project", origin="/project/a.yml")
    configuration.merge({"syslog": {"port": 514}}, scope="project",
                        origin="/project/b.yml")

    assert configuration._layers[0][2] == {"syslog": {"address":
                                                      "/dev/log"}}


def test_load_records_each_file_as_a_layer(configuration, tmp_path):
    (tmp_path / "10-first.toml").write_text('[git]\ninit_message = "one"\n')
    (tmp_path / "20-second.toml").write_text('[syslog]\naddress = "log"\n')

    configuration.load(str(tmp_path), scope="project")

    assert [layer[1] for layer in configuration._layers] == [
        str(tmp_path / "10-first.toml"),
        str(tmp_path / "20-second.toml"),
    ]
    assert [layer[0] for layer in configuration._layers] == ["project",
                                                             "project"]


def test_config_origins_attributes_the_last_layer(configuration):
    configuration._config = {"syslog": {"port": 999}}
    configuration._layers = [
        ("defaults", "defaults.toml", {"syslog": {"port": 514}}),
        ("project", "/project/a.yml", {"syslog": {"port": 999}}),
    ]

    origins = configuration.config_origins("syslog.port")

    assert origins == [("syslog.port", "project", "/project/a.yml", 999)]


def test_config_origins_split_within_a_section(configuration, tmp_path):
    (tmp_path / "10-a.toml").write_text('[syslog]\nport = 514\n')
    (tmp_path / "20-b.toml").write_text('[syslog]\naddress = "log"\n')

    configuration.merge(str(tmp_path), scope="project")

    origins = dict(
        (path, (scope, origin))
        for path, scope, origin, value in
        configuration.config_origins("syslog"))

    assert origins["syslog.port"] == ("project",
                                      str(tmp_path / "10-a.toml"))
    assert origins["syslog.address"] == ("project",
                                         str(tmp_path / "20-b.toml"))


def test_config_origins_fall_back_to_the_defaults(configuration):
    configuration._config = {"syslog": {"port": 514}}
    configuration._layers = [
        ("defaults", "defaults.toml", {"syslog": {"port": 514}}),
    ]

    origins = configuration.config_origins("syslog.port")

    assert origins == [("syslog.port", "defaults", "defaults.toml", 514)]


def test_config_origins_name_the_override(configuration):
    configuration._config = {"syslog": {"level": "DEBUG"}}
    configuration._layers = [
        ("defaults", "defaults.toml", {"syslog": {"level": "NOTICE"}}),
        ("override", "DEBOPS_CONFIG__SYSLOG__LEVEL",
         {"syslog": {"level": "DEBUG"}}),
    ]

    origins = configuration.config_origins("syslog.level")

    assert origins == [("syslog.level", "override",
                        "DEBOPS_CONFIG__SYSLOG__LEVEL", "DEBUG")]


def test_config_origins_list_the_leaves_of_a_subtree(configuration):
    configuration._config = {"views": {"system": {"debops":
                                                  {"namespace": "debops"}}}}
    configuration._layers = [
        ("project", "/project/a.yml",
         {"views": {"system": {"debops": {"namespace": "debops"}}}}),
    ]

    origins = configuration.config_origins("views.system")

    assert origins == [("views.system.debops.namespace", "project",
                        "/project/a.yml", "debops")]


def test_config_origins_for_an_empty_section(configuration):
    configuration._config = {"custom": {}}
    configuration._layers = [("defaults", "defaults.toml", {"custom": {}})]

    origins = configuration.config_origins("custom")

    assert origins == [("custom", "defaults", "defaults.toml", {})]


def test_config_origins_raise_for_a_missing_option(configuration):
    with pytest.raises(OptionNotFoundError):
        configuration.config_origins("nope")


def test_config_get_show_origin_renders_the_columns(configuration):
    configuration._config = {"syslog": {"level": "DEBUG"}}
    configuration._layers = [
        ("override", "DEBOPS_CONFIG__SYSLOG__LEVEL",
         {"syslog": {"level": "DEBUG"}}),
    ]

    out = configuration.config_get("syslog.level", show_origin=True,
                                   show_scope=True)

    assert out == ("override\tDEBOPS_CONFIG__SYSLOG__LEVEL\t"
                   "syslog.level=DEBUG")


def test_config_get_show_origin_keeps_values_with_spaces(configuration):
    """The option and its value are joined as the last column, so a
    value with whitespace stays in one place when the lines are split
    on whitespace."""
    configuration._config = {"custom": {"greeting": "hello world"}}
    configuration._layers = [
        ("project", "/project/a.yml",
         {"custom": {"greeting": "hello world"}}),
    ]

    out = configuration.config_get("custom.greeting", show_origin=True)

    assert out == "/project/a.yml\tcustom.greeting=hello world"


def test_config_get_show_origin_refuses_other_formats(configuration):
    with pytest.raises(ValueError):
        configuration.config_get("syslog", format="json",
                                 show_origin=True)


def test_detached_configuration_loads_the_given_paths(tmp_path):
    (tmp_path / "system" / "conf.d").mkdir(parents=True)
    (tmp_path / "user" / "conf.d").mkdir(parents=True)
    (tmp_path / "system" / "conf.d" / "a.toml").write_text(
        '[server]\nport = 8080\nhost = "one"\n')
    (tmp_path / "user" / "conf.d" / "b.toml").write_text(
        '[server]\nhost = "two"\n')

    config = config_module.Configuration(
        paths=[str(tmp_path / "system" / "conf.d"),
               (str(tmp_path / "user" / "conf.d"), "user")])

    assert config.raw["server"] == {"port": 8080, "host": "two"}
    origins = dict(
        (option, scope) for option, scope, origin, value in
        config.config_origins("server"))

    assert origins["server.host"] == "user"
    assert origins["server.port"] == "system"


def test_detached_configuration_renders_its_defaults(tmp_path,
                                                     monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_PORT", "9090")
    defaults = tmp_path / "defaults.toml"
    defaults.write_text("[server]\n"
                        "port = {{ env['DEBOPS_TEST_PORT'] | d('8080') }}"
                        "\n")

    config = config_module.Configuration(defaults=str(defaults))

    assert config.raw["server"]["port"] == 9090


def test_detached_configuration_accepts_dictionary_defaults():
    config = config_module.Configuration(
        defaults={"server": {"port": 8080}})

    assert config.raw["server"]["port"] == 8080
    assert config.config_origins("server.port") == [
        ("server.port", "defaults", "defaults", 8080)]


def test_detached_configuration_validates_against_its_schema(tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "server": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "port": {"type": "integer"}}}}}))
    (tmp_path / "conf.d").mkdir()
    (tmp_path / "conf.d" / "options.toml").write_text(
        '[server]\nport = "five"\n')

    config = config_module.Configuration(
        paths=[str(tmp_path / "conf.d")], schema=str(schema))

    assert "port" not in config.raw["server"]
    assert config._violations[0]["kind"] == "type"


def test_detached_configuration_without_schema_validates_nothing(
        tmp_path, caplog):
    (tmp_path / "conf.d").mkdir()
    (tmp_path / "conf.d" / "options.yml").write_text("mine:\n  key: 1\n")

    config = config_module.Configuration(paths=[str(tmp_path / "conf.d")])

    assert config.raw["mine"] == {"key": 1}
    assert not caplog.text


def test_detached_unknown_options_have_no_debops_hint(tmp_path, caplog):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({
        "type": "object",
        "additionalProperties": False,
        "properties": {"server": {"type": "object"}}}))
    (tmp_path / "conf.d").mkdir()
    (tmp_path / "conf.d" / "options.yml").write_text("other: 1\n")

    config = config_module.Configuration(
        paths=[str(tmp_path / "conf.d")], schema=str(schema))

    assert "unknown option 'other'" in caplog.text
    assert "custom" not in caplog.text


def test_detached_configuration_applies_its_own_env_prefix(monkeypatch):
    monkeypatch.setenv("MYSVC_CONFIG__SERVER__PORT", "8080")

    config = config_module.Configuration(env_prefix="MYSVC_CONFIG__")

    assert config.raw["server"]["port"] == 8080


def test_detached_configuration_ignores_the_debops_overrides(monkeypatch):
    monkeypatch.setenv("DEBOPS_CONFIG__SYSLOG__LEVEL", "DEBUG")

    config = config_module.Configuration(env_prefix="MYSVC_CONFIG__")

    assert "syslog" not in config.raw


def test_detached_configuration_reads_its_env_files(tmp_path):
    env_file = tmp_path / "environment"
    env_file.write_text("MYSVC_TOKEN=secret\n")

    config = config_module.Configuration(env_files=[str(env_file)])

    assert config.get_env("MYSVC_TOKEN") == "secret"


def test_config_set_coerces_a_string_value(configuration):
    configuration.config_set("syslog.port", "514")

    assert configuration.raw["syslog"]["port"] == 514


def test_config_set_stores_python_values(configuration):
    configuration.config_set("custom.myscript", {"retries": 5})

    assert configuration.raw["custom"]["myscript"] == {"retries": 5}


def test_config_set_checks_python_values_against_the_schema(configuration):
    with pytest.raises(ValueError):
        configuration.config_set("syslog.port", ["not", "an", "integer"])


def test_config_set_refuses_an_unknown_option(configuration):
    with pytest.raises(ValueError) as errmsg:
        configuration.config_set("myscript.retries", 5)

    assert "custom options belong" in str(errmsg.value)


def test_config_set_records_its_layer(configuration):
    configuration.config_set("syslog.port", 514)

    scope, origin, data = configuration._layers[-1]

    assert (scope, origin) == ("override", "config_set")
