# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The OpenTofu providers of a DebOps project view.

The provider requirements of a view are recorded in the
'views.<view>.tofu.providers' option of its configuration drop-in and
drive the generated 'providers.tf' file of the view, which the
reconcile keeps in step. Each entry is a provider source address in
the OpenTofu registry notation -- 'namespace/name', or
'hostname/namespace/name' for providers outside the public registry --
optionally with a version pin separated by '='.


The 'tofu.mkview.default_providers' read is not guarded: the package defaults
guarantee the table."""

import logging

from .registry import view_tofu_options, reconcile_managed_file, render_template

logger = logging.getLogger(__name__)


def resolve_providers(project, providers=None):
    """Return the provider set which a new view is created with.

    The '--provider' options of the command line replace the
    'tofu.default_providers' configuration option, which itself
    defaults to an empty list: a providerless view. The resolution
    applies when a view is created -- the 'tofu.default_providers'
    option is consulted only there; the provider set of an
    existing view lives in its configuration drop-in, which the
    user owns.
    """
    if providers:
        return providers
    return project.config.raw['tofu']['mkview']['default_providers']


def provider_entries(providers):
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


def render_providers(entries):
    """Render the content of the generated 'providers.tf' file."""
    return render_template('providers.tf.j2', providers=entries) + '\n'


def reconcile_providers(project, view, force=False, dry_run=False):
    """Reconcile the generated 'providers.tf' file of a view.

    The file is derived from the 'views.<view>.tofu.providers' option
    of the view's configuration drop-in, which the reconcile keeps in
    step with the recorded set. An empty recorded set removes the
    generated file.

    Returns the list of proposed changes; with 'dry_run' nothing is
    written. Raises ValueError on the user-owned conflict without
    'force'.
    """
    try:
        providers = view_tofu_options(project, view).get('providers')
    except (KeyError, TypeError):
        providers = []
    entries = provider_entries(providers or [])
    expected = render_providers(entries) if entries else None
    entries_repr = ', '.join(
        '{}{}'.format(entry['source'],
                      '=' + entry['version'] if entry['version'] else '')
        for entry in entries)
    return reconcile_managed_file(project, view, 'providers.tf', expected,
                                  set_name='provider set',
                                  entries_repr=entries_repr,
                                  force=force, dry_run=dry_run)
