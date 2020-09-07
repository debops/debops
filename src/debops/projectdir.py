# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .ansibleconfig import AnsibleConfig
import os
import pkgutil
import jinja2
import socket
import distro
import platform


class ProjectDir(object):

    def __init__(self, path=os.getcwd(), project_type='legacy', create=False,
                 refresh=False, config=None):
        self.config = config
        self.path = os.path.abspath(path)
        self.name = os.path.basename(self.path)
        self.project_type = project_type

        # Make sure that we are not operating on the home directory
        if self.path == os.path.expanduser('~'):
            raise IsADirectoryError("You cannot create a project here, "
                                    "it's a home directory")

        # We can create a project if it doesn't exist
        if create:

            # First let's make sure that we are not inside another project
            self._legacy_config_path = self._find_up_dir(self.path,
                                                         ['.debops.cfg'])
            if self._legacy_config_path and not refresh:
                raise IsADirectoryError('You are inside another '
                                        'DebOps project directory')

            self.config.merge_env(self.path)
            self.config.merge(os.path.join(self.path, '.debops.cfg'))
            self.config.merge(os.path.join(self.path, '.debops', 'conf.d'))
            # Let's make a new project
            if self.project_type == 'legacy':
                self._create_legacy_project(self.path, refresh=refresh)

        # Find the project again in case that it was just created
        self._legacy_config_path = self._find_up_dir(self.path,
                                                     ['.debops.cfg'])
        if self._legacy_config_path:
            self.path = os.path.dirname(self._legacy_config_path)
            self.project_type = 'legacy'
        else:
            self.project_type = None

        # If we didn't find a proper project, report an error
        if self.project_type is None:
            raise NotADirectoryError('DebOps project directory not found '
                                     'in ' + self.path)

        project_data = {'projects': {
                self.name: {
                    'path': self.path,
                    'name': self.name,
                    'type': self.project_type,
                    'views': {
                        'system': {}
                    }
                }
            }
        }

        project_data['projects'][self.name]['views']['system'].update(
                self.config.load(os.path.join(self.path, '.debops.cfg')))

        self.config.merge_env(self.path)
        self.config.merge(project_data)

        self.config.merge(os.path.join(self.path, '.debops', 'conf.d'))
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                debops_config=self.config.raw,
                project_type=self.project_type)

    def _find_up_dir(self, path, filenames):
        path = os.path.abspath(path)
        last_path = None
        while path != last_path:
            last_path = path
            path = os.path.join(path, *filenames)
            if os.path.exists(path):
                return path
            path = os.path.dirname(last_path)
        return None

    def _write_file(self, filename, *content):
        """
        If file:`filename` does not exist, create it and write
        var:`content` into it.
        """
        if not os.path.exists(filename):
            with open(filename, "w") as fh:
                fh.writelines(content)

    def _create_legacy_project(self, path, refresh=False):
        skel_dirs = (
            os.path.join("ansible", "inventory", "group_vars", "all"),
            os.path.join("ansible", "inventory", "host_vars"),
            os.path.join("ansible", "collections", "ansible_collections"),
            os.path.join("ansible", "playbooks"),
            os.path.join("ansible", "roles"),
        )

        default_debops_cfg = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'legacy',
                                              'debops.cfg.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_gitattributes = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'legacy',
                                              'gitattributes.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_gitignore = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'legacy',
                                              'gitignore.j2'))
                .decode('utf-8'), trim_blocks=True)

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

        try:
            os.makedirs(path)
        except FileExistsError:
            pass

        for skel_dir in skel_dirs:
            skel_dir = os.path.join(path, skel_dir)
            if not os.path.isdir(skel_dir):
                os.makedirs(skel_dir)

        # Create .debops.cfg
        self._write_file(os.path.join(path, '.debops.cfg'),
                         default_debops_cfg.render(env=os.environ)
                         + '\n')
        self.config.merge(os.path.join(self.path, '.debops.cfg'))

        # Create .gitattributes
        self._write_file(os.path.join(path, '.gitattributes'),
                         default_gitattributes.render(secret_name='secret')
                         + '\n')

        # Create .gitignore
        self._write_file(os.path.join(path, '.gitignore'),
                         default_gitignore.render(secret_name='secret',
                                                  encfs_prefix='.encfs.')
                         + '\n')

        # Create hosts file
        if (platform.system() == "Linux" and
                (distro.linux_distribution(full_distribution_name=False)[0]
                 ).lower() in ("debian", "ubuntu")):
            host_as_controller = True
        else:
            host_as_controller = False

        self._write_file(os.path.join(path, 'ansible', 'inventory', 'hosts'),
                         default_hosts.render(
                             host_as_controller=host_as_controller,
                             hostname=socket.gethostname(),
                             fqdn=socket.getfqdn()))

        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                debops_config=self.config.raw,
                project_type=self.project_type,
                refresh=refresh)
        self.ansible_cfg.write_config()
        if refresh:
            print('Refreshed DebOps project in', path)
        else:
            print('Created new DebOps project in', path)

    def status(self):
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                debops_config=self.config.raw,
                project_type=self.project_type)
        collections = self.ansible_cfg.get_option(
                'collections_paths')
        print('Project type:', self.project_type)
        print('Project root:', self.path)
        print('Ansible Collection paths:')
        for path in collections.strip('"').split(':'):
            print('   ', path)
