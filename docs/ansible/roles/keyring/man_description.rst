.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.keyring`` Ansible role is designed as a helper for other Ansible
roles that manages the APT keyring as well as the GPG keyrings on unprivileged
UNIX accounts. Other Ansible roles can tell the :ref:`debops.keyring` role
which GPG keys should be present or absent in the selected keyrings; the role
then retrieves the GPG keys either from:

- local key store in the :ref:`debops.keyring` role, or located in a directory
  on the Ansible Controller, or

- specified URL, or

- specified `Keybase`__ profile via the `Keybase API`__, or

  .. __: https://keybase.io/
  .. __: https://keybase.io/docs/api/1.0/call/user/pgp_keys.asc

- a default GPG keyserver, if defined


.. warning:: The role is not meant to be used via Ansible inventory to manage
   the APT or GPG keys; users can use the :ref:`debops.apt` role to manage the
   APT keyring via the inventory.

   At the moment there is no solution for unprivileged UNIX account keyrings
   manageable via the inventory. This functionality will be implemented later
   via other DebOps roles that manage UNIX accounts.
