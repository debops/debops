# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from ..exceptions import NoDefaultViewException
from .inventoryspec import apply_spec
from ..utils import host_is_controller
import pkgutil
import jinja2
import socket
import os
import logging

try:
    # shlex.quote is new in Python 3.3
    from shlex import quote as shquote
except ImportError:
    # implement subset of shlex.quote
    def shquote(s):
        if not s:
            return "''"
        return "'" + s.replace("'", "'\"'\"'") + "'"

logger = logging.getLogger(__name__)


class AnsibleInventory(object):

    def __init__(self, project, name='system'):
        self.name = name
        self.project = project
        self.project_type = project.project_type

        if self.project_type == 'modern' and not self.name:
            raise NoDefaultViewException('No default view defined in DebOps '
                                         'configuration. Use "-V|--view" '
                                         'option to select one.')

        if project.project_type == 'legacy':
            self.root_path = os.path.join(project.path, 'ansible')
        else:
            self.root_path = os.path.join(project.path,
                                          'ansible',
                                          'views',
                                          self.name)

        self.path = os.path.join(self.root_path, 'inventory')
        logger.debug('Ansible inventory initialized')

    def existing_paths(self):
        """Return the set of paths which currently exist in the inventory.

        Used to tell apart the files the user has written or edited from the
        ones that DebOps generates, so that a specification can replace the
        latter without touching the former. Directories are included as well as
        files, so that a specification which removes a directory can tell
        whether it was already there before the command started.
        """
        found = set()
        if not os.path.isdir(self.path):
            return found
        for root, dirs, files in os.walk(self.path):
            for directory in dirs:
                found.add(os.path.realpath(os.path.join(root, directory)))
            for filename in files:
                found.add(os.path.realpath(os.path.join(root, filename)))
        return found

    def apply_spec(self, files, pre_existing=frozenset(), overwrite=False,
                   dry_run=False, keep=()):
        """Apply the paths described by a specification in the inventory.

        var:`keep` names the paths which the specification must not remove or
        clear, together with the directories above them.

        Returns the same result mapping as
        :func:`debops.core.inventoryspec.apply_spec`.
        """
        logger.info('Applying inventory specification in {} directory'.format(
            self.path))
        return apply_spec(files, self.path, pre_existing=pre_existing,
                          overwrite=overwrite, dry_run=dry_run, keep=keep)

    def createdirs(self):
        skel_dirs = (
            os.path.join('inventory', 'group_vars', 'all'),
            os.path.join('inventory', 'host_vars'),
            os.path.join('playbooks', 'roles'),
            os.path.join('resources', 'templates', 'by-group', 'all'),
            os.path.join('resources', 'templates', 'by-host'),
            os.path.join('secret'),
        )

        if self.project_type == 'legacy':
            skel_dirs = skel_dirs + (
                    os.path.join('collections', 'ansible_collections'),
                    os.path.join('keyring'),
                    os.path.join('overrides', 'files'),
                    os.path.join('overrides', 'tasks'),
                    os.path.join('overrides', 'templates'),)

        for skel_dir in skel_dirs:
            skel_dir = os.path.join(self.root_path, skel_dir)
            if not os.path.isdir(skel_dir):
                os.makedirs(skel_dir)

    def create(self):

        logger.info('Creating inventory in {} directory'.format(self.root_path))
        try:
            os.makedirs(self.root_path)
        except FileExistsError:
            logger.error('Cannot create view in {}, directory already '
                         'exists'.format(self.root_path),
                         extra={'allow': 'syslog'})
            raise IsADirectoryError("Cannot create view in "
                                    + self.root_path + ", directory "
                                    "already exists")

        # Create directory structure around the inventory
        self.createdirs()

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
        hosts_path = os.path.join(self.path, 'hosts')
        if not os.path.exists(hosts_path):
            with open(hosts_path, 'w') as fh:
                fh.writelines(
                    default_hosts.render(
                        host_as_controller=host_is_controller(),
                        hostname=socket.gethostname(),
                        fqdn=socket.getfqdn()))
            logger.debug('Default hosts file created in Ansible inventory')

        logger.debug('Ansible inventory created')
