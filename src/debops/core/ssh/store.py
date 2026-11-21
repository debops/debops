# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The known_hosts store of the ssh suite: layout, mode and trust.

The store of a view is selected by the 'ssh.known_hosts' option: the
'user' mode resolves to the operator's own known_hosts file, the
'project' mode to the store which the view's 'ansible.cfg' declares
through the 'UserKnownHostsFile' option of its '[ssh_connection]
ssh_args' -- the value the 'view-<view>-ssh.toml' configuration
drop-in writes. The store is the single source shared with Ansible:
the connections of the runners use it because Ansible reads it from
the same 'ssh_args', and the 'debops ssh' commands inject it
explicitly into their composed commands, so that no resolved
argument can bypass it. The two mechanisms differ in one respect
which the commands cannot fix: a host which defines its own
'ansible_ssh_args' replaces the configured value in Ansible's own
variable-over-configuration semantics, and the Ansible connections
to such a host fall back to the operator's own known_hosts.

This module carries the layout and the policy of the stores and
nothing else; it does not import the rest of the ssh suite, so the
project machinery -- the runners, the project directory -- can use
it without pulling the connection composition or the SSHFP
verification in.
"""

import configparser
import os
import pkgutil
import shlex

import jinja2

from ..utils import path_inside_project

USER_KNOWN_HOSTS_STORE = '~/.ssh/known_hosts'


def ssh_store_path(view):
    """Return the store path of a view, relative to the project
    directory."""
    return os.path.join('.debops', 'ssh', 'views', view, 'known_hosts')


def ssh_store_dir(project_path, view):
    """Return the directory of the view's isolated known_hosts store."""
    return os.path.dirname(os.path.join(project_path,
                                        ssh_store_path(view)))


def ssh_store_file(project_path, view):
    """Return the known_hosts file of the view's isolated store."""
    return os.path.join(project_path, ssh_store_path(view))


def ensure_store_dir(store_file, project=None):
    """Create the directory chain of a view's known_hosts store.

    The directories from the '.debops/ssh' root of the project down
    to the store directory are created with the 0700 mode of the
    real '~/.ssh'; existing directories which are open to the group
    or the others are tightened to the same mode. A store outside of
    the project layout gets only its own directory ensured, without
    permission changes. When the project directory is given, the store
    path is refused when it resolves outside of it. Returns the store
    directory.
    """
    store_file = os.path.expanduser(store_file)
    if project is not None and not path_inside_project(store_file, project):
        raise ValueError('Refusing to create a known_hosts store outside '
                         'of the project directory: ' + store_file)
    store_dir = os.path.dirname(os.path.abspath(store_file))
    views_dir = os.path.dirname(store_dir)
    ssh_dir = os.path.dirname(views_dir)
    in_project = False
    if (os.path.basename(views_dir) == 'views'
            and os.path.basename(ssh_dir) == 'ssh'
            and os.path.basename(os.path.dirname(ssh_dir)) == '.debops'):
        # The '.debops' directory keeps the default permissions; only
        # the 'ssh' tree becomes private
        os.makedirs(os.path.dirname(ssh_dir), exist_ok=True)
        chain = [ssh_dir, views_dir, store_dir]
        in_project = True
    else:
        chain = [store_dir]
    for directory in chain:
        existed = os.path.isdir(directory)
        os.makedirs(directory, mode=0o700, exist_ok=True)
        if existed and in_project:
            mode = os.stat(directory).st_mode & 0o777
            if mode & 0o077:
                os.chmod(directory, 0o700)
    return store_dir


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
                           store_path=ssh_store_path(view))


def known_hosts_mode(project):
    """Return the known_hosts mode of the project's active view:
    'user' or 'project'."""
    views = project.config.raw.get('views', {})
    view_config = views.get(project.view, {})
    return view_config.get('ssh', {}).get('known_hosts', 'user')


def quote_store_path(store):
    """Return the store path in the form the ssh option parsing keeps
    as one value.

    A path which carries whitespace would be split into fragment
    paths by the option parsing of ssh, both in the '-o' option value
    and in the 'ssh_config' file; the double-quoted form survives
    both. Paths which carry quotes, apostrophes, backslashes or
    newlines cannot be represented: the value lands inside contexts
    which the shell executes as well -- the ProxyCommand of a jump
    host, the single-quoted composition of the runners -- and an
    apostrophe would break their quoting. Such paths raise ValueError.
    """
    if ('"' in store or "'" in store or '\\' in store
            or '\n' in store or '\r' in store):
        raise ValueError(
            'The known_hosts store path carries quotes, apostrophes, '
            'backslashes or newlines and cannot be written into an '
            'SSH option: ' + store)
    if any(character.isspace() for character in store):
        return '"' + store + '"'
    return store


def known_hosts_option(store):
    """Return the value of the '-o UserKnownHostsFile' option for a
    known_hosts store."""
    return 'UserKnownHostsFile=' + quote_store_path(store)


def entry_key_material(lines):
    """Return the '(key type, key blob)' pairs of known_hosts entry
    lines.

    The comparison of a scanned key against the stored entries runs on
    the key material alone: the hashed form of a host name carries a
    fresh salt on every scan, so the text of an unchanged entry
    changes while its key does not. The marker lines
    ('@cert-authority', '@revoked') carry their material one field
    later.
    """
    material = set()
    for line in lines:
        if line.startswith('#'):
            continue
        fields = line.split()
        if fields and fields[0].startswith('@'):
            if len(fields) < 4:
                continue
            material.add((fields[2], fields[3]))
        elif len(fields) >= 3:
            material.add((fields[1], fields[2]))
    return material


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
            value = token.split('=', 1)[1]
            # The drop-in quotes the store path for the option parsing
            # of ssh; the quotes stay literal inside the single-quoted
            # configuration token
            value = value[1:-1] if value.startswith('"') \
                and value.endswith('"') else value
            return os.path.expanduser(value)
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


def require_store(project):
    """Return the known_hosts store of the active mode, and whether
    the commands must inject it into their composed commands.

    In the 'user' mode the store is the operator's own known_hosts
    file and no injection is needed: ssh consults it anyway. In the
    'project' mode the store is the one declared in the view's
    configuration, and every command which composes an ssh command
    line must inject it as the first ssh option -- ssh applies the
    first obtained value of an option, so no resolved argument can
    bypass the store of the view.

    Raises ValueError when the project mode is active and the view
    does not declare a store; the commands of the ssh suite refuse
    such a view symmetrically.
    """
    mode = known_hosts_mode(project)
    if mode == 'project':
        store = declared_known_hosts_store(project)
        if not store:
            raise ValueError(
                'The project known_hosts mode is active for the view, '
                'but the view does not declare a known_hosts store')
        return store, True
    return os.path.expanduser(USER_KNOWN_HOSTS_STORE), False
