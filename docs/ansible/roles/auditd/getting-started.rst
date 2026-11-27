.. Copyright (C) 2026 seven-beep <github@soulintheshell.com>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

:program:`Auditd` intercepts system calls and serializes audit log entries from
privileged user space applications.


CIS compliance
--------------

The default of this role will try to enforce the CIS recommendations for
:program:`auditd` on Debian 13.

Two divergences with the official recommendations being:

* The role will let :program:`auditd` rotate its own logs, otherwise it would by
  default inevitably halt the targeted machine when the logs would lack space.

* The role will not scan the file systems for SUID/GUID programs as it may be
  too disruptive. It can be switched on with
  :envvar:`auditd__privileged_discovery_policy`. Additionally
  :envvar:`auditd__privileged_discovery_max_size` controls at which file system
  size the scan will fail.


Workaround failures on missing directories
------------------------------------------

One current issue with :program:`auditd` is that for optimization reasons, it
recommends to stop using ``-w`` rules. However, the replacement will fail if it
targets a directory that do not exists, eventually putting the whole
:program:`auditd` daemon on failure.

For this reason the role will detect rules that target directories and comment
rules that target non existent directories.  You should be wary about
directories that may not exist at boot time (eg: in /run).

We recommend you to still use ``-w`` rules for these directories until the issue
is completely addressed.

Examples
~~~~~~~~

.. literalinclude:: examples/raw-w-rule.yml
   :language: yaml
   :lines: 1,4-

.. literalinclude:: examples/paths-rule.yml
   :language: yaml
   :lines: 1,4-

.. literalinclude:: examples/syscalls-rule.yml
   :language: yaml
   :lines: 1,4-


Example inventory
-----------------

To install auditd on a host, you need to add it to the
``[debops_service_auditd]`` Ansible group:

.. code-block:: none

    [debops_service_auditd]
    hostname

Please refer to :ref:`auditd__ref_defaults` for defaults variables.


Example playbook
----------------

You can refer to the current ``service/auditd.yml`` playbook:

.. literalinclude:: ../../../../ansible/playbooks/service/auditd.yml
   :language: yaml
   :lines: 1,4-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what tasks
are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::auditd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Resources
---------

`Official github repository for Auditd`__

.. __: https://github.com/linux-audit/audit-userspace
