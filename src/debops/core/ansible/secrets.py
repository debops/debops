# Copyright (C) 2020-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from ..secrets import SecretStore


class AnsibleSecretStore(SecretStore):
    """The secret store of an Ansible infrastructure view.

    Each view keeps its secrets in the ``secret/`` directory next to
    its inventory, encrypted at rest with EncFS (the ciphertext in
    ``.encfs.secret/``) or through the repository-wide git-crypt.
    """

    def __init__(self, project, view, keys=None, encrypt=None):
        if project.project_type == 'legacy':
            root_path = os.path.join(project.path, 'ansible')
        else:
            root_path = os.path.join(project.path,
                                     'ansible',
                                     'views',
                                     view)

        super().__init__(project,
                         secret_path=os.path.join(root_path, 'secret'),
                         encfs_path=os.path.join(root_path, '.encfs.secret'),
                         keys=keys, encrypt=encrypt)
