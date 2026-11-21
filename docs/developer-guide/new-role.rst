.. Copyright (C) 2021 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Creating a new DebOps role
==========================

Historically, a new role was created by copying an existing role and doing an
initial search and replace. Which has the following problems:

- Which role is up to the latest standards and thus suitable for creating the next role?
- Requires manual work to setup a new role skeleton before work can be started (search and replace).
- For new contributers, this is even more difficult.
- The role standards are going to evolve thus the roles need to be updated.

DebOps uses `Copier`__ to help address those issues.

  .. __: https://copier.readthedocs.io/en/stable/

Setup
-----

- Install copier.
- Clone https://github.com/ypid/debops-template.git next to the DebOps monorepo (:file:`~/.local/share/debops/debops-template`).

Create a new rule
-----------------

To create a role called ``new_role``, in :file:`~/.local/share/debops/debops/ansible/roles` in the DebOps monorepo, run:

.. code-block:: shell

   copier -d "author_fullname=$(git config --get user.name)" -d "author_email=$(git config --get user.email)" copy ../../../debops-template/ new_role

And answer the questions.

Manual post tasks:

- The generated role has quite a bit of meat on the bone. Just remove the parts you don’t need.
- Search for ``TODO`` in the generated role skeleton and address them.
- Integrate the playbook so that it gets called. See how other roles are integrated in :file:`ansible/playbooks/` in the monorepo.
- Write the actual role ;-)

Update a role to the latest role standards
------------------------------------------

In :file:`ansible/roles/${my_role}`, run:

.. code-block:: shell

   copier --force
