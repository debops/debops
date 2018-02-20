Getting started
===============

Default configuration
---------------------

The role will check if Postfix was installed on a host by looking for specific
Ansible fact defined by the :ref:`debops.postfix` role. If Postfix is detected,
``debops.saslauthd`` will automatically configure a ``smtpd`` authentication
service which can be used by Postfix.


Example inventory
-----------------

To install and configure Cyrus SASL daemon on a host, the host needs to be
present in the ``[debops_service_saslauthd]`` Ansible inventory group.

.. code-block:: none

   [debops_service_saslauthd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.saslauthd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/saslauthd.yml
   :language: yaml
