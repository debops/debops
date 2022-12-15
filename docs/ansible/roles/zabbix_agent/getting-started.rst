.. Copyright (C) 2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Default configuration
---------------------

The role supports `multiple flavors of Zabbix Agent`__ included in Debian, one
if which needs to be specified using :envvar:`zabbix_agent__flavor` variable
(the default is ``C`` flavor). To change the installed flavor, the current
installation needs to be removed - to do that, you can execute the role with
and extra variable on the command line:

.. code-block:: console

   debops run service/zabbix_agent -e 'zabbix_agent__deploy_state=absent'

This will tell the role to remove the current installation. After that, by
changing the :envvar:`zabbix_agent__flavor` in the Ansible inventory, you can
install a different flavor of the Zabbix Agent.

.. __: https://www.zabbix.com/documentation/current/en/manual/appendix/agent_comparison


Example inventory
-----------------

To enable the Zabbix agent service on a host it needs to be included in the specific Ansible
inventory group:

.. code-block:: none

   [debops_service_zabbix_agent]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.zabbix_agent`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/zabbix_agent.yml
   :language: yaml
   :lines: 1,5-
