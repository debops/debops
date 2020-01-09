Getting started
===============

.. contents::
   :local:


Default host customization
--------------------------

The role provides the :command:`run-wp-cron` Bash script which can be used to
execute the WP Cron tasks via the command line or :command:`cron` service.

A special daily :command:`cron` job is enabled by default; it looks for the
:file:`wp-config.php` files in the :file:`/home` and :file:`/srv` directories
and changes their permissions to ``0600`` if they are world-readable. This is
done because WordPress installer creates these files with ``0666`` permissions,
which is a security risk in shared hosting environments.


Example inventory
-----------------

To install the WP-CLI framework on a host, the host needs to be added to the
``[debops_service_wpcli]`` Ansible inventory group. This will also install the
PHP environment required to use the script.

.. code-block:: none

   [debops_service_wpcli]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.wpcli`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/wpcli.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::wpcli``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
