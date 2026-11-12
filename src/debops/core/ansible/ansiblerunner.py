# Copyright (C) 2023-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .projectrunner import AnsibleProjectRunner
from ..hooks import run_hooks
import logging
import subprocess

logger = logging.getLogger(__name__)


class AnsibleRunner(AnsibleProjectRunner):
    """Run the :command:`ansible` command in the project environment."""

    def __init__(self, project, ansible_args, bell=False):
        super().__init__(project, bell=bell)

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

        self._parse_ansible_args(ansible_args, project, ansible_flags)

    def execute(self):
        unlocked = False

        if not run_hooks(self.project.path, 'pre-exec',
                         env=self._subprocess_env(self._ansible_env)):
            raise ChildProcessError('Hook pre-exec aborted, '
                                    'not executing Ansible command')

        rc = 0
        try:
            unlocked = self.secrets.unlock()

            executor = subprocess.Popen(' '.join(self._ansible_command),
                                        shell=True, cwd=self.project.path,
                                        env=self._subprocess_env(
                                            self._ansible_env))
            std_out, std_err = executor.communicate()
            rc = executor.returncode

        except KeyboardInterrupt:
            logger.notice('Ansible execution interrupted by user',
                          extra={'allow': 'syslog'})
            raise SystemExit('... aborted by user')

        else:
            self._ring_bell()

        finally:
            if unlocked:
                self.secrets.lock()

        run_hooks(self.project.path, 'post-exec',
                  extra_env={'DEBOPS_RETURN_CODE': rc},
                  env=self._subprocess_env())

        return rc
