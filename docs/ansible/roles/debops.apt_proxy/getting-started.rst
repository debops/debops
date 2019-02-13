Getting started
===============

Default configuration
---------------------

The role will enable APT proxy support automatically if ``http_proxy``,
``https_proxy`` or ``ftp_proxy`` environment variables are set on a given host.
They can be configured using the :ref:`debops.environment` Ansible role.

Unfortunately using the above environment variables directly through :command:`sudo`
is problematic. To mitigate that, you can use the ``inventory__*_environment``
variables configured in the playbook to provide the correct variables to the
role. See the ``debops-playbooks`` documentation for more details.


Example inventory
-----------------

The ``debops.apt_proxy`` role is included by default in the :file:`common.yml`
DebOps playbook, you don't need to add hosts to any groups to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt_proxy`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_proxy.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::apt_proxy``
  Main role tag, should be used in the playbook to execute all tasks.
