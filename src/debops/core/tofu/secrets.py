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

        super().__init__(project,
                         secret_path=os.path.join(root_path, 'secret'),
                         encfs_path=os.path.join(root_path,
                                                 '.encfs.secret'),
                         keys=keys, encrypt=encrypt)
