# Copyright (C) 2020-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import itertools
import logging
import os
import random
import stat
import string
import subprocess
import sys

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


class SecretStore:
    """One encrypted secret directory of a project.

    The store knows the mechanism its directory is encrypted with
    (EncFS or git-crypt) and whether the secrets are currently
    readable, and can unlock and lock them. The location of the
    directory is provided by the subclasses, which know the layout of
    the tool the secrets belong to.

    The :attr:`encrypted`, :attr:`decrypted` and :attr:`crypt_method`
    attributes reflect the state detected at construction time and
    updated by the unlock and lock operations.
    """

    def __init__(self, project, secret_path, encfs_path,
                 keys=None, encrypt=None):
        self.project = project
        self.secret_path = secret_path
        self.encfs_path = encfs_path
        self.keys = keys
        self.encrypt = encrypt

        self.encrypted = False
        self.crypt_method = ''

        self.encfs_keyfile = os.path.join(self.encfs_path, '.encfs6.keyfile')
        self.encfs_configfile = os.path.join(self.encfs_path, '.encfs6.xml')
        self.decrypted = False
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

        if os.path.exists(self.encfs_path):
            self.encrypted = True
            self.crypt_method = 'encfs'
            if os.path.ismount(self.secret_path):
                self.decrypted = True
        elif os.path.exists(self.git_crypt_path):
            self.encrypted = True
            self.crypt_method = 'git-crypt'
            if not self._git_crypt_locked():
                self.decrypted = True
        logger.debug('Secret store initialized at %s', self.secret_path)

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

    def _git_crypt_encrypted_changes(self):
        """Return the working tree changes on git-crypt encrypted paths.

        The change paths come from 'git status --porcelain'; the
        'git check-attr' filter lookup marks the paths which git-crypt
        encrypts. A commit made while the repository is locked stores
        such paths as plaintext, because the clean filter of a locked
        repository passes the content through unchanged.
        """
        status = subprocess.Popen(
            [self._commands['git'], 'status', '--porcelain'],
            cwd=self.project.path, stdout=subprocess.PIPE)
        out, err = status.communicate()
        if status.returncode != 0:
            return []
        paths = []
        for line in out.decode('utf-8', 'replace').splitlines():
            if len(line) < 4:
                continue
            path = line[3:].strip('"')
            if ' -> ' in path:
                # A rename records both sides; either may be encrypted
                old, new = path.split(' -> ', 1)
                paths.extend([old.strip('"'), new.strip('"')])
            else:
                paths.append(path)
        if not paths:
            return []
        check = subprocess.Popen(
            [self._commands['git'], 'check-attr', '--stdin', 'filter'],
            cwd=self.project.path, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        out, err = check.communicate('\n'.join(paths).encode('utf-8'))
        suffix = ': filter: git-crypt'
        encrypted = []
        for line in out.decode('utf-8', 'replace').splitlines():
            line = line.rstrip()
            if line.endswith(suffix):
                encrypted.append(line[:len(line) - len(suffix)])
        return encrypted

    def _get_random_string(self):
        all_chars = string.digits + string.ascii_letters + string.punctuation
        random_string = (''.join(random.choice(all_chars)
                         for i in range(64)))
        return random_string

    def encrypt_encfs(self):
        """Encrypt the secret directory using EncFS.

        A random EncFS password is generated and encrypted with GPG to
        the configured recipients; the volume configuration is encrypted
        alongside the contents. Used when a project or a view is created
        with encrypted secrets.
        """
        logger.debug('Preparing to encrypt secrets using EncFS')
        encfs_keyfile = os.path.join(self.encfs_path, '.encfs6.keyfile')
        encfs_configfile = os.path.join(self.encfs_path, '.encfs6.xml')
        encfs_password = self._get_random_string()

        try:
            gpg_keys = list(self.keys.split(','))
            gpg_recipients = list(
                    itertools.chain.from_iterable(['-r', r]
                                                  for r in gpg_keys))
        except AttributeError:
            logger.error('List of GPG recipients not specified',
                         extra={'allow': 'syslog'})
            raise ValueError('List of GPG recipients not specified')

        if not os.path.exists(self.encfs_path):
            logger.notice('Encrypting secrets using EncFS...',
                          extra={'allow': ['stderr', 'syslog']})
            os.makedirs(self.encfs_path)
            logger.debug('Encrypting EncFS keyfile')
            gpg_cmd = subprocess.Popen([self._commands['gpg'], '--encrypt', '--armor',
                                        '--output', encfs_keyfile] + gpg_recipients,
                                       stdin=subprocess.PIPE)
            gpg_cmd.communicate(encfs_password.encode('utf-8'))
            if (gpg_cmd.returncode != 0 or
                    not os.path.exists(encfs_keyfile)):
                raise ChildProcessError('GPG could not encrypt the '
                                        'EncFS keyfile')

            logger.debug('Creating EncFS filesystem')
            encfs_cmd = subprocess.Popen([
                self._commands['encfs'], self.encfs_path, self.secret_path,
                '--extpass',
                self._commands['gpg'] + ' --decrypt --no-mdc-warning --output - '
                + shquote(encfs_keyfile)],
                stdin=subprocess.PIPE)
            encfs_cmd.communicate(('p\n' + encfs_password).encode('utf-8'))
            if (encfs_cmd.returncode != 0 or
                    not os.path.exists(encfs_configfile)):
                raise ChildProcessError('EncFS did not create the '
                                        'volume configuration')

            # Set the store state to correctly lock the secrets
            self.encrypted = True
            self.crypt_method = 'encfs'
            if os.path.ismount(self.secret_path):
                self.decrypted = True
            self.lock()

            logger.debug('Encrypting EncFS configuration file')
            gpg_cmd = subprocess.Popen([self._commands['gpg'], '--encrypt', '--armor',
                                        '--output', encfs_configfile + '.asc']
                                       + gpg_recipients + [encfs_configfile])
            gpg_cmd.communicate()
            if (gpg_cmd.returncode != 0 or
                    not os.path.exists(encfs_configfile + '.asc')):
                raise ChildProcessError('GPG could not encrypt the '
                                        'volume configuration')
            os.remove(encfs_configfile)
            logger.debug('EncFS configuration complete')

    def unlock(self):
        if self.encrypted:
            logger.debug('Secrets are encrypted, unlocking')
            if self.crypt_method == 'encfs':
                logger.debug('Detected EncFS as encryption method')
                keyfile = os.path.join(self.encfs_path, self.encfs_keyfile)
                configfile = os.path.join(self.encfs_path, self.encfs_configfile)
                crypted_configfile = os.path.join(self.encfs_path,
                                                  self.encfs_configfile + '.asc')

                if os.path.ismount(self.secret_path):
                    self.decrypted = True
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

                    subprocess_env = self.project.environment()
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
                    encfs_failed = encfs.returncode != 0
                    os.remove(configfile)
                    if encfs_failed:
                        raise ChildProcessError('EncFS could not unlock '
                                                'the project secrets')
                    self.decrypted = True
                    logger.debug('EncFS filesystem mounted')
                    return True
            elif self.crypt_method == 'git-crypt':
                logger.debug('Detected git-crypt as encryption method')
                if self._git_crypt_locked():
                    try:
                        auto_commit = (self.project.config
                                       .raw['project']['git']['auto_commit'])
                    except KeyError:
                        # The configuration option might not exist at this time
                        auto_commit = None
                    if auto_commit:
                        encrypted_changes = (
                            self._git_crypt_encrypted_changes())
                        if encrypted_changes:
                            logger.error(
                                'Cannot commit the working tree '
                                'automatically: the repository is locked '
                                'and the changes touch git-crypt encrypted '
                                'paths ({}). A commit made while the '
                                'repository is locked stores the encrypted '
                                'files as plaintext. Clean the encrypted '
                                'paths from the working tree, unlock the '
                                'repository, and commit the changes while '
                                'the secrets are unlocked.'.format(
                                    ', '.join(encrypted_changes)),
                                extra={'allow': 'syslog'})
                            raise ChildProcessError(
                                'Cannot commit the working tree '
                                'automatically: the repository is locked '
                                'and the changes touch git-crypt encrypted '
                                'paths, which the commit would store as '
                                'plaintext')
                        self.project.commit()
                    logger.debug('Unlocking secrets using git-crypt')
                    gitcrypt_cmd = subprocess.Popen([self._commands['git-crypt'],
                                                     'unlock'],
                                                    stderr=subprocess.PIPE)
                    out, err = gitcrypt_cmd.communicate()
                    rc = gitcrypt_cmd.returncode
                    if rc == 0:
                        self.decrypted = True
                        logger.debug('Files encrypted with git-crypt are '
                                     'decrypted')
                        return True
                    else:
                        logger.error('Cannot unlock project secrets, '
                                     'git working directory not clean',
                                     extra={'allow': 'syslog'})
                        raise ChildProcessError('Cannot unlock project secrets, '
                                                'git working directory not clean')
                else:
                    self.decrypted = True
                    logger.debug('git-crypt is already unlocked')
                    return False

        else:
            parent_path = os.path.dirname(self.secret_path)
            if (os.path.exists(parent_path) and os.path.isdir(parent_path)):
                return False
            else:
                raise NotADirectoryError('Cannot find encrypted secrets '
                                         'at ' + parent_path)

    def lock(self):
        if self.encrypted:
            logger.debug('Secrets are encrypted, locking')
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
                    self.decrypted = False
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
                        self.decrypted = False
                        logger.debug('Encrypted files are locked')
                        return True
                    else:
                        logger.error('Cannot lock project secrets, '
                                     'git working directory not clean',
                                     extra={'allow': 'syslog'})
                        raise ChildProcessError('Cannot lock project secrets, '
                                                'git working directory not clean')

        else:
            parent_path = os.path.dirname(self.secret_path)
            if (os.path.exists(parent_path) and os.path.isdir(parent_path)):
                return False
            else:
                raise NotADirectoryError('Cannot find encrypted secrets '
                                         'at ' + parent_path)


class SecretManager:
    """Coordinate the secret stores of a project's tools.

    Each tool that keeps encrypted secrets in the project provides its
    own :class:`SecretStore` in its subpackage; the manager is the
    tool-agnostic entry point which resolves stores by name and can
    operate on one store or on all of them.

    Note that the lock state of a git-crypt store is shared by the
    whole repository: locking one git-crypt-backed store locks every
    git-crypt-encrypted path. EncFS-backed stores are independent.
    """

    def __init__(self, project, view=None):
        self._project = project
        self._view = view

    def _factories(self):
        # Imported lazily: the tool subpackages import this module for
        # the SecretStore base
        from .ansible.secrets import AnsibleSecretStore
        return {'ansible': AnsibleSecretStore}

    def store(self, name='ansible'):
        """Return the secret store of a tool, constructing it on demand."""
        return self._factories()[name](self._project, self._view)

    def unlock(self, name=None):
        """Unlock one secret store, or all of them when no name is given.

        Returns the list of results of the underlying unlock operations.
        """
        return [store.unlock() for store in self._select(name)]

    def lock(self, name=None):
        """Lock one secret store, or all of them when no name is given.

        Returns the list of results of the underlying lock operations.
        """
        return [store.lock() for store in self._select(name)]

    def _select(self, name):
        factories = self._factories()
        if name:
            names = [name]
        else:
            names = sorted(factories)
        return [factories[n](self._project, self._view) for n in names]
