# -*- coding: utf-8 -*-

# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR
from .ansibleconfig import AnsibleConfig
from .ansible.inventory import AnsibleInventory
import os
import pkgutil
import jinja2
import socket
import distro
import platform


class ProjectDir(object):

    def __init__(self, path=os.getcwd(), project_type='legacy', create=False,
                 config=None, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.config = config
        self.path = os.path.abspath(path)
        self.name = os.path.basename(self.path)
        self.project_type = project_type

        # We should work in the project directory as cwd, however Ansible can
        # be executed from anywhere. If $ANSIBLE_CONFIG is defined, use it as the
        # base directory just to be safe. Otherwise, switch to the directory
        # defined at the command line.
        try:
            os.chdir(os.path.dirname(os.environ['ANSIBLE_CONFIG']))
            self.path = os.getcwd()
        except KeyError:
            try:
                os.chdir(self.path)
            except FileNotFoundError:
                # This will be a new project, so let's run with it
                pass

        # Make sure that we are not operating on the home directory
        if self.path == DEBOPS_USER_HOME_DIR:
            raise IsADirectoryError("You cannot create a project here, "
                                    "it's a home directory")

        # Find the project again in case that it was just created
        self._legacy_config_path = self._find_up_dir(self.path,
                                                     ['.debops.cfg'])
        if self._legacy_config_path:
            self.path = os.path.dirname(self._legacy_config_path)
            self.project_type = 'legacy'
        else:
            self.project_type = None

        # If we didn't find a proper project, report an error
        if self.project_type is None and not create:
            raise NotADirectoryError('DebOps project directory not found '
                                     'in ' + self.path)

        project_data = {
            'project': {
                'path': self.path,
                'name': self.name,
                'type': self.project_type,
            },
            'views': {
                'system': {}
            }
        }

        project_data['views']['system'].update(
                self.config.load(os.path.join(self.path, '.debops.cfg')))

        self.config.merge_env(self.path)
        self.config.merge(project_data)

        self.config.merge(os.path.join(self.path, '.debops', 'conf.d'))
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                project_type=self.project_type)
        self.ansible_cfg.load_config()

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

    def _create_legacy_project(self, path):
        self.project_type = 'legacy'

        inventory = AnsibleInventory(self, self.name, **self.kwargs)
        inventory.create()

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

        try:
            os.makedirs(path)
        except FileExistsError:
            pass

        # Create .debops.cfg
        self._write_file(os.path.join(path, '.debops.cfg'),
                         default_debops_cfg.render(env=os.environ)
                         + '\n')

        project_data = {
            'project': {
                'path': self.path,
                'name': self.name,
                'type': self.project_type,
            },
            'views': {
                'system': {}
            }
        }

        project_data['views']['system'].update(
                self.config.load(os.path.join(self.path, '.debops.cfg')))
        self.config.merge(project_data)

        encrypted_secrets = self.kwargs.get('encrypt', None)

        if encrypted_secrets == 'git-crypt':
            # Create .gitattributes
            self._write_file(os.path.join(path, '.gitattributes'),
                             default_gitattributes.render(secret_name='secret')
                             + '\n')

        # Create .gitignore
        self._write_file(os.path.join(path, '.gitignore'),
                         default_gitignore.render(
                             encrypted_secrets=encrypted_secrets,
                             secret_name='secret',
                             encfs_prefix='.encfs.')
                         + '\n')

        debops_cfg = (self.config.raw['views']['system']['ansible'])
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                project_type=self.project_type)
        self.ansible_cfg.load_config()
        self.ansible_cfg.merge_config(debops_cfg)
        self.ansible_cfg.write_config()
        print('Created new DebOps project in', path)

    def create(self):
        # First let's make sure that we are not inside another project
        self._legacy_config_path = self._find_up_dir(self.path,
                                                     ['.debops.cfg'])
        if self._legacy_config_path:
            raise IsADirectoryError('You are inside another '
                                    'DebOps project directory')

        # Let's make a new project
        self._create_legacy_project(self.path)

    def refresh(self):
        debops_cfg = {}
        if self.project_type == 'legacy':
            debops_cfg = (self.config.raw['views']['system']['ansible'])
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                project_type=self.project_type)
        self.ansible_cfg.merge_config(debops_cfg)
        self.ansible_cfg.write_config()
        print('Refreshed DebOps project in', self.path)

    def unlock(self):
        inventory = AnsibleInventory(self, self.name)
        inventory.unlock()

    def lock(self):
        inventory = AnsibleInventory(self, self.name)
        inventory.lock()

    def status(self):
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                project_type=self.project_type)
        self.ansible_cfg.load_config()
        collections = self.ansible_cfg.get_option(
                'collections_paths')
        inventory = AnsibleInventory(self, self.name)
        print('Project type:', self.project_type)
        print('Project root:', self.path)
        if inventory.encrypted:
            print('Inventory secrets are encrypted using ' + inventory.crypt_method)
            if inventory.crypt_method == 'encfs':
                if inventory.encfs_mounted:
                    print('Secret directory is mounted')
        print('Ansible Collection paths:')
        for path in collections.strip('"').split(':'):
            print('   ', path)
