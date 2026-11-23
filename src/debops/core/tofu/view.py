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

from .modules import module_entries, render_modules, \
    reconcile_modules
from .providers import provider_entries, render_providers, \
    reconcile_providers
from .registry import (render_template, view_drop_in_path,
                       view_tofu_options, view_tofu_root,
                       write_view_drop_in)
from .binary import known_version
from .plans import PLAN_DIR, PLAN_FILE_PREFIX, plan_file_names
from .runner import TofuRunner
from ..secrets import (passphrase_length, random_passphrase, unlocked_store)
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
    recorded = view_tofu_options(project, view)
    if 'providers' in recorded and 'modules' in recorded:
        # A view whose drop-in already exists is a broken tree: the
        # recorded sets are authoritative for the regenerated files
        providers = recorded['providers']
        modules = recorded['modules']
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
    with unlocked_store(store):
        length = passphrase_length(project)
        write_file(os.path.join(view_root, 'secret', 'environment'),
                   render_template('environment.j2', view_name=view,
                                   passphrase=random_passphrase(length))
                   + '\n',
                   project=project.path)

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
