# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.runner``, the tool-agnostic runner base.

The base owns the secret-store cycling: the subclass declares which
stores it unlocks and locks through the 'secrets_name' parameter, and
'_unlock_secrets()' reduces the store results to the single flag the
'execute()' implementations gate their re-lock on.
"""

from unittest import mock

from debops.core.runner import Runner
from debops.core.secrets import SecretManager


def make_runner(project, stores, secrets_name=None):
    """A ``Runner`` whose secret manager resolves the given store
    mocks, keyed by store name."""
    runner = Runner(project, secrets_name=secrets_name)
    manager = SecretManager(project, project.view)
    manager._factories = lambda: {
        name: (lambda project, view, store=store: store)
        for name, store in stores.items()}
    runner.secrets = manager
    return runner


def test_unlock_secrets_cycles_the_declared_store(stub_project):
    """A runner which declares a store name unlocks exactly that
    store, and its flag is that store's own result."""
    ansible = mock.Mock()
    ansible.unlock.return_value = True
    other = mock.Mock()
    runner = make_runner(stub_project(), {"ansible": ansible,
                                          "other": other},
                         secrets_name="ansible")

    assert runner._unlock_secrets() is True
    ansible.unlock.assert_called_once_with()
    other.unlock.assert_not_called()


def test_unlock_secrets_reduces_all_stores_with_any(stub_project):
    """A runner which declares no store name unlocks every registered
    store; the flag is True when any of them changed state."""
    ansible = mock.Mock()
    ansible.unlock.return_value = False
    other = mock.Mock()
    other.unlock.return_value = True
    runner = make_runner(stub_project(), {"ansible": ansible,
                                          "other": other})

    assert runner._unlock_secrets() is True
    ansible.unlock.assert_called_once_with()
    other.unlock.assert_called_once_with()


def test_unlock_secrets_reports_no_change_when_stores_stay_unlocked(
        stub_project):
    ansible = mock.Mock()
    ansible.unlock.return_value = False
    other = mock.Mock()
    other.unlock.return_value = False
    runner = make_runner(stub_project(), {"ansible": ansible,
                                          "other": other})

    assert runner._unlock_secrets() is False


def test_lock_secrets_cycles_the_declared_store(stub_project):
    ansible = mock.Mock()
    other = mock.Mock()
    runner = make_runner(stub_project(), {"ansible": ansible,
                                          "other": other},
                         secrets_name="ansible")

    runner._lock_secrets()

    ansible.lock.assert_called_once_with()
    other.lock.assert_not_called()


def test_lock_secrets_cycles_all_stores_when_no_name_is_declared(
        stub_project):
    ansible = mock.Mock()
    other = mock.Mock()
    runner = make_runner(stub_project(), {"ansible": ansible,
                                          "other": other})

    runner._lock_secrets()

    ansible.lock.assert_called_once_with()
    other.lock.assert_called_once_with()


def test_lock_secrets_locks_every_cycled_store_when_any_changed(
        stub_project):
    """The re-lock covers the whole set the runner cycles when at
    least one of its stores changed state.

    With one registered store this is exact: the store the run
    unlocked is the store that gets locked. A second real store will
    need the re-lock to track which stores the run actually unlocked,
    so that stores left unlocked on purpose stay that way.
    """
    ansible = mock.Mock()
    ansible.unlock.return_value = True
    other = mock.Mock()
    other.unlock.return_value = False
    runner = make_runner(stub_project(), {"ansible": ansible,
                                          "other": other})
    assert runner._unlock_secrets() is True

    runner._lock_secrets()

    ansible.lock.assert_called_once_with()
    other.lock.assert_called_once_with()
