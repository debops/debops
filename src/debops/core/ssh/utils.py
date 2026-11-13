# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The machinery shared by the ssh-family commands.

The known_hosts store selection, the store layout of a project view
and the resolution of the connection parameters of an inventory host
are used by 'debops ssh' and 'debops scp' alike; the command-specific
builders live in the sibling modules.
"""

import configparser
import json
import logging
import os
import pkgutil
import shlex
import subprocess

import jinja2

logger = logging.getLogger(__name__)

USER_KNOWN_HOSTS_STORE = '~/.ssh/known_hosts'


def ssh_store_dir(project_path, view):
    """Return the directory of the view's isolated known_hosts store."""
    return os.path.join(project_path, '.debops', 'ssh', 'views', view)


def ssh_store_file(project_path, view):
    """Return the known_hosts file of the view's isolated store."""
    return os.path.join(ssh_store_dir(project_path, view), 'known_hosts')


def render_ssh_drop_in(view):
    """Return the content of the view's SSH known_hosts drop-in.

    The drop-in is a TOML document which declares the project
    known_hosts mode and the view's isolated store through the Ansible
    configuration; the project directory merges it into the
    configuration tree, and the generated 'ansible.cfg' carries the
    store. The '${DEBOPS_PROJECT_PATH}' reference expands when the
    configuration is loaded and when the 'ansible.cfg' is parsed.
    """
    template = jinja2.Template(
            pkgutil.get_data(
                'debops',
                os.path.join('_data', 'templates', 'projectdir', 'modern',
                             'view', 'ssh.toml.j2')).decode('utf-8'),
            trim_blocks=True)
    return template.render(view_name=view,
                           store_path='.debops/ssh/views/' + view
                           + '/known_hosts')


def known_hosts_mode(project):
    """Return the configured known_hosts mode: 'user' or 'project'."""
    return project.config.raw.get('ssh', {}).get('known_hosts', 'user')


def declared_known_hosts_store(project):
    """Return the known_hosts store declared in the view's ansible.cfg.

    The store is the value of the 'UserKnownHostsFile' option in the
    '[ssh_connection] ssh_args' of the generated configuration, written
    by the 'view-<view>-ssh.toml' configuration drop-in. The function
    returns None when the view does not declare a store; such a view
    stays on the user store while the 'project' mode is active.
    """
    try:
        ssh_args = project.ansible_cfg.get_option(
            'ssh_args', section='ssh_connection')
    except (configparser.NoOptionError, configparser.NoSectionError):
        return None
    for token in shlex.split(ssh_args):
        if token.startswith('UserKnownHostsFile='):
            return os.path.expanduser(token.split('=', 1)[1])
    return None


def known_hosts_store(project):
    """Return the known_hosts store of the active mode.

    The 'user' mode resolves to the user's default known_hosts file.
    The 'project' mode resolves to the store declared in the view's
    configuration and returns None when the view does not declare one.
    """
    mode = known_hosts_mode(project)
    if mode == 'project':
        return declared_known_hosts_store(project)
    return os.path.expanduser(USER_KNOWN_HOSTS_STORE)


def resolve_host(project, host):
    """Return the connection parameters of an inventory host.

    The parameters come from the Ansible inventory, resolved with
    'ansible-inventory --host' the same way the Ansible runners resolve
    it. Returns a dict with the keys 'destination', 'user', 'port',
    'identity', 'common_args' and 'extra_args'; parameters the
    inventory does not define are None.

    Raises ValueError when the host is not defined in the inventory of
    the project's view, ChildProcessError when the resolution cannot
    run.
    """
    binary = project.config.raw['binaries']['ansible-inventory']
    try:
        process = subprocess.run(
            [binary, '--host', host], cwd=project.path,
            env=project.environment(), capture_output=True, text=True)
    except OSError as error:
        raise ChildProcessError(
            'Cannot run the inventory resolution: ' + str(error))
    if process.returncode != 0:
        detail = (process.stderr.strip().splitlines() or [''])[-1]
        raise ValueError('Cannot resolve the host "' + host + '": '
                         + detail)
    try:
        variables = json.loads(process.stdout)
    except ValueError:
        raise ValueError('Cannot resolve the host "' + host + '": the '
                         'inventory returned no usable host variables')
    return {
        'destination': variables.get('ansible_host') or host,
        'user': variables.get('ansible_user'),
        'port': variables.get('ansible_port'),
        'identity': variables.get('ansible_ssh_private_key_file'),
        'common_args': variables.get('ansible_ssh_common_args'),
        'extra_args': variables.get('ansible_ssh_extra_args'),
    }
