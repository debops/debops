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
"""

import glob
import logging
import os
import pkgutil
import secrets as secrets_module
import string

import jinja2

from .secrets import TofuSecretStore
from ..utils import write_file

logger = logging.getLogger(__name__)

# The path of the templates relative to the DebOps package data
TEMPLATE_ROOT = os.path.join('_data', 'templates', 'projectdir', 'modern',
                             'tofu')


def _render_template(name, **context):
    """Render one of the tofu view templates shipped with DebOps."""
    template = jinja2.Template(
        pkgutil.get_data('debops', os.path.join(TEMPLATE_ROOT, name))
        .decode('utf-8'), trim_blocks=True)
    return template.render(**context)


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


def _provider_entries(providers):
    """Split the provider arguments into the template's entries.

    Each entry is a provider source address in the OpenTofu registry
    notation -- 'namespace/name', or 'hostname/namespace/name' --
    optionally with a version pin separated by '='. The local name of
    the provider is the last segment of the source address, which is
    how OpenTofu names the provider in the configuration.
    """
    entries = []
    for provider in providers:
        source, _, version = provider.partition('=')
        entries.append({'name': source.rsplit('/', 1)[-1],
                        'source': source,
                        'version': version})
    return entries


def view_tofu_root(project, view):
    """Return the root directory of a project's OpenTofu view."""
    if project.project_type == 'legacy':
        return os.path.join(project.path, 'tofu')
    return os.path.join(project.path, 'tofu', 'views', view)


def create_view(project, view, providers=None):
    """Create the OpenTofu view of a project when it does not exist.

    The view's tree is created from the template shipped with DebOps:
    the OpenTofu configuration with the local backend and the
    encryption stanza, the gitignore and gitattributes which route the
    store, the generated 'providers.tf' file with the selected
    providers and the store's '.env' file with the generated state
    passphrase. An existing view is left alone.

    The store type follows the project's convention: git-crypt when
    the repository is set up for it, EncFS when the Ansible views use
    it, a plain store otherwise. The resolved provider set is recorded
    in the view's configuration drop-in, which drives the generated
    'providers.tf' file from then on. Returns True when the view was
    created, False when it already existed.
    """
    view_root = view_tofu_root(project, view)

    if os.path.exists(os.path.join(view_root, 'main.tf')):
        return False

    encrypted_secrets = detect_store_type(project)
    context = {
        'view_name': view,
        'secret_name': 'secret',
        'encfs_prefix': '.encfs.',
        'encrypted_secrets': encrypted_secrets,
        'providers': _provider_entries(providers or []),
    }

    os.makedirs(os.path.join(view_root, 'secret'), exist_ok=True)
    write_file(os.path.join(view_root, 'main.tf'),
               _render_template('main.tf.j2', **context) + '\n',
               project=project.path)
    write_file(os.path.join(view_root, '.gitignore'),
               _render_template('gitignore.j2', **context) + '\n',
               project=project.path)
    write_file(os.path.join(view_root, '.gitattributes'),
               _render_template('gitattributes.j2', **context) + '\n',
               project=project.path)
    if context['providers']:
        write_file(os.path.join(view_root, 'providers.tf'),
                   _render_template('providers.tf.j2', **context) + '\n',
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


def view_drop_in_path(project, view):
    """Return the path of the view's OpenTofu configuration drop-in."""
    filename_view = view.replace('/', '-')
    return os.path.join(project.path, '.debops', 'conf.d',
                        'view-' + filename_view + '-tofu.toml')


def write_view_drop_in(project, view, providers):
    """Record the provider set of a view in its configuration drop-in.

    The drop-in declares the 'views.<view>.tofu.providers' option,
    which drives the generated 'providers.tf' file of the view. The
    option is merged into the live configuration of the project, so
    that the same process reads the recorded set without reloading it;
    a fresh process reads it through the ordinary configuration
    loading. An existing drop-in is replaced: the '--provider' options
    of the command line are the operator's explicit decision about the
    set.

    The option is replace-semantics: the recorded set is the whole
    provider list, not an addition to it. The configuration merge
    extends lists by design, so the recorded option is cleared from
    the live tree first and the merge lands as the replacement.
    """
    drop_in = view_drop_in_path(project, view)
    write_file(drop_in,
               _render_template('view-tofu.toml.j2', view_name=view,
                                providers=providers or []) + '\n',
               overwrite=True,
               project=project.path)
    try:
        del project.config.raw['views'][view]['tofu']['providers']
    except (KeyError, TypeError):
        pass
    project.config.merge({'views': {view: {'tofu': {'providers':
                                                    providers or []}}}},
                         scope='project', origin=drop_in)


def sync_providers(project, view):
    """Re-derive the generated 'providers.tf' file of an existing view.

    The file is owned by DebOps and derived from the
    'views.<view>.tofu.providers' option of the view's configuration
    drop-in: the file is regenerated whenever the recorded set differs
    from the set it was last written from, and removed when the set is
    empty. Each change is announced; user edits stay in 'main.tf'
    untouched. A view without a drop-in -- a hand-made one -- keeps
    its own provider requirements: the empty recorded set leaves the
    generated file alone.
    """
    view_root = view_tofu_root(project, view)
    providers_path = os.path.join(view_root, 'providers.tf')
    try:
        providers = project.config.raw['views'][view]['tofu']['providers']
    except (KeyError, TypeError):
        providers = []
    entries = _provider_entries(providers or [])

    if not entries:
        if os.path.exists(providers_path):
            os.remove(providers_path)
            logger.notice(
                'Removed the generated providers.tf of the view {!r} in '
                'project {!r}: the recorded provider set is empty'.format(
                    view, project.name),
                extra={'allow': ['stderr', 'syslog']})
        return

    expected = _render_template('providers.tf.j2', providers=entries) + '\n'
    if os.path.exists(providers_path):
        with open(providers_path) as existing:
            if existing.read() == expected:
                return
    write_file(providers_path, expected, overwrite=True,
               project=project.path)
    logger.notice(
        'Updated the generated providers.tf of the view {!r} in project '
        '{!r}: the provider set is now {}'.format(
            view, project.name,
            ', '.join('{}{}'.format(entry['source'],
                                    '=' + entry['version']
                                    if entry['version'] else '')
                      for entry in entries)),
        extra={'allow': ['stderr', 'syslog']})
