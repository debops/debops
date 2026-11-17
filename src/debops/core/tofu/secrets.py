# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from ..secrets import SecretStore


class TofuSecretStore(SecretStore):
    """The secret store of an OpenTofu infrastructure view.

    The view keeps its state files in the ``secret/`` directory next
    to its configuration, encrypted at rest with EncFS (the ciphertext
    in ``.encfs.secret/``) or through the repository-wide git-crypt.
    The OpenTofu-native state encryption carries the confidentiality
    of the state contents themselves; the store guards the key
    material and the unlock lifecycle.
    """

    def __init__(self, project, view, keys=None, encrypt=None):
        if project.project_type == 'legacy':
            root_path = os.path.join(project.path, 'tofu')
        else:
            root_path = os.path.join(project.path,
                                     'tofu',
                                     'views',
                                     view)

        super().__init__(project,
                         secret_path=os.path.join(root_path, 'secret'),
                         encfs_path=os.path.join(root_path,
                                                 '.encfs.secret'),
                         keys=keys, encrypt=encrypt)
