# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu view of a DebOps project directory.

The :command:`debops tofu mkview` command creates a view's ``tofu/``
tree: the template carries the local backend whose state lives in the
view's ``state/`` directory -- encrypted at rest by OpenTofu itself
and tracked in git as ciphertext -- the OpenTofu-native state and
plan encryption, and the dependencies selected through the
configuration or the command line. The store carries the key material:
the ``environment`` file with the state passphrase, written through
the store-cycling window and encrypted by the store when one exists.

The registry-addressed dependencies of the view are managed by the
shared engine in :mod:`debops.core.tofu.registry`; this module carries
the view's orchestration: the tree creation and the secret-store
wiring.
"""

import glob
import logging
import os
import re
import secrets as secrets_module
import string

from .modules import module_entries, render_modules, \
    reconcile_modules
from .providers import provider_entries, render_providers, \
    reconcile_providers
from .registry import render_template, view_drop_in_path, view_tofu_root, \
    write_view_drop_in
from .binary import known_version
from .plans import PLAN_DIR, PLAN_FILE_PREFIX, plan_file_names
from .runner import TofuRunner
from .secrets import TofuSecretStore
from ..utils import write_file
import dotenv

logger = logging.getLogger(__name__)


def detect_store_type(project):
    """Return the store type which the project's convention selects.

    The convention is detected from the state the project already
    carries: a repository-wide git-crypt setup wins, then the EncFS
    marker of the Ansible views. A project with no encrypted store yet
    keeps the tofu store plain -- the state stays protected by the
    OpenTofu-native encryption, and the announcement names the
    upgrade path. Initializing git-crypt here would need GPG
    recipients the wrapper does not know.
    """
    if os.path.exists(os.path.join(project.path, '.git', 'git-crypt',
                                   'keys')):
        return 'git-crypt'
    if glob.glob(os.path.join(project.path, 'ansible', 'views', '*',
                              '.encfs.secret')):
        return 'encfs'
    return None


def _random_passphrase(length):
    """Return a random state passphrase of the given length, drawn
    from the URL-safe alphabet: the environment file carries the
    passphrase without quoting, so the alphabet stays free of the
    characters the file format would have to escape."""
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets_module.choice(alphabet) for _ in range(length))


def create_view(project, view, providers=None, modules=None,
                encrypt=None, keys=None):
    """Create the OpenTofu view of a project: the view tree from the
    templates, the configuration drop-in with the recorded dependency
    sets, and the store with its 'environment' key file written
    through the store-cycling window.

    The store type is detection-driven: the project's detected
    mechanism is the default, and the '--encrypt' decision of
    'debops tofu mkview' is required only when the project carries
    no secret store yet. A git-crypt store is repository-wide -- the
    keys are global, the new view joins it for free; an EncFS store
    is a per-view volume -- every creation needs the GPG recipients
    ('keys') which encrypt the volume keyfile. The 'plain' choice is
    the explicit insecure decision: the key file tracked
    unencrypted, announced as such; it is refused when the project
    already carries a store, because the routing or the volume would
    encrypt the view's secrets anyway.

    An existing view is refused: its files are the user's. Returns
    True when the view was created.
    """
    if not re.match(r'^[A-Za-z0-9][A-Za-z0-9_]*$', view or ''):
        raise ValueError(
            'The view name can carry only letters, digits and '
            'underscores, and must not start with an underscore: '
            + str(view))

    view_root = view_tofu_root(project, view)

    if os.path.exists(os.path.join(view_root, 'main.tf')):
        raise ValueError(
            "The view {!r} already exists in the project; its files "
            'belong to the user'.format(view))

    detected = detect_store_type(project)
    if encrypt is None:
        if detected is None:
            raise ValueError(
                "The '--encrypt' option is required: the project "
                'carries no secret store yet -- the choices are '
                "'encfs', 'git-crypt' and 'plain'")
        encrypt = detected
    if detected is not None:
        if encrypt == 'plain':
            raise ValueError(
                'The project already carries a {!r} store: '
                "'plain' is not a choice for its views".format(
                    detected))
        if encrypt != detected:
            raise ValueError(
                'The project already carries a {!r} store: the '
                "'--encrypt {}' value contradicts it".format(
                    detected, encrypt))

    if encrypt == 'git-crypt' and not os.path.exists(
            os.path.join(project.path, '.git', 'git-crypt', 'keys')):
        logger.error(
            'The repository has no git-crypt setup. Creating a view '
            'cannot initialize repository-wide encryption; use '
            "'debops project init --encrypt git-crypt' on a new "
            'project instead.',
            extra={'allow': 'syslog'})
        raise ValueError(
            'Cannot encrypt the view: the repository is not set up '
            'for git-crypt')

    if encrypt == 'encfs' and not keys:
        raise ValueError(
            'The EncFS encryption requires the GPG recipients which '
            "encrypt the volume keyfile: pass '--keys'")

    # A view whose drop-in already exists is a broken tree: the
    # recorded sets are authoritative for the regenerated files
    try:
        recorded = project.config.raw['views'][view]['tofu']
        providers = recorded['providers']
        modules = recorded['modules']
    except (KeyError, TypeError):
        pass
    encrypted_secrets = encrypt
    provider_entries_list = provider_entries(providers or [])
    module_entries_list = module_entries(modules or {})
    context = {
        'view_name': view,
        'secret_name': 'secret',
        'encfs_prefix': '.encfs.',
        'encrypted_secrets': encrypted_secrets,
        'tofu_version': known_version(project),
    }

    os.makedirs(os.path.join(view_root, 'secret'), exist_ok=True)
    write_file(os.path.join(view_root, 'main.tf'),
               render_template('main.tf.j2', **context) + '\n',
               project=project.path)
    write_file(os.path.join(view_root, '.gitignore'),
               render_template('gitignore.j2', **context) + '\n',
               project=project.path)
    write_file(os.path.join(view_root, '.gitattributes'),
               render_template('gitattributes.j2', **context) + '\n',
               project=project.path)
    if provider_entries_list:
        write_file(os.path.join(view_root, 'providers.tf'),
                   render_providers(provider_entries_list),
                   project=project.path)
    if module_entries_list:
        write_file(os.path.join(view_root, 'modules.tf'),
                   render_modules(module_entries_list),
                   project=project.path)

    write_view_drop_in(project, view, providers or [], modules or [],
                       binary_version=known_version(project))

    store = TofuSecretStore(project, view, keys=keys, encrypt=encrypt)
    if encrypt == 'encfs':
        store.encrypt_encfs()

    # The key material of the view, written through the store-cycling
    # window: the EncFS volume mounts on the unlock, the git-crypt
    # store unlocks when the repository is locked, the plain store
    # passes through
    unlocked = store.unlock()
    try:
        try:
            length = project.config.raw['tofu']['mkview']['secret'][
                'passphrase_length']
        except (KeyError, TypeError):
            length = 32
        write_file(os.path.join(view_root, 'secret', 'environment'),
                   render_template('environment.j2', view_name=view,
                                   passphrase=_random_passphrase(length))
                   + '\n',
                   project=project.path)
    finally:
        if unlocked:
            store.lock()

    if encrypted_secrets == 'git-crypt':
        logger.notice(
            'Created the OpenTofu view {!r} in project {!r}; the '
            'environment file with the state passphrase is tracked '
            'behind the git-crypt store'.format(view, project.name),
            extra={'allow': ['stderr', 'syslog']})
    elif encrypted_secrets == 'encfs':
        logger.notice(
            'Created the OpenTofu view {!r} in project {!r}; the '
            'environment file with the state passphrase is tracked '
            'behind the EncFS store'.format(view, project.name),
            extra={'allow': ['stderr', 'syslog']})
    else:
        logger.warning(
            'Created the OpenTofu view {!r} in project {!r}; the store '
            'is not encrypted: the environment file with the state '
            'passphrase is tracked in plaintext -- initialize the '
            'store through the project encryption flow'.format(
                view, project.name),
            extra={'allow': ['stderr', 'syslog']})

    return True


def reconcile_view(project, view, force=False, dry_run=False):
    """Reconcile the files DebOps owns in an existing view.

    The generated files of the view are DebOps-owned: they carry the
    'Generated by DebOps' marker and are re-derived from the recorded
    options of the view's configuration drop-in. A generated file
    without the marker is user-owned: the reconcile refuses to touch
    it -- the recorded set is inert until the user removes their file
    or passes '--force' to hand the management back to DebOps.

    A view without a drop-in -- a hand-made one -- manages its own
    dependency requirements entirely: the reconcile leaves all of its
    files alone and announces it.

    Returns the list of proposed changes; with 'dry_run' nothing is
    written. Raises ValueError on the user-owned conflict without
    'force'.
    """
    view_root = view_tofu_root(project, view)
    drop_in = view_drop_in_path(project, view)

    if not os.path.exists(drop_in):
        if os.path.exists(os.path.join(view_root, 'main.tf')):
            logger.notice(
                'The view {!r} in project {!r} manages its own OpenTofu '
                'dependency requirements; DebOps does not touch its '
                'files'.format(view, project.name),
                extra={'allow': ['stderr', 'syslog']})
        return []

    return reconcile_providers(project, view, force=force,
                               dry_run=dry_run) + reconcile_modules(
        project, view, force=force, dry_run=dry_run)


# The rekey surgery: the encryption block of the view is rewritten
# per rotation phase. The fallback key provider inherits the label
# the state envelope's metadata references -- the decryption looks
# the provider up by that label, a renamed fallback finds no
# metadata and the state reads as keyless -- and the new primary
# takes the next generation label: 'state' rotates to 'state-2',
# 'state-2' to 'state-3'.

REKEY_ENCRYPTION_ROTATED = """  encryption {{
    key_provider "pbkdf2" "{fallback}" {{
      passphrase = var.old_state_passphrase
    }}

    method "aes_gcm" "{fallback}" {{
      keys = key_provider.pbkdf2.{fallback}
    }}

    key_provider "pbkdf2" "{primary}" {{
      passphrase = var.state_passphrase
    }}

    method "aes_gcm" "{primary}" {{
      keys = key_provider.pbkdf2.{primary}
    }}

    state {{
      method   = method.aes_gcm.{primary}
      fallback {{
        method = method.aes_gcm.{fallback}
      }}
      enforced = true
    }}

    plan {{
      method = method.aes_gcm.{primary}
    }}
  }}
"""

REKEY_ENCRYPTION_CLEAN = """  encryption {{
    key_provider "pbkdf2" "{primary}" {{
      passphrase = var.state_passphrase
    }}

    method "aes_gcm" "{primary}" {{
      keys = key_provider.pbkdf2.{primary}
    }}

    state {{
      method   = method.aes_gcm.{primary}
      enforced = true
    }}

    plan {{
      method = method.aes_gcm.{primary}
    }}
  }}
"""

REKEY_OLD_STATE_VAR = """
variable "old_state_passphrase" {
  type      = string
  sensitive = true
}
"""


def _encryption_block(main_tf):
    """The encryption block of the view configuration: from the
    'encryption {' line to its matching closing brace, None when the
    configuration carries none."""
    lines = main_tf.splitlines(keepends=True)
    start = None
    depth = 0
    for index, line in enumerate(lines):
        if start is None:
            if line.strip() == 'encryption {':
                start = index
                depth = line.count('{') - line.count('}')
            continue
        depth += line.count('{') - line.count('}')
        if depth == 0:
            return ''.join(lines[start:index + 1])
    return None


def _primary_label(block):
    """The label of the key provider the state stanza encrypts
    with: the first method reference in the encryption block, the
    state stanza's."""
    match = re.search(r'method\s*=\s*method\.aes_gcm\.([A-Za-z0-9_-]+)',
                      block)
    if match is None:
        raise ValueError(
            'The encryption block of the view carries no state '
            'encryption method: the rekey cannot rotate it')
    return match.group(1)


def _fallback_label(block):
    """The label of the fallback key provider, None when the block
    carries no fallback -- the shape of a view which is not mid-
    rotation."""
    match = re.search(r'fallback \{[^}]*method\s*=\s*method\.aes_gcm\.'
                      r'([A-Za-z0-9_-]+)', block)
    return match.group(1) if match else None


def _next_primary_label(label):
    """The label of the key provider the rotated state encrypts
    under: the next generation of the current one."""
    stem, separator, generation = label.rpartition('-')
    if separator and generation.isdigit():
        return stem + '-' + str(int(generation) + 1)
    return label + '-2'


def _rekey_env_path(view_root):
    """The environment file of the view's store."""
    return os.path.join(view_root, 'secret', 'environment')


def _rekey_env_value(view_root, key):
    """One TF_VAR_* value of the environment file, None when the key
    is not there."""
    path = _rekey_env_path(view_root)
    if not os.path.exists(path):
        return None
    values = dotenv.dotenv_values(path, interpolate=False)
    return values.get(key)


def _rekey_env_write(project, view_root, passphrase,
                     old_passphrase=None):
    """Rewrite the 'TF_VAR_state_passphrase' line of the environment
    file, carrying or dropping the old-passphrase marker; the user's
    own keys in the file are preserved line-for-line."""
    path = _rekey_env_path(view_root)
    with open(path) as handle:
        lines = handle.read().splitlines()
    kept = [line for line in lines
            if not line.startswith('TF_VAR_state_passphrase=')
            and not line.startswith('TF_VAR_old_state_passphrase=')]
    kept.append('TF_VAR_state_passphrase=' + passphrase)
    if old_passphrase is not None:
        kept.append('TF_VAR_old_state_passphrase=' + old_passphrase)
    write_file(path, '\n'.join(kept) + '\n', overwrite=True,
               project=project.path)


def rekey_view(project, view, workspace=None):
    """Rotate the state passphrase of a view.

    The rotation uses OpenTofu's encryption fallback, the mechanism
    the state migration exercised: the key provider the state
    envelope references becomes the fallback -- its label is
    inherited, the envelope's metadata is looked up by it -- and
    the new primary takes the next generation label. The refresh
    re-encrypts the state under the new primary, the verification
    plan reads the state with the new passphrase alone, and the
    cleanup removes the fallback and the old variable. Every
    interruption short of the final cleanup leaves a recoverable
    state -- a re-run resumes by the markers, the fallback block in
    the encryption stanza and the old-passphrase variable in the
    environment file. The encryption block is rewritten per phase:
    hand-modifications inside it do not survive the rotation.

    The saved plan files are removed and announced: they are
    encrypted under the retired key and the plan stanza carries no
    fallback. The named workspaces carry separate state files and
    need a rekey each. Returns True when the rotation completed.
    """
    view_root = view_tofu_root(project, view)
    main_tf_path = os.path.join(view_root, 'main.tf')
    with open(main_tf_path) as handle:
        main_tf = handle.read()

    block = _encryption_block(main_tf)
    if block is None:
        raise ValueError(
            'The view configuration of {!r} carries no encryption '
            'block: the rekey cannot rotate it'.format(view))
    primary = _primary_label(block)
    fallback = _fallback_label(block)
    resuming = (fallback is not None
                or _rekey_env_value(
                    view_root, 'TF_VAR_old_state_passphrase')
                is not None)

    store = TofuSecretStore(project, view)
    unlocked = store.unlock()
    try:
        old_passphrase = _rekey_env_value(
            view_root, 'TF_VAR_old_state_passphrase')
        new_passphrase = _rekey_env_value(
            view_root, 'TF_VAR_state_passphrase')
        if old_passphrase is None:
            # A fresh rotation: the old passphrase is the current one
            if new_passphrase is None:
                raise ValueError(
                    "The environment file of the view {!r} carries "
                    "no 'TF_VAR_state_passphrase': the state "
                    'encryption cannot be rotated'.format(view))
            old_passphrase = new_passphrase
            try:
                length = project.config.raw['tofu']['mkview']['secret'][
                    'passphrase_length']
            except (KeyError, TypeError):
                length = 32
            new_passphrase = _random_passphrase(length)

        # The environment carries the new primary and the old
        # fallback for as long as the rotation runs
        _rekey_env_write(project, view_root, new_passphrase,
                         old_passphrase)
    finally:
        if unlocked:
            store.lock()

    # The rotation phase: the fallback inherits the label the state
    # envelope references, the new primary takes the next generation
    next_primary = _next_primary_label(primary)
    main_tf = main_tf.replace(
        block,
        REKEY_ENCRYPTION_ROTATED.format(fallback=primary,
                                        primary=next_primary))
    if REKEY_OLD_STATE_VAR not in main_tf:
        state_var = ('variable "state_passphrase" {\n'
                     '  type      = string\n  sensitive = true\n}')
        main_tf = main_tf.replace(
            state_var, state_var + REKEY_OLD_STATE_VAR)
    write_file(main_tf_path, main_tf, overwrite=True,
               project=project.path)

    # The re-encryption: the state reads through the fallback, writes
    # under the new primary
    runner = TofuRunner(project, ['refresh'], workspace=workspace)
    rc = runner.execute()
    if rc != 0:
        raise ChildProcessError(
            "The 'tofu refresh' operation of the view {!r} failed "
            'with exit code {}: the state is not re-encrypted, the '
            'fallback is in place and the rotation can be '
            're-run'.format(view, rc))

    # The cleanup phase: the block without the fallback, the old
    # variable out of the configuration -- the old passphrase stays
    # in the environment until the verification passes
    with open(main_tf_path) as handle:
        main_tf = handle.read()
    block = _encryption_block(main_tf)
    main_tf = main_tf.replace(
        block, REKEY_ENCRYPTION_CLEAN.format(primary=next_primary))
    main_tf = main_tf.replace(REKEY_OLD_STATE_VAR, '')
    write_file(main_tf_path, main_tf, overwrite=True,
               project=project.path)

    # The verification: the state reads with the new passphrase alone
    verification_error = None
    try:
        runner = TofuRunner(project, ['plan'], workspace=workspace)
        rc = runner.execute()
        verification_error = None if rc == 0 else 'exit code {}'.format(rc)
    except (ChildProcessError, ValueError) as errmsg:
        verification_error = str(errmsg)
    if verification_error is not None:
        # The verification failed: the rotation phase goes back in,
        # the state stays readable through the fallback
        with open(main_tf_path) as handle:
            main_tf = handle.read()
        block = _encryption_block(main_tf)
        main_tf = main_tf.replace(
            block,
            REKEY_ENCRYPTION_ROTATED.format(fallback=primary,
                                            primary=next_primary))
        if REKEY_OLD_STATE_VAR not in main_tf:
            state_var = ('variable "state_passphrase" {\n'
                         '  type      = string\n  sensitive = true\n}')
            main_tf = main_tf.replace(
                state_var, state_var + REKEY_OLD_STATE_VAR)
            write_file(main_tf_path, main_tf, overwrite=True,
                       project=project.path)
        raise ChildProcessError(
            "The verification plan of the view {!r} failed ({}): "
            'the rotation phase is back in place, the old passphrase '
            'is still in the environment file -- investigate before '
            'the cleanup runs.'.format(view, verification_error))

    # The cleanup: the old variable out of the environment, the
    # old-key plan files removed
    _rekey_env_write(project, view_root, new_passphrase)
    removed = []
    for name in plan_file_names(view_root):
        if name.startswith(PLAN_FILE_PREFIX):
            os.remove(os.path.join(view_root, PLAN_DIR, name))
            removed.append(os.path.join(PLAN_DIR, name))
    for path in removed:
        logger.notice(
            "Removed the plan file '{}' of the view {!r}: the plan "
            'is encrypted under the retired '
            'passphrase'.format(path, view),
            extra={'allow': ['stderr', 'syslog']})

    logger.notice(
        'The state passphrase of the view {!r} in project {!r} is '
        'rotated: the state reads with the new passphrase, the '
        'fallback is removed'.format(view, project.name),
        extra={'allow': ['stderr', 'syslog']})
    return True
