# Copyright (C) 2023-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .projectrunner import ProjectRunner
from .hooks import run_hooks
import logging
import subprocess
import os

logger = logging.getLogger(__name__)


class EnvRunner(ProjectRunner):
    """Run a command in the DebOps project environment."""

    def __init__(self, project, command_args, bell=False):
        super().__init__(project, bell=bell)

        self._command = command_args

    def show_env(self, scope='local'):
        """Return the lines of the environment listing.

        The 'local' scope lists the variables the project configuration
        defines, the 'full' scope lists the whole environment a command
        would run in.
        """
        if scope == 'local':
            return ['{}={}'.format(key, value)
                    for key, value in self.project.config._env_vars.items()]
        elif scope == 'full':
            return ['{}={}'.format(key, value)
                    for key, value in os.environ.items()]
        return []

    def execute(self):
        unlocked = False

        for key, value in self.project.config._env_vars.items():
            os.environ[key] = value

        if not run_hooks(self.project.path, 'pre-env'):
            raise ChildProcessError('Hook pre-env aborted, '
                                    'not running command in environment')

        rc = 0
        try:
            unlocked = self.inventory.unlock()

            executor = subprocess.Popen(' '.join(self._command),
                                        shell=True, cwd=self.project.path)
            std_out, std_err = executor.communicate()
            rc = executor.returncode

        except KeyboardInterrupt:
            logger.notice('Command execution interrupted by user',
                          extra={'allow': 'syslog'})
            raise SystemExit('... aborted by user')

        finally:
            if unlocked:
                self.inventory.lock()

        run_hooks(self.project.path, 'post-env',
                  extra_env={'DEBOPS_RETURN_CODE': rc})

        return rc
