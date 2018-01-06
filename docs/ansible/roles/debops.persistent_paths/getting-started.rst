Getting started
===============

.. include:: includes/role.rst

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

If the role is used as a dependency role, you as user of the main role do not
need to do anything with this role except from having it installed and using
the appropriate playbook provided by the main role.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.persistent_paths`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/persistent_paths.yml
   :language: yaml


Qubes OS
--------

The ``qubes-core-agent`` package needs to be installed in the TemplateVM which
is the default for the `official Debian templates <https://www.qubes-os.org/doc/templates/debian/>`_.

Note that currently you will need an unreleased version of bind-dirs.sh_ in place for
some roles which use ``debops.persistent_paths`` to work correctly (ref:
`bind-dirs: Create ro if bind target exists <https://github.com/QubesOS/qubes-core-agent-linux/pull/42>`_).

Refer to bind-dirs_ for more details and limitations.

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

``role::persistent_paths:qubes_os``
  Tasks related to Qubes OS.
