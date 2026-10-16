# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Check that the ``service/`` and ``scope/`` playbook sets stay in sync."""

import os

# ``src/tests/unit/<test file>``, so the repository root is four directories up.
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_every_service_playbook_has_a_scoped_twin():
    """Every role shipped with a ``service/<role>.yml`` playbook needs a
    ``scope/<role>.yml`` playbook as well.

    Roles without a service playbook (dependency, infrastructure and
    ``debops-contrib-playbooks`` roles) as well as the service variant
    playbooks (``*-plain``, ``*-nginx``, ...) are not candidates and are
    skipped by construction.
    """
    roles_dir = os.path.join(REPO_ROOT, "ansible", "roles")
    service_dir = os.path.join(REPO_ROOT, "ansible", "playbooks", "service")
    scope_dir = os.path.join(REPO_ROOT, "ansible", "playbooks", "scope")

    missing = [
        role
        for role in sorted(os.listdir(roles_dir))
        if os.path.isdir(os.path.join(roles_dir, role))
        and os.path.exists(os.path.join(service_dir, role + ".yml"))
        and not os.path.exists(os.path.join(scope_dir, role + ".yml"))
    ]

    assert not missing, (
        "Roles with a service playbook but no scoped playbook: "
        + ", ".join(missing)
    )
