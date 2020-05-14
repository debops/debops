.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


.. _journald__ref_fss:

Forward Secure Sealing
----------------------

When the persistent logs are enabled, the :ref:`debops.journald` role
configures Forward Secure Sealing functionality of the Journal by default. The
verification keys are saved in the :file:`secret/journald/fss/` directories on
the Ansible Controller. The role can be used in an "alternative" mode where
Ansible checks the log integrity by running the command:

.. code-block:: console

   debops service/journald --tags role::journald:fss:verify

With this tag, only the task that verifies the logs will be executed.


Example inventory
-----------------

The ``debops.journald`` role is included by default in the ``common.yml``
DebOps playbook; you don't need to add hosts to any Ansible groups to enable
it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.journald`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/journald.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::journald``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::journald:fss:verify``
  The role can be used with this tag to use the Forward Secure Sealing
  funtionality to verify the consistency of the logs stored on the host(s).
  No other tasks will be performed when this tag is used.
