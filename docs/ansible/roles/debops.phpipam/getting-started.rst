Getting started
===============

.. contents::
   :local:


By default phpIPAM is installed on a separate system account ``"phpipam"``,
in :file:`/srv/www/phpipam/` subdirectory and will be accessible on
``https://ipam.<domain>/``. :ref:`debops.nginx` and :ref:`debops.php` roles are used
to configure the required environment.

Example inventory
-----------------

You can install phpIPAM on a host by adding it to
``[debops_service_phpipam]`` group in your Ansible inventory::

    [debops_service_phpipam]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.phpipam`` role to install
DokuWiki:

.. literalinclude:: ../../../../ansible/playbooks/service/phpipam.yml
   :language: yaml


Post-install steps
------------------

When Ansible is finished, you need to finish the configuration by opening the
``https://ipam.<domain>`` page. There you will be able to finish
the installation process.

You can then login and configure it using the administrative
interface.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::phpipam``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
