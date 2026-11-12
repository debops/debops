# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The tool-agnostic base of the project runners.

The runners execute commands in the context of a DebOps project
directory: with the project's environment, the project's hook scripts
around the command and the project's secret stores unlocked for the
duration. Which secret stores are cycled is decided by the subclasses
through the :var:`secrets_name` parameter; a runner which leaves it
unset cycles all registered stores.
"""

from .secrets import SecretManager
import logging
import sys

logger = logging.getLogger(__name__)


class Runner(object):

    def __init__(self, project, bell=False, secrets_name=None):
        self.bell = bell
        self.project = project
        self.secrets = SecretManager(project, project.view)
        self._secrets_name = secrets_name

    def _subprocess_env(self, extra_env=None):
        """Return the environment a project command runs in.

        The ambient environment with the project's configured variables
        on top, plus the runner's own additions last. The mapping is
        handed to the spawned command; the DebOps process environment
        itself is not modified.
        """
        env = self.project.environment()
        if extra_env:
            env.update(extra_env)
        return env

    def _unlock_secrets(self):
        """Unlock the secret stores this runner cycles.

        Returns True when at least one store changed state from locked
        to unlocked, so that the caller knows to lock them again.
        """
        if self._secrets_name:
            results = [self.secrets.store(self._secrets_name).unlock()]
        else:
            results = self.secrets.unlock()
        return any(results)

    def _lock_secrets(self):
        """Lock the secret stores this runner cycles."""
        if self._secrets_name:
            self.secrets.store(self._secrets_name).lock()
        else:
            self.secrets.lock()

    def _ring_bell(self):
        # Notify user at end of execution
        if self.bell:
            # A bare BEL, not a log record: a record's newline would
            # advance the line the bell is meant to leave alone
            sys.stderr.write('\a')
            sys.stderr.flush()
