# Copyright (C) 2020-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR
from .utils import unexpanduser, write_file, host_is_controller, strtobool
from .ansibleconfig import AnsibleConfig
from .ansible.inventory import AnsibleInventory
from .inventoryspec import (parse_spec, merge_specs, apply_spec,
                            render_keep,
                            render_spec, load_template,
                            PATH_RENDERED_VERSIONS,
                            CONTENT_RENDERED_VERSIONS, SPEC_TEMPLATES,
                            SPEC_VERSION)
from .hooks import run_hooks
import os
import pkgutil
import getpass
import jinja2
import socket
import distro
import platform
import pathlib
import git
import subprocess
import sys
import time
import logging

logger = logging.getLogger(__name__)


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

        # Expose current view in runtime environment
        self.config.set_env('DEBOPS_PROJECT_VIEW', self.view)

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
        logger.debug('Project {} loaded'.format(self.name))

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

    def _write_file(self, filename, *content, overwrite=False):
        """
        If file:`filename` does not exist, create it and write
        var:`content` into it. An existing file is only replaced when
        var:`overwrite` is True.

        Returns True if the file was written, False if it already existed and
        overwriting was not requested.
        """
        return write_file(filename, ''.join(content), overwrite=overwrite)

    def _inventory_spec_config(self):
        """Read the 'project.inventory_spec' configuration tree.

        The tree is written into '.debops/conf.d/project.yml' when a modern
        project is created. Projects created before it existed, and legacy
        projects, do not have it; they get the defaults, which permit
        everything the installed DebOps supports.

        Returns a dict with 'enabled', 'max_version' and 'allow_io'.
        """
        try:
            configured = self.config.raw.get('project', {}).get(
                'inventory_spec', {}) or {}
        except AttributeError:
            configured = {}

        enabled = configured.get('enabled', True)
        if isinstance(enabled, str):
            enabled = bool(strtobool(enabled))

        allow_io = configured.get('allow_io', False)
        if isinstance(allow_io, str):
            allow_io = bool(strtobool(allow_io))

        # The version is an integer in the configuration file, but a string
        # is accepted as well, since quoting numbers is an easy mistake to
        # make in YAML
        max_version = configured.get('version', SPEC_VERSION)
        try:
            max_version = int(max_version)
        except (TypeError, ValueError):
            raise ValueError('The project.inventory_spec.version option must '
                             'be an integer, not {!r}'.format(max_version))

        return {'enabled': bool(enabled),
                'max_version': max_version,
                'allow_io': bool(allow_io)}

    def _load_specs(self, inventory_path):
        """Parse the inventory file specifications given on the command line.

        Each '--template' value is resolved in order: '-' reads the document
        from standard input, a name matching a template shipped with DebOps
        loads that template, anything else is read as a file. Template names
        win over files of the same name; use a path such as './hosts' to load
        a file whose name matches a template. Standard input can only be
        consumed once per invocation.

        var:`inventory_path` is the Ansible inventory directory the
        specification is applied to; a version 3 document uses it as the base
        for relative paths given to include().

        Each document's version decides how much of it is templated: a version
        0 document is used as it is written, a version 1 document has its paths
        rendered, and a version 2 or 3 document has its paths and contents
        rendered. This happens before the documents are merged, so each one
        decides for itself.

        Returns a dict of inventory-relative path to file contents and the list
        of kept path patterns, both empty if no specification was requested.
        """
        sources = self.kwargs.get('spec_sources', None) or []

        if not sources:
            return {}, []

        policy = self._inventory_spec_config()

        if not policy['enabled']:
            raise ValueError('Inventory file specifications are disabled in '
                             'this project; the project.inventory_spec.enabled '
                             'option is false')

        if sources.count('-') > 1:
            raise ValueError('Standard input can only be read once, it cannot '
                             'be used for more than one --template option')

        context = self._spec_render_context()

        # The project can pre-authorize I/O in its configuration; the
        # '--allow-io' option grants it for one invocation
        allow_io = (bool(self.kwargs.get('allow_io', False))
                    or policy['allow_io'])
        specs = []

        for value in sources:
            source, spec = self._load_spec_source(value)

            if spec['version'] > policy['max_version']:
                raise ValueError(
                    '{} declares inventory specification version {}, but this '
                    'project allows at most version {} (the '
                    'project.inventory_spec.version option)'.format(
                        source, spec['version'], policy['max_version']))

            # Render before merging, so that a document's own version decides
            # which of its paths and contents are templates, even when
            # documents of different versions are combined. A version which
            # asks for neither is left exactly as it was written.
            version = spec['version']
            if version in PATH_RENDERED_VERSIONS:
                spec = {'version': version,
                        'files': render_spec(spec['files'], context, source,
                                             version=version,
                                             allow_io=allow_io,
                                             include_base=inventory_path,
                                             notify=logger.notice,
                                             render_contents=(
                                                 version in
                                                 CONTENT_RENDERED_VERSIONS)),
                        'keep': render_keep(spec['keep'], context, source,
                                            version=version)}

            specs.append((source, spec))

        files, keep, notices = merge_specs(specs)
        for notice in notices:
            logger.notice(notice)

        return files, keep

    def _load_spec_source(self, value):
        """Read one '--template' value and parse it into a specification.

        Returns the source description used in error messages and the parsed
        document. Resolution follows the order documented for _load_specs():
        standard input, then a shipped template, then a file, with template
        names winning over files of the same name.
        """
        if value == '-':
            if sys.stdin.isatty():
                raise ValueError('Reading an inventory specification from '
                                 'standard input was requested but '
                                 'standard input is a terminal. Pipe the '
                                 'document in, or pass a file name to '
                                 '--template instead.')
            source = 'standard input'
            return source, parse_spec(sys.stdin.read(), source)

        if value in SPEC_TEMPLATES:
            source = 'template "{}"'.format(value)
            return source, load_template(value)

        source = value
        try:
            with open(os.path.expanduser(value), 'r',
                      encoding='utf-8') as fh:
                document = fh.read()
        except OSError as errmsg:
            message = ('Cannot read inventory specification "{}": {}'
                       .format(value, errmsg.strerror))
            if os.sep not in value:
                message += ('; it is also not a template shipped with '
                            'DebOps (' +
                            ', '.join(sorted(SPEC_TEMPLATES)) + ')')
            raise ValueError(message)
        return source, parse_spec(document, source)

    def _spec_render_context(self):
        """Build the variables which a templated specification is rendered
        with.

        These are the variables that the DebOps project templates are rendered
        with, plus the facts of this project, so that one set of rules covers
        both.
        """
        return {
            'env': os.environ,
            'user': getpass.getuser(),
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'host_as_controller': host_is_controller(),
            'secret_name': self.kwargs.get('secret_name', 'secret'),
            'view': self.view,
            'default_view': self.kwargs.get('default_view', self.view),
            'project': {'name': self.name,
                        'path': self.path,
                        'type': self.project_type},
        }

    def _report_spec_result(self, result, base_dir, dry_run):
        """Tell the user which paths a specification changed or left alone.

        The per-path lines are logged at the NOTICE level, so that a template
        which touches many paths does not flood the terminal unless '-v' is
        used. The summary and the hint about '--force' stay on stdout.

        Removals are reported before writes to follow the order in which
        :func:`debops.inventoryspec.apply_spec` performs them, so that a
        document which removes a directory and then re-creates files inside it
        does not read as if it deleted what it had just written.
        """
        for key, verb in (('removed', 'Removed'),
                          ('planned_removed', 'Would remove'),
                          ('written', 'Created'),
                          ('planned', 'Would create'),
                          ('skipped', 'Skipped existing'),
                          ('kept', 'Kept')):
            for target in result.get(key, []):
                logger.notice('{} {}'.format(
                    verb, os.path.relpath(target, base_dir)))

        if result.get('skipped'):
            print("Use '--force' to overwrite or remove paths which already "
                  "exist.", file=self._status_stream())

        if not dry_run and not result.get('skipped'):
            print('Applied the inventory specification.',
                  file=self._status_stream())

    def _status_stream(self):
        """The stream for status messages.

        A 'list' or 'host' inspection prints JSON to standard output, so
        status messages go to standard error to keep the JSON usable in a
        pipe. Everything else stays on standard output.
        """
        if self.kwargs.get('list', False) or self.kwargs.get('host'):
            return sys.stderr
        return sys.stdout

    def _process_spec(self, inventory, pre_existing):
        """Apply an inventory file specification to an Ansible inventory.

        var:`pre_existing` is the set of paths which were present in the
        inventory before this command started, so that the specification can
        replace the files which DebOps itself just generated without touching
        the ones the user has written.
        """
        files, keep = self._load_specs(inventory.path)
        dry_run = self.kwargs.get('dry_run', False)
        overwrite = self.kwargs.get('force', False)

        if files:
            if dry_run:
                logger.info('Inventory specification will not be written to '
                            'disk')

            result = inventory.apply_spec(files, pre_existing=pre_existing,
                                          overwrite=overwrite,
                                          dry_run=dry_run, keep=keep)
            self._report_spec_result(result,
                                     os.path.realpath(inventory.path),
                                     dry_run)

    def _create_modern_project(self, path):
        logger.debug('Initializing new "modern" project directory')
        self.project_type = 'modern'
        default_view = self.kwargs.get('default_view', 'system')
        filename_view = default_view.replace('/', '-')

        # Create modern project directory structure
        self.createdirs(path)

        inventory = AnsibleInventory(self, default_view, **self.kwargs)

        pre_existing = inventory.existing_paths()

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

        self._process_spec(inventory, pre_existing)

        print('Created new DebOps project in', path,
              file=self._status_stream())

    def _create_legacy_project(self, path):
        logger.debug('Initializing new "legacy" project directory')
        self.project_type = 'legacy'

        inventory = AnsibleInventory(self, self.name, **self.kwargs)

        pre_existing = inventory.existing_paths()

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

        self._process_spec(inventory, pre_existing)

        print('Created new DebOps project in', path,
              file=self._status_stream())

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
        logger.debug('Creating new project directory')
        # First let's make sure that we are not inside another project
        self._modern_config_path = self._find_up_dir(self.path,
                                                     ['.debops', 'conf.d'])
        self._legacy_config_path = self._find_up_dir(self.path,
                                                     ['.debops.cfg'])
        if self._legacy_config_path or self._modern_config_path:
            raise IsADirectoryError('You are inside another '
                                    'DebOps project directory')

        if not run_hooks(self.path, 'pre-init'):
            raise RuntimeError('Hook pre-init aborted, not creating project')

        # Let's make a new project
        if self.project_type == 'modern':
            self._create_modern_project(self.path)
        elif self.project_type == 'legacy':
            self._create_legacy_project(self.path)

        create_git_repo = self.kwargs.get('git', None)
        if create_git_repo:
            logger.debug('Initializing git repository in project directory')
            repo = git.Repo.init(self.path)
            repo.git.add(all=True)
            logger.debug('Committing changes in project directory')
            repo.index.commit(self.config.raw['git']['init_message'])

            # Set up encryption using git-crypt
            encrypt_git_repo = self.kwargs.get('encrypt', None)
            if encrypt_git_repo == 'git-crypt':
                logger.debug('Preparing encryption using git-crypt')
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
                logger.debug('Locking files using git-crypt after project '
                             'creation')
                gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                 'lock'],
                                                stdin=subprocess.PIPE)
                gitcrypt_cmd.communicate()

            # Install Ansible Collections after the project is initialized
            install_requirements = self.kwargs.get('requirements', None)
            if install_requirements:
                logger.debug('Installing Ansible Collections specified in '
                             + os.path.join('ansible', 'collections',
                                            'requirements.yml') + ' file')
                os.chdir(self.path)
                try:
                    galaxy_cmd = subprocess.Popen(
                            [self._commands['ansible-galaxy'],
                             'collection', 'install', '-r',
                             os.path.join('ansible',
                                          'collections',
                                          'requirements.yml')],
                            stdin=subprocess.PIPE)
                    galaxy_cmd.communicate()
                except FileNotFoundError:
                    logger.notice('ansible-galaxy not available in $PATH, '
                                  'not installing Ansible Collections')
                logger.debug('Ansible Collections installed in project '
                             'directory')

        run_hooks(self.path, 'post-init')

    def mkview(self, view):

        # Make sure that users are not trying to nest the view inside of
        # another view
        try:
            parent_views = ([path for path
                             in list(self.config.raw['views'].keys())
                             if os.path.commonprefix(
                                 [path, view]) == path])
        except TypeError:
            logger.debug('New view name not specified')
            raise ValueError(f"New view name not specified")

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

                pre_existing = inventory.existing_paths()

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

                self._process_spec(inventory, pre_existing)

                print('Created', view, 'view in DebOps project', self.name,
                      file=self._status_stream())

            else:
                raise ValueError('You must specify name of the view '
                                 'as an argument')

        else:
            raise NotADirectoryError('This functionality only works in '
                                     '"modern" DebOps project directory')

    def commit(self, interactive=False):
        """Commit the current contents of the project directory to the git
        repository automatically."""
        if not self._is_git_repo(self.path):
            return

        run_hooks(self.path, 'pre-commit')

        logger.debug('Detected git repository in project directory')
        repo = git.Repo(self.path)
        repo.git.add(all=True)

        # Check if there are any differences between the current HEAD and
        # the index. If there are, we need to commit them.
        diff_list = repo.head.commit.diff()
        if diff_list:
            try:
                logger.debug('New changes detected, committing')
                repo.index.commit(
                    self.config.raw['project']['git']['auto_commit_message'])
                logger.debug('New changes committed in git repository')
            except KeyError:
                # There was an issue in the configuration, unstage any
                # changes in git index
                logger.warning('Issue in DebOps configuration, unstaging '
                               'changes in git index')
                repo.git.reset()
                if interactive:
                    print('The "project.git.auto_commit_message" option is '
                          'not defined. Not committing any changes.')
        else:
            logger.debug('No new changes detected, nothing to commit')

        run_hooks(self.path, 'post-commit')

    def refresh(self):
        logger.debug("Refresing project directory")

        if not run_hooks(self.path, 'pre-refresh'):
            print('Hook pre-refresh aborted, not refreshing project')
            return

        if self.project_type == 'modern':
            self.createdirs(self.path)

        project_views = list(self.config.raw['views'].keys())
        for view in project_views:
            inventory = AnsibleInventory(self, view, **self.kwargs)
            pre_existing = inventory.existing_paths()
            inventory.createdirs()

            # Only the selected view receives the specification, the other
            # views are refreshed with the internal defaults as before
            if view == self.view:
                self._process_spec(inventory, pre_existing)

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
        print('Refreshed DebOps project in', self.path,
              file=self._status_stream())

        run_hooks(self.path, 'post-refresh')

    def unlock(self):
        run_hooks(self.path, 'pre-unlock')
        inventory = AnsibleInventory(self, self.view)
        inventory.unlock()
        run_hooks(self.path, 'post-unlock')

    def lock(self):
        run_hooks(self.path, 'pre-lock')
        inventory = AnsibleInventory(self, self.view)
        inventory.lock()
        run_hooks(self.path, 'post-lock')
