# Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .utils import unexpanduser
from .ansibleconfig import AnsibleConfig
from .ansible.inventory import AnsibleInventory
import subprocess
import configparser
import textwrap
import os
import sys


class EnvRunner(object):

    def __init__(self, project, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.project = project
        self.inventory = AnsibleInventory(project, name=project.view)

        try:
            self._inventory_paths = (
                    project.ansible_cfg.get_option('inventory').split(','))
        except configparser.NoSectionError:
            path = project.ansible_cfg.path
            if (os.path.exists(path) and os.path.isfile(path)):
                raise ValueError("Cannot find [defaults] section in " + path)
            else:
                raise FileNotFoundError("Cannot find Ansible "
                                        "configuration file at " + path)
        except configparser.NoOptionError:
            errmsg = ('Error: No inventory specified in the "ansible.cfg" '
                      'configuration file. You might want to run '
                      '"debops project refresh" command to ensure that it\'s '
                      'included in the generated file. If this is a legacy '
                      'project, check if the "inventory" option is present '
                      'in the ".debops.cfg" file. The default is:')
            print(textwrap.fill(errmsg, 78))
            print('\n    [ansible defaults]\n    inventory = ansible/inventory')
            sys.exit(1)

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
        try:
            unlocked = self.inventory.unlock()

            executor = subprocess.Popen(' '.join(self._command),
                                        shell=True)
            std_out, std_err = executor.communicate()
            return executor.returncode

        except KeyboardInterrupt:
            if unlocked:
                self.inventory.lock()
            raise SystemExit('... aborted by user')

        finally:
            if unlocked:
                self.inventory.lock()
