# Copyright (C) 2023-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .projectrunner import ProjectRunner
from .hooks import run_hooks
import subprocess
import os


class AnsibleRunner(ProjectRunner):
    """Run the :command:`ansible` command in the project environment."""

    def __init__(self, project, **kwargs):
        super().__init__(project, **kwargs)

        self._ansible_env = {'ANSIBLE_CONFIG': project.ansible_cfg.path}
        self._ansible_command = [
                project.config.raw['binaries']['ansible']
        ]

        self._add_global_vars()

        # List of ansible options which don't expect arguments
        ansible_flags = ['--ask-vault-password', '--ask-vault-pass',
                         '--list-hosts', '--syntax-check',
                         '--version', '-C', '--check',
                         '-D', '--diff', '-K', '--ask-become-pass',
                         '-h', '--help', '-k', '--ask-pass',
                         '-o', '--one-line', '-v', '-vv', '-vvv',
                         '-vvvv', '-vvvvv', '-vvvvvv', '--verbose',
                         '-b', '--become']

        self._parse_ansible_args(project, ansible_flags)

    def execute(self):
        unlocked = False

        for key, value in self._ansible_env.items():
            os.environ[key] = value

        if not run_hooks(self.project.path, 'pre-exec'):
            raise ChildProcessError('Hook pre-exec aborted, '
                                    'not executing Ansible command')

        rc = 0
        try:
            unlocked = self.inventory.unlock()

            executor = subprocess.Popen(' '.join(self._ansible_command),
                                        shell=True)
            std_out, std_err = executor.communicate()
            rc = executor.returncode

        except KeyboardInterrupt:
            raise SystemExit('... aborted by user')

        else:
            self._ring_bell()

        finally:
            if unlocked:
                self.inventory.lock()

        run_hooks(self.project.path, 'post-exec',
                  extra_env={'DEBOPS_RETURN_CODE': rc})

        return rc
