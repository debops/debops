Getting started
===============

Default configuration
---------------------

By default Postscreen will enable the DNS Blocklists if the host has public
IPv4/IPv6 addresses. The DNS Blocklists will be disabled on private networks.

Most of the Postfix configuration is defined in the dependent variables, you
can change the configuration through the inventory directly. Check the
:ref:`debops.postfix` documentation to see how to do this.


Example inventory
-----------------

To install and configure Postscreen on a host, it needs to be present in the
``[debops_service_postscreen]`` Ansible inventory group. The Postfix server
should also be configured beforehand.

.. code-block:: none

   [debops_service_postfix]
   hostname

   [debops_service_postscreen]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.postscreen`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/postscreen.yml
   :language: yaml

Keep in mind that the default Postscreen playbook does not configure firewall
access for Postfix. You still need to use the Postfix playbook to configure the
server instance initially.
