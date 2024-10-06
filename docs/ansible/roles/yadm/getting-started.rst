.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default dotfiles
----------------

The role does not clone any dotfile :command:`git` repositories defined in the
:ref:`yadm__ref_dotfiles` variables by default. To enable this you should set
in the inventory:

.. code-block:: yaml

   yadm__dotfiles_enabled: True

Without this, users still are able to use :command:`yadm` to install their own
preferred dotfiles, and role ensures that commonly used CLI shells are present
so that users are able to login if they use, for example, :command:`/bin/zsh`
as a shell defined in the LDAP directory.

The role exposes the ``ansible_local.yadm.dotfiles`` Ansible local fact, which
defines an absolute path to a default dotfiles repository mirrored locally.
Other Ansible roles can use it to install a default set of dotfiles using
:command:`yadm` on the users' account. If installation of dotfiles is disabled,
or the specified repository is not present, the variable will be empty.


Unsafe Repository error handling
--------------------------------

Due to the `CVE-2022-24765`__ :command:`git` security vulnerability, UNIX
accounts cannot clone local :command:`git` repositories that are not owned by
themselves. This causes issues with the :command:`yadm` repositories managed by
the ``root`` UNIX account via the role. To mitigate that, other Ansible roles
that want to utilize the dotfiles installed by the :ref:`debops.yadm` role need
to add the respective :command:`git` repositories as "safe" in the user's
:file:`~/.gitconfig` configuration file. The :ref:`debops.system_users` and
:ref:`debops.users` Ansible roles already contain the needed tasks and can be
used as examples to follow.

.. __: https://github.blog/open-source/git/git-security-vulnerability-announced/#cve-2022-24765


Example inventory
-----------------

The role is included by default in the ``bootstrap-ldap.yml`` and the
``common.yml`` playbook, therefore you don't need to do anything to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.yadm`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/yadm.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::yadm``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.yadm`` Ansible role:

- Manual pages: :man:`yadm(1)`

- The `yadm homepage`__ with documentation and examples

  .. __: https://yadm.io/

- An `unofficial guide to dotfiles on GitHub`__

  .. __: https://dotfiles.github.io/

- `A curated list of dotfiles resources`__

  .. __: https://github.com/webpro/awesome-dotfiles
