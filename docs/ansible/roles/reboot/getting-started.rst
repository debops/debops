.. Copyright (C) 2022 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

The role will check if a host requires a reboot - this is usually indicated by
the presence of the :file:`/var/run/reboot-required` file. If it's found, the
role will perform a reboot and will wait for the host to come back. Otherwise,
nothing will happen.

The reboot can be forced using the :envvar:`reboot__force` boolean variable,
either via inventory or using the ``--extra-vars`` :command:`ansible-playbook`
parameter, for example:

.. code-block:: console

   debops run reboot -l <host> -e 'reboot__force=true'

If the ``display_skipped_hosts`` option is set to ``False`` in the
:file:`ansible.cfg` configuration file, the task which performs the reboot will
not show up in the :command:`ansible-playbook` output immediately, which might
appear as Ansible "hanging" while waiting for the host to come back. This is an
expected behaviour.


Example inventory
-----------------

The playbook will work only on hosts that are in the main DebOps host group in
the Ansible inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname1
   hostname2


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.reboot`` role:

.. literalinclude:: ../../../../ansible/playbooks/reboot.yml
   :language: yaml
   :lines: 1,5-
