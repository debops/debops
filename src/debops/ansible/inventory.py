# Copyright (C) 2020-2021 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2021 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from debops.exceptions import NoDefaultViewException
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

    def __init__(self, project, name='system', *args, **kwargs):
        self.name = name
        self.project = project
        self.project_type = project.project_type
        self.args = args
        self.kwargs = kwargs

        if self.project_type == 'modern' and not self.name:
            raise NoDefaultViewException('No default view defined in DebOps '
                                         'configuration. Use "-V|--view" '
                                         'option to select one.')

        self.encrypted = False
        self.crypt_method = ''

        self.encfs_keyfile = '.encfs6.keyfile'
        self.encfs_configfile = '.encfs6.xml'
        self.encfs_mounted = False
        self.git_crypt_path = os.path.join(project.path, '.git', 'git-crypt',
                                           'keys')

        self._commands = {
            'gpg': project.config.raw['binaries']['gpg'],
            'encfs': project.config.raw['binaries']['encfs'],
            'git': project.config.raw['binaries']['git'],
            'git-crypt': project.config.raw['binaries']['git-crypt'],
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
        elif os.path.exists(self.git_crypt_path):
            self.encrypted = True
            self.crypt_method = 'git-crypt'
            if not self._git_crypt_locked():
                self.encfs_mounted = True
        logger.debug('Ansible inventory initialized')

    def _git_crypt_locked(self):
        """Detect if git-crypt is locked or not"""
        # Based on solution from https://github.com/AGWA/git-crypt/issues/69
        logger.debug('Checking git-crypt state')
        git_cmd = subprocess.Popen([self._commands['git'], 'config', '--local',
                                    '--get', 'filter.git-crypt.smudge'],
                                   stdout=subprocess.PIPE)
        out, err = git_cmd.communicate()
        if out:
            logger.debug('git-crypt is in unlocked state')
            return False
        else:
            logger.debug('git-crypt is in locked state')
            return True

    def _get_random_string(self):
        all_chars = string.digits + string.ascii_letters + string.punctuation
        random_string = (''.join(random.choice(all_chars)
                         for i in range(64)))
        return random_string

    def _encrypt_secrets_encfs(self):
        logger.debug('Preparing to encrypt secrets using EncFS')
        encfs_keyfile = os.path.join(self.encfs_path, '.encfs6.keyfile')
        encfs_configfile = os.path.join(self.encfs_path, '.encfs6.xml')
        encfs_password = self._get_random_string()

        try:
            gpg_keys = list(self.kwargs.get('keys', None).split(','))
            gpg_recipients = list(
                    itertools.chain.from_iterable(['-r', r]
                                                  for r in gpg_keys))
        except AttributeError:
            logger.error('List of GPG recipients not specified',
                         extra={'block': 'stderr'})
            raise ValueError('List of GPG recipients not specified')

        if not os.path.exists(self.encfs_path):
            print('Encrypting Ansible secrets using EncFS...')
            os.makedirs(self.encfs_path)
            logger.debug('Encrypting EncFS keyfile')
            gpg_cmd = subprocess.Popen([self._commands['gpg'], '--encrypt', '--armor',
                                        '--output', encfs_keyfile] + gpg_recipients,
                                       stdin=subprocess.PIPE)
            gpg_cmd.communicate(encfs_password.encode('utf-8'))
            while not os.path.exists(encfs_keyfile):
                time.sleep(1)

            logger.debug('Creating EncFS filesystem')
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

            logger.debug('Encrypting EncFS configuration file')
            gpg_cmd = subprocess.Popen([self._commands['gpg'], '--encrypt', '--armor',
                                        '--output', encfs_configfile + '.asc']
                                       + gpg_recipients + [encfs_configfile])
            while not os.path.exists(encfs_configfile + '.asc'):
                time.sleep(1)
            os.remove(encfs_configfile)
            logger.debug('EncFS configuration complete')

    def createdirs(self):
        skel_dirs = (
            os.path.join('inventory', 'group_vars', 'all'),
            os.path.join('inventory', 'host_vars'),
            os.path.join('playbooks', 'roles'),
            os.path.join('resources'),
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
                         extra={'block': 'stderr'})
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
            logger.debug('Default hosts file created in Ansible inventory')

        encrypted_secrets = self.kwargs.get('encrypt', None)
        if encrypted_secrets is not None:
            if encrypted_secrets == 'encfs':
                self._encrypt_secrets_encfs()
            elif encrypted_secrets == 'git-crypt':
                # git-crypt is handled at the root of the repository,
                # not in a specific inventory
                pass
        logger.debug('Ansible inventory created')

    def unlock(self):
        if self.encrypted:
            logger.debug('Ansible secrets are encrypted, unlocking')
            if self.crypt_method == 'encfs':
                logger.debug('Detected EncFS as encryption method')
                keyfile = os.path.join(self.encfs_path, self.encfs_keyfile)
                configfile = os.path.join(self.encfs_path, self.encfs_configfile)
                crypted_configfile = os.path.join(self.encfs_path,
                                                  self.encfs_configfile + '.asc')

                if os.path.ismount(self.secret_path):
                    self.encfs_mounted = True
                    logger.debug('EncFS filesystem is already mounted, '
                                 'state not changed')
                    return False
                else:
                    try:
                        if self.project.config.raw['project']['git']['auto_commit']:
                            self.project.commit()
                    except KeyError:
                        # The configuration option might not exist at this time
                        pass
                    if not os.path.isdir(self.secret_path):
                        os.makedirs(self.secret_path)

                    if not os.path.exists(configfile):
                        os.mkfifo(configfile)
                    elif not stat.S_ISFIFO(os.stat(configfile).st_mode):
                        raise IOError(17, configfile + ' exists but is not a fifo')

                    subprocess_env = os.environ.copy()
                    logger.debug('Decrypting and mounting EncFS filesystem')
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
                    logger.debug('EncFS filesystem mounted')
                    return True
            elif self.crypt_method == 'git-crypt':
                logger.debug('Detected git-crypt as encryption method')
                if self._git_crypt_locked():
                    try:
                        if self.project.config.raw['project']['git']['auto_commit']:
                            self.project.commit()
                    except KeyError:
                        # The configuration option might not exist at this time
                        pass
                    logger.debug('Unlocking secrets using git-crypt')
                    gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                     'unlock'],
                                                    stderr=subprocess.PIPE)
                    out, err = gitcrypt_cmd.communicate()
                    rc = gitcrypt_cmd.returncode
                    if rc == 0:
                        self.encfs_mounted = True
                        logger.debug('Files encrypted with git-crypt are '
                                     'decrypted')
                        return True
                    else:
                        logger.error('Cannot unlock project secrets, '
                                     'git working directory not clean',
                                     extra={'block': 'stderr'})
                        raise ChildProcessError('Cannot unlock project secrets, '
                                                'git working directory not clean')
                else:
                    self.encfs_mounted = True
                    logger.debug('git-crypt is already unlocked')
                    return False

        else:
            parent_path = os.path.dirname(self.path)
            if (os.path.exists(parent_path) and os.path.isdir(parent_path)):
                return False
            else:
                raise NotADirectoryError('Cannot find encrypted secrets '
                                         'at ' + parent_path)

    def lock(self):
        if self.encrypted:
            logger.debug('Ansible secrets are encrypted, locking')
            try:
                if self.project.config.raw['project']['git']['auto_commit']:
                    self.project.commit()
            except KeyError:
                # The configuration option might not exist at this time
                pass
            if self.crypt_method == 'encfs':
                logger.debug('Detected EncFS as encryption method')
                if os.path.ismount(self.secret_path):
                    logger.debug('EncFS filesystem is mounted, unmounting')
                    if sys.platform == 'darwin':
                        subprocess.call([self._commands['umount'], self.secret_path])
                    else:
                        subprocess.call([self._commands['fusermount'],
                                         '-u', self.secret_path])
                    self.encfs_mounted = False
                    logger.debug('EncFS filesystem has been unmounted')
                    return True
            elif self.crypt_method == 'git-crypt':
                logger.debug('Detected git-crypt as encryption method')
                if not self._git_crypt_locked():
                    logger.debug('Encrypted files are unlocked, locking')
                    gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                     'lock'],
                                                    stderr=subprocess.PIPE)
                    out, err = gitcrypt_cmd.communicate()
                    rc = gitcrypt_cmd.returncode
                    if rc == 0:
                        self.encfs_mounted = False
                        logger.debug('Encrypted files are locked')
                        return True
                    else:
                        logger.error('Cannot lock project secrets, '
                                     'git working directory not clean',
                                     extra={'block': 'stderr'})
                        raise ChildProcessError('Cannot lock project secrets, '
                                                'git working directory not clean')

        else:
            parent_path = os.path.dirname(self.path)
            if (os.path.exists(parent_path) and os.path.isdir(parent_path)):
                return False
            else:
                raise NotADirectoryError('Cannot find encrypted secrets '
                                         'at ' + parent_path)
