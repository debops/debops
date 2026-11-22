# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu wrapper against the real binary.

The unit suite stubs the tofu subprocess; the load-bearing premises
of the wrapper -- the '-input=false' fail-fast, the silent
re-initialization on a missing state, the workspace layout the
backend records, the plan file round-trip -- hold only against the
real tool. This module runs one view through the core flow with the
'tfcoremock' provider: no cloud, no fleet, the state and the plan
files in a temporary project.
"""

import os
import shutil
import subprocess

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def project_dir(run_debops, debops_env, tmp_path):
    """A modern project with the 'tfcoremock' view: the plain store,
    the explicit insecure decision the mkview contract requires."""
    directory = str(tmp_path / "tofu-integration")
    run_debops("project", "init", "--no-requirements", "-t", "modern",
               directory, env=debops_env, check=True)
    run_debops("tofu", "mkview", "-e", "plain", "tfcoremock",
               cwd=directory, env=debops_env, check=True)
    # The render pairs the tofu view with the Ansible view of the
    # same name; the project machinery creates the default 'system'
    # view only, the paired inventory directory is the user's
    os.makedirs(os.path.join(directory, "ansible", "views", "tfcoremock",
                             "inventory"), exist_ok=True)
    return directory


def saved_plan_file(result):
    """The plan file path from the 'Saved the plan file' notice --
    the notice routes to the terminal, which the subprocess
    captures as stderr."""
    for line in (result.stdout + result.stderr).splitlines():
        if "Saved the plan file" in line:
            return line.split("'")[1]
    raise AssertionError("no plan file was announced:\n"
                         + result.stdout + result.stderr)


@pytest.mark.skipif(shutil.which("tofu") is None,
                    reason="no 'tofu' binary on the PATH")
def test_the_core_flow_against_the_real_binary(run_debops, debops_env,
                                               project_dir):
    """The wrapper's core flow against the real OpenTofu: the init
    records the backend, the plan saves a plan file with the
    sequence id, the plans show renders it, the apply writes the
    state, and the inventory render claims the scaffold."""
    main_tf = os.path.join(project_dir, "tofu", "views", "tfcoremock",
                           "main.tf")
    with open(main_tf, "a") as handle:
        handle.write("""
resource "tfcoremock_simple_resource" "probe" {
  id = "integration-probe"
}

output "inventory_seed" {
  value = {
    probe = {
      address = "192.0.2.10"
      groups  = ["debops_all_hosts"]
    }
  }
}
""")

    run_debops("tofu", "-V", "tfcoremock", "init", cwd=project_dir, env=debops_env,
               check=True)
    plan = run_debops("tofu", "-V", "tfcoremock", "plan",
                      cwd=project_dir, env=debops_env, check=True)
    assert "Saved the plan file" in (plan.stdout + plan.stderr)

    # The plan file carries the sequence id and is addressable
    plans = run_debops("tofu", "-V", "tfcoremock", "plans", cwd=project_dir,
                       env=debops_env, check=True).stdout
    assert "  1  " in plans

    shown = run_debops("tofu", "-V", "tfcoremock", "plans", "show", "1", cwd=project_dir,
                       env=debops_env, check=True).stdout
    assert "tfcoremock_simple_resource.probe" in shown

    debops_env_apply = debops_env
    run_debops("tofu", "-V", "tfcoremock", "apply",
               saved_plan_file(plan), cwd=project_dir,
               env=debops_env_apply, check=True)

    # The state exists and holds the resource -- the file on disk is
    # the encrypted envelope, the wrapper reads it decrypted: the
    # missing-state refusal no longer applies to the next operation
    state_list = run_debops("tofu", "-V", "tfcoremock", "state", "list",
                            cwd=project_dir,
                            env=debops_env, check=True).stdout
    assert "tfcoremock_simple_resource.probe" in state_list

    # The inventory render claims the scaffold placeholder and
    # renders the seeded host
    run_debops("tofu", "-V", "tfcoremock", "inventory", cwd=project_dir, env=debops_env,
               check=True)
    hosts = os.path.join(project_dir, "ansible", "views", "tfcoremock",
                         "inventory", "hosts")
    with open(hosts) as handle:
        content = handle.read()
    assert "[debops_all_hosts]" in content
    assert "192.0.2.10" in content
    assert not os.path.exists(os.path.join(
        project_dir, "ansible", "views", "tfcoremock", "inventory",
        "hosts.yml"))


@pytest.mark.skipif(shutil.which("tofu") is None,
                    reason="no 'tofu' binary on the PATH")
def test_the_missing_state_refuses_on_an_initialized_view(
        run_debops, debops_env, project_dir):
    """The missing-state refusal holds against the real binary: the
    initialized view whose state file is removed refuses the next
    state-touching operation, naming the escape option."""
    main_tf = os.path.join(project_dir, "tofu", "views", "tfcoremock",
                           "main.tf")
    with open(main_tf, "a") as handle:
        handle.write("""
resource "tfcoremock_simple_resource" "probe" {
  id = "integration-probe"
}
""")

    run_debops("tofu", "-V", "tfcoremock", "init", cwd=project_dir, env=debops_env,
               check=True)
    plan = run_debops("tofu", "-V", "tfcoremock", "plan",
                      cwd=project_dir, env=debops_env, check=True)
    run_debops("tofu", "-V", "tfcoremock", "apply",
               saved_plan_file(plan), cwd=project_dir,
               env=debops_env, check=True)

    # The state is tracked in git: the commit is what the auto-commit
    # machinery records, and it is the witness the missing-state
    # refusal reads
    subprocess.run(["git", "add", os.path.join("tofu", "views",
                                               "tfcoremock", "state")],
                   cwd=project_dir, env=debops_env, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "Record the state"],
                   cwd=project_dir, env=debops_env, check=True)

    state_path = os.path.join(project_dir, "tofu", "views",
                              "tfcoremock", "state",
                              "terraform.tfstate")
    os.remove(state_path)

    refused = run_debops("tofu", "-V", "tfcoremock", "plan",
                         cwd=project_dir, env=debops_env)
    assert refused.returncode != 0
    assert "--allow-missing-state" in refused.stderr

    # The escape option proceeds: the deliberate wipe-and-rebuild
    allowed = run_debops("tofu", "-M", "--allow-missing-state",
                         "-V", "tfcoremock", "plan",
                         cwd=project_dir, env=debops_env,
                         check=True)
    assert "Saved the plan file" in (allowed.stdout + allowed.stderr)
