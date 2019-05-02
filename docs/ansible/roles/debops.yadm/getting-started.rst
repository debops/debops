Getting started
===============

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
