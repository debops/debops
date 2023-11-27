# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR
from .utils import unexpanduser
from .ansibleconfig import AnsibleConfig
from .ansible.inventory import AnsibleInventory
import os
import pkgutil
import jinja2
import socket
import distro
import platform
import pathlib
import git
import subprocess
import time


class ProjectDir(object):

    def __init__(self, path=os.getcwd(), project_type='legacy', create=False,
                 config=None, view=None, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.config = config
        self.path = os.path.abspath(path)
        self.name = os.path.basename(self.path)
        self.project_type = self.kwargs.get('type', project_type)

        # We should work in the project directory as cwd, however Ansible can
        # be executed from anywhere. If $ANSIBLE_CONFIG is defined, use it as the
        # base directory just to be safe. Otherwise, switch to the directory
        # defined at the command line.
        try:
            os.chdir(os.path.dirname(os.environ['ANSIBLE_CONFIG']))
            self.path = os.getcwd()
        except (KeyError, FileNotFoundError):
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
        self._modern_config_path = self._find_up_dir(self.path,
                                                     ['.debops', 'conf.d'])
        self._legacy_config_path = self._find_up_dir(self.path,
                                                     ['.debops.cfg'])
        if self._legacy_config_path:
            self.path = os.path.dirname(self._legacy_config_path)
            self.name = os.path.basename(self.path)
            self.project_type = 'legacy'
        elif self._modern_config_path:
            self.path = str(pathlib.Path(self._modern_config_path).parents[1])
            self.name = os.path.basename(self.path)
            self.project_type = 'modern'
        else:
            if not create:
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
            'views': {}
        }

        if self.project_type == 'legacy':
            project_data['views'].update({'system': {}})
            project_data['views']['system'].update(
                    self.config.load(os.path.join(self.path,
                                                  '.debops.cfg')))

        # Expose project root directory in runtime environment
        self.config.set_env('DEBOPS_PROJECT_PATH',
                            unexpanduser(self.path))

        self.config.merge_env(os.path.join(self.path,
                                           '.debops', 'environment'))
        self.config.merge_env(self.path)
        self.config.merge(project_data)

        self.config.merge(os.path.join(self.path, '.debops', 'conf.d'))

        self._commands = {
            'ansible-galaxy': self.config.raw['binaries']['ansible-galaxy'],
            'git-crypt': self.config.raw['binaries']['git-crypt']
        }

        # Set the default view
        try:
            self.view = self.config.raw['project']['default_view']
        except KeyError:
            self.view = 'system'

        # We might be in a project subdirectory, perhaps in a specific view
        if self.path != os.getcwd():
            current_dir = os.getcwd()
            view_dir = None
            view_path = []

            while current_dir != '/' and not view_dir:
                view_path.insert(0, os.path.basename(current_dir))
                if os.path.dirname(current_dir).endswith('/ansible/views'):
                    view_dir = current_dir
                else:
                    current_dir = os.path.dirname(current_dir)

            # We are in a specific view directory, let's switch to that
            if view_dir:

                # Just to make sure, let's check if current view path can be
                # matched to a known view in the configuration tree
                view_name = os.path.join(*view_path)
                matching_views = ([path for path
                                   in list(self.config.raw['views'].keys())
                                   if os.path.commonprefix(
                                       [path, view_name]) == path])

                # There should be just one matching view. If there are none or
                # more than one, stay with the default view
                if len(matching_views) == 1:
                    self.view = matching_views[0]

        # User selected the view using command line arguments
        if view:
            if self.view != view:
                if view in list(self.config.raw['views'].keys()):
                    self.view = view
                else:
                    raise NotADirectoryError('The "' + view + '" view is not '
                                             'present in the "' + self.name
                                             + '" project')

        # Expose current view in configuration tree
        view_data = {
            'project': {
                'view': self.view
                }
            }
        self.config.merge(view_data)

        if self.project_type == 'legacy':
            self.ansible_cfg = AnsibleConfig(
                    os.path.join(self.path, 'ansible.cfg'),
                    project_type=self.project_type)
            if not self.config.get_env('DEBOPS_ANSIBLE_INVENTORY'):
                self.config.set_env('DEBOPS_ANSIBLE_INVENTORY',
                                    unexpanduser(os.path.join(self.path,
                                                              'ansible',
                                                              'inventory')))

        elif self.project_type == 'modern':
            self.ansible_cfg = AnsibleConfig(
                    os.path.join(self.path, 'ansible', 'views',
                                 self.view, 'ansible.cfg'),
                    project_type=self.project_type,
                    view=self.view)
            if not self.config.get_env('DEBOPS_ANSIBLE_INVENTORY'):
                self.config.set_env('DEBOPS_ANSIBLE_INVENTORY',
                                    unexpanduser(os.path.join(self.path,
                                                              'ansible',
                                                              'views', self.view,
                                                              'inventory')))

        self.ansible_cfg.load_config()
        self.config.set_env('ANSIBLE_CONFIG',
                            unexpanduser(self.ansible_cfg.path))

        project_views = list(self.config.raw['views'].keys())
        for view in project_views:
            inventory = AnsibleInventory(self, view, **self.kwargs)

            if inventory.encrypted:
                inventory_data = {
                    'views': {
                        view: {
                          'encryption': {
                            'enabled': inventory.encrypted,
                            'mounted': inventory.encfs_mounted,
                            'type': str(inventory.crypt_method or 'none')
                          }
                        }
                      }
                    }
                self.config.merge(inventory_data)

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

    def _is_git_repo(self, path):
        try:
            _ = git.Repo(path).git_dir
            return True
        except (git.exc.InvalidGitRepositoryError,
                git.exc.NoSuchPathError):
            return False

    def _write_file(self, filename, *content):
        """
        If file:`filename` does not exist, create it and write
        var:`content` into it.
        """
        if not os.path.exists(filename):
            with open(filename, "w") as fh:
                fh.writelines(content)

    def _create_modern_project(self, path):
        self.project_type = 'modern'
        default_view = self.kwargs.get('default_view', 'system')
        filename_view = default_view.replace('/', '-')

        # Create modern project directory structure
        self.createdirs(path)

        inventory = AnsibleInventory(self, default_view, **self.kwargs)
        inventory.create()

        default_project_yml = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'project.yml.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_environment = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'environment.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_view_yml = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'view.yml.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_gitignore = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'gitignore.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_requirements = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'requirements.yml.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_view_gitattributes = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'view',
                                              'gitattributes.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_view_gitignore = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'view',
                                              'gitignore.j2'))
                .decode('utf-8'), trim_blocks=True)

        default_inventory_keyring = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'view',
                                              'inventory',
                                              'group_vars',
                                              'all',
                                              'keyring.yml.j2'))
                .decode('utf-8'), trim_blocks=True)

        # Create .debops/conf.d/project.yml
        self._write_file(os.path.join(path, '.debops', 'conf.d',
                                      'project.yml'),
                         default_project_yml.render(env=os.environ,
                                                    default_view=default_view)
                         + '\n')

        # Create .debops/conf.d/view-<name>.yml
        self._write_file(os.path.join(path, '.debops', 'conf.d',
                                      'view-' + filename_view + '.yml'),
                         default_view_yml.render(env=os.environ,
                                                 view_name=default_view)
                         + '\n')

        # Create .debops/environment
        self._write_file(os.path.join(path, '.debops', 'environment'),
                         default_environment.render(env=os.environ)
                         + '\n')

        encrypted_secrets = self.kwargs.get('encrypt', None)

        # Create .gitignore
        self._write_file(os.path.join(path, '.gitignore'),
                         default_gitignore.render()
                         + '\n')

        # Create ansible/collections/requirements.yml
        self._write_file(os.path.join(path, 'ansible', 'collections',
                                      'requirements.yml'),
                         default_requirements.render()
                         + '\n')

        # Create view/.gitattributes
        self._write_file(os.path.join(path, 'ansible', 'views',
                                      default_view, '.gitattributes'),
                         default_view_gitattributes.render(
                             encrypted_secrets=encrypted_secrets,
                             secret_name='secret',
                             encfs_prefix='.encfs.')
                         + '\n')

        # Create view/.gitignore
        self._write_file(os.path.join(path, 'ansible', 'views',
                                      default_view, '.gitignore'),
                         default_view_gitignore.render(
                             encrypted_secrets=encrypted_secrets,
                             secret_name='secret',
                             encfs_prefix='.encfs.')
                         + '\n')

        # Create view/inventory/group_vars/all/keyring.yml
        self._write_file(os.path.join(path, 'ansible', 'views',
                                      default_view, 'inventory',
                                      'group_vars', 'all', 'keyring.yml'),
                         default_inventory_keyring.render()
                         + '\n')

        self.config.merge(os.path.join(self.path, '.debops', 'conf.d'))

        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible', 'views',
                             default_view, 'ansible.cfg'),
                project_type=self.project_type,
                view=default_view)
        self.ansible_cfg.load_config()
        self.ansible_cfg.merge_config(
                self.config.raw['views'][default_view]['ansible'])
        self.ansible_cfg.write_config()
        print('Created new DebOps project in', path)

    def _create_legacy_project(self, path):
        self.project_type = 'legacy'

        inventory = AnsibleInventory(self, self.name, **self.kwargs)
        inventory.create()

        default_requirements = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'modern',
                                              'requirements.yml.j2'))
                .decode('utf-8'), trim_blocks=True)

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

        default_inventory_keyring = jinja2.Template(
                pkgutil.get_data('debops',
                                 os.path.join('_data',
                                              'templates',
                                              'projectdir',
                                              'legacy',
                                              'ansible',
                                              'inventory',
                                              'group_vars',
                                              'all',
                                              'keyring.yml.j2'))
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

        # Create ansible/collections/requirements.yml
        self._write_file(os.path.join(path, 'ansible', 'collections',
                                      'requirements.yml'),
                         default_requirements.render()
                         + '\n')

        # Create ansible/inventory/group_vars/all/keyring.yml
        self._write_file(os.path.join(path, 'ansible', 'inventory',
                                      'group_vars', 'all', 'keyring.yml'),
                         default_inventory_keyring.render()
                         + '\n')

        debops_cfg = (self.config.raw['views']['system']['ansible'])
        self.ansible_cfg = AnsibleConfig(
                os.path.join(self.path, 'ansible.cfg'),
                project_type=self.project_type)
        self.ansible_cfg.load_config()
        self.ansible_cfg.merge_config(debops_cfg)
        self.ansible_cfg.write_config()
        print('Created new DebOps project in', path)

    def createdirs(self, path):
        skel_dirs = (
            os.path.join(path, '.debops', 'conf.d'),
            os.path.join(path, 'ansible', 'collections',
                         'ansible_collections'),
            os.path.join(path, 'ansible', 'keyring'),
            os.path.join(path, 'ansible', 'overrides', 'files'),
            os.path.join(path, 'ansible', 'overrides', 'tasks'),
            os.path.join(path, 'ansible', 'overrides', 'templates'),
        )

        for skel_dir in skel_dirs:
            if not os.path.isdir(skel_dir):
                os.makedirs(skel_dir)

    def create(self):
        # First let's make sure that we are not inside another project
        self._modern_config_path = self._find_up_dir(self.path,
                                                     ['.debops', 'conf.d'])
        self._legacy_config_path = self._find_up_dir(self.path,
                                                     ['.debops.cfg'])
        if self._legacy_config_path or self._modern_config_path:
            raise IsADirectoryError('You are inside another '
                                    'DebOps project directory')

        # Let's make a new project
        if self.project_type == 'modern':
            self._create_modern_project(self.path)
        elif self.project_type == 'legacy':
            self._create_legacy_project(self.path)

        create_git_repo = self.kwargs.get('git', None)
        if create_git_repo:
            repo = git.Repo.init(self.path)
            repo.git.add(all=True)
            repo.index.commit(self.config.raw['git']['init_message'])

            # Set up encryption using git-crypt
            encrypt_git_repo = self.kwargs.get('encrypt', None)
            if encrypt_git_repo == 'git-crypt':
                try:
                    gpg_keys = list(self.kwargs.get('keys', None).split(','))
                except AttributeError:
                    raise ValueError('List of GPG recipients not specified')

                os.chdir(self.path)
                gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                 'init'],
                                                stdin=subprocess.PIPE)
                gitcrypt_cmd.communicate()
                while not os.path.exists(
                        os.path.join('.git', 'git-crypt', 'keys')):
                    time.sleep(1)
                for gpg_key in gpg_keys:
                    gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                     'add-gpg-user',
                                                    gpg_key], stdin=subprocess.PIPE)
                    gitcrypt_cmd.communicate()

                # Lock the repository after setting up git-crypt
                gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                 'lock'],
                                                stdin=subprocess.PIPE)
                gitcrypt_cmd.communicate()

            # Install Ansible Collections after the project is initialized
            install_requirements = self.kwargs.get('requirements', None)
            if install_requirements:
                os.chdir(self.path)
                galaxy_cmd = subprocess.Popen([self._commands['ansible-galaxy'],
                                               'collection', 'install', '-r',
                                               os.path.join('ansible',
                                                            'collections',
                                                            'requirements.yml')],
                                              stdin=subprocess.PIPE)
                galaxy_cmd.communicate()

    def mkview(self, view):

        # Make sure that users are not trying to nest the view inside of
        # another view
        parent_views = ([path for path
                         in list(self.config.raw['views'].keys())
                         if os.path.commonprefix(
                             [path, view]) == path])
        if parent_views:

            # We can allow views with common directory prefix, but we need to
            # catch a case where a view is created inside another view
            common_prefix = os.path.commonprefix(parent_views)
            if (view.startswith(common_prefix) and view != common_prefix
                    and os.path.dirname(view) in parent_views):
                raise ValueError(f"The '{view}' view cannot be placed inside "
                                 "another view")

        filename_view = view.replace('/', '-')
        if self.project_type == 'modern':
            if view:
                inventory = AnsibleInventory(self, view, **self.kwargs)
                inventory.create()

                default_view_yml = jinja2.Template(
                        pkgutil.get_data('debops',
                                         os.path.join('_data',
                                                      'templates',
                                                      'projectdir',
                                                      'modern',
                                                      'view.yml.j2'))
                        .decode('utf-8'), trim_blocks=True)

                default_view_gitattributes = jinja2.Template(
                        pkgutil.get_data('debops',
                                         os.path.join('_data',
                                                      'templates',
                                                      'projectdir',
                                                      'modern',
                                                      'view',
                                                      'gitattributes.j2'))
                        .decode('utf-8'), trim_blocks=True)

                default_view_gitignore = jinja2.Template(
                        pkgutil.get_data('debops',
                                         os.path.join('_data',
                                                      'templates',
                                                      'projectdir',
                                                      'modern',
                                                      'view',
                                                      'gitignore.j2'))
                        .decode('utf-8'), trim_blocks=True)

                default_inventory_keyring = jinja2.Template(
                        pkgutil.get_data('debops',
                                         os.path.join('_data',
                                                      'templates',
                                                      'projectdir',
                                                      'modern',
                                                      'view',
                                                      'inventory',
                                                      'group_vars',
                                                      'all',
                                                      'keyring.yml.j2'))
                        .decode('utf-8'), trim_blocks=True)

                # Create .debops/conf.d/view-<name>.yml
                self._write_file(
                        os.path.join(self.path, '.debops', 'conf.d',
                                     'view-' + filename_view + '.yml'),
                        default_view_yml.render(env=os.environ,
                                                view_name=view)
                        + '\n')

                encrypted_secrets = self.kwargs.get('encrypt', None)

                # Create view/.gitattributes
                self._write_file(os.path.join(self.path, 'ansible', 'views',
                                              view, '.gitattributes'),
                                 default_view_gitattributes.render(
                                     secret_name='secret',
                                     encrypted_secrets=encrypted_secrets)
                                 + '\n')

                # Create view/.gitignore
                self._write_file(os.path.join(self.path, 'ansible', 'views',
                                              view, '.gitignore'),
                                 default_view_gitignore.render(
                                     encrypted_secrets=encrypted_secrets,
                                     secret_name='secret',
                                     encfs_prefix='.encfs.')
                                 + '\n')

                # Create view/inventory/group_vars/all/keyring.yml
                self._write_file(os.path.join(self.path, 'ansible', 'views',
                                              view, 'inventory',
                                              'group_vars', 'all', 'keyring.yml'),
                                 default_inventory_keyring.render()
                                 + '\n')

                self.config.merge(os.path.join(self.path, '.debops', 'conf.d'))

                self.ansible_cfg = AnsibleConfig(
                        os.path.join(self.path, 'ansible', 'views',
                                     view, 'ansible.cfg'),
                        project_type=self.project_type,
                        view=view)
                self.ansible_cfg.load_config()
                self.ansible_cfg.merge_config(
                        self.config.raw['views'][view]['ansible'])
                self.ansible_cfg.write_config()
                print('Created', view, 'view in DebOps project', self.name)

            else:
                raise ValueError('You must specify name of the view '
                                 'as an argument')

        else:
            raise NotADirectoryError('This functionality only works in '
                                     '"modern" DebOps project directory')

    def commit(self, interactive=False):
        """Commit the current contents of the project directory to the git
        repository automatically."""
        if self._is_git_repo(self.path):
            repo = git.Repo(self.path)
            repo.git.add(all=True)

            # Check if there are any differences between the current HEAD and
            # the index. If there are, we need to commit them.
            diff_list = repo.head.commit.diff()
            if diff_list:
                try:
                    repo.index.commit(
                        self.config.raw['project']['git']['auto_commit_message'])
                except KeyError:
                    # There was an issue in the configuration, unstage any
                    # changes in git index
                    repo.git.reset()
                    if interactive:
                        print('The "project.git.auto_commit_message" option is '
                              'not defined. Not committing any changes.')

    def refresh(self):
        if self.project_type == 'modern':
            self.createdirs(self.path)

        project_views = list(self.config.raw['views'].keys())
        for view in project_views:
            inventory = AnsibleInventory(self, view, **self.kwargs)
            inventory.createdirs()

            if self.project_type == 'modern':
                self.ansible_cfg = AnsibleConfig(
                        os.path.join(self.path, 'ansible', 'views',
                                     view, 'ansible.cfg'),
                        project_type=self.project_type,
                        view=view)
                self.ansible_cfg.load_config()
                self.ansible_cfg.merge_config(
                        self.config.raw['views'][view]['ansible'])
                self.ansible_cfg.write_config()
            elif self.project_type == 'legacy':
                debops_cfg = (self.config.raw['views']['system']['ansible'])
                self.ansible_cfg = AnsibleConfig(
                        os.path.join(self.path, 'ansible.cfg'),
                        project_type=self.project_type)
                self.ansible_cfg.merge_config(debops_cfg)
                self.ansible_cfg.write_config()
        print('Refreshed DebOps project in', self.path)

    def unlock(self):
        inventory = AnsibleInventory(self, self.view)
        inventory.unlock()

    def lock(self):
        inventory = AnsibleInventory(self, self.view)
        inventory.lock()
