# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import pkgutil
import jinja2
import platform
import distro
import socket
import os


class AnsibleInventory(object):

    def __init__(self, project, name='system', *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

        if project.project_type == 'legacy':
            self.root_path = os.path.join(project.path, 'ansible')
        else:
            self.root_path = os.path.join(project.path,
                                          'ansible',
                                          'views',
                                          self.name)

        self.path = os.path.join(self.root_path, 'inventory')

    def create(self):

        try:
            os.makedirs(self.root_path)
        except FileExistsError:
            pass

        skel_dirs = (
            os.path.join('collections', 'ansible_collections'),
            os.path.join('inventory', 'group_vars', 'all'),
            os.path.join('inventory', 'host_vars'),
            os.path.join('keyring'),
            os.path.join('playbooks', 'roles'),
            os.path.join('resources'),
            os.path.join('secret'),
        )

        for skel_dir in skel_dirs:
            skel_dir = os.path.join(self.root_path, skel_dir)
            if not os.path.isdir(skel_dir):
                os.makedirs(skel_dir)

        default_hosts = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'legacy',
                                              'ansible',
                                              'inventory',
                                              'hosts.j2'))
                .decode('utf-8'), trim_blocks=True)

        # Create hosts file
        if (platform.system() == "Linux" and
                (distro.linux_distribution(full_distribution_name=False)[0]
                 ).lower() in ("debian", "ubuntu")):
            host_as_controller = True
        else:
            host_as_controller = False

        hosts_path = os.path.join(self.path, 'hosts')
        if not os.path.exists(hosts_path):
            with open(hosts_path, 'w') as fh:
                fh.writelines(
                    default_hosts.render(
                        host_as_controller=host_as_controller,
                        hostname=socket.gethostname(),
                        fqdn=socket.getfqdn()))
