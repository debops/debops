# -*- coding: utf-8 -*-

# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import pkgutil
import jinja2
import platform
import distro
import socket
import subprocess
import sys
import os
import stat
import string
import itertools
import random
import time

try:
    # shlex.quote is new in Python 3.3
    from shlex import quote as shquote
except ImportError:
    # implement subset of shlex.quote
    def shquote(s):
        if not s:
            return "''"
        return "'" + s.replace("'", "'\"'\"'") + "'"


class AnsibleInventory(object):

    def __init__(self, project, name='system', *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

        self.encrypted = False
        self.crypt_method = ''

        self.encfs_keyfile = '.encfs6.keyfile'
        self.encfs_configfile = '.encfs6.xml'
        self.encfs_mounted = False

        self._commands = {
            'gpg': project.config.raw['binaries']['gpg'],
            'encfs': project.config.raw['binaries']['encfs'],
            'umount': project.config.raw['binaries']['umount'],
            'fusermount': project.config.raw['binaries']['fusermount']
        }

        if project.project_type == 'legacy':
            self.root_path = os.path.join(project.path, 'ansible')
        else:
            self.root_path = os.path.join(project.path,
                                          'ansible',
                                          'views',
                                          self.name)

        self.path = os.path.join(self.root_path, 'inventory')
        self.secret_path = os.path.join(self.root_path, 'secret')
        self.encfs_path = os.path.join(self.root_path, '.encfs.secret')
        if os.path.exists(self.encfs_path):
            self.encrypted = True
            self.crypt_method = 'encfs'
            if os.path.ismount(self.secret_path):
                self.encfs_mounted = True

    def _get_random_string(self):
        all_chars = string.digits + string.ascii_letters + string.punctuation
        random_string = (''.join(random.choice(all_chars)
                         for i in range(64)))
        return random_string

    def _encrypt_secrets_encfs(self):
        encfs_keyfile = os.path.join(self.encfs_path, '.encfs6.keyfile')
        encfs_configfile = os.path.join(self.encfs_path, '.encfs6.xml')
        encfs_password = self._get_random_string()

        try:
            gpg_keys = list(self.kwargs.get('keys', None).split(','))
            gpg_recipients = list(
                    itertools.chain.from_iterable(['-r', r]
                                                  for r in gpg_keys))
        except AttributeError:
            raise ValueError('List of GPG recipients not specified')

        if not os.path.exists(self.encfs_path):
            print('Encrypting Ansible secrets using EncFS...')
            os.makedirs(self.encfs_path)
            gpg_cmd = subprocess.Popen([self._commands['gpg'], '--encrypt', '--armor',
                                        '--output', encfs_keyfile] + gpg_recipients,
                                       stdin=subprocess.PIPE)
            gpg_cmd.communicate(encfs_password.encode('utf-8'))
            while not os.path.exists(encfs_keyfile):
                time.sleep(1)

            encfs_cmd = subprocess.Popen([
                self._commands['encfs'], self.encfs_path, self.secret_path,
                '--extpass',
                self._commands['gpg'] + ' --decrypt --no-mdc-warning --output - '
                + shquote(encfs_keyfile)],
                stdin=subprocess.PIPE)
            encfs_cmd.communicate(('p\n' + encfs_password).encode('utf-8'))

            while not os.path.exists(encfs_configfile):
                time.sleep(1)

            # Set the inventory state to correctly lock the secrets
            self.encrypted = True
            self.crypt_method = 'encfs'
            if os.path.ismount(self.secret_path):
                self.encfs_mounted = True
            self.lock()

            gpg_cmd = subprocess.Popen([self._commands['gpg'], '--encrypt', '--armor',
                                        '--output', encfs_configfile + '.asc']
                                       + gpg_recipients + [encfs_configfile])
            while not os.path.exists(encfs_configfile + '.asc'):
                time.sleep(1)
            os.remove(encfs_configfile)

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
            os.path.join('overrides', 'files'),
            os.path.join('overrides', 'tasks'),
            os.path.join('overrides', 'templates'),
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

        encrypted_secrets = self.kwargs.get('encrypt', None)
        if encrypted_secrets is not None:
            if encrypted_secrets == 'encfs':
                self._encrypt_secrets_encfs()

    def unlock(self):
        if self.encrypted:
            if self.crypt_method == 'encfs':
                keyfile = os.path.join(self.encfs_path, self.encfs_keyfile)
                configfile = os.path.join(self.encfs_path, self.encfs_configfile)
                crypted_configfile = os.path.join(self.encfs_path,
                                                  self.encfs_configfile + '.asc')

                if os.path.ismount(self.secret_path):
                    self.encfs_mounted = True
                    return False
                else:
                    if not os.path.isdir(self.secret_path):
                        os.makedirs(self.secret_path)

                    if not os.path.exists(configfile):
                        os.mkfifo(configfile)
                    elif not stat.S_ISFIFO(os.stat(configfile).st_mode):
                        raise IOError(17, configfile + ' exists but is not a fifo')

                    subprocess_env = os.environ.copy()
                    encfs = subprocess.Popen([
                        self._commands['encfs'], self.encfs_path, self.secret_path,
                        '--extpass',
                        '{} --decrypt --no-mdc-warning --output - {}'.format(
                                self._commands['gpg'], shquote(keyfile))],
                        env=subprocess_env)
                    with open(configfile, 'w') as fh:
                        gpg = subprocess.Popen(
                                [self._commands['gpg'],
                                 '--decrypt', '--no-mdc-warning',
                                 '--output', '-', crypted_configfile],
                                stdout=fh, env=subprocess_env)
                    gpg.communicate()
                    encfs.communicate()
                    os.remove(configfile)
                    self.encfs_mounted = True
                    return True
        else:
            return False

    def lock(self):
        if self.encrypted:
            if self.crypt_method == 'encfs':
                if os.path.ismount(self.secret_path):
                    if sys.platform == 'darwin':
                        subprocess.call([self._commands['umount'], self.secret_path])
                    else:
                        subprocess.call([self._commands['fusermount'],
                                         '-u', self.secret_path])
                    self.encfs_mounted = False
                    return True
        else:
            return False
