# Copyright (C) 2023-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .projectrunner import AnsibleProjectRunner
from ..hooks import run_hooks
import logging
import re
import subprocess

logger = logging.getLogger(__name__)


def parse_list_hosts(output: str) -> list[str]:
    """The host names of 'ansible <pattern> --list-hosts' output.

    The output declares the matched count in a ``hosts (N):``
    header; a count that disagrees with the parsed names is an
    error, so a silently shrunken match cannot open a partial
    batch. An output without the header is refused: warning lines
    must not become host names.
    """
    declared = None
    hosts = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.endswith(':'):
            declared_match = re.match(r'hosts \((\d+)\):$', stripped)
            if declared_match:
                declared = int(declared_match.group(1))
            continue
        if stripped:
            hosts.append(stripped)
    if declared is None:
        raise ValueError(
            'The ansible output declares no host count; warning '
            'lines must not become host names')
    if declared != len(hosts):
        raise ValueError(
            'The pattern declared {} hosts, parsed {}'.format(
                declared, len(hosts)))
    return hosts


class AnsibleRunner(AnsibleProjectRunner):
    """Run the :command:`ansible` command in the project environment."""

    def __init__(self, project, ansible_args, bell=False, accept=False):
        super().__init__(project, bell=bell)

        self._ansible_env = {'ANSIBLE_CONFIG': project.ansible_cfg.path}
        if accept:
            self._enable_accept_new(self._ansible_env)
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
        snapshot = self._snapshot_accepted_keys()

        if not run_hooks(self.project.path, 'pre-exec',
                         env=self._subprocess_env(self._ansible_env)):
            raise ChildProcessError('Hook pre-exec aborted, '
                                    'not executing Ansible command')

        rc = 0
        try:
            unlocked = self._unlock_secrets()

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
                self._lock_secrets()
            self._report_accepted_keys(snapshot)

        run_hooks(self.project.path, 'post-exec',
                  extra_env={'DEBOPS_RETURN_CODE': rc},
                  env=self._subprocess_env())

        return rc

    def capture(self):
        """Run the composed command and capture its standard output.

        A query execution: no hooks run and the secrets stay locked.
        The command runs in the project environment and the captured
        output returns to the caller together with the exit code.
        """
        executor = subprocess.Popen(' '.join(self._ansible_command),
                                    shell=True, cwd=self.project.path,
                                    env=self._subprocess_env(
                                        self._ansible_env),
                                    stdout=subprocess.PIPE)
        out, _ = executor.communicate()
        return (executor.returncode,
                out.decode('utf-8') if out is not None else '')
