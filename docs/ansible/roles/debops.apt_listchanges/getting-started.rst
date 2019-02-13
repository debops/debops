Getting started
===============

.. contents:: Sections
   :local:

Default configuration
---------------------

By default only important NEWS changes will be sent by :command:`apt-listchanges` to
the system administrators. If the role detects that the ``apticron`` is
installed, mails from APT operations will be disabled.


Example inventory
-----------------

The ``debops.apt_listchanges`` role is included in the DebOps :file:`common.yml`
playbook and doesn't need to be enabled on a host.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt_listchanges`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_listchanges.yml
   :language: yaml
