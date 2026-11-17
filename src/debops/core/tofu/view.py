# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu view of a DebOps project directory.

The :command:`debops tofu` wrapper creates a view's ``tofu/`` tree
lazily: the first command in a project without the tree applies the
template, announces what it created and proceeds. The template carries
the local backend whose state files live in the view's encrypted
store, the OpenTofu-native state and plan encryption and the provider
requirements selected through the configuration or the command line.

The registry-addressed dependencies of the view are managed by the
shared engine in :mod:`debops.core.tofu.registry`; this module carries
the view's orchestration: the tree creation and the secret-store
wiring.
"""

import glob
import logging
import os
import secrets as secrets_module
import string

from .providers import provider_entries, render_providers, \
    reconcile_providers
from .registry import render_template, view_drop_in_path, view_tofu_root, \
    write_view_drop_in
from .secrets import TofuSecretStore
from ..utils import write_file

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


def _random_passphrase():
    """Return a random state passphrase, generated from the system's
    random source."""
    alphabet = string.digits + string.ascii_letters + string.punctuation
    return ''.join(secrets_module.choice(alphabet) for _ in range(64))


def create_view(project, view, providers=None):
    """Create the OpenTofu view of a project when it does not exist.

    The view's tree is created from the template shipped with DebOps:
    the OpenTofu configuration with the local backend and the
    encryption stanza, the gitignore and gitattributes which route
    the store, the generated 'providers.tf' file with the selected
    providers and the store's '.env' file with the generated state
    passphrase. An existing view is left alone.

    The store type follows the project's convention: git-crypt when
    the repository is set up for it, EncFS when the Ansible views use
    it, a plain store otherwise. The resolved provider set is recorded
    in the view's configuration drop-in, which drives the generated
    'providers.tf' file from then on. A view whose tree is broken --
    'main.tf' deleted but the drop-in present -- keeps its recorded
    provider set: the drop-in is the user's decision, repair does not
    rewrite it. Returns True when the view was created, False when it
    already existed.
    """
    view_root = view_tofu_root(project, view)

    if os.path.exists(os.path.join(view_root, 'main.tf')):
        return False

    # A view whose drop-in already exists is a broken tree: the
    # recorded provider set is authoritative for the regenerated files
    try:
        providers = project.config.raw['views'][view]['tofu']['providers']
    except (KeyError, TypeError):
        pass
    encrypted_secrets = detect_store_type(project)
    entries = provider_entries(providers or [])
    context = {
        'view_name': view,
        'secret_name': 'secret',
        'encfs_prefix': '.encfs.',
        'encrypted_secrets': encrypted_secrets,
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
    if entries:
        write_file(os.path.join(view_root, 'providers.tf'),
                   render_providers(entries),
                   project=project.path)

    write_view_drop_in(project, view, providers or [])

    env_path = os.path.join(view_root, 'secret', '.env')
    write_file(env_path,
               'TF_VAR_state_passphrase={}\n'.format(
                   _random_passphrase()),
               project=project.path)

    if encrypted_secrets == 'encfs':
        TofuSecretStore(project, view, keys=project.keys,
                        encrypt='encfs').encrypt_encfs()

    if encrypted_secrets == 'git-crypt':
        logger.notice(
            'Created the OpenTofu view {!r} in project {!r}; the state '
            'store is encrypted with git-crypt'.format(view, project.name),
            extra={'allow': ['stderr', 'syslog']})
    elif encrypted_secrets == 'encfs':
        logger.notice(
            'Created the OpenTofu view {!r} in project {!r}; the state '
            'store is encrypted with EncFS'.format(view, project.name),
            extra={'allow': ['stderr', 'syslog']})
    else:
        logger.notice(
            'Created the OpenTofu view {!r} in project {!r}; the state '
            'store is not encrypted -- the state is protected by the '
            'OpenTofu-native encryption, and the store can be encrypted '
            'later through the project encryption flow'.format(
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
    provider requirements entirely: the reconcile leaves all of its
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
                'provider requirements; DebOps does not touch its '
                'files'.format(view, project.name),
                extra={'allow': ['stderr', 'syslog']})
        return []

    return reconcile_providers(project, view, force=force,
                               dry_run=dry_run)
