# Copyright (C) 2023-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .projectrunner import ProjectRunner
from .hooks import run_hooks
import subprocess
import os


class EnvRunner(ProjectRunner):
    """Run a command in the DebOps project environment."""

    def __init__(self, project, **kwargs):
        super().__init__(project, **kwargs)

        self._command = self.kwargs['command_args']

    def show_env(self, scope='local'):
        if scope == 'local':
            for key, value in self.project.config._env_vars.items():
                print('{}={}'.format(key, value))
        elif scope == 'full':
            for key, value in os.environ.items():
                print('{}={}'.format(key, value))

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
                                        shell=True)
            std_out, std_err = executor.communicate()
            rc = executor.returncode

        except KeyboardInterrupt:
            if unlocked:
                self.inventory.lock()
            raise SystemExit('... aborted by user')

        finally:
            if unlocked:
                self.inventory.lock()

        run_hooks(self.project.path, 'post-env',
                  extra_env={'DEBOPS_RETURN_CODE': rc})

        return rc
