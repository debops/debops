Getting started
===============

Default configuration
---------------------

The Postwhite script will be installed on its own UNIX system account and
executed as an unprivileged user. By default the script will be executed daily
by a wrapper to update the SPF whitelists; list of Yahoo! SMTP clients will be
updated weekly.

On the first run of the role, the Postwhite whitelist will be updated in the
background, since it takes ~5 minutes to do so. The wrapper script configured
by the role will automatically reload Postfix when the new whitelist is
generated.


Example inventory
-----------------

To install and configure Postwhite on a host, it needs to be present in the
``[debops_service_postwhite]`` Ansible inventory group. The Postfix server
should also be configured beforehand, with Postscreen enabled.

.. code-block:: none

   [debops_service_postfix]
   hostname

   [debops_service_postscreen]
   hostname

   [debops_service_postwhite]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.postwhite`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/postwhite.yml
   :language: yaml
