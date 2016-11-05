Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:

Initial configuration
---------------------

By default :command:`git` is used as VCS. This can be changed by the inventory
variables :envvar:`etckeeper__vcs`.

Example inventory
-----------------

.. code-block:: YAML

   ## If you don’t what to track hashed passwords.
   etckeeper__gitignore_group:
     - 'shadow'
     - 'shadow-'

In Ansible's inventory.

Example playbook
----------------

Here's an example playbook that uses the ``debops-contrib.etckeeper`` role:

.. literalinclude:: playbooks/etckeeper.yml
   :language: yaml

This playbooks is shipped with this role under
:file:`./docs/playbooks/etckeeper.yml` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::etckeeper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::etckeeper:vcs_config``
  Run tasks related to configuring VCS options.
