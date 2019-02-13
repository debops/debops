Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

By default, Monit uses the SMTP server installed on ``localhost`` to send
e-mails to the ``root`` account. Make sure that the working SMTP server or
relay is available with the proper forwarding, or change the configuration of
the mail server used by Monit via Ansible inventory.

The Monit HTTP server will be enabled by default, however it's not exposed to
the public network and only available on ``localhost`` interface. To protect
the HTTP interface against attacks by unprivileged users on the same host, the
HTTP interface is secured by a randomly generated password, stored in one of
the configuration files. The ``root`` account can use the :command:`monit` CLI
interface to interact with Monit without the need for a password.


Example inventory
-----------------

To enable Monit on a host, you need to add that host in the
``[debops_service_monit]`` Ansible inventory group:

.. code-block:: none

   [debops_service_monit]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.monit`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/monit.yml
   :language: yaml
