.. Copyright (C) 2015-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Initial configuration
---------------------

By default the ``debops.controller`` role will install the DebOps playbooks and roles
from GitHub in the background, using either the ``batch`` command from the ``at``
package, or if the former is not available, ``async`` Ansible task. Keep in mind
that downloading all of the repositories might take a while and the code won't be
available for some time after initial Ansible playbook run.

If you cannot accept this behaviour you can set
:envvar:`controller__update_method` to ``sync``. This will make the roles and
playbooks immediately available after the task is run. However, this will
introduce a significant delay in every playbook run even when no upstream
changes will be found. You should only choose this if you plan to run
``debops`` from the same playbook where you also include the
``debops.controller`` role, e. g. when provisioning a new DebOps environment.

Example inventory
-----------------

To install DebOps on a remote host, you need to add it to
the ``[debops_service_controller]`` Ansible host group:

.. code-block:: none

    [debops_service_controller]
    hostname

Example playbook
----------------

Here's an example playbook that installs DebOps support on a host:

.. literalinclude:: ../../../../ansible/playbooks/service/controller.yml
   :language: yaml
   :lines: 1,5-

The playbooks is shipped with this role under
:file:`docs/playbooks/controller.yml` from which you can symlink it to your
playbook directory.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::controller``
  Main role tag, should be used in the playbook to execute all of the role
  tasks.
