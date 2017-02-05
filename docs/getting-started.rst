Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To manage persistence of paths on a TemplateBasedVM it should be included in the
``debops_service_persistent_paths`` Ansible inventory group:

.. code:: ini

   [debops_service_persistent_paths]
   hostname

The role can also run against a TemplateVM to prepare paths which will then be
persistent in AppVMs based on the TemplateVM.

If the role is used as a dependency role, you as a user of the main role do not
need to do anything with this role except from having it installed.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.persistent_paths`` role:

.. literalinclude:: playbooks/persistent_paths.yml
   :language: yaml

The playbook is shipped with this role under
:file:`./docs/playbooks/persistent_paths.yml` from which you can symlink it to your
playbook directory.

Requirements
------------


Qubes OS
~~~~~~~~

The ``qubes-core-agent`` package needs to be installed in the TemplateVM which
is the default for the `official Debian templates <https://www.qubes-os.org/doc/templates/debian/>`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::persistent_paths``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
