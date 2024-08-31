.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _cgit__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:

.. _cgit__ref_default_setup:

Default setup
-------------

If you don't change any configuration values, the role will setup a
web server (using the :ref:`debops.nginx` role) which will be accessible
via ``https://cgit.<your-domain>`` (or ``http://cgit.<your-domain>`` if
:ref:`debops.pki` is not enabled for the host).

Python packages to support markdown, syntax highlighting, etc, will also
be installed.

By default, :file:`/srv/git/public/` is scanned for repositories which will
be made available via the web interface (the location can be changed using
the :envvar:`cgit__git_dir` variable).


.. _cgit__ref_example_inventory:

Example inventory
-----------------

To install and configure cgit on a host, the host needs to be present in the
``[debops_service_cgit]`` Ansible inventory group.

.. code-block:: none

   [debops_all_hosts]
   cgit

   [debops_service_nginx]
   cgit

   [debops_service_cgit]
   cgit


.. _cgit__ref_example_playbook:

Example playbook
----------------

The following playbook can be used with DebOps. If you are using this role
without DebOps you might need to adapt it to make it work in your setup.

.. literalinclude:: ../../../../ansible/playbooks/service/cgit.yml
   :language: yaml
   :lines: 1,5-

This playbook is also shipped with DebOps as
:file:`ansible/playbooks/service/cgit.yml`.

.. _cgit__ref_ansible_tags:

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, e.g. when you are sure that most of
the configuration is already in the desired state.

Available role tags:

``role::cgit``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::cgit:pkg``
  Run tasks related to system package installation.

``role::cgit:config``
  Run tasks related to the cgit configuration.

``role::cgit:dir``
  Run tasks related to the directory structure holding public git repositories.
