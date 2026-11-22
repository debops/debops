# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from ..secrets import SecretStore
from .registry import view_tofu_root


class TofuSecretStore(SecretStore):
    """The secret store of an OpenTofu infrastructure view.

    The store guards the key material of the view and the unlock
    lifecycle: the OpenTofu-native state encryption carries the
    confidentiality of the state contents themselves. The state
    lives in the view's ``state/`` directory, tracked in git as
    native ciphertext; the ``secret/`` directory beside the view
    configuration holds the passphrase and the credentials,
    encrypted at rest with EncFS (the ciphertext in
    ``.encfs.secret/``) or through the repository-wide git-crypt.
    """

    def __init__(self, project, view, keys=None, encrypt=None):
        root_path = view_tofu_root(project, view)
        self._root = root_path

        super().__init__(project,
                         secret_path=os.path.join(root_path, 'secret'),
                         encfs_path=os.path.join(root_path,
                                                 '.encfs.secret'),
                         keys=keys, encrypt=encrypt)

    def unlock(self):
        """Unlock the store of the view, or report it absent.

        The project-wide store cycle ('debops env', the project
        unlock) cycles every registered store: a project which opted
        out of OpenTofu carries no view and no store, and the cycle
        must not demand one -- the unlock reports absence instead of
        the 'not found' refusal the generic store raises."""
        if not os.path.isdir(self._root):
            return False
        return super().unlock()

    def lock(self):
        """Lock the store of the view, or report it absent."""
        if not os.path.isdir(self._root):
            return False
        return super().lock()
